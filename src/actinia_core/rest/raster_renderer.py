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
from flask_restful_swagger_2 import swagger
import os
from flask import jsonify, make_response, Response
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.renderer_base import RendererBaseResource
from actinia_core.models.response_models import ProcessingErrorResponseModel
from actinia_core.processing.common.raster_renderer import \
    start_job, start_rgb_job, start_shade_job

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class SyncEphemeralRasterRendererResource(RendererBaseResource):
    """Render a raster image with g.region/d.rast approach synchronously
    """

    @swagger.doc({
        'tags': ['Raster Management'],
        'description': 'Render a raster map layer as a PNG image. '
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
                'name': 'raster_name',
                'description': 'The name of the raster map layer to render',
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
    def get(self, location_name, mapset_name, raster_name):
        """Render a raster map layer as a PNG image.
        """
        parser = self.create_parser()
        args = parser.parse_args()
        options = self.create_parser_options(args)

        if isinstance(options, dict) is False:
            return options

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=raster_name)

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


class SyncEphemeralRasterRGBRendererResource(RendererBaseResource):
    """Render three raster layer as rgb image with g.region/d.rgb approach synchronously
    """

    def extract_rgb_maps(self, args, mapset_name):
        """Parse the request parameters for red green and blue raster layers

        Args:
            args (dict): The argument dictionary with rendering options
            mapset_name (str): Name of the mapset

        Returns:
             dict:
             A dictionary of d.rgb options or a error response if width or height
             are invalid and if the mapset is present in the raster layer names.

        """
        options = self.create_parser_options(args)

        if "@" in args["red"]:
            return self.get_error_response(
                message="Mapset name is not allowed in layer names")

        if "@" in args["green"]:
            return self.get_error_response(
                message="Mapset name is not allowed in layer names")

        if "@" in args["blue"]:
            return self.get_error_response(
                message="Mapset name is not allowed in layer names")

        options["red"] = "%s@%s" % (args["red"], mapset_name)
        options["green"] = "%s@%s" % (args["green"], mapset_name)
        options["blue"] = "%s@%s" % (args["blue"], mapset_name)

        return options

    @swagger.doc({
        'tags': ['Raster Management'],
        'description': 'Render three raster map layer as composed RGB PNG image. '
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
                'default': 'landsat'
            },
            {
                'name': 'red',
                'description': 'The name of the raster map layer to render '
                               'as color red',
                'required': True,
                'in': 'query',
                'type': 'string',
                'default': 'lsat5_1987_30'
            },
            {
                'name': 'green',
                'description': 'The name of the raster map layer to render as '
                               'color green',
                'required': True,
                'in': 'query',
                'type': 'string',
                'default': 'lsat5_1987_20'
            },
            {
                'name': 'blue',
                'description': 'The name of the raster map layer to render as '
                               'color blue',
                'required': True,
                'in': 'query',
                'type': 'string',
                'default': 'lsat5_1987_10'
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
                'description': 'The RGB composition PNG image'},
            '400': {
                'description': 'The error message and a detailed log why '
                               'rendering did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name):
        """Render three raster map layer as composed RGB PNG image.
        """

        parser = self.create_parser()
        parser.add_argument(
            'red', required=True, type=str,
            help='The name of the raster layer associated with the color red')
        parser.add_argument(
            'green', required=True, type=str,
            help='The name of the raster layer associated with the color green')
        parser.add_argument(
            'blue', required=True, type=str,
            help='The name of the raster layer associated with the color blue')

        args = parser.parse_args()
        rgb_options = self.extract_rgb_maps(args, mapset_name)

        if isinstance(rgb_options, dict) is False:
            return rgb_options

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name)

        rdc.set_user_data(rgb_options)

        enqueue_job(self.job_timeout, start_rgb_job, rdc)

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


class SyncEphemeralRasterShapeRendererResource(RendererBaseResource):
    """Render two raster layer as shade image with g.region/d.shade approach
    synchronously
    """

    def extract_shade_maps(self, args, mapset_name):
        """Parse the request parameters for shade and color raster layers

        Args:
            args (dict): The argument dictionary with rendering options
            mapset_name: Name of the mapset

        Returns:
             dict:
             A dictionary of d.shade options an error response if width or
             height are invalid and if the mapset is present in the raster
             layer names

        """
        options = self.create_parser_options(args)

        if "@" in args["shade"]:
            return self.get_error_response(
                message="Mapset name is not allowed in layer names")

        if "@" in args["color"]:
            return self.get_error_response(
                message="Mapset name is not allowed in layer names")

        options["shade"] = "%s@%s" % (args["shade"], mapset_name)
        options["color"] = "%s@%s" % (args["color"], mapset_name)

        return options

    @swagger.doc({
        'tags': ['Raster Management'],
        'description': 'Render two raster layers as a composed shade PNG image. '
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
                'name': 'shade',
                'description': 'The name of the raster map layer to be used '
                               'for shading',
                'required': True,
                'in': 'query',
                'type': 'string',
                'default': 'aspect'
            },
            {
                'name': 'color',
                'description': 'The name of the raster map layer to be used for '
                               'coloring',
                'required': True,
                'in': 'query',
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
            }
        ],
        'produces': ["image/png"],
        'responses': {
            '200': {
                'description': 'The shade/color composition PNG image'},
            '400': {
                'description': 'The error message and a detailed log why '
                               'rendering did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name):
        """Render two raster layers as a composed shade PNG image
        """
        parser = self.create_parser()
        parser.add_argument(
            'shade', required=True, type=str,
            help='The name of the raster layer associated with shading')
        parser.add_argument(
            'color', required=True, type=str,
            help='The name of the raster layer associated with color')

        args = parser.parse_args()
        options = self.extract_shade_maps(args, mapset_name)

        if isinstance(options, dict) is False:
            return options

        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name)

        rdc.set_user_data(options)

        enqueue_job(self.job_timeout, start_shade_job, rdc)

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
