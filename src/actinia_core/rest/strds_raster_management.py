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
from flask_restful_swagger_2 import swagger
from flask import jsonify, make_response
import tempfile
import pickle
from actinia_api.swagger2.actinia_core.schemas.strds_raster_management import \
     STRDSRasterListResponseModel, RasterListRegisterModel, STRDSRasterListEntryModel

from actinia_core.core.request_parser import where_parser
from actinia_core.processing.actinia_processing.ephemeral.persistent_processing \
     import PersistentProcessing
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.models.response_models import \
    ProcessingResponseModel, ProcessingErrorResponseModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class STRDSRasterManagement(ResourceBase):
    """Manage raster layer in a space time raster dataset
    """

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Get a list of all raster map layers that are registered '
                       'in a STRDS that is located in a specific location/mapset. '
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
                'description': 'A where statement to select user specific '
                               'raster map layers from the STRDS',
                'required': False,
                'in': 'query',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns a list of all raster map '
                               'layers that are registered a specific STRDS and '
                               'the log of the process chain that was used to '
                               'create the response.',
                'schema': STRDSRasterListResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why '
                               'creating a list of raster map layers from STRDS '
                               'did not succeeded',
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
        'description': 'Register raster map layers in a STRDS located in a '
                       'specific location/mapset. '
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
                'description': 'The list of raster map layers to be registered '
                               'in the STRDS',
                'required': True,
                'in': 'body',
                'schema': RasterListRegisterModel
            }
        ],
        'responses': {
            '200': {
                'description': 'Registration of raster map layers was '
                               'successfully finished.',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why raster '
                               'map layer registration did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def put(self, location_name, mapset_name, strds_name):
        """Register raster map layers in a STRDS located in a specific
        location/mapset.
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
        'description': 'Unregister raster map layers from a STRDS located in a '
                       'specific location/mapset. '
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
                'description': 'The list of raster map layers to be '
                               'unregistered from the STRDS',
                'required': True,
                'in': 'body',
                'schema': {"type": "array", "items": {"type": "string"}}
            }
        ],
        'responses': {
            '200': {
                'description': 'Unregistration of raster map layers was '
                               'successfully finished.',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why raster '
                               'map layer unregistration did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name, strds_name):
        """Unregister raster map layers from a STRDS located in a specific
        location/mapset.
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

        input_file = tempfile.NamedTemporaryFile(
            dir=self.temp_file_path, delete=True, mode="w")

        for map_entry in self.request_data:
            if ("name" not in map_entry
                    or "start_time" not in map_entry
                    or "end_time" not in map_entry):
                raise AsyncProcessError(
                    "Wrong input format for raster map layer registration")

            line = "%s|%s|%s\n" % (
                map_entry["name"], map_entry["start_time"], map_entry["end_time"])
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

        input_file = tempfile.NamedTemporaryFile(
            dir=self.temp_file_path, delete=True, mode="w")

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
