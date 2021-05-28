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
STRDS raster map layer management

TODO: Integrate into the ephemeral process chain approach
"""
from copy import deepcopy
from flask_restful_swagger_2 import Schema
from actinia_core.models.response_models import \
    ProcessingResponseModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class STRDSRasterListEntryModel(Schema):
    """Schema that contains list entry

    columns=id,start_time,end_time,north,south,east,west,min,max,rows,cols
    """
    description = "A single raster map layer information entry"
    type = 'object'
    properties = {
        'id': {'type': 'string'},
        'start_time': {'type': 'string'},
        'end_time': {'type': 'string'},
        'min': {'type': 'string'},
        'max': {'type': 'string'},
        'north': {'type': 'string'},
        'south': {'type': 'string'},
        'east': {'type': 'string'},
        'west': {'type': 'string'},
        'rows': {'type': 'string'},
        'cols': {'type': 'string'}
    }
    example = {
        "cols": "201",
        "east": "75.5",
        "end_time": "2013-06-01 00:00:00",
        "id": "precipitation_monthly_mm_760@PERMANENT",
        "max": "403.8",
        "min": "0.0",
        "north": "75.5",
        "rows": "464",
        "south": "25.25",
        "start_time": "2013-05-01 00:00:00",
        "west": "-40.5"
    }


class STRDSRasterListResponseModel(ProcessingResponseModel):
    """Response schema for STRDS raster map layer list information.
    """
    type = 'object'
    properties = deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = {}
    properties["process_results"]["type"] = "array"
    properties["process_results"]["items"] = STRDSRasterListEntryModel
    required = deepcopy(ProcessingResponseModel.required)
    # required.append("process_results")
    example = {
        "accept_datetime": "2018-05-06 21:28:18.583050",
        "accept_timestamp": 1525634898.5830483,
        "api_info": {
            "endpoint": "strdsrastermanagement",
            "method": "GET",
            "path": "/locations/ECAD/mapsets/PERMANENT/strds/"
                    "precipitation_1950_2013_yearly_mm/raster_layers",
            "request_url": "http://localhost:5000/locations/ECAD/mapsets/"
                           "PERMANENT/strds/precipitation_1950_2013_yearly_mm/"
                           "raster_layers?where=start_time>'2010-01-01'"
        },
        "datetime": "2018-05-06 21:28:19.187395",
        "http_code": 200,
        "message": "Processing successfully finished",
        "process_chain_list": [
            {
                "1": {
                    "flags": "u",
                    "inputs": {
                        "columns": "id,start_time,end_time,north,south,east,"
                                   "west,min,max,rows,cols",
                        "input": "precipitation_1950_2013_yearly_mm@PERMANENT",
                        "separator": "|",
                        "where": "start_time>'2010-01-01'"
                    },
                    "module": "t.rast.list",
                    "outputs": {
                        "output": {
                            "name": "/home/soeren/actinia/workspace/temp_db/"
                                    "gisdbase_1b72938d2ef54c199f6627b8720f21e1/"
                                    ".tmp/tmptps71vn7"
                        }
                    }
                }
            }
        ],
        "process_log": [
            {
                "executable": "t.rast.list",
                "parameter": [
                    "input=precipitation_1950_2013_yearly_mm@PERMANENT",
                    "where=start_time>'2010-01-01'",
                    "separator=|",
                    "columns=id,start_time,end_time,north,south,east,west,min,"
                    "max,rows,cols",
                    "output=/home/soeren/actinia/workspace/temp_db/"
                    "gisdbase_1b72938d2ef54c199f6627b8720f21e1/.tmp/tmptps71vn7",
                    "-u"
                ],
                "return_code": 0,
                "run_time": 0.5023984909057617,
                "stderr": [
                    ""
                ],
                "stdout": ""
            }
        ],
        "process_results": [
            {
                "cols": "201",
                "east": "75.5",
                "end_time": "2011-01-01 00:00:00",
                "id": "precipitation_yearly_mm_60@PERMANENT",
                "max": "2899.6",
                "min": "22.5",
                "north": "75.5",
                "rows": "464",
                "south": "25.25",
                "start_time": "2010-01-01 00:00:00",
                "west": "-40.5"
            },
            {
                "cols": "201",
                "east": "75.5",
                "end_time": "2012-01-01 00:00:00",
                "id": "precipitation_yearly_mm_61@PERMANENT",
                "max": "4226.0",
                "min": "10.0",
                "north": "75.5",
                "rows": "464",
                "south": "25.25",
                "start_time": "2011-01-01 00:00:00",
                "west": "-40.5"
            },
            {
                "cols": "201",
                "east": "75.5",
                "end_time": "2013-01-01 00:00:00",
                "id": "precipitation_yearly_mm_62@PERMANENT",
                "max": "3442.6",
                "min": "0.0",
                "north": "75.5",
                "rows": "464",
                "south": "25.25",
                "start_time": "2012-01-01 00:00:00",
                "west": "-40.5"
            }
        ],
        "progress": {
            "num_of_steps": 1,
            "step": 1
        },
        "resource_id": "resource_id-729ace44-6245-43c7-a875-d2059c1a1549",
        "status": "finished",
        "time_delta": 0.6043989658355713,
        "timestamp": 1525634899.1873734,
        "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/user/"
                      "resource_id-729ace44-6245-43c7-a875-d2059c1a1549"
        },
        "user_id": "user"
    }


class RasterListEntryModel(Schema):
    type = 'object'
    properties = {
        'name': {'type': 'string'},
        'start_time': {'type': 'string'},
        'end_time': {'type': 'string'}
    }


class RasterListRegisterModel(Schema):
    type = 'array'
    items = RasterListEntryModel
    example = [
        {
            "end_time": "2013-06-01 00:00:00",
            "start_time": "2013-05-01 00:00:00",
            "name": "precipitation_monthly_mm_760",
        },
        {
            "end_time": "2013-07-01 00:00:00",
            "start_time": "2013-06-01 00:00:00",
            "name": "precipitation_monthly_mm_761",
        }
    ]
