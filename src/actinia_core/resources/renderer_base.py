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
Render base classes
"""

from flask_restful import reqparse
from .ephemeral_processing import EphemeralProcessing
from .resource_base import ResourceBase
import os

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


REGION_PARAMETERS = {
    'parameters': [
        {
            'name': 'n',
            'description': 'Northern border',
            'required': False,
            'in': 'query',
            'type': 'double'
        },
        {
            'name': 's',
            'description': 'Southern border',
            'required': False,
            'in': 'query',
            'type': 'double'
        },
        {
            'name': 'e',
            'description': 'Eastern border',
            'required': False,
            'in': 'query',
            'type': 'double'
        },
        {
            'name': 'w',
            'description': 'Western border',
            'required': False,
            'in': 'query',
            'type': 'double'
        },
        {
            'name': 'width',
            'description': 'Image width',
            'required': False,
            'in': 'query',
            'type': 'double'
        },
        {
            'name': 'height',
            'description': 'Image height',
            'required': False,
            'in': 'query',
            'type': 'double'
        }
    ]
}


class RendererBaseResource(ResourceBase):
    """Base class for render resources
    """

    def create_parser(self):
        """Create the render option arguments

        The parameter contain:

            n : for north
            s : for south
            e : for east
            w : for west
            width : for the image width
            height : for the image height
            start_time : start time for STRDS where selection
            end_time : end time for STRDS where selection

        Returns:
            The argument parser

        """
        parser = reqparse.RequestParser()
        parser.add_argument('n', type=float, location='args',
                            help='Northern border must be specified as double value')
        parser.add_argument('e', type=float, location='args',
                            help='Eastern border must be specified as double value')
        parser.add_argument('w', type=float, location='args',
                            help='Western border must be specified as double value')
        parser.add_argument('s', type=float, location='args',
                            help='Southern border must be specified as double value')
        parser.add_argument('width', type=float, location='args',
                            help='Image width must be specified as double value')
        parser.add_argument('height', type=float, location='args',
                            help='Image height must be specified as double value')
        parser.add_argument('start_time', type=str, location='args',
                            help='Start time for STRDS raster map layer selection')
        parser.add_argument('end_time', type=str, location='args',
                            help='Start time for STRDS raster map layer selection')

        return parser

    def create_parser_options(self, args):
        """Parse the request parameters for raster and vector rendering

        By default the width is 800, the height is 600 pixel.

        Args:
            args (dict): The argument dictionary with rendering options

        Returns:
             dict:
             A dictionary of render options or an error response object in an case of error.
             In case of an error response object, an update to the resource logger was performed.

        """
        options = {}
        options["width"] = 800
        options["height"] = 600
        if "n" in args and args["n"] is not None:
            options["n"] = args["n"]
        if "s" in args and args["s"] is not None:
            options["s"] = args["s"]
        if "e" in args and args["e"] is not None:
            options["e"] = args["e"]
        if "w" in args and args["w"] is not None:
            options["w"] = args["w"]
        if "width" in args and args["width"] is not None:
            if args["width"] < 1:
                return self.get_error_response(message="Width must be larger than 0")
            if args["width"] > 10000:
                return self.get_error_response(message="Width can not be larger than 10000")
            options["width"] = args["width"]
        if "height" in args and args["height"] is not None:
            if args["height"] < 1:
                return self.get_error_response(message="Height must be larger than 0")
            if args["height"] > 10000:
                return self.get_error_response("Height can not be larger than 10000")
            options["height"] = args["height"]
        if "start_time" in args and args["start_time"] is not None:
            options["start_time"] = args["start_time"]
        if "end_time" in args and args["end_time"] is not None:
            options["end_time"] = args["end_time"]
        return options


class EphemeralRendererBase(EphemeralProcessing):

    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)

    def _setup_render_environment_and_region(self, options, result_file, legacy=True):
        """Setup the render environment and create a g.region
         process chain entry to setup the extent from the options.

        Args:
            options: The parser options that contain n, s, e and w entries for region settings
            result_file: The resulting PNG file name
            legacy: If True use the legacy process chain format for the g.region process definition

        Returns:
            A process chain entry of g.region

        """
        os.putenv("GRASS_RENDER_IMMEDIATE", "png")
        os.putenv("GRASS_RENDER_WIDTH", str(options["width"]))
        os.putenv("GRASS_RENDER_HEIGHT", str(options["height"]))
        os.putenv("GRASS_RENDER_TRANSPARENT", "TRUE")
        os.putenv("GRASS_RENDER_TRUECOLOR", "TRUE")
        os.putenv("GRASS_RENDER_FILE", result_file)
        os.putenv("GRASS_RENDER_FILE_READ", "TRUE")

        if legacy is True:
            pc = {"module":"g.region","inputs":{},"flags":"g"}
            if options:
                for key in options:
                    if key in ["n", "s", "e", "w"]:
                        value = options[key]
                        pc["inputs"][key] = value
        else:
            pc = {"id": "2",
                  "module": "g.region",
                  "inputs": [],
                  "flags": "g"}
            if options:
                for key in options:
                    if key in ["n", "s", "e", "w"]:
                        value = options[key]
                        pc["inputs"].append({"param":key, "value":str(value)})

        return pc
