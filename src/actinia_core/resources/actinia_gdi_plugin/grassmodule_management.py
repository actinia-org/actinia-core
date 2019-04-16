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
import os
import shutil
import json
from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
from flask_restful_swagger_2 import Schema
import pickle
import uuid
# from flask_restful_swagger_2 import Resource

from actinia_core.resources.ephemeral_processing import EphemeralProcessing
from actinia_core.resources.resource_base import ResourceBase
from actinia_core.resources.common.redis_interface import start_job
from actinia_core.resources.common.response_models import StringListProcessingResultResponseModel, \
    ProcessingErrorResponseModel
from actinia_core.resources.common.config import global_config

__license__ = "GPLv3"
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
                'schema': ModuleListResponseModel
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

        * not using enqueue_job to get always a response
        * the function creates a new location and delete it in the end,
            cause not all users can access a location

        """

        # check if location exists
        location_name = 'location_for_listing_modules_' + str(uuid.uuid4())
        location = os.path.join(global_config.GRASS_DATABASE, location_name) # '/actinia_core/grassdb/location_for_listing_modules'
        # Check the location path
        if os.path.isdir(location):
            return self.get_error_response(message="Unable to create location. "
                                                   "Location <%s> exists in global database." % location_name)
        # Check also for the user database
        location = os.path.join(self.grass_user_data_base, self.user_group, location_name) # '/actinia_core/userdata/superadmin/location_for_listing_modules'
        # Check the location path
        if os.path.isdir(location):
            return self.get_error_response(message="Unable to create location. "
                                                   "Location <%s> exists in user database." % location_name)

        # create new location cause not each user can access a location
        if not os.path.isdir(os.path.join(self.grass_user_data_base, self.user_group)):
            os.mkdir(os.path.join(self.grass_user_data_base, self.user_group))
        os.mkdir(location)
        mapset = os.path.join(location, 'PERMANENT')
        os.mkdir(mapset)
        with open(os.path.join(mapset, 'DEFAULT_WIND'), 'w') as out:
            out.write("proj:       3\nzone:       0\nnorth:      1N\n"
                + "south:      0\neast:       1E\nwest:       0\ncols:       1"
                + "\nrows:       1\ne-w resol:  1\nn-s resol:  1\ntop:        "
                + "1.000000000000000\nbottom:     0.000000000000000\ncols3:   "
                + "   1\nrows3:      1\ndepths:     1\ne-w resol3: 1\nn-s reso"
                + "l3: 1\nt-b resol:  1")
        with open(os.path.join(mapset, 'MYNAME'), 'w') as out:
            out.write("")
        with open(os.path.join(mapset, 'PROJ_EPSG'), 'w') as out:
            out.write("epsg: 4326")
        with open(os.path.join(mapset, 'PROJ_INFO'), 'w') as out:
            out.write("name: WGS 84\ndatum: wgs84\nellps: wgs84\nproj: ll\n"
                + "no_defs: defined\ntowgs84: 0.000,0.000,0.000")
        with open(os.path.join(mapset, 'PROJ_UNITS'), 'w') as out:
            out.write("unit: degree\nunits: degrees\nmeters: 1.0")
        with open(os.path.join(mapset, 'WIND'), 'w') as out:
            out.write("proj:       3\nzone:       0\nnorth:      1N\n"
                + "south:      0\neast:       1E\nwest:       0\ncols:       1"
                + "\nrows:       1\ne-w resol:  1\nn-s resol:  1\ntop:        "
                + "1.000000000000000\nbottom:     0.000000000000000\ncols3:   "
                + "   1\nrows3:      1\ndepths:     1\ne-w resol3: 1\nn-s reso"
                + "l3: 1\nt-b resol:  1")

        # self.user_credentials["permissions"]['accessible_datasets'][location_name] = ['PERMANENT']

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name="PERMANENT")
        if rdc:
            start_job(self.job_timeout, list_modules, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        j_data = json.loads(response_model['process_log'][-1]['stdout'])

        module_list = []
        for data in j_data:
            description = data['attributes']['description']
            keywords = data['attributes']['keywords']
            name = data['name']
            module_response = (ModuleResponseModel(id=name, description=description, categories=keywords.split(',')))
            module_list.append(module_response)

        # remove location
        location = os.path.join(global_config.GRASS_DATABASE, location_name)
        if os.path.isdir(location):
            shutil.rmtree(location)
        location = os.path.join(self.grass_user_data_base, self.user_group, location_name)
        if os.path.isdir(location):
            shutil.rmtree(location)
        # del self.user_credentials["permissions"]['accessible_datasets'][location_name]

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

    def _execute(self, skip_permission_check=True):
    
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
