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
Base class for asynchronous processing
"""

import math
import os
import pickle
import requests
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import uuid

from flask import json
from requests.auth import HTTPBasicAuth

from actinia_core.core.common.config import global_config, DEFAULT_CONFIG_PATH
from actinia_core.core.common.process_object import Process
from actinia_core.core.grass_init import GrassInitializer
from actinia_core.core.messages_logger import MessageLogger
from actinia_core.core.redis_lock import RedisLockingInterface
from actinia_core.core.resources_logger import ResourceLogger
from actinia_core.core.mapset_merge_utils import change_mapsetname
from actinia_core.core.common.process_chain import (
    get_param_stdin_part,
    ProcessChainConverter,
)
from actinia_core.core.common.exceptions import (
    AsyncProcessError,
    AsyncProcessTermination,
    RsyncError,
)
from actinia_core.core.common.exceptions import AsyncProcessTimeLimit
from actinia_core.models.response_models import (
    ProcessingResponseModel,
    ExceptionTracebackModel,
)
from actinia_core.models.response_models import (
    create_response_from_model,
    ProcessLogModel,
    ProgressInfoModel,
)
from actinia_core.core.interim_results import InterimResult, get_directory_size
from actinia_core.rest.base.user_auth import (
    check_project_mapset_module_access,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann, Lina Krisztian"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"


class EphemeralProcessing(object):
    """This class processes GRASS data on the local machine in a temporary
    mapset.

    The temporary mapset will be removed by this class when the processing is
    finished

    Creating the temporary database and mapset:

    1. Create a new gisdbase in a temporary directory

       e.g: /tmp/soeren_disdbase

    2. Create the required project directory

       e.g: /tmp/soeren_temp_gisdbase/ECAD

    3. Softlink the PERMANENT and all required mapsets into the
       new project directory from the original project,
       check the input parameter of the module for which mapsets must be linked

       e.g: /mount/groups/[user group]/projects/ECAD/PERMANENT
        -> /tmp/soeren_temp_gisdbase/ECAD/PERMANENT
       e.g: /mount/groups/[user group]/projects/ECAD/Temperature
        -> /tmp/soeren_temp_gisdbase/ECAD/Temperature

    4. Set the GRASS GIS environmental variables to point to the new gisdbase,
       project and PERMANENT mapset

    5. Create a new mapset with g.mapset in the temporary project directory

       e.g: /tmp/soeren_temp_gisdbase/ECAD/MyMapset

    6. Run and poll each process in the process chain until finished and update
       the resource log entry
       - Create a poll loop and check the subprocess status
       - Update the resource entry with progress info

    7. When finished create the response:
         * put the output of all modules into the response document

    8. Remove the temporary gisdbase

    9. Send the response document with status finished and resource links

    """

    def __init__(self, rdc):
        """Constructor

        Args:
            rdc (ResourceDataContainer): The data container that contains all
                                         required variables for processing

        """
        # Fluentd hack to work in a multiprocessing environment
        try:
            from fluent import sender

            if sender:
                self.has_fluent = True
        except Exception:
            self.has_fluent = False

        # rdc = ResourceDataContainer()

        self.rdc = rdc
        if os.path.exists(DEFAULT_CONFIG_PATH) is True and os.path.isfile(
            DEFAULT_CONFIG_PATH
        ):
            self.config = global_config
            self.rdc.config = self.config
        else:
            self.config = self.rdc.config

        self.data = self.rdc.user_data
        self.grass_temp_database = self.config.GRASS_TMP_DATABASE

        self.request_data = self.rdc.request_data
        self.user_id = self.rdc.user_id
        self.user_group = self.rdc.user_group
        self.user_credentials = rdc.user_credentials

        self.resource_id = self.rdc.resource_id
        self.iteration = self.rdc.iteration
        self.status_url = self.rdc.status_url
        self.api_info = self.rdc.api_info
        self.interim_result = InterimResult(
            self.user_id,
            self.resource_id,
            self.iteration,
            self.api_info["endpoint"],
        )

        self.grass_data_base = self.rdc.grass_data_base  # Global database
        # User database base path, this path will be
        self.grass_user_data_base = self.rdc.grass_user_data_base
        # extended with the user group name in the setup
        self.grass_base_dir = self.rdc.grass_base_dir

        self.project_name = self.rdc.project_name
        self.mapset_name = self.rdc.mapset_name
        # Set this True if the work is performed based on global database
        self.is_global_database = False

        self.map_name = self.rdc.map_name

        self.orig_time = self.rdc.orig_time
        self.orig_datetime = self.rdc.orig_datetime

        # Create the unique temporary gisdbase and mapset names
        self.unique_id = str(uuid.uuid4()).replace("-", "")
        self.temp_grass_data_base_name = "gisdbase_" + self.unique_id
        self.temp_mapset_name = "mapset_" + self.unique_id
        self.temp_mapset_path = None

        self.ginit = None
        self.ginit_tmpfiles = list()

        # Successfully finished message
        self.finish_message = "Processing successfully finished"

        # The temporary GRASS database
        self.temp_grass_data_base = (
            None  # Path to the temporary grass database
        )
        self.temp_project_path = None  # Path to the temporary project
        self.temp_file_path = None  # The path to store temporary created files
        self.global_project_path = (
            None  # The path to the global project to link
        )
        self.user_project_path = None  # The path to the user project to link

        # List of resources that should be created
        self.resource_export_list = list()
        self.resource_url_list = list()

        # Initialize the user specific permissions
        self.cell_limit = 0
        self.process_time_limit = 0
        self.process_num_limit = 0
        # Set this True so that regions are not checked before processing
        self.skip_region_check = False

        # The stdout, stderr and parameter log of the module chains
        self.module_output_log = list()
        # The stdout, stderr and parameter log of the module chains
        # using a dict with the process id as key
        self.module_output_dict = dict()
        # The list of output parser definitions that must be applied
        # after the module run. The parser result will be stored in
        # the module_result dictionary using the parser id
        self.output_parser_list = []
        # A dictionary that has the process id as key to store module
        self.module_results = dict()
        # outputs like images, dicts, files and so on

        self.required_mapsets = (
            list()
        )  # The process chain analysis will provide
        # a list of required mapsets that must be
        # linked in the temporary project

        # The module that was called in the process chain, to detect g.region
        # calls and check for correct region settings
        self.last_module = "g.region"
        # Count the processes executed from the process chain
        self.process_count = 0

        self.ginit = None

        # The state of the whole processing that is checked in the final
        # section of the run function
        self.run_state = {"success": None}

        # The progress info object
        self.progress = ProgressInfoModel(step=0, num_of_steps=0)
        # The count of self._run_process() and self._run_module() calls
        self.progress_steps = 0
        # The number of processes that should be processes
        self.number_of_processes = 0

        self.setup_flag = False

        # The names of the temporarily generated files
        # "key":"temporary_file_path"
        self.temporary_pc_files = {}
        # The counter to generate unique temporary file names
        self.temp_file_count = 0
        # This dictionary contains the output of a process on stdout
        self.process_dict = {}

        # The class that is used to create the response
        self.response_model_class = ProcessingResponseModel
        # The class that converts process chain definitions into
        self.proc_chain_converter = None
        # process lists that will be executed. This variable is
        # initiated in the setup method
        # The list of all process chains that were processed
        self.process_chain_list = []
        # A list of all processes that will be executed
        self.actinia_process_list = list()
        # A list of all processes that will be executed
        self.actinia_process_dict = dict()
        # The URL of a webhook that should becalled after processing of a
        self.webhook_finished = None
        # process chain finished

        # The URL of a webhook that should be called for each status/progress
        # update
        self.webhook_update = None
        # The authentication for the webhook (base 64 decoded
        # "username:password")
        self.webhook_auth = None

    def _send_resource_update(self, message, results=None):
        """Create an HTTP response document and send it to the status database

        Args:
            message (str): The message
            results (dict): Results of the processing using the process chain
                            id for identification

        """
        data = create_response_from_model(
            self.response_model_class,
            status="running",
            user_id=self.user_id,
            resource_id=self.resource_id,
            queue=self.rdc.queue,
            iteration=self.iteration,
            # process_log=self.module_output_log,
            progress=self.progress,
            results=results,
            message=message,
            orig_time=self.orig_time,
            orig_datetime=self.orig_datetime,
            http_code=200,
            status_url=self.status_url,
            api_info=self.api_info,
        )
        self._send_to_database(document=data, final=False)

    def _send_resource_finished(self, message, results=None):
        """Create an HTTP response document and send it to the status database

        Args:
            message (str): The message
            results (dict): Results of the processing using the process chain
                            id for identification

        """
        data = create_response_from_model(
            self.response_model_class,
            status="finished",
            user_id=self.user_id,
            resource_id=self.resource_id,
            queue=self.rdc.queue,
            iteration=self.iteration,
            process_log=self.module_output_log,
            progress=self.progress,
            results=results,
            message=message,
            orig_time=self.orig_time,
            orig_datetime=self.orig_datetime,
            http_code=200,
            status_url=self.status_url,
            api_info=self.api_info,
            resource_urls=self.resource_url_list,
            process_chain_list=self.process_chain_list,
        )
        self._send_to_database(document=data, final=True)

    def _send_resource_terminated(self, message, results=None):
        """Create an HTTP response document and send it to the status database

        Args:
            message (str): The message
            results (dict): Results of the processing using the process chain
                            id for identification

        """
        data = create_response_from_model(
            self.response_model_class,
            status="terminated",
            user_id=self.user_id,
            resource_id=self.resource_id,
            queue=self.rdc.queue,
            iteration=self.iteration,
            process_log=self.module_output_log,
            progress=self.progress,
            results=results,
            message=message,
            orig_time=self.orig_time,
            orig_datetime=self.orig_datetime,
            http_code=200,
            status_url=self.status_url,
            api_info=self.api_info,
            process_chain_list=self.process_chain_list,
        )
        self._send_to_database(document=data, final=True)

    def _send_resource_time_limit_exceeded(self, message, results=None):
        """Create an HTTP response document and send it to the status database

        Args:
            message (str): The message
            results (dict): Results of the processing using the process chain
                            id for identification

        """
        data = create_response_from_model(
            self.response_model_class,
            status="terminated",
            user_id=self.user_id,
            resource_id=self.resource_id,
            queue=self.rdc.queue,
            iteration=self.iteration,
            process_log=self.module_output_log,
            progress=self.progress,
            results=results,
            message=message,
            orig_time=self.orig_time,
            orig_datetime=self.orig_datetime,
            http_code=400,
            status_url=self.status_url,
            api_info=self.api_info,
            process_chain_list=self.process_chain_list,
        )
        self._send_to_database(document=data, final=True)

    def _send_resource_error(self, message, results=None, exception=None):
        """Create an HTTP response document and send it to the status database

        Args:
            message (str): The message
            results (dict): Results of the processing using the process chain
                            id for identification

        """
        data = create_response_from_model(
            self.response_model_class,
            status="error",
            user_id=self.user_id,
            resource_id=self.resource_id,
            queue=self.rdc.queue,
            iteration=self.iteration,
            process_log=self.module_output_log,
            progress=self.progress,
            results=results,
            message=message,
            orig_time=self.orig_time,
            orig_datetime=self.orig_datetime,
            http_code=400,
            status_url=self.status_url,
            api_info=self.api_info,
            process_chain_list=self.process_chain_list,
            exception=exception,
        )
        self._send_to_database(document=data, final=True)

    def _send_to_database(self, document, final=False):
        """Send the document to the database

        The resource expiration time set in the actinia config file will be
        used for every resource commit.

        If a webhook URL is provided, the JSON response will be send to the
        provided endpoint using a POST request.

        Args:
            document (str): The response document
            final (bool): Set True if this was the final resource commit
                          (no update) to activate the webhook call

        """

        self.resource_logger.commit(
            user_id=self.user_id,
            resource_id=self.resource_id,
            iteration=self.iteration,
            document=document,
            expiration=self.config.REDIS_RESOURCE_EXPIRE_TIME,
        )

        # Call the webhook after the final result was send to the database
        try:
            if final is True and self.webhook_finished is not None:
                self._post_to_webhook(document, "finished")
            elif final is False and self.webhook_update is not None:
                self._post_to_webhook(document, "update")
        except Exception as e:
            e_type, e_value, e_tb = sys.exc_info()
            model = ExceptionTracebackModel(
                message=str(e_value),
                traceback=traceback.format_tb(e_tb),
                type=str(e_type),
            )
            run_state = {"error": str(e), "exception": model}
            print(str(run_state))
            self.message_logger.error(
                "Unable to send webhook request. Traceback: %s"
                % str(run_state)
            )

    def _post_to_webhook(self, document, type):
        """Helper method to send a post request to a webhook.
        The finished webhook will be retried until it has reached the number
        of tries. The number of tries is WEBHOOK_RETRIES which can be set in the
        config.

        Args:
            document (str): The response document
            type (str): The webhook type: 'finished' or 'update'
        """
        self.message_logger.info(
            "Send POST request to %s webhook url: %s"
            % (type, self.webhook_finished)
        )
        webhook_url = None
        if type == "finished":
            webhook_url = self.webhook_finished
            webhook_retries = self.config.WEBHOOK_RETRIES
            webhook_sleep = self.config.WEBHOOK_SLEEP
        if type == "update":
            webhook_url = self.webhook_update
            webhook_retries = 1
            webhook_sleep = 0

        _, response_model = pickle.loads(document)

        webhook_not_reached = True
        retry = 0
        while webhook_not_reached is True and retry < webhook_retries:
            retry += 1
            try:
                if self.webhook_auth:
                    # username is expected to be without colon (':')
                    resp = requests.post(
                        webhook_url,
                        json=json.dumps(response_model),
                        auth=HTTPBasicAuth(
                            self.webhook_auth.split(":")[0],
                            ":".join(self.webhook_auth.split(":")[1:]),
                        ),
                        timeout=10,
                    )
                else:
                    resp = requests.post(
                        webhook_url,
                        json=json.dumps(response_model),
                        timeout=10,
                    )
                if not (500 <= resp.status_code and resp.status_code < 600):
                    webhook_not_reached = False
            except Exception:
                time.sleep(webhook_sleep)
        if (
            webhook_not_reached is False and resp.status_code not in [200, 204]
        ) or webhook_not_reached is True:
            raise AsyncProcessError(
                "Unable to access %s webhook URL %s" % (type, webhook_url)
            )

    def _get_previous_iteration_process_chain(self):
        """Helper method to check the old resource run and get the step of the
        process chain where to continue

        Returns:
            pc_step (int): The number of the step in the process chain where to
                           continue
           old_process_chain (dict): The process chain of the old resource run
        """
        # check old resource
        pc_step = 0

        for iter in range(1, self.rdc.iteration):
            if iter == 1:
                old_response_data = self.resource_logger.get(
                    self.user_id, self.resource_id
                )
            else:
                old_response_data = self.resource_logger.get(
                    self.user_id, self.resource_id, iter
                )
            if old_response_data is None:
                return None
            _, response_model = pickle.loads(old_response_data)
            for element in response_model["process_log"]:
                self.module_output_dict[element["id"]] = element

            pc_step += response_model["progress"]["step"] - 1
        old_process_chain = response_model["process_chain_list"][0]

        return pc_step, old_process_chain

    def _validate_process_chain(
        self,
        process_chain=None,
        skip_permission_check=False,
        old_process_chain=None,
        pc_step=None,
    ):
        """
        Create the process list and check for user permissions.

        The following permissions are checked:

            - If the required modules are in the users module white list
            - If the user is allowed to access the required mapsets that
              are specified in the module input parameter
            - If the user is allowed to execute the number of processes

        Args:
            process_chain (dict): The process chain to be checked and converted
                                  into a process list
            skip_permission_check (bool): If set True, the permission checks
                                          of module access and process num
                                          limits are not performed
            old_process_chain (dict): The process chain of the previous
                                      resource run to be checked and converted
                                      for e.g. stdout

        Raises:
            This function raises AsyncProcessError in case of an error.

        Returns: list:
            The process list
        """

        if old_process_chain is not None:
            self.proc_chain_converter.process_chain_to_process_list(
                old_process_chain
            )
            self.proc_chain_converter.import_descr_list = list()
            self.proc_chain_converter.resource_export_list = list()

        # Backward compatibility
        if process_chain is None:
            process_list = (
                self.proc_chain_converter.process_chain_to_process_list(
                    self.request_data
                )
            )
            self.process_chain_list.append(self.request_data)
        else:
            process_list = (
                self.proc_chain_converter.process_chain_to_process_list(
                    process_chain
                )
            )
            self.process_chain_list.append(process_chain)
        if pc_step is not None:
            del process_list[:pc_step]

        # Check for the webhook
        if (
            hasattr(self.proc_chain_converter, "webhook_finished")
            and self.proc_chain_converter.webhook_finished is not None
        ):
            self.webhook_finished = self.proc_chain_converter.webhook_finished
        if (
            hasattr(self.proc_chain_converter, "webhook_update")
            and self.proc_chain_converter.webhook_update is not None
        ):
            self.webhook_update = self.proc_chain_converter.webhook_update
        if (
            hasattr(self.proc_chain_converter, "webhook_auth")
            and self.proc_chain_converter.webhook_auth is not None
        ):
            self.webhook_auth = self.proc_chain_converter.webhook_auth

        # Check for empty process chain
        if len(process_list) == 0 and len(self.resource_export_list) == 0:
            raise AsyncProcessError("Empty process chain, nothing to compute")

        # Check if the user is allowed to execute this number of processes
        if (
            skip_permission_check is False
            and len(process_list) > self.process_num_limit
        ):
            raise AsyncProcessError(
                "Process limit exceeded, a maximum of %i "
                "processes are allowed in the process chain."
                % self.process_num_limit
            )

        # Check if the module description was correct and if the
        # module or executable is in the user white list.
        for process in process_list:
            # Add the process to the internal list and dict
            # to access it in the python udf environment
            self._add_actinia_process(process)

            if process.exec_type == "grass" or process.exec_type == "exec":
                if skip_permission_check is False:
                    if process.skip_permission_check is False:
                        resp = check_project_mapset_module_access(
                            user_credentials=self.user_credentials,
                            config=self.config,
                            module_name=process.executable,
                        )
                        if resp is not None:
                            raise AsyncProcessError(
                                "Module or executable <%s> is not supported"
                                % process.executable
                            )
            else:
                message = (
                    "Wrong process description, type: %s "
                    "module/executable: %s, args: %s"
                    % (
                        str(process.exec_type),
                        str(process.executable),
                        str(process.executable_params),
                    )
                )
                raise AsyncProcessError(message)

        # Update the processing
        self._update_num_of_steps(len(process_list))

        return process_list

    def _setup(self, init_grass=True):
        """Setup the logger, the mapset lock and the credentials. Create the
        temporary grass database and temporary file directories

        ATTENTION: This method must be called first before any processing can
        take place

        What is done:

        - Create the resource and message logger
        - Create the redis lock interface for resource locking
        - Set cell limit, process number limit and process time limit from user
          credentials.
        - Create all required paths to original and temporary project and
          mapsets.
            - temp_project_path
            - global_project_path
            - grass_user_data_base <- This path will be created if it does not
              exist
            - user_project_path <- This path will be created if it does not
              exist
            - temp_grass_data_base <- This path will be created
            - temp_file_path <- This path will be created
            - Check if the current working project is in a persistent (global)
              GRASS GIS database (is_global_database)
        - Create the process chain to process list converter

        Args:
            init_grass (bool): Set true to initialize the user credentials
                               and the temporary database and project paths

        """
        # The setup should only be executed once
        if self.setup_flag is True:
            return
        else:
            self.setup_flag = True

        # fluent sender for this subprocess
        fluent_sender = None
        if self.has_fluent is True:
            from fluent import sender

            fluent_sender = sender.FluentSender(
                "actinia_core_logger",
                host=self.config.LOG_FLUENT_HOST,
                port=self.config.LOG_FLUENT_PORT,
            )
        kwargs = dict()
        kwargs["host"] = self.config.REDIS_SERVER_URL
        kwargs["port"] = self.config.REDIS_SERVER_PORT
        if (
            self.config.REDIS_SERVER_PW
            and self.config.REDIS_SERVER_PW is not None
        ):
            kwargs["password"] = self.config.REDIS_SERVER_PW
        self.resource_logger = ResourceLogger(
            **kwargs, fluent_sender=fluent_sender
        )

        self.message_logger = MessageLogger(
            config=self.config,
            user_id=self.user_id,
            fluent_sender=fluent_sender,
        )

        self.lock_interface = RedisLockingInterface()
        self.lock_interface.connect(**kwargs)
        del kwargs
        self.process_time_limit = int(
            self.user_credentials["permissions"]["process_time_limit"]
        )

        # Check and create all required paths to global, user and temporary
        # projects
        if init_grass is True:
            self._setup_paths()

        self.proc_chain_converter = ProcessChainConverter(
            config=self.config,
            temp_file_path=self.temp_file_path,
            process_dict=self.process_dict,
            temporary_pc_files=self.temporary_pc_files,
            required_mapsets=self.required_mapsets,
            resource_export_list=self.resource_export_list,
            output_parser_list=self.output_parser_list,
            message_logger=self.message_logger,
            send_resource_update=self._send_resource_update,
        )

    def _setup_paths(self):
        """Helper method to setup the paths"""
        self.cell_limit = int(
            self.user_credentials["permissions"]["cell_limit"]
        )
        self.process_num_limit = int(
            self.user_credentials["permissions"]["process_num_limit"]
        )
        # Setup the required paths
        self.temp_grass_data_base = os.path.join(
            self.grass_temp_database, self.temp_grass_data_base_name
        )
        self.temp_file_path = os.path.join(self.temp_grass_data_base, ".tmp")

        if self.project_name:
            self.temp_project_path = os.path.join(
                self.temp_grass_data_base, self.project_name
            )
            self.global_project_path = os.path.join(
                self.grass_data_base, self.project_name
            )
            # Create the user database path if it does not exist
            if not os.path.exists(self.grass_user_data_base):
                os.mkdir(self.grass_user_data_base)
            # Create the user group specific path, if it does not exist and set
            # the grass user database path accordingly
            self.grass_user_data_base = os.path.join(
                self.grass_user_data_base, self.user_group
            )
            if not os.path.exists(self.grass_user_data_base):
                os.mkdir(self.grass_user_data_base)
            # Create the user group specific project path, if it does not
            # exist
            self.user_project_path = os.path.join(
                self.grass_user_data_base, self.project_name
            )
            if not os.path.exists(self.user_project_path):
                os.mkdir(self.user_project_path)
            # Check if the project is located in the global database
            self.is_global_database = False
            project = os.path.join(self.grass_data_base, self.project_name)
            if os.path.isdir(project):
                self.is_global_database = True
        # Create the database, project and temporary file directories
        os.mkdir(self.temp_grass_data_base)
        os.mkdir(self.temp_file_path)

    def _create_temp_database(self, mapsets=None):
        """Create a temporary gis database with project and mapsets
        from the global and user group database for processing.

        IMPORTANT: All processing and mapaste management is performed within a
        temporary database!

        Link the required existing mapsets of global and user group projects
        into the temporary project directory.

        Linking is performed in two steps:
            1.) If the project is a global project, then the mapsets from the
                global project are linked in the temporary projects
            2.) Then link all required mapsets from the user group project
                into the temporary project

        Only mapsets from the global project are linked into the temporary
        project to which the user group has access.
        It checks for access in the global database but not in the user group
        database. The user can always access its own data of its group.

        Args:
            mapsets: A list of mapset names that should be linked into
                     the temporary project. If the list is empty, all
                     available user accessible mapsets of the global
                     and user group specific project will be linked.

        Raises:
            This function raises AsyncProcessError in case of an error.

        """
        # Assign default mapsets
        if mapsets is None:
            mapsets = []

        try:
            # Create the temporary project directory
            os.mkdir(self.temp_project_path)

            # Always link the PERMANENT mapset
            if len(mapsets) > 0 and "PERMANENT" not in mapsets:
                mapsets.append("PERMANENT")

            mapsets_to_link = []
            check_all_mapsets = False
            if not mapsets:
                check_all_mapsets = True

            # User and global project mapset linking
            self._link_mapsets(mapsets, mapsets_to_link, check_all_mapsets)

            # Check if we missed some of the required mapsets
            if check_all_mapsets is False:
                mapset_list = []
                for mapset_path, mapset in mapsets_to_link:
                    mapset_list.append(mapset)

                for mapset in mapsets:
                    if mapset not in mapset_list:
                        raise AsyncProcessError(
                            "Unable to link all required mapsets into "
                            "temporary project. Missing or un-accessible "
                            f"mapset <{mapset}> in project "
                            f"<{self.project_name}>"
                        )

            # Link the original mapsets from global and user database into the
            # temporary project
            for mapset_path, mapset in mapsets_to_link:
                if (
                    os.path.isdir(os.path.join(self.temp_project_path, mapset))
                    is False
                ):
                    os.symlink(
                        mapset_path,
                        os.path.join(self.temp_project_path, mapset),
                    )

        except Exception as e:
            raise AsyncProcessError(
                "Unable to create a temporary GIS database"
                ", Exception: %s" % str(e)
            )

    def _link_mapsets(self, mapsets, mapsets_to_link, check_all_mapsets):
        """Helper method to link projects mapsets

        Args:
            mapsets (list): List of mapsets in project
            mapsets_to_link (list): List of mapsets paths to link
            check_all_mapsets (bool): If set True, the mapsets list is created
                                      with all projects on project_path

        Returns:
            mapsets (list): List of mapsets in project
            mapsets_to_link (list): List of mapsets paths to link
        """
        # Global project mapset linking
        if self.is_global_database is True:
            # List all available mapsets in the global project
            mapsets, mapsets_to_link = self._list_all_available_mapsets(
                self.global_project_path,
                mapsets,
                check_all_mapsets,
                mapsets_to_link,
                True,
            )
        # Check for leftover mapsets
        left_over_mapsets = []
        for mapset in mapsets:
            if mapset not in mapsets_to_link:
                left_over_mapsets.append(mapset)
        # List all available mapsets in the user project
        mapsets, mapsets_to_link = self._list_all_available_mapsets(
            self.user_project_path,
            left_over_mapsets,
            check_all_mapsets,
            mapsets_to_link,
            False,
        )
        return mapsets, mapsets_to_link

    def _list_all_available_mapsets(
        self,
        project_path,
        mapsets,
        check_all_mapsets,
        mapsets_to_link,
        global_db=False,
    ):
        """Helper method to list all available mapsets and for global database
        it is checked if the mapset can be accessed.

        Args:
            project_path (str): Path to project (global or user)
            mapsets (list): List of mapsets names to link.
                            The mapsets list can be empty, if check_all_mapsets
                            is True the list is filled with all mapsets from
                            the project_path
            check_all_mapsets (bool): If set True, the mapsets list is created
                                      with all projects on project_path
            mapsets_to_link (list): List of mapset paths to link
            global_db (bool): If set True, the project/mapset access is
                              checked

        Returns:
            mapsets (list): List of mapsets in project
            mapsets_to_link (list): List of mapsets paths to link
        """
        if os.path.isdir(project_path):
            if check_all_mapsets is True:
                mapsets = os.listdir(project_path)
            for mapset in mapsets:
                mapset_path = os.path.join(project_path, mapset)
                if os.path.isdir(mapset_path) and os.access(
                    mapset_path, os.R_OK & os.X_OK
                ):
                    # Check if a WIND file exists to be sure it is a mapset
                    if (
                        os.path.isfile(os.path.join(mapset_path, "WIND"))
                        is True
                    ):
                        if mapset not in mapsets_to_link and global_db is True:
                            # Link the mapset from the global database
                            # only if it can be accessed
                            resp = check_project_mapset_module_access(
                                user_credentials=self.user_credentials,
                                config=self.config,
                                project_name=self.project_name,
                                mapset_name=mapset,
                            )
                            if resp is None:
                                mapsets_to_link.append((mapset_path, mapset))
                        elif (
                            mapset not in mapsets_to_link
                            and global_db is False
                        ):
                            mapsets_to_link.append((mapset_path, mapset))
                    else:
                        raise AsyncProcessError(
                            "Invalid mapset <%s> in project <%s>"
                            % (mapset, self.project_name)
                        )
        else:
            if global_db is True:
                msg = (
                    "Unable to access global project <%s>" % self.project_name
                )
            else:
                msg = "Unable to access user project <%s>" % self.project_name
            raise AsyncProcessError(msg)
        return mapsets, mapsets_to_link

    def _create_grass_environment(
        self, grass_data_base, mapset_name="PERMANENT"
    ):
        """Sets up the GRASS environment to run modules

        Args:
            mapset_name (str): The mapset that should used for processing,
                               default is PERMANENT

        Raises:
            This method will raise an AsyncProcessError if the mapset is
            not in the access list of the user.

        """
        self.message_logger.info(
            "Initlialize GRASS grass_data_base: %s; project: %s; mapset: %s"
            % (grass_data_base, self.project_name, mapset_name)
        )

        self.ginit = GrassInitializer(
            grass_data_base=grass_data_base,
            grass_base_dir=self.config.GRASS_GIS_BASE,
            project_name=self.project_name,
            mapset_name=mapset_name,
            config=self.config,
            grass_addon_path=self.config.GRASS_ADDON_PATH,
            user_id=self.user_id,
        )

        self.ginit.initialize()

    def _create_temporary_mapset(
        self,
        temp_mapset_name,
        source_mapset_name=None,
        interim_result_mapset=None,
        interim_result_file_path=None,
    ):
        """Create the temporary mapset and switch into it

        This method needs an initialized the GRASS environment.

        It will check access to all required mapsets and adds them to the
        mapset search path.

        IMPORTANT: You need to call self._create_grass_environment() to set up
        the environment before calling this method.

        A new temporary mapset is created. All in the process chain detected
        mapsets of input maps or STDS will be added to the mapset search path
        using g.mapsets.

        Optionally the WIND file of a source mapset can be copied into the
        temporary mapset.

        Args:
            temp_mapset_name (str): The name of the temporary mapset to be
                                    created
            source_mapset_name (str): The name of the source mapset to copy the
                                      WIND file from
            interim_result_mapset (str): The path to the mapset which is saved
                                         as interim result and should be used
                                         as start mapset for the job resumtion
            interim_result_file_path (str): The path of the interim result
                                            temporary file path


        Raises:
            This function will raise an exception if the
            g.mapset/g.mapsets/db.connect modules fail

        """
        self.temp_mapset_path = os.path.join(
            self.temp_project_path, temp_mapset_name
        )

        # if interim_result_mapset is set copy the mapset from the interim
        # results
        if interim_result_mapset:
            self.message_logger.info(
                "Rsync interim result mapset to temporary GRASS DB"
            )
            # change mapset name for groups, raster VRTs and tgis
            for directory in ["group", "cell_misc", "tgis"]:
                change_mapsetname(
                    os.path.join(interim_result_mapset, directory),
                    directory,
                    os.path.basename(interim_result_mapset),
                    os.path.basename(self.temp_mapset_path),
                )
            rsync_status = self.interim_result.rsync_mapsets(
                interim_result_mapset, self.temp_mapset_path
            )
            if rsync_status != "success":
                raise RsyncError(
                    "Error while rsyncing of interim results to new temporare "
                    "mapset"
                )
            self.interim_result.rsync_additional_mapsets(
                os.path.dirname(self.temp_mapset_path)
            )
        if interim_result_file_path:
            self.message_logger.info(
                "Rsync interim result file path to temporary GRASS DB"
            )
            rsync_status = self.interim_result.rsync_mapsets(
                interim_result_file_path, self.temp_file_path
            )
            if rsync_status != "success":
                raise RsyncError(
                    "Error while rsyncing of interim temporary file path to "
                    "new temporare file path"
                )

        self.ginit.run_module(
            "g.mapset", ["-c", "mapset=%s" % temp_mapset_name]
        )

        if self.required_mapsets:
            self.ginit.run_module(
                "g.mapsets",
                [
                    "operation=add",
                    "mapset=%s" % (",".join(self.required_mapsets)),
                ],
            )

            self.message_logger.info(
                "Added the following mapsets to the mapset "
                "search path: " + ",".join(self.required_mapsets)
            )

        # Set the vector database connection to vector map specific databases
        self.ginit.run_module(
            "db.connect",
            # TODO GRASS GIS 9.0
            [
                "driver=sqlite",
                "database=$GISDBASE/$LOCATION_NAME/$MAPSET/vector/$MAP/"
                "sqlite.db",
            ],
        )

        # self.ginit.run_module("g.gisenv", ["set=DEBUG=2",])

        # If a source mapset is provided, the WIND file will be copied from it
        # to the temporary mapset
        if source_mapset_name is not None and interim_result_mapset is None:
            source_mapset_path = os.path.join(
                self.temp_project_path, source_mapset_name
            )
            if os.path.exists(os.path.join(source_mapset_path, "WIND")):
                shutil.copyfile(
                    os.path.join(source_mapset_path, "WIND"),
                    os.path.join(self.temp_mapset_path, "WIND"),
                )

    def _cleanup(self):
        """Clean up the GrassInitializer files created in
        self._setup() and remove the created temporary database.

        """
        if self.ginit:
            self.ginit.clean_up()

        if (
            self.temp_grass_data_base is not None
            and os.path.exists(self.temp_grass_data_base)
            and os.path.isdir(self.temp_grass_data_base)
        ):
            shutil.rmtree(self.temp_grass_data_base, ignore_errors=True)
        if self.ginit_tmpfiles:
            for tmpfile in self.ginit_tmpfiles:
                try:
                    os.remove(tmpfile)
                except Exception as e:
                    self.message_logger.debug(
                        f"Temporary file {tmpfile} can't be removed: {e}"
                    )

    def _check_pixellimit_rimport(self, process_executable_params):
        """Check the current r.import command against the user cell limit.

        Raises:
            This method will raise an AsyncProcessError exception

        """
        rimport_inp = [x for x in process_executable_params if "input=" in x][
            0
        ].split("=")[1]
        rimport_out = [x for x in process_executable_params if "output=" in x][
            0
        ].split("=")[1]
        vrt_out = f"{rimport_out}_{os.getpid()}_tmp.vrt"
        self.ginit_tmpfiles.append(vrt_out)

        # define extent_region if set (otherwise empty list)
        extent_region = [
            x for x in process_executable_params if "extent=" in x
        ]

        # build VRT of rimport input
        gdabuildvrt_params = list()
        # if extent=region set, vrt only for region, not complete input
        if extent_region:
            # first query region extents
            errorid, stdout_gregion, _ = self.ginit.run_module(
                "g.region", ["-ug"]
            )
            if errorid != 0:
                raise AsyncProcessError(
                    "Unable to check the computational region size"
                )
            # parse region extents for creation of vrt (-te flag from gdalbuildvrt)
            list_out_gregion = stdout_gregion.split("\n")
            gdabuildvrt_params.append("-te")
            gdabuildvrt_params.append(list_out_gregion[4])  # xmin/w
            gdabuildvrt_params.append(list_out_gregion[3])  # ymin/s
            gdabuildvrt_params.append(list_out_gregion[5])  # xmax/e
            gdabuildvrt_params.append(list_out_gregion[2])  # ymax/n
        # out and input for gdalbuildvrt
        gdabuildvrt_params.append(vrt_out)
        gdabuildvrt_params.append(rimport_inp)
        # build vrt with previous defined parameters
        (
            errorid,
            _,
            _,
        ) = self.ginit.run_module("/usr/bin/gdalbuildvrt", gdabuildvrt_params)

        # gdalinfo for created vrt
        gdalinfo_params = [vrt_out]
        errorid, stdout_gdalinfo, _ = self.ginit.run_module(
            "/usr/bin/gdalinfo", gdalinfo_params
        )
        # parse "Size" output of gdalinfo
        rastersize_list = (
            stdout_gdalinfo.split("Size is")[1].split("\n")[0].split(",")
        )
        # size = x-dim*y-dim
        rastersize_x = int(rastersize_list[0])
        rastersize_y = int(rastersize_list[1])
        rastersize = rastersize_x * rastersize_y

        # if different import/reprojection resolution set:
        rimport_res = [
            x for x in process_executable_params if "resolution=" in x
        ]
        res_val = None
        # If raster exceeds cell limit already in original resolution, next part can be skipped
        if rimport_res and (rastersize < self.cell_limit):
            # determine estimated resolution
            errorid, _, stderr_estres = self.ginit.run_module(
                "r.import", [vrt_out, "-e"]
            )
            if "Estimated" in stderr_estres:
                # if data in different projection get rest_est with output of r.import -e
                res_est = float(stderr_estres.split("\n")[-2].split(":")[1])
            else:
                # if data in same projection can use gdalinfo output
                res_xy = (
                    stdout_gdalinfo.split("Pixel Size = (")[1]
                    .split(")\n")[0]
                    .split(",")
                )
                # get estimated resolution
                # (analoug as done within r.import -e: estres = math.sqrt((n - s) * (e - w) / cells))
                res_est = math.sqrt(abs(float(res_xy[0]) * float(res_xy[1])))
            # determine set resolution value
            resolution = rimport_res[0].split("=")[1]
            if resolution == "value":
                res_val = [
                    float(
                        [
                            x
                            for x in process_executable_params
                            if "resolution_value=" in x
                        ][0].split("=")[1]
                    )
                ] * 2
            elif resolution == "region":
                # if already queried above reuse, otherwise execute g.region command
                try:
                    stdout_gregion
                except Exception:
                    (
                        errorid,
                        stdout_gregion,
                        _,
                    ) = self.ginit.run_module("g.region", ["-ug"])
                res_val_ns = float(
                    [x for x in stdout_gregion.split("\n") if "nsres=" in x][
                        0
                    ].split("=")[1]
                )
                res_val_ew = float(
                    [x for x in stdout_gregion.split("\n") if "ewres=" in x][
                        0
                    ].split("=")[1]
                )
                res_val = [res_val_ns, res_val_ew]
        if res_val:
            if (res_val[0] < res_est) | (res_val[1] < res_est):
                # only check if smaller resolution set
                res_change_x = res_est / res_val[1]
                res_change_y = res_est / res_val[0]
                # approximate raster size after resampling
                # by using factor of changed resolution
                rastersize = (
                    rastersize_x * res_change_x * rastersize_y * res_change_y
                )

        # compare estimated raster output size with pixel limit
        # and raise exception if exceeded
        if rastersize > self.cell_limit:
            raise AsyncProcessError(
                "Processing pixel limit exceeded for raster import. "
                "Please set e.g. region smaller."
            )

    def _check_reset_region(self):
        """Check the current region settings against the user cell limit.

        Reset the current processing region to a meaningful state
        so that the user cell limit is not reached and the mapset can be
        accessed again.

        Raises:
            This method will raise an AsyncProcessError exception

        """
        if self.skip_region_check is True:
            return

        errorid, stdout_buff, _ = self.ginit.run_module("g.region", ["-ug"])

        if errorid != 0:
            raise AsyncProcessError(
                "Unable to check the computational region size"
            )

        str_list = stdout_buff.split()
        region = {}
        for line in str_list:
            if "=" in line:
                option = line.split("=", 1)
                region[option[0]] = option[1]

        self.message_logger.info(str(region))

        num_cells = int(region["cells"])
        ns_res = float(region["nsres"])
        ew_res = float(region["ewres"])

        if num_cells > self.cell_limit:
            self._adjust_region_size(num_cells, ns_res, ew_res)

    def _adjust_region_size(self, num_cells, ns_res, ew_res):
        """Helper method to adjust the region size

        Args:
            num_cells (int): GRASS GIS number of cells of the region
            ns_res (float): GRASS GIS north-south cell resolution of the region
            ew_res (float): GRASS GIS east-west cell resolution of the region

        Raises:
            This method will raise an AsyncProcessError exception

        """
        fak = num_cells / self.cell_limit
        fak += 2.0
        fak = math.sqrt(fak) + 2.0
        ns_res = ns_res * fak
        ew_res = ew_res * fak
        errorid, stdout_buff, stderr_buff = self.ginit.run_module(
            "g.region", ["nsres=%f" % ns_res, "ewres=%f" % ew_res, "-g"]
        )
        self.message_logger.info(stdout_buff)
        if errorid != 0:
            raise AsyncProcessError(
                "Unable to adjust the region settings to nsres: "
                "%f ewres: %f error: %s" % (ns_res, ew_res, stderr_buff)
            )
        raise AsyncProcessError(
            "Region too large, set a coarser resolution to minimum nsres: "
            "%f ewres: %f [num_cells: %d]" % (ns_res, ew_res, num_cells)
        )

    def _increment_progress(self, num=1):
        """Increment the progress step by a specific number

        Args:
            num (int): The number for which the progress should be increased
        """
        self.progress_steps += num
        self.progress["step"] = self.progress_steps

    def _add_actinia_process(self, process: Process):
        """Add an actinia process to the list and dictionary

        Args:
            process: The actinia process
        """
        self.actinia_process_dict[process.id] = process
        self.actinia_process_list.append(process)

    def _update_num_of_steps(self, num):
        """Update the number of total steps

        Args:
            num: The number of processes to be added to the total number of
                 processes
        """
        self.number_of_processes += num
        self.progress["num_of_steps"] = self.number_of_processes

    def _wait_for_process(
        self, module_name, module_parameter, proc, poll_time
    ):
        """
        Wait for a specific process. Catch termination requests, process
        time limits and send updates to the user.

        Args:
            module_name: The name of the GRASS module or executable
            module_parameter: The parameter of a GRASS module or a executable
            proc: The process to wait for and monitor
            poll_time: The poll time to send updates and check for termination

        Returns:
            (float)
            The run time in seconds

        """

        start_time = time.time()

        termination_check_count = 0
        update_check_count = 0
        while True:
            if proc.poll() is not None:
                break
            else:
                # Sleep some time and update the resource status
                time.sleep(poll_time)
                termination_check_count += 1
                update_check_count += 1

                # Check all 10 loops for termination
                if termination_check_count == 10:
                    termination_check_count = 0
                    # check if the resource should be terminated
                    # and kill the current process
                    if (
                        self.resource_logger.get_termination(
                            self.user_id, self.resource_id, self.iteration
                        )
                        is True
                    ):
                        proc.kill()
                        raise AsyncProcessTermination(
                            "Process <%s> was terminated "
                            "by user request" % module_name
                        )

                # Send all 100 loops a status update
                if update_check_count == 100:
                    update_check_count = 0
                    # Check max runtime of process
                    curr_time = time.time()
                    if (curr_time - start_time) > self.process_time_limit:
                        proc.kill()
                        raise AsyncProcessTimeLimit(
                            "Time (%i seconds) exceeded to run executable %s"
                            % (self.process_time_limit, module_name)
                        )
                    # Reduce the length of the command line parameters for
                    # lesser logging overhead
                    mparams = str(module_parameter)
                    if len(mparams) > 100:
                        mparams = "%s ... %s" % (mparams[0:50], mparams[-50:])
                    message = (
                        f"Running executable {module_name} with parameters "
                        f"{mparams} for {curr_time - start_time} seconds"
                    )
                    self._send_resource_update(message)

        return time.time() - start_time

    def _run_process(self, process, poll_time=0.05):
        """
        Run a process actinia_core.core.common.process_object.Process) with
        options and send progress updates to the resource database.

        IMPORTANT: Use this method to run programs that are not GRASS modules.

        Check each poll the termination status of the resource.
        If the termination state is set True, terminate the current process
        and raise an AsyncProcessTermination exception that must be caught
        by the run() method.

        Args:
            process actinia_core.core.common.process_object.Process):
                The process object that should be executed
            poll_time (float): The time to check the process status and to send
                               updates to the resource db

        Raises:
            AsyncProcessError:
            AsyncProcessTermination:
            AsyncProcessTimeLimit:

        Returns:
            tuple:
            (returncode, stdout_buff, stderr_buff)

        """
        if (
            self.resource_logger.get_termination(
                self.user_id, self.resource_id, self.iteration
            )
            is True
        ):
            raise AsyncProcessTermination(
                "Process <%s> was terminated by "
                "user request" % process.executable
            )

        return self._run_executable(process, poll_time)

    def _run_module(self, process, poll_time=0.05):
        """Run the GRASS module actinia_core.core.common.process_object.Process
        with its module options and send progress updates to the database
        server that manages the resource entries.

        Check before each module run the size of the region. If the maximum
        number of cells are exceeded then raise an AsyncProcessError exception
        that the maximum number of cells are exceeded and reset them to a
        meaningful state, so that the user can still run processes in the
        mapset.

        The region is checked for the first module of a process chain and after
        that, for each g.region call that was present in the process chain.

        Check each poll the termination status of the resource.
        If the termination state is set True, terminate the current process
        and raise an AsyncProcessTermination exception that must be caught
        by the run() method.

        By default the status of the running process is checked each 0.005
        seconds. This is the minimum amount of time a process can run. If many
        tiny running processes are executed in a large process chain, then this
        value must be adjusted.

        Args:
            process actinia_core.core.common.process_object.Process):
                The process object that should be executed
            poll_time (float): The time to check the process status and to send
                               updates to the resource db

        Raises:
            AsyncProcessError:
            AsyncProcessTermination:
            AsyncProcessTimeLimit:

        Returns:
            tuple:
            (returncode, stdout_buff, stderr_buff)

        """
        # Count the processes
        self.process_count += 1
        # Check for each 20. process if a kill request was received
        # This is required in case a single of many fast running processes in a
        # chain is not able to trigger the termination check in the while loop
        if self.process_count % 20 == 0:
            if (
                self.resource_logger.get_termination(
                    self.user_id, self.resource_id, self.iteration
                )
                is True
            ):
                raise AsyncProcessTermination(
                    "Process <%s> was terminated "
                    "by user request" % process.executable
                )

            message = "Running module %s with parameters %s" % (
                process.executable,
                str(process.executable_params),
            )
            self._send_resource_update(message)

        # Check pixel limit for r.import operations
        if process.executable == "r.import":
            self._check_pixellimit_rimport(process.executable_params)

        # Check reset region if a g.region call was present in the process
        # chain. By default the initial value of last_module is "g.region" to
        # assure for first run of a process from the process chain, the region
        # settings are evaluated
        if (
            self.last_module == "g.region"
            and process.skip_permission_check is False
        ):
            self._check_reset_region()
        # Save the last module name. This is needed to check the region
        # settings
        self.last_module = process.executable

        return self._run_executable(process, poll_time)

    def _run_executable(self, process, poll_time=0.005):
        """Runs a GRASS module or aactinia_core.core.Unix executable and sets
        up the correct handling of stdout, stderr and stdin, creates the
        process log model and returns stdout, stderr and the return code.

        It creates the temporary file paths.

        The returncode of 0 indicates that it ran successfully. A negative
        value -N indicates that the child was terminated by signal N (POSIX
        only; see also
        https://en.wikipedia.org/wiki/Signal_(IPC)#Default_action).

        Args:
            process actinia_core.core.common.process_object.Process):
                The process object that should be executed
            poll_time (float): The time to check the process status and to send
                               updates to the resource db

        Raises:
            AsyncProcessError:
            AsyncProcessTermination:
            AsyncProcessTimeLimit:

        Returns:
            tuple:
            (returncode, stdout_buff, stderr_buff)

        """

        # Use temporary files to catch stdout and stderr
        stdout_buff = tempfile.NamedTemporaryFile(
            mode="w+b", delete=True, dir=self.temp_file_path
        )
        stderr_buff = tempfile.NamedTemporaryFile(
            mode="w+b", delete=True, dir=self.temp_file_path
        )
        stdin_file = None

        if process.param_stdin_sources:
            for num, func in process.param_stdin_sources.items():
                func_name = f"PARAM_STDIN_FUNC_{num}"
                for i in range(len(process.executable_params)):
                    param = process.executable_params[i]
                    if func_name in param:
                        _, val = param.split("=", 1)
                        par_val = func().strip()
                        val_splitted = val.split(func_name)
                        for j in range(1, len(val_splitted)):
                            filtered_par_value = par_val
                            filtered_func_name = func_name
                            # filter stdout/stderr
                            if "::" in val_splitted[j]:
                                filter = get_param_stdin_part(
                                    val_splitted[j][2:]
                                )
                                if "=" not in par_val:
                                    raise AsyncProcessError(
                                        "Error while running executable "
                                        f"<{process.executable}>: <{filter}> "
                                        "cannot be selected. Maybe you have to "
                                        "set the '-g' flag for the stdout/stderr "
                                        "module."
                                    )
                                filtered_par_value = {
                                    x.split("=")[0]: x.split("=")[1]
                                    for x in par_val.split()
                                }[filter]
                                filtered_func_name += f"::{filter}"
                            process.executable_params[i] = (
                                process.executable_params[i].replace(
                                    filtered_func_name, filtered_par_value
                                )
                            )

        if process.stdin_source is not None:
            tmp_file = self.proc_chain_converter.generate_temp_file_path()
            stdin_file = open(tmp_file, "w")
            stdin_file.write(process.stdin_source())
            stdin_file.close()
            stdin_file = open(tmp_file, "r")

        self._increment_progress(num=1)

        # GRASS andactinia_core.core.Unix executables have different run
        # methods
        if process.exec_type in "grass":
            proc = self.ginit.run_module(
                process.executable,
                process.executable_params,
                raw=True,
                stdout=stdout_buff,
                stderr=stderr_buff,
                stdin=stdin_file,
            )
        else:
            inputlist = list()
            inputlist.append(process.executable)
            inputlist.extend(process.executable_params)

            proc = subprocess.Popen(
                args=inputlist,
                stdout=stdout_buff,
                stderr=stderr_buff,
                stdin=stdin_file,
            )

        run_time = self._wait_for_process(
            process.executable, process.executable_params, proc, poll_time
        )

        proc.wait()

        stdout_buff.flush()
        stderr_buff.flush()
        stdout_buff.seek(0)
        stderr_buff.seek(0)
        stdout_string = stdout_buff.read().decode()
        stderr_string = stderr_buff.read().decode()
        stdout_buff.close()
        stderr_buff.close()
        if stdin_file:
            stdin_file.close()

        process.set_stdouts(stdout=stdout_string, stderr=stderr_string)

        kwargs = {
            "id": process.id,
            "executable": process.executable,
            "parameter": process.executable_params,
            "return_code": proc.returncode,
            "stdout": stdout_string,
            "stderr": stderr_string.split("\n"),
            "run_time": run_time,
        }
        if self.temp_mapset_path:
            kwargs["mapset_size"] = get_directory_size(self.temp_mapset_path)

        plm = ProcessLogModel(**kwargs)

        self.module_output_log.append(plm)
        # Store the log in an additional dictionary for automated output
        # generation
        if process.id is not None:
            self.module_output_dict[process.id] = plm

        if proc.returncode != 0:
            raise AsyncProcessError(
                "Error while running executable <%s>" % process.executable
            )

        # save interim results
        if (
            self.interim_result.saving_interim_results is True
            and self.temp_mapset_path is not None
        ):
            self.interim_result.save_interim_results(
                self.progress_steps, self.temp_mapset_path, self.temp_file_path
            )
        elif self.temp_mapset_path is None:
            self.message_logger.debug(
                "No temp mapset path set. Because of that no interim results"
                " can be saved!"
            )

        return proc.returncode, stdout_string, stderr_string

    def _create_temporary_grass_environment(
        self,
        source_mapset_name=None,
        interim_result_mapset=None,
        interim_result_file_path=None,
    ):
        """Create a temporary GRASS GIS environment

        This method will:
            1. create the temporary database
            2. sets-up the GRASS environment
            3. Create temporary mapset

        This method will link the required mapsets that are
        defined in *self.required_mapsets* into the project.
        The mapsets may be from the global and/or user database.

        Args:
            source_mapset_name (str): The name of the source mapset to copy the
                                      WIND file from
            interim_result_mapset (str): The path to the mapset which is saved
                                         as interim result and should be used
                                         as start mapset for the job resumtion
            interim_result_file_path (str): The path of the interim result
                                            temporary file path
        Raises:
            This method will raise an AsyncProcessError
        """

        # Create the temp database and link the
        # required mapsets into it
        self._create_temp_database(self.required_mapsets)

        # Initialize the GRASS environment and switch into PERMANENT
        # mapset, which is always linked
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base, mapset_name="PERMANENT"
        )

        # Create the temporary mapset and switch into it
        self._create_temporary_mapset(
            temp_mapset_name=self.temp_mapset_name,
            source_mapset_name=source_mapset_name,
            interim_result_mapset=interim_result_mapset,
            interim_result_file_path=interim_result_file_path,
        )

    def _execute(self, skip_permission_check=False):
        """Overwrite this function in subclasses.

        This function will be executed by the run() function

        - Setup logger and credentials
        - Analyse the process chain
        - Create the temporal database
        - Initialize the GRASS environment and create the temporary mapset
        - Run the modules
        - Parse the stdout output of the modules and generate the module
          results

        Args:
            skip_permission_check (bool): If set True, the permission checks of
                                          module access and process num
                                          limits are not performed

        Raises:
            This method will raise an AsyncProcessError, AsyncProcessTimeLimit
            or AsyncProcessTermination

        """
        # Create the process chain
        if self.rdc.iteration is not None:
            process_list = self._create_temporary_grass_environment_and_process_list_for_iteration(
                skip_permission_check=skip_permission_check
            )
        else:
            process_list = (
                self._create_temporary_grass_environment_and_process_list(
                    skip_permission_check=skip_permission_check
                )
            )

        # Run all executables
        self._execute_process_list(process_list=process_list)
        # Parse the module sdtout outputs and create the results
        self._parse_module_outputs()

    def _create_temporary_grass_environment_and_process_list_for_iteration(
        self, process_chain=None, skip_permission_check=False
    ):
        """Helper method to:

        - Setup logger and credentials
        - Analyse the process chain
        - Create the temporal database
        - Initialize the GRASS environment and create the temporary mapset
        - Return the created process list

        Args:
            process_chain (dict): The process chain to be checked and converted
                                  into a process list
            skip_permission_check (bool): If set True, the permission checks
                                          of module access and process num
                                          limits are not performed

        Raises:
            This method will raise an AsyncProcessError

        Returns: list
                  The process list to be executed by _execute_process_list()

        """
        # Setup the user credentials and logger
        self._setup()

        # Create and check the process chain
        (
            pc_step,
            old_process_chain_list,
        ) = self._get_previous_iteration_process_chain()
        self.interim_result.set_old_pc_step(pc_step)
        process_list = self._validate_process_chain(
            process_chain=self.request_data,
            old_process_chain=old_process_chain_list,
            skip_permission_check=skip_permission_check,
            pc_step=pc_step,
        )

        # check iterim results
        (
            interim_result_mapset,
            interim_result_file_path,
        ) = self.interim_result.check_interim_result_mapset(
            pc_step, self.iteration - 1
        )
        if interim_result_mapset is None:
            return None

        # Init GRASS and create the temporary mapset with the interim results
        self._create_temporary_grass_environment(
            interim_result_mapset=interim_result_mapset,
            interim_result_file_path=interim_result_file_path,
        )

        return process_list

    def _create_temporary_grass_environment_and_process_list(
        self, process_chain=None, skip_permission_check=False
    ):
        """Helper method to:

        - Setup logger and credentials
        - Analyse the process chain
        - Create the temporal database
        - Initialize the GRASS environment and create the temporary mapset
        - Return the created process list

        Args:
            process_chain (dict): The process chain to be checked and converted
                                  into a process list
            skip_permission_check (bool): If set True, the permission checks
                                          of module access and process num
                                          limits are not performed

        Raises:
            This method will raise an AsyncProcessError

        Returns: list
                  The process list to be executed by _execute_process_list()

        """
        # Setup the user credentials and logger
        self._setup()

        # Create and check the process chain
        process_list = self._validate_process_chain(
            process_chain=process_chain,
            skip_permission_check=skip_permission_check,
        )

        # Init GRASS and create the temporary mapset
        self._create_temporary_grass_environment()

        return process_list

    def _parse_module_outputs(self):
        """Parse the module stdout outputs and parse them into the required
        formats: table, list or kv

        This functions analyzes the output_parser_list for entries to parse.
        It will convert the stdout strings into tables, lists or key/value
        outputs and stores the result in the module_result dictionary using the
        provided id of the StdoutParser.

        """

        for entry in self.output_parser_list:
            for process_id, stdout_def in entry.items():
                id = stdout_def["id"]
                format = stdout_def["format"]
                delimiter = stdout_def["delimiter"]
                if process_id not in self.module_output_dict:
                    raise AsyncProcessError(
                        "Unable to find process id in module output dictionary"
                    )
                stdout = self.module_output_dict[process_id]["stdout"]
                # Split the rows by the \n new line delimiter
                rows = stdout.strip().split("\n")
                if "table" in format:
                    result = []
                    for row in rows:
                        row = row.strip()
                        values = row.split(delimiter)
                        value_list = []
                        for value in values:
                            value_list.append(value.strip())
                        result.append(value_list)
                elif "list" in format:
                    result = []
                    for row in rows:
                        value = row.strip()
                        result.append(value)
                elif "kv" in format:
                    result = dict()
                    for row in rows:
                        row = row.strip()
                        key, value = row.split(delimiter, 1)
                        result[key.strip()] = value.strip()
                elif "json" in format:
                    result = None
                    try:
                        result = {
                            i[0]: i[1]
                            for i in [
                                entry.split(delimiter, 1)
                                for entry in stdout.strip("\n").split("\n")
                            ]
                        }
                    except Exception:
                        try:
                            result = json.loads(stdout)
                        except Exception:
                            pass
                    finally:
                        if not result:
                            result = stdout
                else:
                    raise AsyncProcessError("Wrong stdout parser format")

                # Store the parser result
                self.module_results[id] = result

    def _execute_process_list(self, process_list):
        """
        Run all modules or executables that are specified in the process list

        Args:
            process_list: The process list that was generated by
                          _validate_process_chain() which is also called in
                          _create_temporary_grass_environment_and_process_list()

        Raises:
            This method will raise an AsyncProcessError, AsyncProcessTimeLimit
            or AsyncProcessTermination

        """
        for process in process_list:
            if process.exec_type == "grass":
                self._run_module(process)
            elif process.exec_type == "exec":
                self._run_process(process)
            elif process.exec_type == "python":
                eval(process.executable)

    def _interim_results(self):
        """Check if interim results should be saved or cleaned up"""

        if (
            "error" in self.run_state
            and self.interim_result.saving_interim_results == "onError"
        ):
            if self.progress_steps > 0:
                self.interim_result.delete_interim_results()
                self.interim_result.save_interim_results(
                    self.progress_steps - 1,
                    self.temp_mapset_path,
                    self.temp_file_path,
                    force_copy=True,
                )
        elif (
            "success" in self.run_state
            and self.interim_result.saving_interim_results is not False
        ):
            self.interim_result.delete_interim_results()

    def _final_cleanup(self):
        """Overwrite this function in subclasses to perform the final cleanup,
        by default this function calls self._cleanup() to remove the temporary
        gis database.
        This function should not raise any exceptions. Extend the cleaning
        functionality here.
        """
        # Clean up and remove the temporary gisdbase
        self._cleanup()

    def run(self):
        """This function will run the processing and will catch and process
        any exceptions that were raised while processing. Call this function to
        run the processing.

        You have to implement/overwrite two methods that are called here:

            * self._execute()
            * self._interim_results()
            * self._final_cleanup()

            e_type, e_value, e_traceback = sys.exc_info()
            message = [e.__class__, e_type, e_value, traceback.format_tb(
                       e_traceback)]
            message = pprint.pformat(message)
        """

        try:
            # Run the _execute function that does all the work
            self._execute()
        except AsyncProcessTermination as e:
            self.run_state = {"terminated": str(e)}
        except AsyncProcessTimeLimit as e:
            self.run_state = {"time limit exceeded": str(e)}
        except AsyncProcessError as e:
            e_type, e_value, e_tb = sys.exc_info()
            model = ExceptionTracebackModel(
                message=str(e_value),
                traceback=traceback.format_tb(e_tb),
                type=str(e_type),
            )
            self.run_state = {"error": str(e), "exception": model}
        except KeyboardInterrupt as e:
            e_type, e_value, e_tb = sys.exc_info()
            model = ExceptionTracebackModel(
                message=str(e_value),
                traceback=traceback.format_tb(e_tb),
                type=str(e_type),
            )
            self.run_state = {"error": str(e), "exception": model}
        except Exception as e:
            e_type, e_value, e_tb = sys.exc_info()
            model = ExceptionTracebackModel(
                message=str(e_value),
                traceback=traceback.format_tb(e_tb),
                type=str(e_type),
            )
            self.run_state = {"error": str(e), "exception": model}
        finally:
            try:
                # Check if interim results should be saved and save them
                self._interim_results()
                # Call the final cleanup, before sending the status messages
                self._final_cleanup()
            except Exception as e:
                e_type, e_value, e_tb = sys.exc_info()
                model = ExceptionTracebackModel(
                    message=str(e_value),
                    traceback=traceback.format_tb(e_tb),
                    type=str(e_type),
                )
                self.run_state = {"error": str(e), "exception": model}
            # After all processing finished, send the final status
            if "success" in self.run_state:
                self._send_resource_finished(
                    message=self.finish_message, results=self.module_results
                )
            elif "terminated" in self.run_state:
                # Send an error message if an exception was raised
                self._send_resource_terminated(
                    message=self.run_state["terminated"]
                )
            elif "time limit exceeded" in self.run_state:
                self._send_resource_time_limit_exceeded(
                    message=self.run_state["time limit exceeded"]
                )
            elif "error" in self.run_state:
                # Send an error message if an exception was raised
                self._send_resource_error(
                    message=self.run_state["error"],
                    exception=self.run_state["exception"],
                )
            else:
                self._send_resource_error(message="Unknown error")
