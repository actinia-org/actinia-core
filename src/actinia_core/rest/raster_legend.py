# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2024 Sören Gebbert and mundialis GmbH & Co. KG
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

import os
from flask import jsonify, make_response, Response
from flask_restful import reqparse
from flask_restful_swagger_2 import swagger
from actinia_api.swagger2.actinia_core.apidocs import raster_legend

from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.processing.common.raster_legend import start_job


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class SyncEphemeralRasterLegendResource(ResourceBase):
    """Render the raster legend with d.legend"""

    def create_parser(self):
        # Create a legend parser
        parser = reqparse.RequestParser()
        parser.add_argument(
            "at",
            type=str,
            location="args",
            help="Size and placement as percentage of "
            "screen coordinates (0,0 is lower left). "
            "bottom,top,left,right 0-100%",
        )
        parser.add_argument(
            "range",
            type=str,
            location="args",
            help="Use a subset of the map range for the legend " "(min,max)",
        )
        parser.add_argument(
            "use",
            type=str,
            location="args",
            help="List of discrete category numbers/values for legend",
        )
        parser.add_argument(
            "fontsize",
            type=float,
            location="args",
            help="Size of the font 1-360",
        )
        parser.add_argument(
            "labelnum",
            type=float,
            location="args",
            help="Number of text labels for smooth gradient legend",
        )
        parser.add_argument(
            "width",
            type=float,
            location="args",
            help="North-South resolution must be specified as " "double value",
        )
        parser.add_argument(
            "height",
            type=float,
            location="args",
            help="East-West resolution must be specified as " "double value",
        )

        return parser

    def create_parser_options(self, args):
        """Parse the request parameters for raster legends

        Args:
            args (dict): The argument dictionary with display options

        Returns:
             dict:
             A dictionary of display parameter or an error response in case of
             an error
        """
        options = {}
        options["width"] = 600
        options["height"] = 800
        options["at"] = "0,100,0,15"

        if "labelnum" in args and args["labelnum"] is not None:
            options["labelnum"] = args["labelnum"]
        if "use" in args and args["use"] is not None:
            options["use"] = args["use"]
        if "at" in args and args["at"] is not None:
            options["at"] = args["at"]
        if "range" in args and args["range"] is not None:
            options["range"] = args["range"]
        if "use" in args and args["use"] is not None:
            options["use"] = args["use"]
        if "fontsize" in args and args["fontsize"] is not None:
            options["fontsize"] = args["fontsize"]
        if "width" in args and args["width"] is not None:
            if args["width"] < 1:
                return self.get_error_response(
                    message="Width must be larger than 0"
                )
            if args["width"] > 10000:
                return self.get_error_response(
                    message="Width can not be larger than 10000"
                )
            options["width"] = args["width"]
        if "height" in args and args["height"] is not None:
            if args["height"] < 1:
                return self.get_error_response(
                    message="Height must be larger than 0"
                )
            if args["height"] > 10000:
                return self.get_error_response(
                    message="Height can not be larger than 10000"
                )
            options["height"] = args["height"]

        return options

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", raster_legend.get_doc))
    def get(self, project_name, mapset_name, raster_name):
        """Render the legend of a raster map layer as a PNG image."""
        parser = self.create_parser()
        args = parser.parse_args()
        options = self.create_parser_options(args)

        if isinstance(options, dict) is False:
            return options

        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=raster_name,
        )

        rdc.set_user_data(options)

        enqueue_job(
            self.job_timeout, start_job, rdc, queue_type_overwrite=True
        )

        http_code, response_model = self.wait_until_finish(0.05)
        if http_code == 200:
            result_file = response_model["process_results"]
            # Open the image file, read it and then delete it
            if result_file:
                if os.path.isfile(result_file):
                    image = open(result_file, "rb").read()
                    os.remove(result_file)
                    return Response(image, mimetype="image/png")
        return make_response(jsonify(response_model), http_code)
