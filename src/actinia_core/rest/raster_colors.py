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
Raster colors management

TODO: Maybe more tests required, test_raster_colors.py is in place and works
"""

from flask_restful_swagger_2 import swagger
from flask import jsonify, make_response
from actinia_api.swagger2.actinia_core.apidocs import raster_colors

from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.processing.common.raster_colors import start_job_colors_out
from actinia_core.processing.common.raster_colors import start_job_from_rules

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class SyncPersistentRasterColorsResource(ResourceBase):
    """Manage the color table"""

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", raster_colors.get_doc))
    def get(self, project_name, mapset_name, raster_name):
        """Get the color definition of an existing raster map layer.

        Args:
            project_name: Name of the project
            mapset_name: Name of the mapset
            raster_name: name of the raster map

        """
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=raster_name,
        )

        enqueue_job(
            self.job_timeout,
            start_job_colors_out,
            rdc,
            queue_type_overwrite=True,
        )
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", raster_colors.post_doc))
    def post(self, project_name, mapset_name, raster_name):
        """Set the color definition for an existing raster map layer.

        The JSON input should contain the color rules, a predefined color table
        or a raster layer:

            {"rules":["1 0:0:0", "default 255:255:255"]}
            {"color":"gbr"}
            {"raster":"elevation"}


        Args:
            project_name: Name of the project
            mapset_name: Name of the mapset
            raster_name: name of the raster map

        Raises:
            InvalidUsage in case the color definition is false

        """
        rdc = self.preprocess(
            has_json=True,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=raster_name,
        )

        if isinstance(self.request_data, dict) is False:
            return self.get_error_response(
                message="Missing raster color definition in JSON content"
            )

        if len(self.request_data) > 1:
            return self.get_error_response(
                message="The color settings expect a single entry"
            )

        if "rules" in self.request_data:
            if isinstance(self.request_data["rules"], list) is False:
                return self.get_error_response(
                    message="Wrong rules definitions in JSON content"
                )
        elif "color" in self.request_data:
            pass
        elif "raster" in self.request_data:
            if "@" not in self.request_data["raster"]:
                return self.get_error_response(
                    message="Missing mapset definition in raster name"
                )
        else:
            return self.get_error_response(
                message="Missing raster color definitions in JSON content"
            )

        enqueue_job(self.job_timeout, start_job_from_rules, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)
