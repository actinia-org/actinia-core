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
STRDS raster map layer management

TODO: Integrate into the ephemeral process chain approach
"""
from flask_restful_swagger_2 import swagger
from flask import jsonify, make_response
import pickle
from actinia_api.swagger2.actinia_core.apidocs import strds_raster_management

from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.request_parser import where_parser
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.processing.common.strds_raster_management import (
    unregister_raster,
    register_raster,
    list_raster_strds,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class STRDSRasterManagement(ResourceBase):
    """Manage raster layer in a space time raster dataset"""

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", strds_raster_management.get_doc))
    def get(self, project_name, mapset_name, strds_name):
        """
        Get a list of all raster map layers that are registered in a STRDS
        """
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=strds_name,
        )

        if rdc:
            args = where_parser.parse_args()
            rdc.set_user_data(args)

            enqueue_job(
                self.job_timeout,
                list_raster_strds,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("put", strds_raster_management.put_doc))
    def put(self, project_name, mapset_name, strds_name):
        """Register raster map layers in a STRDS located in a specific
        project/mapset.
        """
        rdc = self.preprocess(
            has_json=True,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=strds_name,
        )

        if rdc:
            enqueue_job(self.job_timeout, register_raster, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("delete", strds_raster_management.delete_doc))
    def delete(self, project_name, mapset_name, strds_name):
        """
        Unregister raster map layers from a STRDS located in a specific
        project/mapset.
        """
        rdc = self.preprocess(
            has_json=True,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=strds_name,
        )

        if rdc:
            enqueue_job(
                self.job_timeout,
                unregister_raster,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)
