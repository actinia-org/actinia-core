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
STRDS map layer management

TODO: Integrate into the ephemeral process chain approach
"""
import pickle
from flask import jsonify, make_response
from flask_restful import reqparse
from flask_restful_swagger_2 import swagger
from actinia_api.swagger2.actinia_core.apidocs import strds_management

from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.core.request_parser import where_parser
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.processing.common.strds_management import (
    list_raster_mapsets,
    strds_create,
    strds_delete,
    strds_info,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class SyncSTRDSListerResource(ResourceBase):
    """List all STRDS in a project/mapset"""

    layer_type = None

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", strds_management.list_get_doc))
    def get(self, project_name, mapset_name):
        """
        Get a list of all STRDS that are located in a specific project/mapset.
        """
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
        )

        if rdc:
            args = where_parser.parse_args()
            rdc.set_user_data(args)

            enqueue_job(
                self.job_timeout,
                list_raster_mapsets,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)


"""
STRDS Management
"""

recursive_parser = reqparse.RequestParser()
recursive_parser.add_argument(
    "recursive",
    type=bool,
    help="Set True to recursively remove the STRDS and all registered raster "
    "map layer",
    location="args",
)


class STRDSManagementResource(ResourceBase):
    """List all STRDS in a project/mapset"""

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", strds_management.get_doc))
    def get(self, project_name, mapset_name, strds_name):
        """
        Get information about a STRDS that is located in a specific
        project/mapset.
        """
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=strds_name,
        )
        if rdc:
            enqueue_job(
                self.job_timeout, strds_info, rdc, queue_type_overwrite=True
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("delete", strds_management.delete_doc))
    def delete(self, project_name, mapset_name, strds_name):
        """Delete a STRDS that is located in a specific project/mapset."""
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=strds_name,
        )

        if rdc:
            args = recursive_parser.parse_args()
            rdc.set_user_data(args)

            enqueue_job(
                self.job_timeout, strds_delete, rdc, queue_type_overwrite=True
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", strds_management.post_doc))
    def post(self, project_name, mapset_name, strds_name):
        """Create a new STRDS in a specific project/mapset."""
        rdc = self.preprocess(
            has_json=True,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=strds_name,
        )

        if rdc:
            enqueue_job(self.job_timeout, strds_create, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)
