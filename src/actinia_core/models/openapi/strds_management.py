# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2019 Sören Gebbert and mundialis GmbH & Co. KG
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
STRDS map layer management

TODO: Integrate into the ephemeral process chain approach
"""
from copy import deepcopy
from flask_restful_swagger_2 import Schema
from actinia_core.models.response_models import ProcessingResponseModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class STRDSInfoModel(Schema):
    """Schema that contains space-time raster dataset (STRDS) information
    """
    description = "Information about a specific space-time raster dataset (STRDS)"
    type = 'object'
    properties = {
        "aggregation_type": {'type': 'string'},
        "band_names": {'type': 'string'},
        "band_reference": {'type': 'string'},
        "bottom": {'type': 'string'},
        "creation_time": {'type': 'string'},
        "creator": {'type': 'string'},
        "east": {'type': 'string'},
        "end_time": {'type': 'string'},
        "ewres_max": {'type': 'string'},
        "ewres_min": {'type': 'string'},
        "granularity": {'type': 'string'},
        "id": {'type': 'string'},
        "map_time": {'type': 'string'},
        "mapset": {'type': 'string'},
        "max_max": {'type': 'string'},
        "max_min": {'type': 'string'},
        "min_max": {'type': 'string'},
        "min_min": {'type': 'string'},
        "modification_time": {'type': 'string'},
        "name": {'type': 'string'},
        "north": {'type': 'string'},
        "number_of_bands": {'type': 'string'},
        "nsres_max": {'type': 'string'},
        "nsres_min": {'type': 'string'},
        "number_of_maps": {'type': 'string'},
        "raster_register": {'type': 'string'},
        "semantic_type": {'type': 'string'},
        "south": {'type': 'string'},
        "start_time": {'type': 'string'},
        "temporal_type": {'type': 'string'},
        "top": {'type': 'string'},
        "west": {'type': 'string'}
    }
    example = {
        "aggregation_type": "None",
        "band_names": "None",
        "band_reference": "None",
        "bottom": "0.0",
        "creation_time": "2016-08-11 16:44:29.756411",
        "creator": "soeren",
        "east": "75.5",
        "end_time": "2013-07-01 00:00:00",
        "ewres_max": "0.25",
        "ewres_min": "0.25",
        "granularity": "1 month",
        "id": "precipitation_1950_2013_monthly_mm@PERMANENT",
        "map_time": "interval",
        "mapset": "PERMANENT",
        "max_max": "1076.9",
        "max_min": "168.9",
        "min_max": "3.2",
        "min_min": "0.0",
        "modification_time": "2016-08-11 16:45:14.032432",
        "name": "precipitation_1950_2013_monthly_mm",
        "north": "75.5",
        "nsres_max": "0.25",
        "nsres_min": "0.25",
        "number_of_bands": "None",
        "number_of_maps": "762",
        "raster_register": "raster_map_register_934719ed2b4841818386a6f9c5f11b09",
        "semantic_type": "mean",
        "south": "25.25",
        "start_time": "1950-01-01 00:00:00",
        "temporal_type": "absolute",
        "top": "0.0",
        "west": "-40.5"
    }


class STRDSInfoResponseModel(ProcessingResponseModel):
    """Response schema for STRDS information.
    """
    type = 'object'
    properties = deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = STRDSInfoModel
    required = deepcopy(ProcessingResponseModel.required)
    # required.append("process_results")
    example = {
        "accept_datetime": "2018-05-02 10:36:43.119861",
        "accept_timestamp": 1525257403.119857,
        "api_info": {
            "endpoint": "strdsmanagementresource",
            "method": "GET",
            "path": "/locations/ECAD/mapsets/PERMANENT/strds/"
                    "precipitation_1950_2013_yearly_mm",
            "request_url": "http://localhost:8080/locations/ECAD/mapsets/"
                           "PERMANENT/strds/precipitation_1950_2013_yearly_mm"
        },
        "datetime": "2018-05-02 10:36:43.677867",
        "http_code": 200,
        "message": "Information gathering for STRDS "
                   "<precipitation_1950_2013_yearly_mm> successful",
        "process_chain_list": [
            {
                "1": {
                    "flags": "g",
                    "inputs": {
                        "input": "precipitation_1950_2013_yearly_mm",
                        "type": "strds"
                    },
                    "module": "t.info"
                }
            }
        ],
        "process_log": [
            {
                "executable": "t.info",
                "parameter": [
                    "type=strds",
                    "input=precipitation_1950_2013_yearly_mm",
                    "-g"
                ],
                "return_code": 0,
                "run_time": 0.4944636821746826,
                "stderr": [
                    ""
                ],
                "stdout": "..."}
        ],
        "process_results": {
            "aggregation_type": "None",
            "band_names": "None",
            "band_reference": "None",
            "bottom": "0.0",
            "creation_time": "2017-12-29 15:58:40.020820",
            "creator": "soeren",
            "east": "75.5",
            "end_time": "2013-01-01 00:00:00",
            "ewres_max": "0.25",
            "ewres_min": "0.25",
            "granularity": "1 year",
            "id": "precipitation_1950_2013_yearly_mm@PERMANENT",
            "map_time": "interval",
            "mapset": "PERMANENT",
            "max_max": "5132.0",
            "max_min": "2498.3",
            "min_max": "35.2",
            "min_min": "0.0",
            "modification_time": "2017-12-29 15:58:44.396206",
            "name": "precipitation_1950_2013_yearly_mm",
            "north": "75.5",
            "nsres_max": "0.25",
            "nsres_min": "0.25",
            "number_of_bands": "None",
            "number_of_maps": "63",
            "raster_register": "raster_map_register_87e1edbaf2da4a27a03da04fa9f3a7f1",
            "semantic_type": "mean",
            "south": "25.25",
            "start_time": "1950-01-01 00:00:00",
            "temporal_type": "absolute",
            "top": "0.0",
            "west": "-40.5"
        },
        "progress": {
            "num_of_steps": 1,
            "step": 1
        },
        "resource_id": "resource_id-1f178974-684d-417e-a3f4-878708b7382b",
        "status": "finished",
        "time_delta": 0.5580840110778809,
        "timestamp": 1525257403.6778474,
        "urls": {
            "resources": [],
            "status": "http://localhost:8080/resources/user/"
                      "resource_id-1f178974-684d-417e-a3f4-878708b7382b"
        },
        "user_id": "user"
    }


class STRDSCreationModel(Schema):
    """Schema for STRDS creation
    """
    description = "Information required to create a new STRDS"
    type = 'object'
    properties = {
        'title': {
            'type': 'string',
            'description': 'The title of the STRDS',
        },
        'description': {
            'type': 'string',
            'description': 'The description of the STRDS',
        },
        'temporaltype': {
            'type': 'string',
            'description': 'The temporal type of the STRDS, which can be '
                           'absolute and relative',
            'default': "absolute"
        }
    }
    required = ['title', 'description']
    example = {"title": "Monthly mean temperature from 1950-2010 for Germany",
               "description": "Monthly mean temperature from 1950-2010 for Germany "
                              "in degree celsius",
               "ttype": "absolute"}
