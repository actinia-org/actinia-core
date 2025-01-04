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
from flask import jsonify, make_response, Response
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.renderer_base import RendererBaseResource
import os
from flask_restful_swagger_2 import swagger
from actinia_api.swagger2.actinia_core.apidocs import strds_renderer

from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.processing.common.strds_renderer import start_job

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class SyncEphemeralSTRDSRendererResource(RendererBaseResource):
    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", strds_renderer.get_doc))
    def get(self, project_name, mapset_name, strds_name):
        """
        Render the raster map layers of a specific STRDS as a single image.
        """
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
            map_name=strds_name,
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
