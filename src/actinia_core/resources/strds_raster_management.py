# -*- coding: utf-8 -*-
"""
TODO: Integrate into the ephemeral process chain approach
"""
from flask_restful_swagger_2 import swagger, Schema
from flask import jsonify, make_response
from copy import deepcopy
import tempfile
from actinia_core.resources.common.request_parser import where_parser
from actinia_core.resources.async_persistent_processing import AsyncPersistentProcessing
from actinia_core.resources.async_resource_base import AsyncEphemeralResourceBase
from actinia_core.resources.common.redis_interface import enqueue_job
from actinia_core.resources.common.exceptions import AsyncProcessError
from actinia_core.resources.common.response_models import ProcessingResponseModel

__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class STRDSRasterListEntryModel(Schema):
    """Schema that contains list entry

    columns=id,start_time,end_time,north,south,east,west,min,max,rows,cols
    """
    type = 'object'
    properties = {
        'id':  {'type': 'string'},
        'start_time': {'type': 'string'},
        'end_time':   {'type': 'string'},
        'min':   {'type': 'string'},
        'max':   {'type': 'string'},
        'north': {'type': 'string'},
        'south': {'type': 'string'},
        'east':  {'type': 'string'},
        'west':  {'type': 'string'},
        'rows':  {'type': 'string'},
        'cols':  {'type': 'string'}
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
      "accept_datetime": "2017-05-23 13:01:32.517207",
      "accept_timestamp": 1495537292.517203,
      "api_info": {
        "endpoint": "strdsrastermanagement",
        "method": "GET",
        "path": "/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_monthly_mm/raster_layers",
        "request_url": "http://localhost:5000/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_monthly_mm/raster_layers?where=start_time > '2013-05-01'"
      },
      "datetime": "2017-05-23 13:01:33.607950",
      "http_code": 200,
      "message": "Processing successfully finished",
      "process_log": [
        {
          "executable": "t.rast.list",
          "parameter": [
            "input=precipitation_1950_2013_monthly_mm@PERMANENT",
            "separator=|",
            "where=start_time > '2013-05-01'",
            "columns=id,start_time,end_time,north,south,east,west,min,max,rows,cols",
            "output=/tmp/gisdbase_cdc689a958b948a58cb4165e5a4d9daf/.tmp/tmpBFJABA",
            "-u"
          ],
          "return_code": 0,
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
          "end_time": "2013-06-01 00:00:00",
          "id": "precipitation_monthly_mm_760@PERMANENT",
          "max": "403.8",
          "min": "0.0",
          "north": "75.5",
          "rows": "464",
          "south": "25.25",
          "start_time": "2013-05-01 00:00:00",
          "west": "-40.5"
        },
        {
          "cols": "201",
          "east": "75.5",
          "end_time": "2013-07-01 00:00:00",
          "id": "precipitation_monthly_mm_761@PERMANENT",
          "max": "283.4",
          "min": "0.0",
          "north": "75.5",
          "rows": "464",
          "south": "25.25",
          "start_time": "2013-06-01 00:00:00",
          "west": "-40.5"
        }
      ],
      "progress": {
        "num_of_steps": 1,
        "step": 1
      },
      "resource_id": "resource_id-f6651ec2-73bc-42bc-aa64-aa21ee8ab35d",
      "status": "finished",
      "timestamp": 1495537293.607947,
      "urls": {
        "resources": [],
        "status": "http://localhost:5000/status/soeren/resource_id-f6651ec2-73bc-42bc-aa64-aa21ee8ab35d"
      },
      "user_id": "soeren"
    }


class RasterListEntryModel(Schema):
    type = 'object'
    properties = {
        'name':  {'type': 'string'},
        'start_time': {'type': 'string'},
        'end_time':   {'type': 'string'}
    }

class RasterListRegisterModel(Schema):
    type = 'array'
    items = STRDSRasterListEntryModel


