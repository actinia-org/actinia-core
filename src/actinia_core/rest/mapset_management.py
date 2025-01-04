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
Mapset management resources

* List all mapsets
* Create mapset, Delete mapset, Get info about a mapset
* Lock mapset, unlock mapset, get mapset lock status
"""

from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
import pickle
from actinia_api.swagger2.actinia_core.apidocs import mapset_management

from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.core.common.app import auth
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.rest.base.user_auth import check_user_permissions
from actinia_core.rest.base.user_auth import check_admin_role, check_user_role
from actinia_core.processing.common.mapset_management import (
    list_raster_mapsets,
    read_current_region,
    create_mapset,
    delete_mapset,
    get_mapset_lock,
    lock_mapset,
    unlock_mapset,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Julia Haas, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class ListMapsetsResource(ResourceBase):
    """List all mapsets in a project"""

    layer_type = None

    # @check_queue_type_overwrite()
    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", mapset_management.get_doc))
    def get(self, project_name):
        """
        Get a list of all mapsets that are located in a specific project.
        """
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name="PERMANENT",
        )
        if rdc:
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


class MapsetManagementResourceUser(ResourceBase):
    """This class returns information about a mapset"""

    def __init__(self):
        ResourceBase.__init__(self)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", mapset_management.get_user_doc))
    def get(self, project_name, mapset_name):
        """
        Get the current computational region of the mapset and the projection
        of the project as WKT string.
        """
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
        )

        enqueue_job(
            self.job_timeout,
            read_current_region,
            rdc,
            queue_type_overwrite=True,
        )
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


class MapsetManagementResourceAdmin(ResourceBase):
    """This class manages the creation, deletion and modification of mapsets

    This is allowed for administrators and users
    """

    decorators = [
        log_api_call,
        check_user_permissions,
        check_user_role,
        auth.login_required,
    ]

    def __init__(self):
        ResourceBase.__init__(self)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", mapset_management.post_user_doc))
    def post(self, project_name, mapset_name):
        """Create a new mapset in an existing project."""
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
        )

        enqueue_job(self.job_timeout, create_mapset, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    def put(self, project_name, mapset_name):
        """Modify the region of a mapset

        TODO: Implement region setting

        Args:
            project_name (str): Name of the project
            mapset_name (str): Name of the mapset

        Returns:
            flaks.Response:
            HTTP 200 and JSON document in case of success, HTTP 400 otherwise

        """
        pass

    @endpoint_decorator()
    @swagger.doc(check_endpoint("delete", mapset_management.delete_user_doc))
    def delete(self, project_name, mapset_name):
        """Delete an existing mapset"""
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
        )

        enqueue_job(
            self.job_timeout, delete_mapset, rdc, queue_type_overwrite=True
        )
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


class MapsetLockManagementResource(ResourceBase):
    """Lock a mapset"""

    decorators = [
        log_api_call,
        check_user_permissions,
        check_admin_role,
        auth.login_required,
    ]

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", mapset_management.get_lock_doc))
    def get(self, project_name, mapset_name):
        """Get the project/mapset lock status."""
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
        )

        enqueue_job(
            self.job_timeout, get_mapset_lock, rdc, queue_type_overwrite=True
        )
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", mapset_management.post_lock_doc))
    def post(self, project_name, mapset_name):
        """Create a project/mapset lock."""
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
        )

        enqueue_job(self.job_timeout, lock_mapset, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("delete", mapset_management.delete_lock_doc))
    def delete(self, project_name, mapset_name):
        """Delete a project/mapset lock."""
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
        )

        enqueue_job(
            self.job_timeout, unlock_mapset, rdc, queue_type_overwrite=True
        )
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)
