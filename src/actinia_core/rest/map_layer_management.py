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
Raster layer resources
"""
from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
import pickle
from actinia_api.swagger2.actinia_core.apidocs import map_layer_management

from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.core.request_parser import glist_parser
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.processing.common.map_layer_management import (
    list_raster_layers,
    remove_raster_layers,
    rename_raster_layers,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class MapsetLayersResource(ResourceBase):
    """Manage layers of a mapset"""

    def __init__(self, layer_type):
        ResourceBase.__init__(self)
        self.layer_type = layer_type

    def _get(self, project_name, mapset_name):
        """Return a collection of all available layers
        in the provided mapset.

        Optionally can g.list parameters be provided::

            http://<url>?pattern="*"

        Args:
            project_name (str): The name of the project
            mapset_name (str): The name of the mapset

        Return:
            flask.Response: HTTP 200 and a list of layers as JSON document in
                            case of success, HTTP 400 otherwise

        Example::

            {"Process result":
              [ "lsat7_2002_10",
                "lsat7_2002_20",
                "lsat7_2002_30",
                "lsat7_2002_40",
                "lsat7_2002_50",
                "lsat7_2002_61",
                "lsat7_2002_62",
                "lsat7_2002_70",
                "lsat7_2002_80"
              ],
              "Status": "success"
            }

        """
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
        )

        if rdc:
            args = glist_parser.parse_args()
            rdc.set_user_data((args, self.layer_type))
            enqueue_job(
                self.job_timeout,
                list_raster_layers,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    def _delete(self, project_name, mapset_name):
        """Remove a list of layers identified by a pattern

        The g.remove "pattern" parameters must be provided::

            http://<url>?pattern="*"

        Args:
            project_name (str): The name of the project
            mapset_name (str): The name of the mapset

        Return:
            flask.Response: HTTP 200 in case of success, HTTP 400 otherwise

        """
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
        )

        if rdc:
            args = glist_parser.parse_args()
            rdc.set_user_data((args, self.layer_type))
            enqueue_job(
                self.job_timeout,
                remove_raster_layers,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    def _put(self, project_name, mapset_name):
        """Rename a list of layers

        The old names and new names must be provided as a
        list of tuples:

            [(a, a_new),(b, b_new),(c, c_new), ...]

        Args:
            project_name (str): The name of the project
            mapset_name (str): The name of the mapset

        Return:
            flask.Response: HTTP 200 in case of success, HTTP 400 otherwise

        """
        rdc = self.preprocess(
            has_json=True,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
        )

        # Analyse the name list
        if isinstance(self.request_data, list) is False:
            return self.get_error_response(
                message="Wrong format for layer list"
            )

        if len(self.request_data) == 0:
            return self.get_error_response(message="Empty layer list")

        for name_tuple in self.request_data:
            if (
                isinstance(name_tuple, tuple) is False
                and isinstance(name_tuple, list) is False
            ):
                return self.get_error_response(
                    message="List entry is not a tuple or list"
                )

            if len(name_tuple) != 2:
                return self.get_error_response(
                    message="A tuple of layer names must have 2 entries"
                )

        if rdc:
            args = glist_parser.parse_args()
            rdc.set_user_data((args, self.layer_type))
            enqueue_job(self.job_timeout, rename_raster_layers, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)


class RasterLayersResource(MapsetLayersResource):
    """Manage raster layers of a mapset"""

    def __init__(self):
        MapsetLayersResource.__init__(self, layer_type="raster")

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", map_layer_management.raster_get_doc))
    def get(self, project_name, mapset_name):
        """Get a list of raster map layer names that are located in a specific
        project/mapset
        """
        return self._get(project_name, mapset_name)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("put", map_layer_management.raster_put_doc))
    def put(self, project_name, mapset_name):
        """Rename a single raster map layer or a list of raster map layers that
        are located in a specific project/mapset
        """
        return self._put(project_name, mapset_name)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint("delete", map_layer_management.raster_delete_doc)
    )
    def delete(self, project_name, mapset_name):
        """Delete a single raster map layer or a list of raster map layer names
        that are located in a specific project/mapset
        """
        return self._delete(project_name, mapset_name)


class VectorLayersResource(MapsetLayersResource):
    """Manage vector layers of a mapset"""

    def __init__(self):
        MapsetLayersResource.__init__(self, layer_type="vector")

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", map_layer_management.vector_get_doc))
    def get(self, project_name, mapset_name):
        """Get a list of vector map layer names that are located in a specific
        project/mapset
        """
        return self._get(project_name, mapset_name)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("put", map_layer_management.vector_put_doc))
    def put(self, project_name, mapset_name):
        """Rename a single vector map layer or a list of vector map layers that
        are located in a specific project/mapset
        """
        return self._put(project_name, mapset_name)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint("delete", map_layer_management.vector_delete_doc)
    )
    def delete(self, project_name, mapset_name):
        """Delete a single vector map layer or a list of vector map layer names
        that are located in a specific project/mapset
        """
        return self._delete(project_name, mapset_name)