class STRDSRasterManagement(AsyncEphemeralResourceBase):
    """Manage raster layer in a space time raster dataset
    """

    @swagger.doc({
        'tags': ['space-time raster dataset management'],
        'description': 'Return of all raster map layers that are registered in '
                       'a STRDS that is located in a specific location/mapset. '
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
                'schema':STRDSRasterListResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why creating a list of raster '
                               'map layers from STRDS did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name, strds_name):
        """Return information about a STRDS that is located in a specific location/mapset
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        args = where_parser.parse_args()
        rdc.set_user_data(args)

        enqueue_job(self.job_timeout, list_raster_strds, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['space-time raster dataset management'],
        'description': 'Register raster map layer in a STRDS in a specific location/mapset. '
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
                'schema':ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why raster map layer '
                               'registration did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def put(self, location_name, mapset_name, strds_name):
        """Register raster layer in a strds
        """
        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        enqueue_job(self.job_timeout, register_raster, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['space-time raster dataset management'],
        'description': 'Unregister raster map layer from a STRDS in a specific location/mapset. '
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
                'schema':ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why raster map layer '
                               'unregistration did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name, strds_name):
        """Unregister raster layer from the strds
        """
        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        enqueue_job(self.job_timeout, unregister_raster, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


def list_raster_strds(*args):
    processing = AsyncPersistentListRasterSTRDS(*args)
    processing.run()


class AsyncPersistentListRasterSTRDS(AsyncPersistentProcessing):
    """List all mapsets in a location
    """

    def __init__(self, *args):

        AsyncPersistentProcessing.__init__(self, *args)
        self.response_model_class = STRDSRasterListResponseModel

    def _execute(self):

        self._setup()

        result_file = tempfile.NamedTemporaryFile(dir=self.temp_file_path, delete=True)

        pc = {"1":{"module":"t.rast.list",
                   "inputs":{"input": "%s@%s"%(self.map_name, self.mapset_name),
                             "columns": "id,start_time,end_time,north,south,"
                                        "east,west,min,max,rows,cols",
                             "separator": "|"},
                   "outputs": {"output": {"name": result_file.name}},
                   "flags": "u"}}

        if self.rdc.user_data:
            for option in self.rdc.user_data:
                if self.rdc.user_data[option] is not None:
                    pc["1"]["inputs"][option] = self.rdc.user_data[option]

        process_chain = self._validate_process_chain(skip_permission_check=True,
                                                     process_chain=pc)

        self._create_temp_database(mapsets=self.required_mapsets)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.mapset_name)
        self._execute_process_chain(process_chain)

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
    processing = AsyncPersistentRegisterRaster(*args)
    processing.run()


class AsyncPersistentRegisterRaster(AsyncPersistentProcessing):
    """Register a list of timestamped raster map layers in a STRDS
    """

    def __init__(self, *args):
        AsyncPersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()

        input_file = tempfile.NamedTemporaryFile(dir=self.temp_file_path, delete=True)

        for map_entry in self.request_data:
            if "name" not in map_entry or "start_time" not in map_entry or "end_time" not in map_entry:
                raise AsyncProcessError("Wrong input format for raster map layer registration")

            line = "%s|%s|%s\n"%(map_entry["name"], map_entry["start_time"], map_entry["end_time"])
            input_file.write(line)
        input_file.flush()

        pc = {"1":{"module":"t.register",
                   "inputs":{"input": "%s@%s"%(self.map_name, self.mapset_name),
                             "type": "raster",
                             "separator": "|",
                             "file": input_file.name}}}

        self._check_lock_target_mapset()
        self._create_temp_database(mapsets=self.required_mapsets)
        process_chain = self._validate_process_chain(skip_permission_check=True,
                                                     process_chain=pc)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.mapset_name)

        self._execute_process_chain(process_chain)

        input_file.close()


def unregister_raster(*args):
    processing = AsyncPersistentUnregisterRaster(*args)
    processing.run()


class AsyncPersistentUnregisterRaster(AsyncPersistentProcessing):
    """Unregister a list of timestamped raster map layers from a STRDS
    """

    def __init__(self, *args):
        AsyncPersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()

        input_file = tempfile.NamedTemporaryFile(dir=self.temp_file_path, delete=True)

        for map_name in self.request_data:
            line = "%s\n"%map_name
            input_file.write(line)
        input_file.flush()

        pc = {"1":{"module":"t.unregister",
                   "inputs":{"input": "%s@%s"%(self.map_name, self.mapset_name),
                             "type": "raster",
                             "file": input_file.name}}}

        process_chain = self._validate_process_chain(skip_permission_check=True,
                                                     process_chain=pc)
        self._check_lock_target_mapset()
        self._create_temp_database(mapsets=self.required_mapsets)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.mapset_name)

        self._execute_process_chain(process_chain)

        input_file.close()
