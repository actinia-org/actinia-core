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
Raster map renderer
"""
from flask import jsonify, make_response, Response
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.renderer_base import RendererBaseResource
import os
from flask_restful_swagger_2 import swagger
from actinia_core.models.response_models import ProcessingErrorResponseModel
from actinia_core.processing.common.strds_renderer import start_job

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class SyncEphemeralSTRDSRendererResource(RendererBaseResource):

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Render the raster map layers of a specific STRDS as a '
                       'single image. All raster layers are rendered in order '
                       'of their time stamps, from past to future. '
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
                               'required raster map layer',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            },
            {
                'name': 'strds_name',
                'description': 'The name of the STRDS to render',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'elevation'
            },
            {
                'name': 'n',
                'description': 'Northern border',
                'required': False,
                'in': 'query',
                'type': 'number',
                'format': 'double'
            },
            {
                'name': 's',
                'description': 'Southern border',
                'required': False,
                'in': 'query',
                'type': 'number',
                'format': 'double'
            },
            {
                'name': 'e',
                'description': 'Eastern border',
                'required': False,
                'in': 'query',
                'type': 'number',
                'format': 'double'
            },
            {
                'name': 'w',
                'description': 'Western border',
                'required': False,
                'in': 'query',
                'type': 'number',
                'format': 'double'
            },
            {
                'name': 'width',
                'description': 'Image width in pixel, default is 800',
                'required': False,
                'in': 'query',
                'type': 'number',
                'format': 'integer',
                'default': 800
            },
            {
                'name': 'height',
                'description': 'Image height in pixel, default is 600',
                'required': False,
                'in': 'query',
                'type': 'number',
                'format': 'integer',
                'default': 600
            },
            {
                'name': 'start_time',
                'description': 'Raster map layers that have equal or greater '
                               'the start time will be rendered',
                'required': False,
                'in': 'query',
                'type': 'string'
            },
            {
                'name': 'end_time',
                'description': 'Raster map layers that have equal or lower the '
                               'end time will be rendered',
                'required': False,
                'in': 'query',
                'type': 'string'
            }
        ],
        'produces': ["image/png"],
        'responses': {
            '200': {
                'description': 'The PNG image'},
            '400': {
                'description': 'The error message and a detailed log why '
                               'rendering did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name, strds_name):
        """Render the raster map layers of a specific STRDS as a single image.
        """
        parser = self.create_parser()
        args = parser.parse_args()
        options = self.create_parser_options(args)

        if isinstance(options, dict) is False:
            return options

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        rdc.set_user_data(options)

        enqueue_job(self.job_timeout, start_job, rdc)

        http_code, response_model = self.wait_until_finish(0.05)
        if http_code == 200:
            result_file = response_model["process_results"]
            # Open the image file, read it and then delete it
            if result_file:
                if os.path.isfile(result_file):
                    image = open(result_file, "rb").read()
                    os.remove(result_file)
                    return Response(image, mimetype='image/png')
        return make_response(jsonify(response_model), http_code)
