# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2018 Sören Gebbert and mundialis GmbH & Co. KG
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
Asynchronous computation in specific temporary generated and then copied
or original mapsets
"""
import pickle
import os
import shutil
import subprocess
from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger

from .ephemeral_processing import EphemeralProcessing
from .resource_base import ResourceBase
from .common.redis_interface import enqueue_job
from .common.exceptions import AsyncProcessError
from .common.process_chain import ProcessChainModel
from .common.response_models import ProcessingResponseModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

DESCR="""Execute a user defined process chain in an existing mapset
of the persistent user database or in a new mapset that will be
created by this reuqest in the persistent user database.

The process chain is executed asynchronously. The provided status URL
in the response must be polled to gain information about the processing
progress and finishing status.

**Note**

    Space-time dataset processing can only be performed in a new mapset
    that is created by this resource call, since merging of temporal databases
    of different mapsets is not supported yet.

The mapset that is used for processing will be locked until the process
chain execution finished (successfully or not), even if the mapset is be created by the request.
Other requests on the locked mapset will abort with a mapset lock error.

The persistent user database will not be modified if
the process chain does not run successfully. The processing is performed
in an ephemeral database and then merged or copied into the persistent user database.

**Note**

    Make sure that the process chain definition identifies all raster, vector or
    space time datasets correctly with name and mapset: name@mapset.

    All required mapsets will be identified by analysing the input parameter
    of all module descriptions in the provided process chain
    and mounted into the ephemeral database that is used for processing.

