# -*- coding: utf-8 -*-
"""
TODO: Integrate into the ephemeral process chain approach
"""
import pickle
from flask import jsonify, make_response
from flask_restful import reqparse
from copy import deepcopy
from flask_restful_swagger_2 import swagger, Schema
from actinia_core.resources.common.request_parser import where_parser
from actinia_core.resources.async_persistent_processing import AsyncPersistentProcessing
from actinia_core.resources.async_resource_base import AsyncEphemeralResourceBase
from actinia_core.resources.common.redis_interface import enqueue_job
from actinia_core.resources.common.exceptions import AsyncProcessError
from actinia_core.resources.common.response_models import ProcessingResponseModel,\
    StringListProcessingResultResponseModel

__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"



class ListSTRDSResource(AsyncEphemeralResourceBase):
    """List all STRDS in a location/mapset
    """
    layer_type = None
    @swagger.doc({
        'tags': ['space-time raster dataset management'],
        'description': 'Return a list of all STRDS that are located in a specific location/mapset. '
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
                'schema':StringListProcessingResultResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why listing of '
                               'STRDS did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name):
        """Return a list of all STRDS in a location/mapset
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
    processing = AsyncPersistentListSTRDS(*args)
    processing.run()


class AsyncPersistentListSTRDS(AsyncPersistentProcessing):

    def __init__(self, *args):

        AsyncPersistentProcessing.__init__(self, *args)
        self.response_model_class = StringListProcessingResultResponseModel

    def _execute(self):

        self._setup()

        pc = {"1":{"module":"t.list",
                   "inputs":{"type": "strds",
                             "column":"name"}}}

        # Make sure that only the current mapset is used for strds listing
        has_where = False

        if self.rdc.user_data:
            for option in self.rdc.user_data:
                if self.rdc.user_data[option] is not None:
                    if "where" in option:
                        select = self.rdc.user_data[option] + " AND mapset = \'%s\'"%self.mapset_name
                        pc["1"]["inputs"]["where"] = select
                        has_where = True
                    else:
                        pc["1"]["inputs"][option] = self.rdc.user_data[option]

        if has_where is False:
            select = "mapset=\'%s\'"%self.mapset_name
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

###############################################################################
################ STRDS Management #############################################
###############################################################################

class STRDSInfoModel(Schema):
    """Schema that contains space-time raster dataset (STRDS) information
    """
    type = 'object'
    properties = {
        'aggregation_type': {'type': 'string'},
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


recursive_parser = reqparse.RequestParser()
recursive_parser.add_argument('recursive', type=bool, help='Set True to recursively remove '
                                                       'the STRDS and all registred raster '
                                                       'map layer', location='args')


class STRDSCreationModel(Schema):
    """Schema for random raster map layer generation using r.mapcalc in a specific region
    """
    type = 'object'
    properties = {
        'title': {
            'type': 'string',
            'description':'The title of the STRDS',
        },
        'description': {
            'type': 'string',
            'description':'The description of the STRDS',
        },
        'temporaltype': {
            'type': 'string',
            'description':'The temporal type of the STRDS, which can be absolute and relative',
            'default': "absolute"
        }
    }
    required=['title', 'description']
    example={"title": "Monthly mean temperature from 1950-2010 for Germany",
             "description": "Monthly mean temperature from 1950-2010 for Germany "
                            "in degree celsius",
             "ttype": "absolute"}


class STRDSManagementResource(AsyncEphemeralResourceBase):
    """List all STRDS in a location/mapset
    """
    @swagger.doc({
        'tags': ['space-time raster dataset management'],
        'description': 'Return information about a STRDS that is located in a specific location/mapset. '
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
                'schema':STRDSInfoResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why information gathering of the'
                               'STRDS did not succeeded',
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
        if rdc:
            enqueue_job(self.job_timeout, strds_info, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['space-time raster dataset management'],
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
                'schema':ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why deletion of the'
                               'STRDS did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name, strds_name):
        """Delete a STRDS that is located in a specific location/mapset
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
        'tags': ['space-time raster dataset management'],
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
                'schema':ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why creation of the'
                               'STRDS did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def post(self, location_name, mapset_name, strds_name):
        """Create a new STRDS in a specific location/mapset
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
    processing = AsyncPersistentSTRDSInfo(*args)
    processing.run()


class AsyncPersistentSTRDSInfo(AsyncPersistentProcessing):
    """Gather the STRDS information
    """

    def __init__(self, *args):

        AsyncPersistentProcessing.__init__(self, *args)
        self.response_model_class = STRDSInfoResponseModel

    def _execute(self):

        self._setup()

        pc = {"1":{"module":"t.info",
                   "inputs":{"type": "strds",
                             "input": self.map_name},
              "flags": "gh"}}

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
        self.finish_message = "Information gathering for STRDS <%s> successful"%self.map_name


def strds_delete(*args):
    processing = AsyncPersistentSTRDSDelete(*args)
    processing.run()


class AsyncPersistentSTRDSDelete(AsyncPersistentProcessing):
    """Delete a STRDS
    """

    def __init__(self, *args):
        AsyncPersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()
        self.required_mapsets.append(self.target_mapset_name)

        args = self.rdc.user_data

        pc = {"1":{"module":"t.remove",
                   "inputs":{"type": "strds",
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
        self.finish_message = "STRDS <%s> successfully deleted"%self.map_name


def strds_create(*args):
    processing = AsyncPersistentSTRDSCreate(*args)
    processing.run()


class AsyncPersistentSTRDSCreate(AsyncPersistentProcessing):
    """Create a STRDS
    """

    def __init__(self, *args):
        AsyncPersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()
        self.required_mapsets.append(self.target_mapset_name)

        pc_1 = {}
        pc_1["1"] = {"module": "t.list","inputs": {"type": "strds",
                                                   "where": "id = \'%s@%s\'"%(self.map_name,
                                                                              self.target_mapset_name)}}
        # Check the first process chain
        pc_1 = self._validate_process_chain(skip_permission_check=True,
                                            process_chain=pc_1)

        pc_2 = {"1":{"module":"t.create",
                     "inputs":{"type": "strds",
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
            raise AsyncProcessError("STRDS <%s> exists."%self.map_name)

        self._execute_process_list(pc_2)

        self.finish_message = "STRDS <%s> successfully created"%self.map_name

