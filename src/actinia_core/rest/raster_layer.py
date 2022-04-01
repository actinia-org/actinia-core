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
Raster layer resources
"""
from flask import jsonify, make_response, request
from flask_restful_swagger_2 import swagger
import os
import pickle
from uuid import uuid4
from werkzeug.utils import secure_filename
from actinia_api.swagger2.actinia_core.schemas.raster_layer import \
     RasterInfoResponseModel

from actinia_core.core.common.app import URL_PREFIX
from actinia_core.rest.base.map_layer_base import MapLayerRegionResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.utils import allowed_file
from actinia_core.models.response_models import \
    ProcessingResponseModel, ProcessingErrorResponseModel
from actinia_core.models.response_models import SimpleResponseModel
from actinia_core.processing.common.raster_layer import \
     start_info_job, start_delete_job, start_create_job

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
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
                       'An example request is \'curl -L -u "XXX:XXX" -X POST '
                       '-H "Content-Type: multipart/form-data" -F '
                       '"file=@/home/....tif" http://localhost:8088'
                       f'{URL_PREFIX}/'
                       'locations/nc_spm_08/mapsets/test_mapset/raster_layers/'
                       'testraster\'. Minimum required user role: user.',
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
                'description': 'Raster map layer import information',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why raster map '
                               'layer import failed',
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
