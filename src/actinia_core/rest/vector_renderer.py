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
Raster map renderer

"""

import tempfile
import os
from flask_restful_swagger_2 import swagger
from flask import jsonify, make_response, Response
from .ephemeral_processing import EphemeralProcessing
from actinia_core.core.redis_interface import enqueue_job
from .renderer_base import RendererBaseResource, EphemeralRendererBase
from actinia_core.models.response_models import ProcessingErrorResponseModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class SyncEphemeralVectorRendererResource(RendererBaseResource):
    """Render a vector layer with g.region/d.vect approach synchronously
    """

    @swagger.doc({
        'tags': ['Vector Management'],
        'description': 'Render a single vector map layer. Minimum required user '
                       'role: user.',
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
                'name': 'vector_name',
                'description': 'The name of the vector map layer to render',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'boundary_county'
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
    def get(self, location_name, mapset_name, vector_name):
        """Render a single vector map layer
        """
        parser = self.create_parser()
        args = parser.parse_args()
        options = self.create_parser_options(args)

        if isinstance(options, dict) is False:
            return options

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=vector_name)

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


def start_job(*args):
    processing = EphemeralVectorRenderer(*args)
    processing.run()


class EphemeralVectorRenderer(EphemeralRendererBase):

    def __init__(self, *args):

        EphemeralProcessing.__init__(self, *args)

    def _execute(self, skip_permission_check=True):
        """Render the vector image

        Workflow:

            1. The default region is set to the vector region
            2. User specific region settings are applied
            3. d.vect is invoked to create the PNG file

        """

        self._setup()

        vector_name = self.map_name
        options = self.rdc.user_data
        self.required_mapsets.append(self.mapset_name)

        result_file = tempfile.mktemp(suffix=".png")

        region_pc = self._setup_render_environment_and_region(
            options=options, result_file=result_file)

        pc = {}
        pc["1"] = {"module": "g.region", "inputs": {
            "vector": vector_name + "@" + self.mapset_name}}
        pc["2"] = region_pc
        pc["3"] = {
            "module": "d.vect",
            "inputs": {"map": vector_name + "@" + self.mapset_name},
            "flags": "c"}

        # Run the selected modules
        self.skip_region_check = True
        process_list = self._create_temporary_grass_environment_and_process_list(
            process_chain=pc, skip_permission_check=True)
        self._execute_process_list(process_list)

        self.module_results = result_file
