# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2022 Sören Gebbert and mundialis GmbH & Co. KG
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
from uuid import uuid4
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from actinia_api.swagger2.actinia_core.schemas.vector_layer import \
    VectorInfoResponseModel, VectorRegionCreationModel

from actinia_core.core.common.app import URL_PREFIX
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.utils import allowed_file
from actinia_core.models.response_models import \
    ProcessingResponseModel, ProcessingErrorResponseModel, SimpleResponseModel
from actinia_core.rest.base.map_layer_base import MapLayerRegionResourceBase
from actinia_core.processing.common.vector_layer import \
    start_create_job, start_delete_job, start_info_job

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
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
