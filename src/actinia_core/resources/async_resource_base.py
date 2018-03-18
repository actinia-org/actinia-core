# -*- coding: utf-8 -*-
"""
Base class for asynchronous responses
"""
import pickle
import time
import uuid
from datetime import datetime
from flask import make_response, jsonify
from flask import request, g
from flask.json import loads as json_loads
from flask_restful_swagger_2 import Resource
from actinia_core.resources.common.app import auth
from actinia_core.resources.common.app import flask_api
from actinia_core.resources.common.config import global_config
from actinia_core.resources.common.logging_interface import log_api_call
from actinia_core.resources.common.messages_logger import MessageLogger
from actinia_core.resources.common.resources_logger import ResourceLogger
from actinia_core.resources.common.exceptions import InvalidUsage
from actinia_core.resources.common.resource_data_container import ResourceDataContainer
from actinia_core.resources.common.response_models import ProcessingResponseModel
from actinia_core.resources.common.response_models import create_response_from_model, ApiInfoModel
from actinia_core.resources.resource_streamer import RequestStreamerResource
from actinia_core.resources.user_auth import check_user_permissions, create_dummy_user
from actinia_core.resources.resource_management import ResourceManager

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class AsyncEphemeralResourceBase(Resource):
    """This is the base class for all GRASS GIS asynchronous processing resources.
    """

    # Authorization is required for all resources
    # User permissions must be checked for all resources
    # API logging is required for all resources
    # decorators = [log_api_call, check_user_permissions, auth.login_required]

    decorators = []

    if global_config.LOG_API_CALL is True:
        decorators.append(log_api_call)

    if global_config.CHECK_CREDENTIALS is True:
        decorators.append(check_user_permissions)

    if global_config.LOGIN_REQUIRED is True:
        decorators.append(auth.login_required)
    else:
        decorators.append(create_dummy_user)

    def __init__(self):

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

        self.resource_logger = ResourceLogger(host=global_config.REDIS_SERVER_URL,
                                              port=global_config.REDIS_SERVER_PORT)
        self.message_logger = MessageLogger()

        self.grass_data_base = global_config.GRASS_DATABASE
        self.grass_user_data_base = global_config.GRASS_USER_DATABASE
        self.grass_base_dir = global_config.GRASS_GIS_BASE
        self.grass_start_script = global_config.GRASS_GIS_START_SCRIPT
        self.grass_addon_path = global_config.GRASS_ADDON_PATH

        # Generate the resource id
        self.request_id, self.resource_id = self.generate_uuids()

        # The base URL's for resources that will be streamed
        self.resource_url_base = None

        # Generate the status URL
        self.status_url = flask_api.url_for(ResourceManager,
                                            user_id=self.user_id,
                                            resource_id=self.resource_id,
                                            _external=True)

        if global_config.FORCE_HTTPS_URLS is True and "http://" in self.status_url:
            self.status_url = self.status_url.replace("http://", "https://")

        self.request_url = request.url
        self.resource_url = None
        self.request_data = None
        self.response_data = None
        self.job_timeout = 0

        # Replace this with the correct response model in subclasses
        self.response_model_class = ProcessingResponseModel  # The class that is used to create the response

        # Put API information in the response for later accounting
        self.api_info = ApiInfoModel(endpoint=request.endpoint,
                                     method=request.method,
                                     path=request.path,
                                     request_url=self.request_url)

    def raise_invalid_usage(self, message, status_code=400):
        """
        Invoke the InvalidUsage exception and send an error status to the Redis database

        Args:
            message: The error message that should be shown to the user
            status_code: The HTTP status code

        Raises:
            InvalidUsage exception

        """
        iua = InvalidUsage(message=message, user_id=self.user_id, resource_id=self.resource_id,
                           status_url=self.status_url, orig_time=self.orig_time,
                           orig_datetime=self.orig_datetime, status_code=status_code)
        self.message_logger.error("Error: status code %s message: %s" % (str(status_code), message))
        self.resource_logger.commit(user_id=self.user_id, resource_id=self.resource_id, document=iua.to_pickle(),
                                    expiration=global_config.REDIS_RESOURCE_EXPIRE_TIME)
        raise iua

    def create_error_response(self, message, status="error", http_code=400):
        """Create an error response, that by default sets the status to error and the http_code to 400

        This method sets the self.response_data variable.

        Args:
            message: The error message
            status: The status, by default error
            http_code: The hhtp code by default 400

        """
        self.response_data = create_response_from_model(self.response_model_class,
                                                        status=status,
                                                        user_id=self.user_id,
                                                        resource_id=self.resource_id,
                                                        process_log=None,
                                                        results={},
                                                        message=message,
                                                        http_code=http_code,
                                                        orig_time=self.orig_time,
                                                        orig_datetime=self.orig_datetime,
                                                        status_url=self.status_url,
                                                        api_info=self.api_info)

    def get_error_response(self, message, status="error", http_code=400):
        """Return the error response.

        This function will generate an error response using make_response()
        In addition, a resource update is send using the error response.

        Args:
            message: The error message
            status: The status, by default error
            http_code: The hhtp code by default 400

        Returns:
            the result of make_response()

        """
        self.create_error_response(message=message, status=status, http_code=http_code)
        self.resource_logger.commit(user_id=self.user_id,
                                    resource_id=self.resource_id,
                                    document=self.response_data)
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
                self.create_error_response(message="No JSON data in request: Exception: %s" % str(e))
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
            self.create_error_response(message="No XML data section in HTTP header.")
            return False

        if request.data:
            self.request_data = request.data
            return True
        else:
            self.create_error_response(message="Empty XML data section in HTTP header.")
            return False

    def preprocess(self, has_json=True, has_xml=False,
                   location_name=None, mapset_name=None, map_name=None):
        """Preprocessing steps for asynchronous processing

            - Check if the request has a data field
            - Check if the module chain description can be loaded
            - Initialize the response and request ids as well as the
              url for status polls
            - Send an accept entry to the resource redis database

        Args:
            has_json (bool):Set True if the request has JSON data, False otherwise
            has_xml (bool):Set True if the request has XML data, False otherwise
            location_name (str): The name of the location to work in
            mapset_name (str): The name of the target mapset in which the computation should be performed
            map_name: The name of the map or other resource (raster, vector, STRDS, color, ...)

        Returns:
            The ResourceDataContainer that contains all required information for the async process
            or None if the request was wrong. Then use the self.response_data variable to send a response.

        """
        print("Hello")
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

        # Compute the job timeout of the worker queue from the user credentials
        process_time_limit = self.user_credentials["permissions"]["process_time_limit"]
        process_num_limit = self.user_credentials["permissions"]["process_num_limit"]
        self.job_timeout = int(process_time_limit * process_num_limit * 20)

        # Create the resource URL base and use a placeholder for the file name
        # The placeholder __None__ must be replaced by the resource URL generator
        self.resource_url_base = flask_api.url_for(RequestStreamerResource,
                                                   user_id=self.user_id,
                                                   resource_id=self.resource_id,
                                                   file_name="__None__",
                                                   _external=True)

        if global_config.FORCE_HTTPS_URLS is True and "http://" in self.resource_url_base:
            self.resource_url_base = self.resource_url_base.replace("http://", "https://")

        # Create the accepted response that will be always send
        self.response_data = create_response_from_model(self.response_model_class,
                                                        status="accepted",
                                                        user_id=self.user_id,
                                                        resource_id=self.resource_id,
                                                        process_log=None,
                                                        results={},
                                                        message="Resource accepted",
                                                        http_code=200,
                                                        orig_time=self.orig_time,
                                                        orig_datetime=self.orig_datetime,
                                                        status_url=self.status_url,
                                                        api_info=self.api_info)

        # Send the status to the database
        self.resource_logger.commit(self.user_id, self.resource_id, self.response_data)

        # Return the ResourceDataContainer that includes all
        # required data for the asynchronous processing
        return ResourceDataContainer(grass_data_base=self.grass_data_base,
                                     grass_user_data_base=self.grass_user_data_base,
                                     grass_base_dir=self.grass_base_dir,
                                     request_data=self.request_data,
                                     user_id=self.user_id,
                                     user_group=self.user_group,
                                     user_credentials=self.user_credentials,
                                     resource_id=self.resource_id,
                                     status_url=self.status_url,
                                     api_info=self.api_info,
                                     resource_url_base=self.resource_url_base,
                                     orig_time=self.orig_time,
                                     orig_datetime=self.orig_datetime,
                                     config=global_config,
                                     location_name=location_name,
                                     mapset_name=mapset_name,
                                     map_name=map_name)

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

    def wait_until_finish(self, poll_time=0.2):
        """Wait until a resource finished, terminated or failed with an error

        Call this method if a job was enqueued and the POST/GET/DELETE/PUT method should wait for it

        Args:
            poll_time (float): Time to sleep between Redis db polls for process status requests

        Returns:
            (int, dict)
            The http_code and the generated data dictionary
        """
        # Wait for the async process by asking the redis database for updates
        while True:
            response_data = self.resource_logger.get(self.user_id,
                                                     self.resource_id)
            if not response_data:
                message = "Unable to receive process status. User id %s resource id %s" % (self.user_id,
                                                                                           self.resource_id)
                return make_response(message, 400)

            http_code, response_model = pickle.loads(response_data)
            if response_model["status"] == "finished" \
                    or response_model["status"] == "error" \
                    or response_model["status"] == "timeout" \
                    or response_model["status"] == "terminated":
                break
            time.sleep(poll_time)

        return (http_code, response_model)
