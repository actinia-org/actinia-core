# -*- coding: utf-8 -*-
"""
Raster layer resources
"""
from flask_restful_swagger_2 import swagger, Schema

from flask_restful import reqparse
from .async_resource_base import AsyncEphemeralResourceBase

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class SetRegionModel(Schema):
    """This schema represents the computational region definition for raster
     and vector map layers.

        n : for north
        s : for south
        e : for east
        w : for west
        res : resolution of the region
        ewres: east-west resolution
        nsres: north-south resolution
        raster: Raster layer name with mapset to set the region from
        align: Raster layer name with mapset to align the region to
        zoom: Raster layer name with mapset to zoom the region to
        vector: Vector layer name with mapset to set the region from

    """
    type = 'object'
    properties = {
        'region': {
            'type': 'string',
            'description': 'Set current region from named region'
        },
        'raster': {
            'type': 'string',
            'description': 'Raster layer name with mapset to set the region from'
        },
        'align': {
            'type': 'string',
            'description': 'Raster layer name with mapset to align the region to'
        },
        'zoom': {
            'type': 'string',
            'description': 'Raster layer name with mapset to zoom the region to'
        },
        'vector': {
            'type': 'string',
            'description': 'Vector layer name with mapset to set the region from'
        },
        'n': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the northern edge'
        },
        's': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the southern edge'
        },
        'w': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the western edge'
        },
        'e': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the eastern edge'
        },
        't': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the top edge'
        },
        'b': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the bottom edge'
        },
        'nsres': {
            'type': 'number',
            'format': 'double',
            'description': 'North-south 2D grid resolution'
        },
        'res': {
            'type': 'number',
            'format': 'double',
            'description': '2D grid resolution (north-south and east-west)'
        },
        'ewres': {
            'type': 'number',
            'format': 'double',
            'description': 'East-west 2D grid resolution'
        },
        'res3': {
            'type': 'number',
            'format': 'double',
            'description': '3D grid resolution (north-south, east-west and top-bottom)'
        },
        'tbres': {
            'type': 'number',
            'format': 'double',
            'description': 'Top-bottom 3D grid resolution'
        }
    }


class MapLayerRegionResourceBase(AsyncEphemeralResourceBase):
    """The base class for map layer (raster, vector) resources that make use of region settings
    """

    def create_parser(self):
        """Create the g.region option arguments

        The parameter contain:

            n : for north
            s : for south
            e : for east
            w : for west
            res : resolution of the region
            ewres: east-west resolution
            nsres: north-south resolution
            raster: Raster layer name with mapset to set the region from
            align: Raster layer name with mapset to align the region to
            zoom: Raster layer name with mapset to zoom the region to
            vector: Vector layer name with mapset to set the region from

        Returns:
            The argument parser

        """
        parser = reqparse.RequestParser()
        parser.add_argument('n', type=float, help='Northern border must be specified as double value')
        parser.add_argument('e', type=float, help='Eastern border must be specified as double value')
        parser.add_argument('w', type=float, help='Western border must be specified as double value')
        parser.add_argument('s', type=float, help='Southern border must be specified as double value')
        parser.add_argument('res', type=float, help='Resolution must be specified as double value')
        parser.add_argument('nsres', type=float, help='North-South resolution must be specified as double value')
        parser.add_argument('ewres', type=float, help='East-West resolution must be specified as double value')
        parser.add_argument('raster', type=str, help='The raster layer name from which the region should be used, with mapset information: name@mapset')
        parser.add_argument('align', type=str, help='The raster layer name from which the region should be aligned, with mapset information: name@mapset')
        parser.add_argument('zoom', type=str, help='The raster layer name to which the region should be zoomed, with mapset information: name@mapset')
        parser.add_argument('vector', type=str, help='The vector layer name from which the region should be used, with mapset information: name@mapset')

        return parser

    def create_parser_options(self, args):
        """Parse the request parameters for g.region from parsed arguments
        that were created with the create_parser.

        Args:
            args (dict): The argument dictionary with g.region options

        Returns:
             dict:
             A dict of g.region parameter
        """
        options = {}
        if "n" in args and args["n"] is not None:
            options["n"] = args["n"]
        if "s" in args and args["s"] is not None:
            options["s"] = args["s"]
        if "e" in args and args["e"] is not None:
            options["e"] = args["e"]
        if "w" in args and args["w"] is not None:
            options["w"] = args["w"]

        if "res" in args and args["res"] is not None:
            options["res"] = args["res"]
            if options["res"] < 0:
                return self.get_error_response(message="Resolution can not be negative")

        if "nsres" in args and args["nsres"] is not None:
            options["nsres"] = args["nsres"]
            if options["nsres"] < 0:
                return self.get_error_response(message="North-south resolution can not be negative")

        if "ewres" in args and args["ewres"] is not None:
            options["ewres"] = args["ewres"]
            if options["ewres"] < 0:
                return self.get_error_response(message="East-west resolution can not be negative")

        if "raster" in args and args["raster"] is not None:
            options["raster"] = args["raster"]
            if "@" not in args["raster"]:
                return self.get_error_response(message="The raster layer to set the region from must "
                                                       "contain the mapset: name@mapset")

        if "align" in args and args["align"] is not None:
            options["align"] = args["align"]
            if "@" not in args["align"]:
                return self.get_error_response(message="The raster layer to align the region from must "
                                                       "contain the mapset: name@mapset")

        if "zoom" in args and args["zoom"] is not None:
            options["zoom"] = args["zoom"]
            if "@" not in args["zoom"]:
                return self.get_error_response(message="The raster layer to zoom the region to must "
                                                       "contain the mapset: name@mapset")

        if "vector" in args and args["vector"] is not None:
            options["vector"] = args["vector"]
            if "@" not in args["vector"]:
                return self.get_error_response(message="The vector layer to set the region from must "
                                                       "contain the mapset: name@mapset")

        return options
