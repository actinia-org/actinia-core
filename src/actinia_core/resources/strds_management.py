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
import pickle
from flask import jsonify, make_response
from flask_restful import reqparse
from copy import deepcopy
from flask_restful_swagger_2 import swagger, Schema
from .common.request_parser import where_parser
from .persistent_processing import PersistentProcessing
from .resource_base import ResourceBase
from .common.redis_interface import enqueue_job
from .common.exceptions import AsyncProcessError
from .common.response_models import ProcessingResponseModel, \
    StringListProcessingResultResponseModel, ProcessingErrorResponseModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class SyncSTRDSListerResource(ResourceBase):
    """List all STRDS in a location/mapset
    """
    layer_type = None

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Get a list of all STRDS that are located in a specific location/mapset. '
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
                'name': 'where',
                'description': 'A where statement to select user specific STRDS',
                'required': False,
                'in': 'query',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns a list of STRDS names and timestamps and the log '
                               'of the process chain that was used to create the response.',
                'schema': StringListProcessingResultResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why listing of '
                               'STRDS did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name):
        """Get a list of all STRDS that are located in a specific location/mapset.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name)

        if rdc:
            args = where_parser.parse_args()
            rdc.set_user_data(args)

            enqueue_job(self.job_timeout, list_raster_mapsets, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)


def list_raster_mapsets(*args):
    processing = PersistentSTRDSLister(*args)
    processing.run()


class PersistentSTRDSLister(PersistentProcessing):

    def __init__(self, *args):

        PersistentProcessing.__init__(self, *args)
        self.response_model_class = StringListProcessingResultResponseModel

    def _execute(self):

        self._setup()

        pc = {"1": {"module": "t.list",
                    "inputs": {"type": "strds",
                               "column": "name"}}}

        # Make sure that only the current mapset is used for strds listing
        has_where = False

        if self.rdc.user_data:
            for option in self.rdc.user_data:
                if self.rdc.user_data[option] is not None:
                    if "where" in option:
                        select = self.rdc.user_data[option] + \
                            " AND mapset = \'%s\'" % self.mapset_name
                        pc["1"]["inputs"]["where"] = select
                        has_where = True
                    else:
                        pc["1"]["inputs"][option] = self.rdc.user_data[option]

        if has_where is False:
            select = "mapset=\'%s\'" % self.mapset_name
            pc["1"]["inputs"]["where"] = select

        process_list = self._validate_process_chain(skip_permission_check=True,
                                                    process_chain=pc)
        self._create_temp_database()
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.mapset_name)

        self._execute_process_list(process_list)

        mapset_lists = []
        mapsets = self.module_output_log[0]["stdout"].split()

        for mapset in mapsets:
            mapset_lists.append(mapset.strip())

        self.module_results = mapset_lists


"""
STRDS Management
"""


class STRDSInfoModel(Schema):
    """Schema that contains space-time raster dataset (STRDS) information
    """
    description = "Information about a specific space-time raster dataset (STRDS)"
    type = 'object'
    properties = {
        "aggregation_type": {'type': 'string'},
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
            "path": "/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm",
            "request_url": "http://localhost:8080/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm"
        },
        "datetime": "2018-05-02 10:36:43.677867",
        "http_code": 200,
        "message": "Information gathering for STRDS <precipitation_1950_2013_yearly_mm> successful",
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
            "status": "http://localhost:8080/resources/user/resource_id-1f178974-684d-417e-a3f4-878708b7382b"
        },
        "user_id": "user"
    }


recursive_parser = reqparse.RequestParser()
recursive_parser.add_argument('recursive', type=bool, help='Set True to recursively remove '
                                                           'the STRDS and all registred raster '
                                                           'map layer', location='args')


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
            'description': 'The temporal type of the STRDS, which can be absolute and relative',
            'default': "absolute"
        }
    }
    required = ['title', 'description']
    example = {"title": "Monthly mean temperature from 1950-2010 for Germany",
               "description": "Monthly mean temperature from 1950-2010 for Germany "
                              "in degree celsius",
               "ttype": "absolute"}


class STRDSManagementResource(ResourceBase):
    """List all STRDS in a location/mapset
    """

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Get information about a STRDS that is located in a specific location/mapset. '
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
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns information about a specific STRDS and the log '
                               'of the process chain that was used to create the response.',
                'schema': STRDSInfoResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why information gathering of the'
                               'STRDS did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name, strds_name):
        """Get information about a STRDS that is located in a specific location/mapset.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)
        if rdc:
            enqueue_job(self.job_timeout, strds_info, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Delete a STRDS that is located in a specific location/mapset. '
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
                'name': 'recursive',
                'description': 'Delete the STRDS and all registered raster map layer recursively',
                'required': False,
                'in': 'query',
                'type': 'boolean'
            }
        ],
        'responses': {
            '200': {
                'description': 'Deletion of the STRDS was successfully finished.',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why deletion of the'
                               'STRDS did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name, strds_name):
        """Delete a STRDS that is located in a specific location/mapset.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        if rdc:
            args = recursive_parser.parse_args()
            rdc.set_user_data(args)

            enqueue_job(self.job_timeout, strds_delete, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Create a new STRDS in a specific location/mapset. '
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
                'name': 'metadata',
                'description': 'Temporal type, title and description of the STRDS',
                'required': True,
                'in': 'body',
                'schema': STRDSCreationModel
            }
        ],
        'responses': {
            '200': {
                'description': 'Creation of the STRDS was successfully finished.',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why creation of the'
                               'STRDS did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def post(self, location_name, mapset_name, strds_name):
        """Create a new STRDS in a specific location/mapset.
        """
        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        if rdc:
            enqueue_job(self.job_timeout, strds_create, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)


def strds_info(*args):
    processing = PersistentSTRDSInfo(*args)
    processing.run()


class PersistentSTRDSInfo(PersistentProcessing):
    """Gather the STRDS information
    """

    def __init__(self, *args):

        PersistentProcessing.__init__(self, *args)
        self.response_model_class = STRDSInfoResponseModel

    def _execute(self):

        self._setup()

        pc = {"1": {"module": "t.info",
                    "inputs": {"type": "strds",
                               "input": self.map_name},
                    "flags": "g"}}

        process_list = self._validate_process_chain(skip_permission_check=True,
                                                    process_chain=pc)
        self._create_temp_database()
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.mapset_name)

        self._execute_process_list(process_list)

        kv_list = self.module_output_log[0]["stdout"].split("\n")

        strds = {}

        for string in kv_list:
            if "=" in string:
                k, v = string.split("=", 1)
                strds[k] = v

        self.module_results = STRDSInfoModel(**strds)
        self.finish_message = "Information gathering for STRDS <%s> successful" % self.map_name


def strds_delete(*args):
    processing = PersistentSTRDSDeleter(*args)
    processing.run()


class PersistentSTRDSDeleter(PersistentProcessing):
    """Delete a STRDS
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()
        self.required_mapsets.append(self.target_mapset_name)

        args = self.rdc.user_data

        pc = {"1": {"module": "t.remove",
                    "inputs": {"type": "strds",
                               "inputs": self.map_name},
                    "flags": ""}}

        if args and "recursive" in args and args["recursive"] is True:
            pc["1"]["flags"] = "rf"

        process_list = self._validate_process_chain(skip_permission_check=True,
                                                    process_chain=pc)

        self._create_temp_database()
        self._check_lock_target_mapset()

        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_list(process_list)
        self.finish_message = "STRDS <%s> successfully deleted" % self.map_name


def strds_create(*args):
    processing = PersistentSTRDSCreator(*args)
    processing.run()


class PersistentSTRDSCreator(PersistentProcessing):
    """Create a STRDS
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()
        self.required_mapsets.append(self.target_mapset_name)

        pc_1 = {}
        pc_1["1"] = {"module": "t.list", "inputs": {"type": "strds",
                                                    "where": "id = \'%s@%s\'" % (self.map_name,
                                                                                 self.target_mapset_name)}}
        # Check the first process chain
        pc_1 = self._validate_process_chain(skip_permission_check=True,
                                            process_chain=pc_1)

        pc_2 = {"1": {"module": "t.create",
                      "inputs": {"type": "strds",
                                 "output": self.map_name}}}

        if self.request_data:
            for key in self.request_data:
                pc_2["1"]["inputs"][key] = self.request_data[key]

        pc_2 = self._validate_process_chain(skip_permission_check=True,
                                            process_chain=pc_2)
        self._create_temp_database()
        self._check_lock_target_mapset()

        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_list(pc_1)

        # check if STRDS exists
        raster_list = self.module_output_log[0]["stdout"].split("\n")

        if len(raster_list[0]) > 0:
            raise AsyncProcessError("STRDS <%s> exists." % self.map_name)

        self._execute_process_list(pc_2)

        self.finish_message = "STRDS <%s> successfully created" % self.map_name
