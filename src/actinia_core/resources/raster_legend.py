# -*- coding: utf-8 -*-
"""
Raster map renderer
"""

from flask import jsonify, make_response, Response
from flask_restful import reqparse
from .async_ephemeral_processing import AsyncEphemeralProcessing
from .async_resource_base import AsyncEphemeralResourceBase
from .common.redis_interface import enqueue_job
import tempfile
import os

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class SyncEphemeralRasterLegendResource(AsyncEphemeralResourceBase):
    """Render the raster legend with d.legend
    """
    def create_parser(self):
        # Create a legend parser
        parser = reqparse.RequestParser()
        parser.add_argument('at', type=str, location='args',
                            help='Size and placement as percentage of '
                                 'screen coordinates (0,0 is lower left). '
                                 'bottom,top,left,right 0-100%')
        parser.add_argument('range', type=str, location='args',
                            help='Use a subset of the map range for the legend (min,max)')
        parser.add_argument('use', type=str, location='args',
                            help='List of discrete category numbers/values for legend')
        parser.add_argument('fontsize', type=float, location='args',
                            help='Size of the font 1-360')
        parser.add_argument('labelnum', type=float, location='args',
                            help='Number of text labels for smooth gradient legend')
        parser.add_argument('width', type=float, location='args',
                            help='North-South resolution must be specified as double value')
        parser.add_argument('height', type=float, location='args',
                            help='East-West resolution must be specified as double value')

        return parser

    def create_parser_options(self, args):
        """Parse the request parameters for raster legends

        Args:
            args (dict): The argument dictionary with display options

        Returns:
             dict:
             A dictionary of display parameter or an error response in case of an error
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
                return self.get_error_response(message="Width must be larger than 0")
            if args["width"] > 10000:
                return self.get_error_response(message="Width can not be larger than 10000")
            options["width"] = args["width"]
        if "height" in args and args["height"] is not None:
            if args["height"] < 1:
                return self.get_error_response(message="Height must be larger than 0")
            if args["height"] > 10000:
                return self.get_error_response(message="Height can not be larger than 10000")
            options["height"] = args["height"]

        return options

    def get(self, location_name, mapset_name, raster_name):
        """Render the raster legend with d.legend

        Args:
            location_name: Name of the location
            mapset_name: Name of the mapset
            raster_name: name of the raster map

        Returns:
            flask.Response:
            HTTP 200 with image/png content in case of success, HTTP 400 otherwise

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


def start_job(*args):
    processing = AsyncEphemeralRasterLegend(*args)
    processing.run()


class AsyncEphemeralRasterLegend(AsyncEphemeralProcessing):

    def __init__(self, *args):

        AsyncEphemeralProcessing.__init__(self, *args)

    def _execute(self, skip_permission_check=True):
        """Render the raster legend with d.legend
        """
        self._setup()

        self.required_mapsets.append(self.mapset_name)
        raster_name = self.map_name

        options = self.rdc.user_data

        result_file = tempfile.mktemp(suffix=".png")

        os.putenv("GRASS_RENDER_IMMEDIATE", "png")
        os.putenv("GRASS_RENDER_WIDTH", str(options["width"]))
        os.putenv("GRASS_RENDER_HEIGHT", str(options["height"]))
        os.putenv("GRASS_RENDER_TRANSPARENT", "TRUE")
        os.putenv("GRASS_RENDER_TRUECOLOR", "TRUE")
        os.putenv("GRASS_RENDER_FILE", result_file)
        os.putenv("GRASS_RENDER_FILE_READ", "TRUE")

        pc = {}
        pc["1"] = {"module":"d.legend","inputs":{"raster":raster_name + "@" + self.mapset_name}}
        for key in options:
            if key not in ["width", "height"]:
                value = options[key]
                pc["1"]["inputs"][key] = value

        process_list = self._create_temporary_grass_environment_and_process_list(process_chain=pc,
                                                                                 skip_permission_check=True)
        self._execute_process_list(process_list)

        self.module_results = result_file
