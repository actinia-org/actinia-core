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
Vector layer resources
"""
from flask import jsonify, make_response, request
from flask_restful_swagger_2 import swagger
import os
import pickle
from shutil import rmtree
from uuid import uuid4
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from actinia_api.swagger2.actinia_core.schemas.vector_layer import \
    VectorInfoResponseModel, VectorRegionCreationModel, \
    VectorAttributeModel, VectorInfoModel

from actinia_core.core.common.app import URL_PREFIX
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.core.utils import allowed_file
from actinia_core.models.response_models import \
    ProcessingResponseModel, ProcessingErrorResponseModel, SimpleResponseModel
from .ephemeral_processing import EphemeralProcessing
from .persistent_processing import PersistentProcessing
from .map_layer_base import MapLayerRegionResourceBase

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class VectorLayerResource(MapLayerRegionResourceBase):
    """Manage a vector map layer
    """

    @swagger.doc({
        'tags': ['Vector Management'],
        'description': 'Get information about an existing vector map layer. '
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
                'description': 'The name of the mapset that contains the '
                               'required vector map layer',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            },
            {
                'name': 'vector_name',
                'description': 'The name of the vector map layer to get '
                               'information about',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'boundary_county'
            }
        ],
        'consumes': ['application/json'],
        'produces': ["application/json"],
        'responses': {
            '200': {
                'description': 'The vector map layer information',
                'schema': VectorInfoResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why '
                               'gathering vector map layer information '
                               'did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name, vector_name):
        """Get information about an existing vector map layer.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=vector_name)

        if rdc:
            enqueue_job(self.job_timeout, start_info_job, rdc)
            http_code, response_model = self.wait_until_finish(0.02)
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['Vector Management'],
        'description': 'Delete an existing vector map layer. '
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
                'description': 'The name of the mapset that contains the '
                               'required vector map layer',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'vector_name',
                'description': 'The name of the vector map layer to be deleted',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'produces': ["application/json"],
        'responses': {
            '200': {
                'description': 'Successfully delete a vector map layer',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why vector map '
                               'layer deletion did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name, vector_name):
        """Delete an existing vector map layer.
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=vector_name)

        if rdc:
            enqueue_job(self.job_timeout, start_delete_job, rdc)
            http_code, response_model = self.wait_until_finish(0.1)
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['Vector Management'],
        'description': 'Create a new vector map layer by uploading a GPKG, '
                       'zipped Shapefile or GeoJSON. '
                       'This method will fail if the map already exists. '
                       'An example request is \'curl -L -u "XXX:XXX" -X POST '
                       '-H "Content-Type: multipart/form-data" -F '
                       '"file=@/home/....gpkg" http://localhost:8088'
                       f'{URL_PREFIX}/'
                       'locations/nc_spm_08/mapsets/test_mapset/vector_layers/'
                       'testvector\'. Minimum required user role: user.',
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
                               'required vector map layer',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'vector_name',
                'description': 'The name of the new vector map layer to be created',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'creation_params',
                'description': 'Parameters to create random vector point map '
                               'layer in a specific region.',
                'required': True,
                'in': 'body',
                'schema': VectorRegionCreationModel
            }
        ],
        'consumes': ['Content-Type: multipart/form-data'],
        'produces': ["application/json"],
        'responses': {
            '200': {
                'description': 'The vector map layer import information',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why '
                               'vector map layer import failed',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def post(self, location_name, mapset_name, vector_name):
        """Create a new vector layer by uploading a GPKG, zipped Shapefile,
        or GeoJSON.
        """

        allowed_extensions = ['gpkg', 'zip', 'json', 'geojson']

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

        # create download cache path if it does not exist
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

        # Shapefile upload as zip
        if extension == 'zip':
            unzip_folder = os.path.join(self.download_cache, f'unzip_{id}')
            with ZipFile(file_path, "r") as zip_ref:
                zip_ref.extractall(unzip_folder)
            shp_files = [entry for entry in os.listdir(
                unzip_folder) if entry.endswith('.shp')]
            if len(shp_files) == 0:
                return make_response(jsonify(SimpleResponseModel(
                    status="error",
                    message="No .shp file found in zip file.")), 400)
            elif len(shp_files) > 1:
                return make_response(jsonify(SimpleResponseModel(
                    status="error",
                    message=f"{len(shp_files)} .shp files found in zip file."
                            "Please put only one in the zip file.")), 400)
            else:
                os.remove(file_path)
                file_path = os.path.join(unzip_folder, shp_files[0])

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=vector_name)
        if rdc:
            rdc.set_request_data(file_path)
            enqueue_job(self.job_timeout, start_create_job, rdc)

        http_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), http_code)


def start_info_job(*args):
    processing = EphemeralVectorInfo(*args)
    processing.run()


class EphemeralVectorInfo(EphemeralProcessing):

    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)
        self.response_model_class = VectorInfoResponseModel

    def _execute(self):
        """Read info from a vector layer

        Use a temporary mapset for processing
        """
        self._setup()

        vector_name = self.rdc.map_name
        self.required_mapsets.append(self.mapset_name)

        pc = {}
        pc["1"] = {
            "module": "v.info",
            "inputs": {"map": vector_name + "@" + self.mapset_name},
            "flags": "gte"}

        pc["2"] = {
            "module": "v.info",
            "inputs": {"map": vector_name + "@" + self.mapset_name},
            "flags": "h"}

        pc["3"] = {
            "module": "v.info",
            "inputs": {"map": vector_name + "@" + self.mapset_name},
            "flags": "c"}

        self.skip_region_check = True
        process_list = self._create_temporary_grass_environment_and_process_list(
            process_chain=pc, skip_permission_check=True)
        self._execute_process_list(process_list)

        kv_list = self.module_output_log[0]["stdout"].split("\n")

        vector_info = {}
        # Regular metadata
        for string in kv_list:
            if "=" in string:
                k, v = string.split("=", 1)
                vector_info[k] = v

        kv_list = self.module_output_log[1]["stdout"].split("\n")
        # Command that created the vector
        for string in kv_list:
            if "COMMAND:" in string:
                k, v = string.split(":", 1)
                vector_info[k] = v

        datatypes = self.module_output_log[2]["stdout"].split("\n")

        # Datatype of the vector table
        attr_list = []
        for string in datatypes:
            if "|" in string:
                dt_dict = {}
                col_type, col_name = string.split("|", 1)
                dt_dict["type"] = col_type
                dt_dict["column"] = col_name
                attr_list.append(VectorAttributeModel(**dt_dict))

        vector_info["Attributes"] = attr_list

        self.module_results = VectorInfoModel(**vector_info)


def start_delete_job(*args):
    processing = PersistentVectorDeleter(*args)
    processing.run()


class PersistentVectorDeleter(PersistentProcessing):

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        """Delete a specific vector layer from a location in the user database

        Use the original mapset for processing
        """
        self._setup()

        vector_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        pc = {}
        pc["1"] = {"module": "g.remove", "inputs": {"type": "vector",
                                                    "name": vector_name},
                   "flags": "f"}

        self.skip_region_check = True
        process_list = self._validate_process_chain(process_chain=pc,
                                                    skip_permission_check=True)
        self._check_lock_target_mapset()
        self._create_grass_environment(grass_data_base=self.grass_user_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_list(process_list)

        if "WARNING: No data base element files found" in "\n".join(
                self.module_output_log[0]["stderr"]):
            raise AsyncProcessError("Vector layer <%s> not found" % (vector_name))

        self.finish_message = "Vector layer <%s> successfully removed." % vector_name


def start_create_job(*args):
    processing = PersistentVectorCreator(*args)
    processing.run()


class PersistentVectorCreator(PersistentProcessing):

    def __init__(self, *args):

        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        """Create a specific vector layer

        This approach is complex, since the vector generation is performed in a local
        temporary mapset that is later merged into the target mapset. Workflow:

        1. Check the process chain
        2. Lock the temp and target mapsets
        3. Setup GRASS and create the temporary mapset
        4. Execute g.list of the first process chain to check if the target
           vector exists
        5. If the target vector does not exist then run v.import
        6. Copy the local temporary mapset to the storage and merge it into the
           target mapset
        """
        self._setup()

        vector_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        pc_1 = {}
        pc_1["1"] = {"module": "g.list", "inputs": {"type": "vector",
                                                    "pattern": vector_name,
                                                    "mapset": self.target_mapset_name}}
        # Check the first process chain
        self.skip_region_check = True
        pc_1 = self._validate_process_chain(skip_permission_check=True,
                                            process_chain=pc_1)

        pc_2 = {}
        pc_2["1"] = {"module": "v.import",
                     "inputs": {"input": self.rdc.request_data},
                     "outputs": {"output": {"name": vector_name}}}
        # Check the second process chain
        self.skip_region_check = True
        pc_2 = self._validate_process_chain(skip_permission_check=True,
                                            process_chain=pc_2)

        self._check_lock_target_mapset()
        self._lock_temp_mapset()
        self._create_temporary_grass_environment(
            source_mapset_name=self.target_mapset_name)
        self._execute_process_list(pc_1)

        # check if vector exists
        raster_list = self.module_output_log[0]["stdout"].split("\n")

        if len(raster_list[0]) > 0:
            raise AsyncProcessError("Vector layer <%s> exists." % vector_name)

        self._execute_process_list(pc_2)
        self._copy_merge_tmp_mapset_to_target_mapset()

        # Delete imported file
        msg = ""
        try:
            if self.rdc.request_data.endswith('.shp'):
                rmtree(os.path.dirname(self.rdc.request_data), ignore_errors=True)
            else:
                os.remove(self.rdc.request_data)
        except Exception:
            msg = " WARNING: Uploaded file cannot be removed."

        self.finish_message = (f"Vector layer <{vector_name}> successfully "
                               f"imported.{msg}")
