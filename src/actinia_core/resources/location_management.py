# -*- coding: utf-8 -*-
"""
TODO: Integrate into the ephemeral process chain approach

"""

from flask import jsonify, make_response
import os
import shutil
from flask_restful_swagger_2 import swagger, Schema
from actinia_core.resources.common.app import auth
from actinia_core.resources.common.logging_interface import log_api_call
from actinia_core.resources.user_auth import very_admin_role
from actinia_core.resources.user_auth import check_user_permissions
from actinia_core.resources.common.response_models import ProcessingResponseModel
from actinia_core.resources.common.response_models import SimpleResponseModel, MapsetInfoResponseModel
from actinia_core.resources.async_resource_base import AsyncEphemeralResourceBase
from actinia_core.resources.async_persistent_processing import AsyncPersistentProcessing
from actinia_core.resources.mapset_management import AsyncPersistentGetProjectionRegionInfo
from actinia_core.resources.common.redis_interface import enqueue_job
from actinia_core.resources.common.exceptions import AsyncProcessError


__license__ = "GPLv3"
__author__     = "S�ren Gebbert"
__copyright__  = "Copyright 2016, S�ren Gebbert"
__maintainer__ = "S�ren Gebbert"
__email__      = "soerengebbert@googlemail.com"


class LocationListResponseModel(Schema):
    """Response schema for location lists
    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The status of the resource, values: accepted, running, finished, terminated, error'
        },
        'locations': {
            'type': 'array',
            'items':{"type":"string"},
            'description': 'The list of locations in the GRASS database'
        }
    }
    example = {"locations": ["nc_spm_08" "LL", "ECAD"],"status": "success"}
    required = ["status", "locations"]


class ListLocationsResource(AsyncEphemeralResourceBase):
    """This resource represents grass database directory
    that contains locations.
    """

    def __init__(self):
        AsyncEphemeralResourceBase.__init__(self)

    """Return a list of all available locations that are located in the GRASS database
    """
    layer_type = None
    @swagger.doc({
        'tags': ['location management'],
        'description': 'Return a list of all available locations that are located in the '
                       'GRASS database and the user has access to. Minimum required user role: user.',
        'responses': {
            '200': {
                'description': 'This response returns a list of location names',
                'schema':LocationListResponseModel
            },
            '400': {
                'description': 'The error message',
                'schema':SimpleResponseModel
            }
        }
    })
    def get(self):
        """Return a list of all available locations
        """
        locations = []

        if os.path.isdir(self.grass_data_base):
            dirs = os.listdir(self.grass_data_base)
            for dir in dirs:
                dir_path = os.path.join(self.grass_data_base, dir)
                if os.path.isdir(dir_path) and os.access(dir_path, os.R_OK & os.X_OK):
                    # Check for PERMANENT mapset existence
                    mapset_path = os.path.join(dir_path, "PERMANENT")
                    if os.path.isdir(mapset_path) and os.access(mapset_path, os.R_OK & os.X_OK):
                        # Check access rights to the global database
                        # Super admin can see all locations
                        if self.has_superadmin_role or dir in self.user_credentials["permissions"]["accessible_datasets"]:
                            locations.append(dir)
        # List all locations in the user database
        user_database = os.path.join(self.grass_user_data_base, self.user_group)
        if os.path.isdir(user_database):
            dirs = os.listdir(user_database)
            for dir in dirs:
                dir_path = os.path.join(user_database, dir)
                if os.path.isdir(dir_path) and os.access(dir_path, os.R_OK & os.X_OK):
                    # Check for PERMANENT mapset existence
                    mapset_path = os.path.join(dir_path, "PERMANENT")
                    if os.path.isdir(mapset_path) and os.access(mapset_path, os.R_OK & os.X_OK):
                        locations.append(dir)
        if locations:
            return make_response(jsonify(LocationListResponseModel(status="success", locations=locations)), 200)
        else:
            return make_response(jsonify(SimpleResponseModel(status="error",
                                                             message="Unable to access GRASS database.")), 405)


class ProjectionInfoModel(Schema):
    """Schema to define projection information as JSON input in POST requests
    """
    type = 'object'
    properties = {
        'epsg': {
            'type': 'string',
            'description': 'The EPSG code of the projection that should be used to create a location'
        }
    }
    example = {"epsg": "4326"}
    required = ["epsg"]


class LocationManagementResourceUser(AsyncEphemeralResourceBase):
    """This class returns informations about a specific location
    """
    def __init__(self):
        AsyncEphemeralResourceBase.__init__(self)

    @swagger.doc({
        'tags': ['location management'],
        'description': 'Return the location projection and current computational '
                       'region of the PERMANENT mapset. Minimum required user role: user.',
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
                'description': 'The location projection and current computational '
                               'region of the PERMANENT mapset',
                'schema':MapsetInfoResponseModel
            },
            '400': {
                'description': 'The error message',
                'schema':ProcessingResponseModel
            }
        }
    })
    def get(self, location_name):
        """Return the current region of the mapset
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name="PERMANENT")

        enqueue_job(self.job_timeout, read_current_region, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


class LocationManagementResourceAdmin(AsyncEphemeralResourceBase):
    """This class manages the creation, deletion and modification of a mapsets

    This is only allowed for administrators
    """
    decorators = [log_api_call, check_user_permissions,
                  very_admin_role, auth.login_required]

    def __init__(self):
        AsyncEphemeralResourceBase.__init__(self)

    @swagger.doc({
        'tags': ['location management'],
        'description': 'Delete an existing location and everything inside from the user database. '
                       'Minimum required user role: admin.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location to be deleted',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'Success message for location deletion',
                'schema':SimpleResponseModel
            },
            '400': {
                'description': 'The error message',
                'schema':SimpleResponseModel
            }
        }
    })
    def delete(self, location_name):
        """Delete a specific location by name
        """
        # Delete only locations from the user database
        location = os.path.join(self.grass_user_data_base, self.user_group, location_name)
        permanent_mapset =  os.path.join(location, "PERMANENT")
        wind_file =  os.path.join(permanent_mapset, "WIND")
        # Check the location path, only "valid" locations can be deleted
        if os.path.isdir(location):
            if os.path.isdir(permanent_mapset) and os.path.isfile(wind_file):
                try:
                    shutil.rmtree(location)
                    return make_response(jsonify(SimpleResponseModel(status="success",
                                                                     message="location %s deleted"%location_name)),
                                         200)
                except Exception as e:
                    return make_response(jsonify(SimpleResponseModel(status="error",
                                                  message="Unable to delete "
                                                          "location %s Exception %s"%(location_name,str(e)))),
                                         500)

        return make_response(jsonify(SimpleResponseModel(status="error",
                                                         message="location %s does not exists"%location_name)),
                             400)

    @swagger.doc({
        'tags': ['location management'],
        'description': 'Create a new location based on EPSG code in the user database. '
                       'Minimum required user role: admin.',
        'consumes':['application/json'],
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location to be created',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'epsg_code',
                'description': 'The EPSG code',
                'required': True,
                'in': 'body',
                'schema': ProjectionInfoModel
            }
        ],
        'responses': {
            '200': {
                'description': 'Create a new location based on EPSG code',
                'schema':ProcessingResponseModel
            },
            '400': {
                'description': 'The error message',
                'schema':ProcessingResponseModel
            }
        }
    })
    def post(self, location_name):
        """Create a new location based on EPSG code
        """
        # Create only new locations if they did not exist in the global database
        location = os.path.join(self.grass_data_base, location_name)
        # Check the location path
        if os.path.isdir(location):
            self.raise_invalid_usage(message="Unable to create location. "
                                             "Location <%s> exists in global database."%location_name)
        # Check also for the user database
        location = os.path.join(self.grass_user_data_base, self.user_group, location_name)
        # Check the location path
        if os.path.isdir(location):
            self.raise_invalid_usage(message="Unable to create location. "
                                             "Location <%s> exists in user database."%location_name)

        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name,
                              mapset_name="PERMANENT")

        enqueue_job(self.job_timeout, create_location, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


def create_location(*args):
    processing = AsyncPersistentLocationCreator(*args)
    processing.run()


class AsyncPersistentLocationCreator(AsyncPersistentProcessing):
    """Create a new location based on EPSG code
    """

    def __init__(self, *args):
        AsyncPersistentProcessing.__init__(self, *args)

    def _execute(self):

        new_location = self.location_name

        self.location_name = self.config.GRASS_DEFAULT_LOCATION

        self._setup()

        epsg_code = self.request_data["epsg"]

        self._create_temp_database()

        pc = {"1":{"module":"g.proj",
                   "inputs":{"epsg":epsg_code,
                             "location":new_location},
                   "flags":"t"}}

        process_chain = self._validate_process_chain(process_chain=pc,
                                                     skip_permission_check=True)

        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name="PERMANENT")

        self._execute_process_chain(process_chain)

        if os.path.isdir(os.path.join(self.temp_grass_data_base, new_location)):
            shutil.move(os.path.join(self.temp_grass_data_base, new_location), self.grass_user_data_base)
        else:
            raise AsyncProcessError("Unable to create location <%s>"%new_location)

        self.finish_message = "Location <%s> successfully created"%new_location


def read_current_region(*args):
    processing = AsyncPersistentGetProjectionRegionInfo(*args)
    processing.run()
