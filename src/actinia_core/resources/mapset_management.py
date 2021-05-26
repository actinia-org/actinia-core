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
Mapset management resources

* List all mapsets
* Create mapset, Delete mapset, Get info about a mapset
* Lock mapset, unlock mapset, get mapset lock status
"""

import shutil
from flask import jsonify, make_response
from copy import deepcopy
from flask_restful_swagger_2 import swagger
import pickle
from .persistent_processing import PersistentProcessing
from .resource_base import ResourceBase
from .common.app import auth
from .common.api_logger import log_api_call
from .common.redis_interface import enqueue_job
from .common.exceptions import AsyncProcessError
from .user_auth import check_user_permissions
from .user_auth import very_admin_role
from .common.response_models import ProcessingResponseModel, \
    StringListProcessingResultResponseModel, MapsetInfoResponseModel, \
    RegionModel, ProcessingErrorResponseModel
# from .common.response_models import MapsetInfoModel

from .common.config import global_config
from .common.redis_base import RedisBaseInterface

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ListMapsetsResource(ResourceBase):
    """List all mapsets in a location
    """
    layer_type = None

    @swagger.doc({
        'tags': ['Mapset Management'],
        'description': 'Get a list of all mapsets that are located in a '
                       'specific location. '
                       'Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns a list of mapset names '
                               'and the log of the process chain that was used '
                               'to create the response.',
                'schema': StringListProcessingResultResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why listing of '
                               'mapsets did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name):
        """Get a list of all mapsets that are located in a specific location.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name="PERMANENT")
        if rdc:
            enqueue_job(self.job_timeout, list_raster_mapsets, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)


def list_raster_mapsets(*args):
    processing = PersistentMapsetLister(*args)
    processing.run()