"""


class AsyncPersistentResource(ResourceBase):

    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc({
        'tags': ['Processing'],
        'description': DESCR,
        'consumes':['application/json'],
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The location name',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            },
        {
            'name': 'mapset_name',
            'description': 'The name of an existing mapset or a new mapset that should be created',
            'required': True,
            'in': 'path',
            'type': 'string'
        },
            {
                'name': 'process_chain',
                'description': 'The process chain that should be executed',
                'required': True,
                'in': 'body',
                'schema': ProcessChainModel
            }
        ],
        'responses': {
            '200': {
                'description': 'The result of the process chain execution',
                'schema':ProcessingResponseModel
            },
            '400': {
                'description':'The error message and a detailed log why process chain execution '
                              'did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
     })
    def post(self, location_name, mapset_name):
        """Execute a user defined process chain that creates a new mapset or runs in an existing one.

        The process chain that describes the GRASS modules that should be
        executed must be provided as JSON payload of the POST request.

        Args:
            location_name (str): The name of the location
            mapset_name (str): The name of the mapset

        Returns:
            flask.Response:
            The HTTP status and a JSON document that includes the
            status URL of the task that must be polled for updates.

        Process chain input format::

            {                                           # A process chain is a dict with entries for each module that should be run
               Id:{                                     # Id must be numerical and indicates the process order
                    "module":<module_name>,             # Name of the module to run
                    "stdin":<Id::stdout | Id::stderr>     # Use the output of a specific module as input for this module
                                                        # Id:stdout, Id:stderr are available
                    "inputs":{                          # Definition of all input parameters as key:value pairs
                             <parameter name>:<value>,  # e.g.: value == "raster_name@mapset_name" or "degree" or 0.0
                             <parameter name>:<value>   # e.g.: value == $file::slope_output_file to specify an output file
                                                        # that name will be automatically generated by the API.
                    },
                    "outputs":{                         # Definition of all outputs using key:value pairs
                        <parameter name>:{
                            "name":<value>,             # Output name e.g. "my_aspect_map" or a temporary file id
                                                        # definition: $file::id  eg: $file::aspect_output_file
                                                        # This file can be used in other module as input
                            "export":{                  # Export options, if present this map will be exported
                                "format":<value>        # Set the export format raster=GeoTiff (default), vector = shape (default)
                                "type":<output type>,   # Output type e.g.: raster, vector, file, stds
                            }
                        },
                        <parameter name>:{
                            "name":<value>,             # Output name e.g. "my_slope_map"
                            "export":{                  # Export options, if present this map will be exported
                                "format":<value>        # Set the export format raster=GeoTiff (default), vector = shape (default)
                                "type":<output type>,   # Output type e.g.: raster, vector, file, stds
                            }
                        }
                    },
                    "flags":<flags>,                    # All flags in a string e.g.: "ge"
                    "overwrite":<True|False>,           # Set True to overwrite existing data
                    "verbose":<True|False>              # Verbosity of the module
                },
               Id:{                                     # The id of an executable command, that is not a grass module
                    "executable":<path>,                # The name and path of the executable e.g. /bin/cp
                    "stdin":<Id::stdout | Id::stderr>     # Use the output of a specific module as input for this module
                                                        # Id::stdout, Id::stderr are available
                    "parameters":[<parameter>,]         # A list of strings that represent the parameters that may contain
                                                        # temporary file definitions: $file::id  eg: $file::aspect_output_file
               },
                ...
            }

        """
        # Preprocess the post call
        rdc = self.preprocess(has_json=True, location_name=location_name, mapset_name=mapset_name)

        if rdc:
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


def start_job(*args):
    processing = PersistentProcessing(*args)
    processing.run()


class PersistentProcessing(EphemeralProcessing):
    """Processing of grass modules in a temporary or original mapset.

    This class is designed to run GRASS modules that are specified in a process chain
    in a temporary mapset that later on is copied into the original location or merged
    into an existing mapset.

    Locking concept:

        - Check if the target mapset exists
        - Lock the target mapset
        - Create a temporary mapset lock (name is generated in constructor)
        - Create the temporary mapset in the local storage
        - Process

    If target mapset exists:

        - Move the temporary mapset after processing to the user group database
        - Merge the temporary mapset into the target mapset
        - Delete the temporary mapset
        - Unlock the two mapsets after processing is finished, terminated or raised an error

    If target mapset does not exists:

        - After processing finished successfully, copy the
          temporary mapset to the original user group specific location using the target mapset name
        - Unlock the two mapsets after processing is finished, terminated or raised an error

    """
    def __init__(self, rdc):
        """Constructor

        Args:
            rdc (ResourceDataContainer): The data container that contains all required variables for processing

        """

        EphemeralProcessing.__init__(self, rdc)
        self.target_mapset_name = self.mapset_name
        self.target_mapset_exists = False     # By default the target mapset does not exists
        self.target_mapset_lock_set = False   # Set True if this process was successful in setting the lock
        self.orig_mapset_path = None

        # We have two mapset lock ids. The target mapset and the temporary mapset
        self.target_mapset_lock_id = self._generate_mapset_lock_id(self.user_group,
                                                                   self.location_name,
                                                                   self.target_mapset_name)

        self.temp_mapset_lock_id = self._generate_mapset_lock_id(self.user_group,
                                                                 self.location_name,
                                                                 self.temp_mapset_name)
        self.temp_mapset_lock_set = False

    def _generate_mapset_lock_id(self, user_group, location_name, mapset_name):
        """Generate a unique id to lock a mapset in the redis database

        Locations are user group specific. Hence different user groups may have
        locations with the same names and with equal mapset names.

        In the same user group, a location/mapset must be locked to grant exclusive
        access rights.

        Args:
            user_group: The user group used for locking
            location_name: The location name in which the mapset is located for locking
            mapset_name: The mapset name that should be locked

        Returns:
            The lock id

        """
        return "%s/%s/%s"%(user_group, location_name, mapset_name)

    def _lock_temp_mapset(self):
        """Lock the temporary mapset

        This method sets in case of success: self.tmp_mapset_lock_set = True
        """
        # Lock the temporary mapset for the time that the user can allocate at maximum
        ret = self.lock_interface.lock(resource_id=self.temp_mapset_lock_id,
                                       expiration=self.process_time_limit*self.process_num_limit)

        if ret == 0:
            raise AsyncProcessError("Unable to lock temporary mapset <%s>, "
                                    "resource is already locked"%self.target_mapset_name)
        self.message_logger.info("Mapset <%s> locked"%self.target_mapset_name)

        # if we manage to come here, the lock was correctly set
        self.temp_mapset_lock_set = True

    def _check_mapset(self, mapset):
        """Check if the target mapset exists

        This method will check if the target mapset exists in the global and user group locations.
        If the mapset is in the global database, then an AsyncProcessError will be raised, since
        global location/mapsets can not be modified.

        This method sets in case of success:

            self.target_mapset_lock_set = True
            self.tmp_mapset_lock_set = True

        Raises:
            AsyncProcessError

        """
        mapset_exists = False

        # Check if the global location is accessible and that the target mapset does not exist
        if self.is_global_database is True:
            # Break if the target mapset exists in the global database
            if os.path.exists(self.global_location_path) and \
                    os.path.isdir(self.global_location_path) and \
                            os.access(self.global_location_path, os.R_OK | os.X_OK | os.W_OK) is True:

                self.orig_mapset_path = os.path.join(self.global_location_path, mapset)

                if os.path.exists(self.orig_mapset_path) is True:
                    if os.access(self.orig_mapset_path, os.R_OK | os.X_OK | os.W_OK) is True:
                        raise AsyncProcessError("Mapset <%s> exists in the global "
                                                "dataset and can not be modified."%mapset)
            else:
                raise AsyncProcessError("Unable to access global location <%s>"%self.location_name)

        # Always check if the targte mapset already exists and set the flag accordingly
        if os.path.exists(self.user_location_path) and \
                os.path.isdir(self.user_location_path) and \
                        os.access(self.user_location_path, os.R_OK | os.X_OK | os.W_OK) is True:

            self.orig_mapset_path = os.path.join(self.user_location_path, mapset)

            if os.path.exists(self.orig_mapset_path) is True:
                if os.access(self.orig_mapset_path, os.R_OK | os.X_OK | os.W_OK) is True:
                    mapset_exists = True
                    # Add the existing mapset to the required ones for mapset search path settings
                    self.required_mapsets.append(mapset)
                else:
                    raise AsyncProcessError("Unable to access mapset <%s> "
                                            "path %s"%(mapset,
                                            self.orig_mapset_path))
            else:
                mapset_exists = False
        else:
            raise AsyncProcessError("Unable to access user location <%s>"%self.location_name)

        return mapset_exists

    def _check_lock_target_mapset(self):
        """Check if the target mapset exists and lock it, then lock the temporary mapset

        This method will check if the target mapset exists in the global and user location.
        If the mapset is in the global database, then an AsyncProcessError will be raised, since
        global mapsets can not be modified.

        This method sets in case of success:

            self.target_mapset_lock_set = True
            self.tmp_mapset_lock_set = True

        Raises:
            AsyncProcessError

        """
        self.target_mapset_exists = self._check_mapset(self.target_mapset_name)
        self._lock_target_mapset()

    def _lock_target_mapset(self):
        """Lock the target mapset

        Raises:
            AsyncProcessError

        """

        # Lock the mapset for the time that the user can allocate at maximum
        ret = self.lock_interface.lock(resource_id=self.target_mapset_lock_id,
                                       expiration=self.process_time_limit*self.process_num_limit)

        if ret == 0:
            raise AsyncProcessError("Unable to lock location/mapset <%s/%s>, "
                                    "resource is already locked"%(self.location_name,
                                                                  self.target_mapset_name))
        self.message_logger.info("location/mapset <%s/%s> locked"%(self.location_name,
                                                                   self.target_mapset_name))

        # if we manage to come here, the lock was correctly set
        self.target_mapset_lock_set = True

    def _merge_mapset_into_target(self, source_mapset, target_mapset):
        """Link the source mapset content into the target mapset

        TODO: Implement support for temporal database merging

        Attention: Only raster and vector layers are copied at the moment
        """
        self.message_logger.info("Copy source mapset <%s> content "
                                 "into the target mapset <%s>"%(source_mapset, target_mapset))

        # Raster adn vector directories
        directories = ["cell", "misc", "fcell",
                       "cats", "cellhd",
                       "cell_misc", "colr", "colr2",
                       "hist", "vector"]

        for directory in directories:
            source_path = os.path.join(self.user_location_path, source_mapset, directory)
            target_path = os.path.join(self.user_location_path, target_mapset)

            if os.path.exists(source_path) is True:
                # Hardlink the sources into the target
                stdout=subprocess.PIPE
                stderr=subprocess.PIPE

                p = subprocess.Popen(["/bin/cp", "-flr",
                                      "%s"%source_path,
                                      "%s/."%target_path],
                                     stdout=stdout,
                                     stderr=stderr)
                (stdout_buff, stderr_buff) = p.communicate()
                if p.returncode != 0:
                    raise AsyncProcessError("Unable to merge mapsets. Error in linking:"
                                            " stdout: %s stderr: %s"%(stdout_buff, stderr_buff))

    def _copy_merge_tmp_mapset_to_target_mapset(self):
        """Copy the temporary mapset into the original location

        In case the mapset does not exists, then use the target mapset name, otherwise use
        the temporary mapset name for copying which is later on merged into the target mapset
        and then removed
        """

        # Extent the mapset lock for an hour, since copying can take long
        if self.target_mapset_lock_set is True:
            ret = self.lock_interface.extend(resource_id=self.target_mapset_lock_id,
                                             expiration=3600)
            if ret == 0:
                raise AsyncProcessError("Unable to extend lock for mapset "
                                        "<%s>"%self.target_mapset_name)

        if self.temp_mapset_lock_set is True:
            ret = self.lock_interface.extend(resource_id=self.temp_mapset_lock_id,
                                             expiration=3600)
            if ret == 0:
                raise AsyncProcessError("Unable to extend lock for "
                                        "temporary mapset <%s>"%self.temp_mapset_name)

        self.message_logger.info("Copy temporary mapset from %s to %s"%(self.temp_mapset_path,
                                                                    os.path.join(self.user_location_path,
                                                                                 self.target_mapset_name)))

        source_path = self.temp_mapset_path

        # In case the mapset does not exists, then use the target mapset name, otherwise use
        # the temporary mapset name for copying which is later on merged into the target mapset
        # and then removed
        if self.target_mapset_exists is True:
            target_path = self.user_location_path + "/."
            message = "Copy temporary mapset <%s> to target location " \
                      "<%s>"%(self.temp_mapset_name, self.location_name)
        else:
            target_path = os.path.join(self.user_location_path, self.target_mapset_name)
            message = "Copy temporary mapset <%s> to target location " \
                      "<%s>"%(self.target_mapset_name, self.location_name)

        self._send_resource_update(message)

        try:
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
            p = subprocess.Popen(["/bin/cp", "-fr",
                                  "%s"%source_path,
                                  "%s"%target_path],
                                 stdout=stdout,
                                 stderr=stderr)
            (stdout_buff, stderr_buff) = p.communicate()
            if p.returncode != 0:
                raise AsyncProcessError("Unable to copy temporary mapset to "
                                        "original location. Copy error "
                                        "stdout: %s stderr: %s returncode: %i"%(stdout_buff,
                                                                                stderr_buff,
                                                                                p.returncode))
        except Exception as e:
            raise AsyncProcessError("Unable to copy temporary mapset to "
                                    "original location. Exception %s"%str(e))

        # Merge the temp mapset into the target mapset in case the target already exists
        if self.target_mapset_exists is True:
            self._merge_mapset_into_target(self.temp_mapset_name, self.target_mapset_name)
            shutil.rmtree(os.path.join(self.user_location_path, self.temp_mapset_name))

    def _execute_process_list(self, process_list):
        """Extend the mapset lock and execute the provided process list

        Args:
            process_list: The process list to execute

        Raises:
            This method will raise an AsyncProcessError or AsyncProcessTermination
        """
        for process in process_list:
            # Extent the lock for each process by max processing time * 2
            if self.target_mapset_lock_set is True:
                ret = self.lock_interface.extend(resource_id=self.target_mapset_lock_id,
                                                 expiration=self.process_time_limit * 2)
                if ret == 0:
                    raise AsyncProcessError("Unable to extend lock for mapset <%s>"%self.target_mapset_name)

            if self.temp_mapset_lock_set is True:
                # Extent the lock for each process by max processing time * 2
                ret = self.lock_interface.extend(resource_id=self.temp_mapset_lock_id,
                                                 expiration=self.process_time_limit * 2)
                if ret == 0:
                    raise AsyncProcessError("Unable to extend lock for "
                                            "temporary mapset <%s>"%self.temp_mapset_name)

            if process.exec_type == "grass":
                self._run_module(process)
            elif process.exec_type == "exec":
                self._run_process(process)
            elif process.exec_type == "python":
                eval(process.executable)

    def _execute(self, skip_permission_check=False):
        """Overwrite this function in subclasses

            - Call self._setup()
            - Analyse the process chain
            - Check the target mapset and lock it for the maximum time
              a user can consume -> process_num_limit*process_time_limit
            - Initialize and create the temporal database and mapset
              or use the original mapset
            - Run the modules and extend the lock each run
            - Copy the mapset if it has not already exist
            - Cleanup and unlock the mapset

        """
        # Setup the user credentials and logger
        self._setup()
        # Create the process chain
        process_list = self._validate_process_chain()
        # Check and lock the target and temp mapsets
        self._check_lock_target_mapset()

        if self.target_mapset_exists is False:
            # Create the temp database and link the
            # required mapsets into it
            self._create_temp_database(self.required_mapsets)

            # Initialize the GRASS environment and switch into PERMANENT
            # mapset, which is always linked
            self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                           mapset_name="PERMANENT")

            # Create the temporary mapset wth the same name as the targte mapset and switch into it
            self._create_temporary_mapset(temp_mapset_name=self.target_mapset_name)
            self.temp_mapset_name = self.target_mapset_name
        else:
            # Init GRASS environment and create the temporary mapset
            self._create_temporary_grass_environment(source_mapset_name=self.target_mapset_name)
            self._lock_temp_mapset()

        # Execute the process list
        self._execute_process_list(process_list)
        # Copy local mapset to original location, merge mapsets
        # if necessary
        self._copy_merge_tmp_mapset_to_target_mapset()

    def _final_cleanup(self):
        """Final cleanup called in the run function at the very end of processing
        """
        # Clean up and remove the temporary gisdbase
        self._cleanup()
        # Unlock the mapsets
        if self.target_mapset_lock_set is True:
            self.lock_interface.unlock(self.target_mapset_lock_id)
        if self.temp_mapset_lock_set is True:
            self.lock_interface.unlock(self.temp_mapset_lock_id)
