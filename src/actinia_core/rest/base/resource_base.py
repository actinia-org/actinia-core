# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2024 Sören Gebbert and mundialis GmbH & Co. KG
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#######

"""
Base class for asynchronous and synchronous responses
"""
import os
import pickle
import time
import uuid
from datetime import datetime
from flask import make_response, jsonify
from flask import request, g
from flask.json import loads as json_loads
from flask_restful_swagger_2 import Resource
from actinia_core.rest.base.deprecated_locations import (
    location_deprecated_decorator,
)
from actinia_core.rest.base.user_auth import check_user_permissions
from actinia_core.rest.base.user_auth import create_dummy_user
from actinia_core.core.common.app import auth
from actinia_core.core.common.app import flask_api
from actinia_core.core.common.config import global_config
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.core.messages_logger import MessageLogger
from actinia_core.core.resources_logger import ResourceLogger
from actinia_core.core.resource_data_container import ResourceDataContainer
from actinia_core.models.response_models import ProcessingResponseModel
from actinia_core.models.response_models import (
    create_response_from_model,
    ApiInfoModel,
)
from actinia_core.rest.resource_streamer import RequestStreamerResource
from actinia_core.rest.resource_management import ResourceManager


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class ResourceBase(Resource):
    """
    This is the base class for all asynchronous and synchronous processing
    resources.
    """

    # Authorization is required for all resources
    # User permissions must be checked for all resources
    # API logging is required for all resources
    # decorators = [log_api_call, check_user_permissions, auth.login_required]

    decorators = []

    # Add decorators for deprecated GRASS GIS locations
    decorators.append(location_deprecated_decorator)

    if global_config.LOG_API_CALL is True:
        decorators.append(log_api_call)

    if global_config.CHECK_CREDENTIALS is True:
        decorators.append(check_user_permissions)

    if global_config.LOGIN_REQUIRED is True:
        decorators.append(auth.login_required)
    else:
        decorators.append(create_dummy_user)

    def __init__(self, resource_id=None, iteration=None, post_url=None):
        # Configuration
        Resource.__init__(self)

        # Store the user id, user group and all credentials of the current user
        self.user = g.user
        self.user_id = g.user.get_id()
        self.user_group = g.user.get_group()
        self.user_role = g.user.get_role()
        self.has_superadmin_role = g.user.has_superadmin_role()
        self.user_credentials = g.user.get_credentials()

        self.orig_time = time.time()
        self.orig_datetime = str(datetime.now())

        kwargs = dict()
        kwargs["host"] = global_config.REDIS_SERVER_URL
        kwargs["port"] = global_config.REDIS_SERVER_PORT
        if (
            global_config.REDIS_SERVER_PW
            and global_config.REDIS_SERVER_PW is not None
        ):
            kwargs["password"] = global_config.REDIS_SERVER_PW
        self.resource_logger = ResourceLogger(**kwargs)
        del kwargs

        self.message_logger = MessageLogger()

        self.grass_data_base = global_config.GRASS_DATABASE
        self.grass_user_data_base = global_config.GRASS_USER_DATABASE
        self.grass_base_dir = global_config.GRASS_GIS_BASE
        self.grass_start_script = global_config.GRASS_GIS_START_SCRIPT
        self.grass_addon_path = global_config.GRASS_ADDON_PATH
        self.download_cache = os.path.join(
            global_config.DOWNLOAD_CACHE, self.user_id
        )

        # Set the resource id
        if resource_id is None:
            # Generate the resource id
            self.request_id, self.resource_id = self.generate_uuids()
        else:
            self.resource_id = resource_id
            self.request_id = self.generate_request_id_from_resource_id()

        if global_config.QUEUE_TYPE == "per_job":
            self.queue = "%s_%s" % (
                global_config.WORKER_QUEUE_PREFIX,
                self.resource_id,
            )
        elif global_config.QUEUE_TYPE == "per_user":
            self.queue = "%s_%s" % (
                global_config.WORKER_QUEUE_PREFIX,
                self.user_id,
            )
        elif global_config.QUEUE_TYPE == "redis":
            self.queue = "%s_%s" % (global_config.WORKER_QUEUE_PREFIX, "count")
        else:
            self.queue = "local"

        # set iteration and post_url
        self.iteration = iteration
        self.post_url = post_url

        # The base URL's for resources that will be streamed
        self.resource_url_base = None

        # Generate the status URL
        self.status_url = flask_api.url_for(
            ResourceManager,
            user_id=self.user_id,
            resource_id=self.resource_id,
            _external=True,
        )

        if (
            global_config.FORCE_HTTPS_URLS is True
            and "http://" in self.status_url
        ):
            self.status_url = self.status_url.replace("http://", "https://")

        self.request_url = request.url
        self.resource_url = None
        self.request_data = None
        self.response_data = None
        self.job_timeout = 0

        # Replace this with the correct response model in subclasses
        # The class that is used to create the response
        self.response_model_class = ProcessingResponseModel

        # Put API information in the response for later accounting
        kwargs = {
            # For deprecated location endpoints remove "_locations" from
            # endpoint class name
            "endpoint": request.endpoint.replace("_locations", ""),
            "method": request.method,
            "path": request.path,
            "request_url": self.request_url,
        }
        if self.post_url is not None:
            kwargs["post_url"] = self.post_url
        self.api_info = ApiInfoModel(**kwargs)

    def create_error_response(self, message, status="error", http_code=400):
        """Create an error response, that by default sets the status to error
        and the http_code to 400

        This method sets the self.response_data variable.

        Args:
            message: The error message
            status: The status, by default error
            http_code: The hhtp code by default 400

        """
        self.response_data = create_response_from_model(
            self.response_model_class,
            status=status,
            user_id=self.user_id,
            resource_id=self.resource_id,
            queue=self.queue,
            iteration=self.iteration,
            process_log=None,
            results={},
            message=message,
            http_code=http_code,
            orig_time=self.orig_time,
            orig_datetime=self.orig_datetime,
            status_url=self.status_url,
            api_info=self.api_info,
        )

    def get_error_response(self, message, status="error", http_code=400):
        """Return the error response.

        This function will generate an error response using make_response()
        In addition, a resource update is send using the error response.

        Args:
            message: The error message
            status: The status, by default error
            http_code: The http code by default 400

        Returns:
            the result of make_response()

        """
        self.create_error_response(
            message=message, status=status, http_code=http_code
        )
        self.resource_logger.commit(
            user_id=self.user_id,
            resource_id=self.resource_id,
            iteration=self.iteration,
            document=self.response_data,
        )
        http_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), http_code)

    def check_for_json(self):
        """Check if the Payload is a JSON document

        Return: bool:
            True in case of success, False otherwise
        """
        # First check for the data field and create JSON from it
        if hasattr(request, "data") is True:
            try:
                self.request_data = json_loads(request.data)
            except Exception as e:
                self.create_error_response(
                    message="No JSON data in request: Exception: %s" % str(e)
                )
                return False

        if request.is_json is False:
            self.create_error_response(message="No JSON data in request")
            return False

        self.request_data = request.get_json()

        return True

    def check_for_xml(self):
        """Check if the Payload is a XML document

        Return: bool:
            True in case of success, False otherwise
        """

        if "Content-Type" not in request.headers:
            self.create_error_response(message="XML content type is required.")
            return False

        if "XML" not in request.headers["Content-Type"].upper():
            self.create_error_response(message="XML content type is required.")
            return False

        # Check if payload was provided
        if hasattr(request, "data") is False:
            self.create_error_response(
                message="No XML data section in HTTP header."
            )
            return False

        if request.data:
            self.request_data = request.data
            return True
        else:
            self.create_error_response(
                message="Empty XML data section in HTTP header."
            )
            return False

    def preprocess(
        self,
        has_json=True,
        has_xml=False,
        project_name=None,
        mapset_name=None,
        map_name=None,
        process_chain_list=None,
    ):
        """Preprocessing steps for asynchronous processing

            - Check if the request has a data field
            - Check if the module chain description can be loaded
            - Initialize the response and request ids as well as the
              url for status polls
            - Send an accept entry to the resource redis database

        Args:
            has_json (bool): Set True if the request has JSON data, False
                             otherwise
            has_xml (bool): Set True if the request has XML data, False
                            otherwise
            project_name (str): The name of the project to work in
            mapset_name (str): The name of the target mapset in which the
                               computation should be performed
            map_name: The name of the map or other resource (raster, vector,
                      STRDS, color, ...)
            process_chain_list (dict): The process chain list (e.g. for the
                                       job resumption when no new postbody is
                                       send in the PUT request)

        Returns:
            The ResourceDataContainer that contains all required information
            for the async process or None if the request was wrong. Then use
            the self.response_data variable to send a response.

        """
        if has_json is True and has_xml is True:
            if request.is_json is True:
                self.request_data = request.get_json()
            else:
                if self.check_for_xml() is False:
                    return None
        elif has_xml is True:
            if self.check_for_xml() is False:
                return None
        elif has_json is True:
            if self.check_for_json() is False:
                return None
        elif process_chain_list is not None:
            self.request_data = process_chain_list

        # Compute the job timeout of the worker queue from the user credentials
        process_time_limit = self.user_credentials["permissions"][
            "process_time_limit"
        ]
        process_num_limit = self.user_credentials["permissions"][
            "process_num_limit"
        ]
        self.job_timeout = int(process_time_limit * process_num_limit * 20)

        # Create the resource URL base and use a placeholder for the file name
        # The placeholder __None__ must be replaced by the resource URL
        # generator
        self.resource_url_base = flask_api.url_for(
            RequestStreamerResource,
            user_id=self.user_id,
            resource_id=self.resource_id,
            file_name="__None__",
            _external=True,
        )

        if (
            global_config.FORCE_HTTPS_URLS is True
            and "http://" in self.resource_url_base
        ):
            self.resource_url_base = self.resource_url_base.replace(
                "http://", "https://"
            )

        # Create the accepted response that will be always send
        self.response_data = create_response_from_model(
            self.response_model_class,
            status="accepted",
            user_id=self.user_id,
            resource_id=self.resource_id,
            queue=self.queue,
            iteration=self.iteration,
            process_log=None,
            results={},
            message="Resource accepted",
            http_code=200,
            orig_time=self.orig_time,
            orig_datetime=self.orig_datetime,
            status_url=self.status_url,
            api_info=self.api_info,
        )

        # Send the status to the database
        self.resource_logger.commit(
            self.user_id, self.resource_id, self.iteration, self.response_data
        )

        # Return the ResourceDataContainer that includes all
        # required data for the asynchronous processing
        return ResourceDataContainer(
            grass_data_base=self.grass_data_base,
            grass_user_data_base=self.grass_user_data_base,
            grass_base_dir=self.grass_base_dir,
            request_data=self.request_data,
            user_id=self.user_id,
            user_group=self.user_group,
            user_credentials=self.user_credentials,
            resource_id=self.resource_id,
            iteration=self.iteration,
            status_url=self.status_url,
            api_info=self.api_info,
            resource_url_base=self.resource_url_base,
            orig_time=self.orig_time,
            orig_datetime=self.orig_datetime,
            config=global_config,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=map_name,
        )

    def generate_uuids(self):
        """Return a unique request and resource id based on uuid4

        Returns:
            (str, str):
            request_id, resource_id as strings
        """
        new_uuid = uuid.uuid4()
        request_id = "request_id-" + str(new_uuid)
        resource_id = "resource_id-" + str(new_uuid)

        return request_id, resource_id

    def generate_request_id_from_resource_id(self):
        return self.resource_id.replace("resource_id-", "request_id-")

    def wait_until_finish(self, poll_time=0.2):
        """Wait until a resource finished, terminated or failed with an error

        Call this method if a job was enqueued and the POST/GET/DELETE/PUT
        method should wait for it

        Args:
            poll_time (float): Time to sleep between Redis db polls for process
                               status requests

        Returns:
            (int, dict)
            The http_code and the generated data dictionary
        """
        # Wait for the async process by asking the redis database for updates
        while True:
            response_data = self.resource_logger.get(
                self.user_id, self.resource_id, self.iteration
            )
            if not response_data:
                message = (
                    "Unable to receive process status. User id "
                    "%s resource id %s and iteration %d"
                    % (self.user_id, self.resource_id, self.iteration)
                )
                return make_response(message, 400)

            http_code, response_model = pickle.loads(response_data)
            if (
                response_model["status"] == "finished"
                or response_model["status"] == "error"
                or response_model["status"] == "timeout"
                or response_model["status"] == "terminated"
            ):
                break
            time.sleep(poll_time)

        return (http_code, response_model)
