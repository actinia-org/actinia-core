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
from flask_restful_swagger_2 import swagger, Schema
from flask import jsonify, make_response
from copy import deepcopy
import tempfile
import pickle
from .common.request_parser import where_parser
from .persistent_processing import PersistentProcessing
from .resource_base import ResourceBase
from .common.redis_interface import enqueue_job
from .common.exceptions import AsyncProcessError
from .common.response_models import ProcessingResponseModel, ProcessingErrorResponseModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


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
            "path": "/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm/raster_layers",
            "request_url": "http://localhost:5000/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm/raster_layers?where=start_time>'2010-01-01'"
        },
        "datetime": "2018-05-06 21:28:19.187395",
        "http_code": 200,
        "message": "Processing successfully finished",
        "process_chain_list": [
            {
                "1": {
                    "flags": "u",
                    "inputs": {
                        "columns": "id,start_time,end_time,north,south,east,west,min,max,rows,cols",
                        "input": "precipitation_1950_2013_yearly_mm@PERMANENT",
                        "separator": "|",
                        "where": "start_time>'2010-01-01'"
                    },
                    "module": "t.rast.list",
                    "outputs": {
                        "output": {
                            "name": "/home/soeren/actinia/workspace/temp_db/gisdbase_1b72938d2ef54c199f6627b8720f21e1/.tmp/tmptps71vn7"
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
                    "columns=id,start_time,end_time,north,south,east,west,min,max,rows,cols",
                    "output=/home/soeren/actinia/workspace/temp_db/gisdbase_1b72938d2ef54c199f6627b8720f21e1/.tmp/tmptps71vn7",
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
            "status": "http://localhost:5000/resources/user/resource_id-729ace44-6245-43c7-a875-d2059c1a1549"
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


class STRDSRasterManagement(ResourceBase):
    """Manage raster layer in a space time raster dataset
    """

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Get a list of all raster map layers that are registered in a STRDS  '
                       'that is located in a specific location/mapset. '
                       'Minimum required user role: user.',
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
            },
            {
                'name': 'strds_name',
                'description': 'The name of the STRDS',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'where',
                'description': 'A where statement to select user specific raster map layers from the STRDS',
                'required': False,
                'in': 'query',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns a list of all raster map layers '
                               'that are registered a specific STRDS and the log '
                               'of the process chain that was used to create the response.',
                'schema': STRDSRasterListResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why creating a list of raster '
                               'map layers from STRDS did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name, strds_name):
        """Get a list of all raster map layers that are registered in a STRDS
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        if rdc:
            args = where_parser.parse_args()
            rdc.set_user_data(args)

            enqueue_job(self.job_timeout, list_raster_strds, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Register raster map layers in a STRDS located in a specific location/mapset. '
                       'Minimum required user role: user.',
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
            },
            {
                'name': 'strds_name',
                'description': 'The name of the STRDS',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'raster_list',
                'description': 'The list of raster map layers to be registered in the STRDS',
                'required': True,
                'in': 'body',
                'schema': RasterListRegisterModel
            }
        ],
        'responses': {
            '200': {
                'description': 'Registration of raster map layers was successfully finished.',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why raster map layer '
                               'registration did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def put(self, location_name, mapset_name, strds_name):
        """Register raster map layers in a STRDS located in a specific location/mapset.
        """
        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        if rdc:
            enqueue_job(self.job_timeout, register_raster, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Unregister raster map layers from a STRDS located in a specific location/mapset. '
                       'Minimum required user role: user.',
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
            },
            {
                'name': 'strds_name',
                'description': 'The name of the STRDS',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'raster_list',
                'description': 'The list of raster map layers to be unregistered from the STRDS',
                'required': True,
                'in': 'body',
                'schema': {"type": "array", "items": {"type": "string"}}
            }
        ],
        'responses': {
            '200': {
                'description': 'Unregistration of raster map layers was successfully finished.',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why raster map layer '
                               'unregistration did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name, strds_name):
        """Unregister raster map layers from a STRDS located in a specific location/mapset.
        """
        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        if rdc:
            enqueue_job(self.job_timeout, unregister_raster, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)


def list_raster_strds(*args):
    processing = PersistentRasterSTRDSLister(*args)
    processing.run()


class PersistentRasterSTRDSLister(PersistentProcessing):
    """List all mapsets in a location
    """

    def __init__(self, *args):

        PersistentProcessing.__init__(self, *args)
        self.response_model_class = STRDSRasterListResponseModel

    def _execute(self):

        self._setup()

        result_file = tempfile.NamedTemporaryFile(dir=self.temp_file_path, delete=True)

        pc = {"1": {"module": "t.rast.list",
                    "inputs": {"input": "%s@%s" % (self.map_name, self.mapset_name),
                               "columns": "id,start_time,end_time,north,south,"
                                          "east,west,min,max,rows,cols",
                               "separator": "|"},
                    "outputs": {"output": {"name": result_file.name}},
                    "flags": "u"}}

        if self.rdc.user_data:
            for option in self.rdc.user_data:
                if self.rdc.user_data[option] is not None:
                    pc["1"]["inputs"][option] = self.rdc.user_data[option]

        process_list = self._validate_process_chain(skip_permission_check=True,
                                                    process_chain=pc)

        self._create_temp_database(mapsets=self.required_mapsets)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.mapset_name)
        self._execute_process_list(process_list)

        result_file.flush()
        result = open(result_file.name, "r").readlines()
        result_file.close()

        output_list = []
        for line in result:
            values = line.strip().split("|")
            output_list.append(STRDSRasterListEntryModel(id=values[0],
                                                         start_time=values[1],
                                                         end_time=values[2],
                                                         north=values[3],
                                                         south=values[4],
                                                         east=values[5],
                                                         west=values[6],
                                                         min=values[7],
                                                         max=values[8],
                                                         rows=values[9],
                                                         cols=values[10]))

        self.module_results = output_list


def register_raster(*args):
    processing = PersistentRasterSTRDSRegisterer(*args)
    processing.run()


class PersistentRasterSTRDSRegisterer(PersistentProcessing):
    """Register a list of timestamped raster map layers in a STRDS
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()

        input_file = tempfile.NamedTemporaryFile(dir=self.temp_file_path, delete=True, mode="w")

        for map_entry in self.request_data:
            if "name" not in map_entry or "start_time" not in map_entry or "end_time" not in map_entry:
                raise AsyncProcessError("Wrong input format for raster map layer registration")

            line = "%s|%s|%s\n" % (map_entry["name"], map_entry["start_time"], map_entry["end_time"])
            input_file.write(line)
        input_file.flush()
        input_file.seek(0)

        pc = {"1": {"module": "t.register",
                    "inputs": {"input": "%s@%s" % (self.map_name, self.mapset_name),
                               "type": "raster",
                               "separator": "|",
                               "file": input_file.name}}}

        self._check_lock_target_mapset()
        self._create_temp_database(mapsets=self.required_mapsets)
        process_list = self._validate_process_chain(skip_permission_check=True,
                                                    process_chain=pc)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.mapset_name)

        self._execute_process_list(process_list)

        input_file.close()


def unregister_raster(*args):
    processing = PersistentRasterSTRDSUnregisterer(*args)
    processing.run()


class PersistentRasterSTRDSUnregisterer(PersistentProcessing):
    """Unregister a list of timestamped raster map layers from a STRDS
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()

        input_file = tempfile.NamedTemporaryFile(dir=self.temp_file_path, delete=True, mode="w")

        for map_name in self.request_data:
            line = "%s\n" % map_name
            input_file.write(line)
        input_file.flush()

        pc = {"1": {"module": "t.unregister",
                    "inputs": {"input": "%s@%s" % (self.map_name, self.mapset_name),
                               "type": "raster",
                               "file": input_file.name}}}

        process_list = self._validate_process_chain(skip_permission_check=True,
                                                    process_chain=pc)
        self._check_lock_target_mapset()
        self._create_temp_database(mapsets=self.required_mapsets)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.mapset_name)

        self._execute_process_list(process_list)

        input_file.close()