class PersistentMapsetLister(PersistentProcessing):
    """List all mapsets in a location
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)
        self.response_model_class = StringListProcessingResultResponseModel

    def _execute(self):
        self._setup()
        # Create the temporary database and link all available mapsets into is
        self._create_temp_database()

        pc = {"1": {"module": "g.mapsets", "inputs": {"separator": "newline"},
                    "flags": "l"}}

        process_list = self._validate_process_chain(process_chain=pc,
                                                    skip_permission_check=True)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name="PERMANENT")

        self._execute_process_list(process_list)

        mapset_lists = []
        mapsets = self.module_output_log[0]["stdout"].split()

        for mapset in mapsets:
            mapset_lists.append(mapset.strip())

        self.module_results = mapset_lists


class MapsetManagementResourceUser(ResourceBase):
    """This class returns information about a mapsets
    """

    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc({
        'tags': ['Mapset Management'],
        'description': 'Get the current computational region of the mapset and the '
                       'projection of the location as WKT string. Minimum required '
                       'user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            }
        ],
        'responses': {
            '200': {
                'description': 'The current computational region of the '
                               'mapset and the projection of the location',
                'schema': MapsetInfoResponseModel
            },
            '400': {
                'description': 'The error message and a detailed error log',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name):
        """Get the current computational region of the mapset and the projection
        of the location as WKT string.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name)

        enqueue_job(self.job_timeout, read_current_region, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


class MapsetManagementResourceAdmin(ResourceBase):
    """This class manages the creation, deletion and modification of a mapsets

    This is only allowed for administrators
    """
    decorators = [log_api_call, check_user_permissions,
                  very_admin_role, auth.login_required]

    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc({
        'tags': ['Mapset Management'],
        'description': 'Create a new mapset in an existing location. Minimum '
                       'required user role: admin.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'Success message for mapset creation',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed error log',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def post(self, location_name, mapset_name):
        """Create a new mapset in an existing location.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name)

        enqueue_job(self.job_timeout, create_mapset, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    def put(self, location_name, mapset_name):
        """Modify the region of a mapset

        TODO: Implement region setting

        Args:
            location_name (str): Name of the location
            mapset_name (str): Name of the mapset

        Returns:
            flaks.Response:
            HTTP 200 and JSON document in case of success, HTTP 400 otherwise

        """
        pass

    @swagger.doc({
        'tags': ['Mapset Management'],
        'description': 'Delete an existing mapset. Minimum required user role: admin.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'Success message for mapset deletion',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed error log',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name):
        """Delete an existing mapset.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name)

        enqueue_job(self.job_timeout, delete_mapset, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


def read_current_region(*args):
    processing = PersistentGetProjectionRegionInfo(*args)
    processing.run()


class PersistentGetProjectionRegionInfo(PersistentProcessing):
    """Read the current region and projection information
    """

    integer_values = ["projection", "zone", "rows", "rows3",
                      "cols", "cols3", "depths", "cells", "cells3"]
    float_values = ["n", "s", "e", "w", "t", "b", "nsres",
                    "nsres3", "ewres", "ewres3", "tbres"]

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)
        self.response_model_class = MapsetInfoResponseModel

    def _execute(self):

        self._setup()

        pc = {"1": {"module": "g.region",
                    "flags": "ug3"},
              "2": {"module": "g.proj",
                    "flags": "fw"}}

        # Do not check the region size
        self.skip_region_check = True
        process_list = self._validate_process_chain(process_chain=pc,
                                                    skip_permission_check=True)
        self._create_temp_database(self.required_mapsets)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_list(process_list)

        mapset_region = {}
        region_settings = self.module_output_log[0]["stdout"].split()

        for region_token in region_settings:
            if "=" in region_token:
                key, value = region_token.strip().split("=")
                if key in self.integer_values:
                    mapset_region[key] = int(value)
                if key in self.float_values:
                    mapset_region[key] = float(value)

        self.module_results = dict(region=RegionModel(**mapset_region),
                                   projection=self.module_output_log[1]["stdout"])

        # self.module_results = MapsetInfoModel(region=RegionModel(**mapset_region),
        #                             projection=self.module_output_log[1]["stdout"])


def create_mapset(*args):
    processing = PersistentMapsetCreator(*args)
    processing.run()


class PersistentMapsetCreator(PersistentProcessing):
    """Create a mapset in an existing location
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()
        # Create temporary database
        self._create_temp_database()

        pc = {"1": {"module": "g.mapsets",
                    "flags": "l"}}

        process_list = self._validate_process_chain(process_chain=pc,
                                                    skip_permission_check=True)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name="PERMANENT")

        self._execute_process_list(process_list)

        mapset_list = []
        mapsets = self.module_output_log[0]["stdout"].split()

        for mapset in mapsets:
            mapset_list.append(mapset.strip())

        if self.target_mapset_name in mapset_list:
            raise AsyncProcessError("Mapset <%s> exists." % self.target_mapset_name)

        # Create the new temporary mapset and merge it into the user database location
        self._check_lock_target_mapset()
        self.required_mapsets = ["PERMANENT"]
        self._create_temporary_mapset(temp_mapset_name=self.temp_mapset_name)
        self._copy_merge_tmp_mapset_to_target_mapset()

        self.finish_message = \
            "Mapset <%s> successfully created." % self.target_mapset_name


def delete_mapset(*args):
    processing = PersistentMapsetDeleter(*args)
    processing.run()


class PersistentMapsetDeleter(PersistentProcessing):
    """Delete a mapset from a location

    1. Create temporary database
    2. Check if PERMANENT mapset or global mapset which are not allowed to be deleted
    3. Check if the mapset exists
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()

        # For debug purpose
        # self.lock_interface.unlock(self.target_mapset_lock_id)

        if "PERMANENT" == self.target_mapset_name:
            raise AsyncProcessError("The PERMANENT mapset can not be deleted. "
                                    "You must remove the location to get rid of it.")

        # Delete existing mapset
        self._check_lock_target_mapset()
        # The variable self.orig_mapset_path is set by _check_lock_target_mapset()
        if self.target_mapset_exists is True:
            shutil.rmtree(self.orig_mapset_path)
            self.lock_interface.unlock(self.target_mapset_lock_id)
            self.finish_message = \
                "Mapset <%s> successfully removed." % self.target_mapset_name
        else:
            raise AsyncProcessError("Mapset <%s> does not exits" %
                                    self.target_mapset_name)


class MapsetLockManagementResponseModel(ProcessingResponseModel):
    """The response content that is returned by the GET request
    """
    type = 'object'
    properties = deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = {}
    properties["process_results"]["type"] = "boolean"
    required = deepcopy(ProcessingResponseModel.required)
    example = {
        "accept_datetime": "2018-05-02 11:03:26.529673",
        "accept_timestamp": 1525259006.5296717,
        "api_info": {
            "endpoint": "mapsetlockmanagementresource",
            "method": "GET",
            "path": "/locations/nc_spm_08/mapsets/PERMANENT/lock",
            "request_url": "http://localhost:8080/locations/nc_spm_08/mapsets/"
                           "PERMANENT/lock"
        },
        "datetime": "2018-05-02 11:03:26.586348",
        "http_code": 200,
        "message": "Mapset lock state: False",
        "process_chain_list": [],
        "process_log": [],
        "process_results": False,
        "progress": {
            "num_of_steps": 0,
            "step": 0
        },
        "resource_id": "resource_id-162101d9-2abc-417e-83ef-dc6f52ed7aaf",
        "status": "finished",
        "time_delta": 0.056743621826171875,
        "timestamp": 1525259006.5863316,
        "urls": {
            "resources": [],
            "status": "http://localhost:8080/resources/admin/"
                      "resource_id-162101d9-2abc-417e-83ef-dc6f52ed7aaf"
        },
        "user_id": "admin"
    }


class MapsetLockManagementResource(ResourceBase):
    """Lock a mapset
    """
    decorators = [log_api_call, check_user_permissions,
                  very_admin_role, auth.login_required]

    @swagger.doc({
        'tags': ['Mapset Management'],
        'description': 'Get the location/mapset lock status. '
                       'Minimum required user role: admin.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            }
        ],
        'responses': {
            '200': {
                'description': 'Get the location/mapset lock status, either '
                               '"True" or "None"',
                'schema': MapsetLockManagementResponseModel
            },
            '400': {
                'description': 'The error message and a detailed error log',
                'schema': ProcessingResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name):
        """Get the location/mapset lock status.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name)

        enqueue_job(self.job_timeout, get_mapset_lock, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['Mapset Management'],
        'description': 'Create a location/mapset lock. A location/mapset lock can '
                       'be created so that no operation can be performed on it '
                       'until it is unlocked. '
                       'Minimum required user role: admin.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            }
        ],
        'responses': {
            '200': {
                'description': 'Success message if the location/mapset was '
                               'locked successfully',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed error log',
                'schema': ProcessingResponseModel
            }
        }
    })
    def post(self, location_name, mapset_name):
        """Create a location/mapset lock.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name)

        enqueue_job(self.job_timeout, lock_mapset, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['Mapset Management'],
        'description': 'Delete a location/mapset lock. A location/mapset lock '
                       'can be deleted so that operation can be performed on '
                       'it until it is locked. '
                       'Minimum required user role: admin.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            }
        ],
        'responses': {
            '200': {
                'description': 'Success message if the location/mapset was '
                               'unlocked successfully',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed error log',
                'schema': ProcessingResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name):
        """Delete a location/mapset lock.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name)

        enqueue_job(self.job_timeout, unlock_mapset, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


def get_mapset_lock(*args):
    processing = PersistentGetMapsetLock(*args)
    processing.run()


class PersistentGetMapsetLock(PersistentProcessing):
    """Get the mapset lock status
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()
        self._check_target_mapset_exists()
        if self.target_mapset_exists is False:
            raise AsyncProcessError(
                ("Unable to get lock status of mapset <%s> in location <%s>:"
                 " Mapset does not exist")
                % (self.mapset_name, self.location_name))
        else:
            self.module_results = self.lock_interface.get(
                self.target_mapset_lock_id)
            self.finish_message = "Mapset lock state: %s" % str(
                self.module_results)


def lock_mapset(*args):
    processing = PersistentMapsetLocker(*args)
    processing.run()


class PersistentMapsetLocker(PersistentProcessing):
    """Lock a mapset
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()
        self._check_lock_target_mapset()
        if self.target_mapset_exists is False:
            raise AsyncProcessError(
                "Unable to lock mapset <%s>. Mapset doesn not exists."
                % self.target_mapset_name)

        self.finish_message = \
            "Mapset <%s> successfully locked" % self.target_mapset_name

    def _final_cleanup(self):
        """Final cleanup called in the run function at the very end of processing
        """
        # Clean up and remove the temporary files
        self._cleanup()


def unlock_mapset(*args):
    processing = PersistentMapsetUnlocker(*args)
    processing.run()


class PersistentMapsetUnlocker(PersistentProcessing):
    """Unlock a locked mapset
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()
        self._check_target_mapset_exists()
        if self.target_mapset_exists is False:
            raise AsyncProcessError(
                ("Unable to unlock mapset <%s> in location <%s>:"
                 " Mapset does not exist")
                % (self.mapset_name, self.location_name))
        else:
            self.lock_interface.unlock(self.target_mapset_lock_id)
            self.finish_message = \
                "Mapset <%s> successfully unlocked" % self.target_mapset_name


class MapsetLockManagementResourceAdmin(ResourceBase):
    """ Get all locked mapsets
    """
    decorators = [log_api_call, check_user_permissions,
                  very_admin_role, auth.login_required]

    def get(self):
        redis_interface = RedisBaseInterface()
        kwargs = dict()
        kwargs["host"] = global_config.REDIS_SERVER_URL
        kwargs["port"] = global_config.REDIS_SERVER_PORT
        if global_config.REDIS_SERVER_PW and global_config.REDIS_SERVER_PW is not None:
            kwargs["password"] = global_config.REDIS_SERVER_PW
        redis_interface.connect(**kwargs)
        redis_connection = redis_interface.redis_server
        keys_locked = redis_connection.keys("RESOURCE-LOCK*")
        keys_locked_dec = [key.decode() for key in keys_locked]
        mapsets_locked = ["/".join(key.split("/")[-2:]) for key in keys_locked_dec]
        import pdb; pdb.set_trace()
