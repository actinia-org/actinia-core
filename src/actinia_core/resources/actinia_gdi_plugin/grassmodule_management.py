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
Module management


* List all modules

"""
import shutil
import json
from flask import jsonify, make_response
from copy import deepcopy
from flask_restful_swagger_2 import swagger
from flask_restful_swagger_2 import Schema
import pickle

from actinia_core.resources.location_management import LocationManagementResourceAdmin, create_location
from actinia_core.resources.ephemeral_processing import EphemeralProcessing
from actinia_core.resources.resource_base import ResourceBase
from actinia_core.resources.common.app import auth
from actinia_core.resources.common.logging_interface import log_api_call
from actinia_core.resources.common.redis_interface import enqueue_job, start_job
from actinia_core.resources.common.exceptions import AsyncProcessError
from actinia_core.resources.user_auth import check_user_permissions
from actinia_core.resources.user_auth import very_admin_role
from actinia_core.resources.common.response_models import ProcessingResponseModel, \
    StringListProcessingResultResponseModel, MapsetInfoResponseModel, \
    MapsetInfoModel, RegionModel, ProcessingErrorResponseModel

from actinia_core.resources.common.config import global_config

__license__    = "GPLv3"
__author__ = "Anika Bettge"
__copyright__ = "Copyright 2019, mundialis"
__maintainer__ = "Anika Bettge"


class ModuleResponseModel(Schema):
    """Response schema for module
    """
    """Response schema for module lists
    """
    type = 'object'
    properties = {
        'id': {
            'type': 'string',
            'description': 'Unique identifier of the process. '
        },
        'summary': {
            'type': 'string',
            'description': 'A short summary of what the process does.'
        },
        'description': {
            'type': 'string',
            'description': 'Detailed description to fully explain the entity.'
        },
        'categories': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'A list of categories.'
        }
    }
    example = {
        "id": "v.random",
        "description": "Generates random 2D/3D vector points.",
        "categories": ["vector", "sampling", "statistics", "random", "point pattern", "stratified random sampling", "level1"]}
    required = ["id", "description"]


class ModuleListResponseModel(Schema):
    """Response schema for module lists
    the answer bases on openeo v0.4: https://open-eo.github.io/openeo-api/v/0.4.0/apireference/#tag/Process-Discovery/paths/~1processes/get
       module name is set to id
       the keywords to the categories
       description is set to the required description and not to the optional summary
    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The status of the resource, values: accepted, running, finished, terminated, error'
        },
        'processes': {
            'type': 'array',
            'items': ModuleResponseModel,
            'description': 'The list of modules in GRASS GIS'
        }
    }
    example = {"processes": [{
        "id": "v.random",
        "description": "Generates random 2D/3D vector points.",
        "categories": ["vector", "sampling", "statistics", "random", "point pattern", "stratified random sampling", "level1"]}
        ], "status": "success"}
    required = ["status", "processes"]


class ListModules(ResourceBase):
    """List all modules
    """
    layer_type = None

    @swagger.doc({
        'tags': ['Module Management'],
        'description': 'Get a list of modules. '
                       'Minimum required user role: user.',
        'responses': {
            '200': {
                'description': 'This response returns a list of module names and the log '
                               'of the process chain that was used to create the response.',
                'schema': StringListProcessingResultResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why listing of '
                               'modules did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self):
        """Get a list of all modules.
        """
        # not using enqueue_job to get always a response
        import subprocess
        import os

        grass_module = "g.search.modules"
        grass_module_path = os.path.join(global_config.GRASS_GIS_START_SCRIPT, "bin", grass_module)
        if os.path.isfile(grass_module_path) is not True:
            grass_module_path = os.path.join(global_config.GRASS_GIS_START_SCRIPT, "scripts", grass_module)

        # # create location
        location_name = 'utm32n' #'location_for_listing_modules'
        # location_manager = LocationManagementResourceAdmin()
        # # location_manager.post("list_modules")
        # location = os.path.join(location_manager.grass_data_base, location_name)
        # # Check the location path
        # if os.path.isdir(location):
        #     return self.get_error_response(message="Unable to create location. "
        #                                            "Location <%s> exists in global database." % location_name)
        # # Check also for the user database
        # location = os.path.join(self.grass_user_data_base, self.user_group, location_name)
        # # Check the location path
        # if os.path.isdir(location):
        #     return self.get_error_response(message="Unable to create location. "
        #                                            "Location <%s> exists in user database." % location_name)

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name, #"list_modules",# 'utm32n', # TODO
                              mapset_name="PERMANENT")
        # if rdc:
        #     start_job(self.job_timeout, create_location, rdc)
        # # else:
        # #     raise AsyncProcessError("Unable to create location <%s>" % new_location)


        if rdc:
            start_job(self.job_timeout, list_modules, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        # import pdb; pdb.set_trace()
        j_data = json.loads(response_model['process_results'])


        module_list = []
        for data in j_data:
            description = data['attributes']['description']
            keywords = data['attributes']['keywords']
            name = data['name']
            module_response = (ModuleResponseModel(id=name, description=description, categories=keywords.split(',')))
            module_list.append(module_response)

        return make_response(jsonify(ModuleListResponseModel(status="success", processes=module_list)), 200)


def list_modules(*args):
    processing = EphemeralModuleLister(*args)
    processing.run()


class EphemeralModuleLister(EphemeralProcessing):
    """List all modules
    """

    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)
        self.response_model_class = StringListProcessingResultResponseModel

    def _execute(self):

        self._setup()

        # Create the temporary database and link all available mapsets into is
        self._create_temp_database()

        pc = {"1": {"module": "g.search.modules", "inputs": {"keyword": ""},
                    "flags": "j"}}

        process_list = self._validate_process_chain(process_chain=pc,
                                                    skip_permission_check=True)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name="PERMANENT")

        self._execute_process_list(process_list)

        self.module_results = self.module_output_log[0]["stdout"]
