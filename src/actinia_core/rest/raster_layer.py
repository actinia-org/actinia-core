# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2021 Sören Gebbert and mundialis GmbH & Co. KG
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
Raster layer resources
"""
from flask import jsonify, make_response, request
from flask_restful_swagger_2 import swagger
import os
import pickle
from uuid import uuid4
from werkzeug.utils import secure_filename

from actinia_core.rest.ephemeral_processing import EphemeralProcessing
from actinia_core.rest.persistent_processing import PersistentProcessing
from actinia_core.rest.map_layer_base import MapLayerRegionResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.core.utils import allowed_file
from actinia_core.models.response_models import \
    ProcessingResponseModel, ProcessingErrorResponseModel
from actinia_core.models.response_models import SimpleResponseModel
from actinia_core.models.openapi.raster_layer import \
     RasterInfoResponseModel, RasterInfoModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class RasterLayerResource(MapLayerRegionResourceBase):
    """Return information about a specific raster layer as JSON
    """

    @swagger.doc({
        'tags': ['Raster Management'],
        'description': 'Get information about an existing raster map layer. '
                       'Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The location name',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset that contains the required '
                               'raster map layer',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            },
            {
                'name': 'raster_name',
                'description': 'The name of the raster map layer to get '
                               'information about',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'elevation'
            }
        ],
        'consumes': ['application/json'],
        'produces': ["application/json"],
        'responses': {
            '200': {
                'description': 'The raster map layer information',
                'schema': RasterInfoResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why '
                               'gathering raster map '
                               'layer information did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name, raster_name):
        """Get information about an existing raster map layer.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=raster_name)
        if rdc:
            enqueue_job(self.job_timeout, start_info_job, rdc)
            http_code, response_model = self.wait_until_finish(0.02)
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['Raster Management'],
        'description': 'Delete an existing raster map layer. Minimum required '
                       'user role: user.',
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
                'description': 'The name of the mapset that contains the '
                               'required raster map layer',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'raster_name',
                'description': 'The name of the raster map layer to be deleted',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'produces': ["application/json"],
        'responses': {
            '200': {
                'description': 'Successfuly delete a raster map layer',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why '
                               'raster map '
                               'layer deletion did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name, raster_name):
        """Delete an existing raster map layer.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=raster_name)
        if rdc:
            enqueue_job(self.job_timeout, start_delete_job, rdc)
            http_code, response_model = self.wait_until_finish(0.1)
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['Raster Management'],
        'description': 'Create a new raster map layer by uploading a GeoTIFF. '
                       'This method will fail if the map already exists. '
                       'Minimum required user role: user.',
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
                'description': 'The name of the mapset in which the raster map '
                               'layer should be created',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'raster_name',
                'description': 'The name of the new raster map layer to be created',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'consumes': ['Content-Type: multipart/form-data'],
        'produces': ["application/json"],
        'responses': {
            '200': {
                'description': 'Raster map layer creation information',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why raster map '
                               'layer creation did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def post(self, location_name, mapset_name, raster_name):
        """Create a new raster layer by uploading a GeoTIFF
        """

        allowed_extensions = ['tif', 'tiff']

        # TODO check if another content type can be used
        content_type = request.content_type.split(';')[0]
        if content_type != "multipart/form-data":
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="Content type is not 'multipart/form-data'")), 400)

        if 'file' not in request.files:
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="No file part indicated in postbody.")), 400)

        # create download cache path if does not exists
        if os.path.exists(self.download_cache):
            pass
        else:
            os.mkdir(self.download_cache)

        # save file from request
        id = str(uuid4())
        file = request.files['file']
        if file.filename == '':
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="No selected file")), 400)
        if allowed_file(file.filename, allowed_extensions):
            name, extension = secure_filename(file.filename).rsplit('.', 1)
            filename = f"{name}_{id}.{extension}"
            file_path = os.path.join(self.download_cache, filename)
            file.save(file_path)
        else:
            os.remove(file_path)
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="File has a not allowed extension. "
                        f"Please use {','.join(allowed_extensions)}.")), 400)

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=raster_name)
        if rdc:
            rdc.set_request_data(file_path)
            enqueue_job(self.job_timeout, start_create_job, rdc)

        http_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), http_code)


def start_info_job(*args):
    processing = EphemeralRasterInfo(*args)
    processing.run()


class EphemeralRasterInfo(EphemeralProcessing):

    def __init__(self, *args):

        EphemeralProcessing.__init__(self, *args)

    def _execute(self):
        """Read info from a raster layer

        Use a temporary mapset for processing
        """
        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.mapset_name)

        pc = {}
        pc["1"] = {
            "module": "r.info", "inputs": {
                "map": raster_name + "@" + self.mapset_name},
            "flags": "gre"}

        self.skip_region_check = True
        process_list = self._create_temporary_grass_environment_and_process_list(
            process_chain=pc, skip_permission_check=True)
        self._execute_process_list(process_list)

        kv_list = self.module_output_log[0]["stdout"].split("\n")

        raster_info = {}

        for string in kv_list:
            if "=" in string:
                k, v = string.split("=", 1)
                raster_info[k] = v

        self.module_results = RasterInfoModel(**raster_info)


def start_delete_job(*args):
    processing = PersistentRasterDeleter(*args)
    processing.run()


class PersistentRasterDeleter(PersistentProcessing):

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        """Delete a specific raster layer

        Use the original mapset for processing
        """
        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        pc = {}
        pc["1"] = {"module": "g.remove", "inputs": {"type": "raster",
                                                    "name": raster_name},
                   "flags": "f"}

        self.skip_region_check = True
        process_list = self._validate_process_chain(process_chain=pc,
                                                    skip_permission_check=True)
        self._check_lock_target_mapset()
        self._create_temp_database(self.required_mapsets)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_list(process_list)

        if "WARNING: No data base element files found" in "\n".join(
                self.module_output_log[0]["stderr"]):
            raise AsyncProcessError("Raster layer <%s> not found" % raster_name)

        self.finish_message = "Raster layer <%s> successfully removed." % raster_name


def start_create_job(*args):
    processing = PersistentRasterCreator(*args)
    processing.run()


class PersistentRasterCreator(PersistentProcessing):

    def __init__(self, *args):

        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        """Create a specific raster layer

        This approach is complex, since the raster generation is performed in a local
        temporary mapset that is later merged into the target mapset. Workflow:

        1. Check the process chain
        2. Lock the temp and target mapsets
        3. Setup GRASS and create the temporary mapset
        4. Execute g.list of the first process chain to check if the target
           raster exists
        5. If the target raster does not exists then run r.import
        6. Copy the local temporary mapset to the storage and merge it into the
           target mapset
        """
        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        pc_1 = {}
        pc_1["1"] = {"module": "g.list", "inputs": {
            "type": "raster",
            "pattern": raster_name,
            "mapset": self.target_mapset_name}}
        # Check the first process chain
        pc_1 = self._validate_process_chain(skip_permission_check=True,
                                            process_chain=pc_1)

        pc_2 = {}
        pc_2["1"] = {
            "module": "r.import",
            "inputs": {
                "input": self.rdc.request_data,
                "output": raster_name
                }
        }
        # Check the second process chain
        pc_2 = self._validate_process_chain(skip_permission_check=True,
                                            process_chain=pc_2)

        self._check_lock_target_mapset()
        self._lock_temp_mapset()
        self._create_temporary_grass_environment()
        self._execute_process_list(pc_1)

        # check if raster exists
        raster_list = self.module_output_log[0]["stdout"].split("\n")

        if len(raster_list[0]) > 0:
            try:
                os.remove(self.rdc.request_data)
            except Exception:
                pass
            raise AsyncProcessError(
                "Raster layer <%s> exists. Please rename it or delete the old "
                "raster layer" % raster_name)

        self._execute_process_list(pc_2)
        self._copy_merge_tmp_mapset_to_target_mapset()

        # Delete imported file
        msg = ""
        try:
            os.remove(self.rdc.request_data)
        except Exception:
            msg = " WARNING: Uploaded file can not be removed."

        self.finish_message = f"Raster layer <{raster_name}> successfully created.{msg}"
