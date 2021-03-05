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
Raster colors management

TODO: Tests required
"""

from flask_restful_swagger_2 import swagger, Schema
from flask import jsonify, make_response
from .ephemeral_processing import EphemeralProcessing
from .persistent_processing import PersistentProcessing
from .resource_base import ResourceBase
from .common.redis_interface import enqueue_job
import tempfile
import os
import atexit
from .common.response_models import ProcessingResponseModel, ProcessingErrorResponseModel,\
    StringListProcessingResultResponseModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class RasterColorModel(Schema):
    """Response schema that is used in cases that no asynchronous run was performed.

    """
    description = "Set the color table for an existing raster map layer with a set of rules, " \
                  "a specific color or an other raster map layer"
    type = 'object'
    properties = {
        'rules': {
            'type': 'array',
            'description': 'A list of rules to set the color table of a raster map layer',
            'items': {'type': "string"}
        },
        'color': {
            'type': 'string',
            'description': 'The name of a color to be set for a raster map layer'
        },
        'raster': {
            'type': 'string',
            'description': 'The name of an existing raster map layer to copy the color table from'
        }
    }
    example = {
        "rules": ["1 0:0:0",
                  "default 255:255:255"],
        "color": "ndvi",
        "raster": "elevation@PERMANENT"
    }


class SyncPersistentRasterColorsResource(ResourceBase):
    """Manage the color table
    """

    @swagger.doc({
        'tags': ['Raster Management'],
        'description': 'Get the color definition of an existing raster map layer. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The location name',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset that contains the required raster map layer',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'raster_name',
                'description': 'The name of the raster map layer to get the color table from',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'produces': ["application/json"],
        'responses': {
            '200': {
                'description': 'A list of color rules',
                'schema': StringListProcessingResultResponseModel
            },
            '400': {
                'description': 'The error message and a detailed error log',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name, raster_name):
        """Get the color definition of an existing raster map layer.

        Args:
            location_name: Name of the location
            mapset_name: Name of the mapset
            raster_name: name of the raster map

        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=raster_name)

        enqueue_job(self.job_timeout, start_job_colors_out, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['Raster Management'],
        'description': 'Set the color definition for an existing raster map layer. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The location name',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset that contains the required raster map layer',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'raster_name',
                'description': 'The name of the raster map layer to set the color table',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'color',
                'description': 'The color definition.',
                'required': True,
                'in': 'body',
                'schema': RasterColorModel
            }
        ],
        'produces': ["application/json"],
        'consumes': ["application/json"],
        'responses': {
            '200': {
                'description': 'Successfuly set the color table for a raster map layer',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed error log',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def post(self, location_name, mapset_name, raster_name):
        """Set the color definition for an existing raster map layer.

        The JSON input should contain the color rules, a predefined color table
        or a raster layer:

            {"rules":["1 0:0:0", "default 255:255:255"]}
            {"color":"gbr"}
            {"raster":"elevation"}


        Args:
            location_name: Name of the location
            mapset_name: Name of the mapset
            raster_name: name of the raster map

        Raises:
            InvalidUsage in case the color definition is false

        """
        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=raster_name)

        if isinstance(self.request_data, dict) is False:
            return self.get_error_response(message="Missing raster color definition in JSON content")

        if len(self.request_data) > 1:
            return self.get_error_response(message="The color settings expect a single entry")

        if "rules" in self.request_data:
            if isinstance(self.request_data["rules"], list) is False:
                return self.get_error_response(message="Wrong rules definitions in JSON content")
        elif "color" in self.request_data:
            pass
        elif "raster" in self.request_data:
            if "@" not in self.request_data["raster"]:
                return self.get_error_response(message="Missing mapset definition in raster name")
        else:
            return self.get_error_response(message="Missing raster color definitions in JSON content")

        enqueue_job(self.job_timeout, start_job_from_rules, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


def start_job_colors_out(*args):
    processing = EphemeralRasterColorsOutput(*args)
    processing.run()


class EphemeralRasterColorsOutput(EphemeralProcessing):

    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)

    def _execute(self, skip_permission_check=True):

        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.mapset_name)

        result_file = tempfile.mktemp(suffix=".color", dir=self.temp_file_path)

        self.request_data = {
            "1": {"module": "r.colors.out", "inputs": {"map": "", "rules": ""}}}
        self.request_data["1"]["inputs"]["map"] = raster_name + "@" + self.mapset_name
        self.request_data["1"]["inputs"]["rules"] = result_file

        # Run the selected modules
        process_list = self._create_temporary_grass_environment_and_process_list(
            skip_permission_check=True)
        self._execute_process_list(process_list)

        result = open(result_file, "r").read().strip().split("\n")

        self.module_results = result


def start_job_from_rules(*args):
    processing = PersistentRasterColorsRules(*args)
    processing.run()


class PersistentRasterColorsRules(PersistentProcessing):
    """Set the color table of a raster map from color rules

    Perform the processing in the original mapset
    """

    def __init__(self, *args):

        PersistentProcessing.__init__(self, *args)

    def _execute(self, skip_permission_check=True):

        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        options = self.request_data

        pc = {"1": {"module": "r.colors", "inputs": {}}}
        pc["1"]["inputs"]["map"] = raster_name + "@" + self.target_mapset_name

        if "rules" in options:
            rules_file = tempfile.mktemp(suffix=".color")
            rules = open(rules_file, "w")

            for line in options["rules"]:
                rules.write(line + "\n")
            rules.close()

            pc["1"]["inputs"]["rules"] = rules_file
            atexit.register(remove_rules_file, rules_file)
        else:
            for option in options:
                pc["1"]["inputs"][option] = options[option]

        process_list = self._validate_process_chain(process_chain=pc,
                                                    skip_permission_check=True)
        self._check_lock_target_mapset()
        self._create_temp_database(self.required_mapsets)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_list(process_list)


def remove_rules_file(rules_file):
    os.remove(rules_file)
