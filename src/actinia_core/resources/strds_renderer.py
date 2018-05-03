# -*- coding: utf-8 -*-
"""
Raster map renderer

"""

from flask import jsonify, make_response, Response
from .ephemeral_processing import EphemeralProcessing
from .common.redis_interface import enqueue_job
from .renderer_base import RendererBaseResource, EphemeralRendererBase
import tempfile
import os
from flask_restful_swagger_2 import swagger
from .common.response_models import ProcessingResponseModel

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class SyncEphemeralSTRDSRendererResource(RendererBaseResource):
    """Render a list of raster images with g.region/d.rast.multi approach synchronously
    """

    @swagger.doc({
        'tags': ['strds rendering'],
        'description': 'Render the raster map layer of a STRDS. Minimum required user role: user.',
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
                'description': 'The name of the mapset that contains the required raster map layer',
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
                'description': 'Raster map layers that have equal or greater the start time will be rendered',
                'required': False,
                'in': 'query',
                'type': 'string'
            },
            {
                'name': 'end_time',
                'description': 'Raster map layers that have equal or lower the end time will be rendered',
                'required': False,
                'in': 'query',
                'type': 'string'
            }
        ],
        'produces':["image/png"],
        'responses': {
            '200': {
                'description': 'The PNG image'},
            '400': {
                'description':'The error message and a detailed log why rendering did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name, strds_name):
        """Render a raster image with g.region/d.rast approach
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


def start_job(*args):
    processing = EphemeralSTRDSRenderer(*args)
    processing.run()


class EphemeralSTRDSRenderer(EphemeralRendererBase):

    def __init__(self, *args):

        EphemeralProcessing.__init__(self, *args)

    def _execute(self, skip_permission_check=True):
        """Render the raster map layers of a STRDS

        Workflow:

            1. A list of raster map layers is generated from a t.rast.list call that can be
               constrained with time and region settings
            1. The default region is set to the the cumulative raster layer regions
            2. User specific region settings are applied
            3. d.rast.multi is invoked to create the PNG file

        """

        self._setup()

        strds_name = self.map_name
        options = self.rdc.user_data
        self.required_mapsets.append(self.mapset_name)

        result_file = tempfile.mktemp(suffix=".png")

        g_region_query = self._setup_render_environment_and_region(options=options,
                                                                   result_file=result_file,
                                                                   legacy=False)
        where_list = []

        if "start_time" in options :
            where_list.append("start_time >= \'%s\'"%options["start_time"])
        if "end_time" in options:
            where_list.append("end_time  <= \'%s\'"%options["end_time"])
        if "n" in options:
            where_list.append("south <= %f"%options["n"])
        if "s" in options:
            where_list.append("north >= %f"%options["s"])
        if "e" in options:
            where_list.append("west <= %f"%options["e"])
        if "w" in options:
            where_list.append("east >= %f"%options["w"])

        where = " AND ".join(where_list)

        t_rast_list = {"id": "1",
                       "module": "t.rast.list",
                       "inputs": [{"param":"input", "value":"%s@%s"%(strds_name, self.mapset_name)},
                                  {"param":"method", "value":"comma"},
                                  {"param":"where", "value":where}]}

        pc = {
            "version":1,
            "list": []
        }
        pc["list"].append(t_rast_list)
        # Run the selected modules
        self.skip_region_check = True
        process_chain = self._create_temporary_grass_environment_and_process_list(process_chain=pc,
                                                                                  skip_permission_check=True)
        self._execute_process_list(process_chain)

        map_list = self.module_output_log[0]["stdout"].strip()

        g_region = {"id": "2",
                    "module": "g.region",
                    "inputs": [{"param":"raster", "value":map_list}],
                    "flags":"p"}

        g_region_query["id"] = "3"
        g_region_query["flags"] = "g"

        pc = {
            "version":1,
            "list": []
        }
        pc["list"].append(g_region)
        pc["list"].append(g_region_query)

        process_list = self._validate_process_chain(process_chain=pc, skip_permission_check=True)
        self._execute_process_list(process_list)

        # Compute the cell size for visualization
        region_settings = self.module_output_log[2]["stdout"].strip()
        param_list = region_settings.split()
        n = 0
        s = 0
        e = 0
        w = 0
        for param in param_list:
            if "n=" == param[:2]:
                n = float(param.split("=")[1])
            if "s=" == param[:2]:
                s = float(param.split("=")[1])
            if "e=" == param[:2]:
                e = float(param.split("=")[1])
            if "w=" == param[:2]:
                w = float(param.split("=")[1])

        width = float(options["width"])
        height = float(options["height"])

        ewres = abs(e - w)/width
        nsres = abs(n - s)/height

        g_region_adjust = {"id": "4",
                           "module": "g.region",
                           "inputs": [{"param":"ewres", "value":"%f"%ewres},
                                      {"param":"nsres", "value":"%f"%nsres}],
                           "flags":"g"}

        d_rast = {"id": "6",
                  "module": "d.rast.multi",
                  "inputs": [{"param":"map", "value":map_list}]}

        pc = {
            "version":1,
            "list": []
        }
        pc["list"].append(g_region_adjust)
        pc["list"].append(d_rast)

        process_list = self._validate_process_chain(process_chain=pc, skip_permission_check=True)
        self._execute_process_list(process_list)

        self.module_results = result_file
