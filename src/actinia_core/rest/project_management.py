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
Location management

TODO: Integrate into the ephemeral process chain approach
"""

from flask import jsonify, make_response
import os
import shutil
import pickle
from flask_restful_swagger_2 import swagger
from actinia_api.swagger2.actinia_core.apidocs import location_management
from actinia_api.swagger2.actinia_core.schemas.location_management import (
    LocationListResponseModel,
)

from actinia_core.core.common.app import auth
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.rest.base.user_auth import check_user_role
from actinia_core.rest.base.user_auth import check_user_permissions
from actinia_core.models.response_models import SimpleResponseModel
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.utils import ensure_valid_path
from actinia_core.processing.common.project_management import (
    read_current_region,
    create_project,
)
from actinia_core.version import G_VERSION

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class ListProjectsResource(ResourceBase):
    """This resource represents GRASS GIS database directory
    that contains projects.
    """

    def __init__(self):
        ResourceBase.__init__(self)

    """
    Return a list of all available projects that are located in the GRASS
    database
    """
    layer_type = None

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", location_management.get_doc))
    def get(self):
        """Get a list of all available projects"""
        projects = []

        if os.path.isdir(self.grass_data_base):
            dirs = os.listdir(self.grass_data_base)
            for dir in dirs:
                dir_path = os.path.join(self.grass_data_base, dir)
                if os.path.isdir(dir_path) and os.access(
                    dir_path, os.R_OK & os.X_OK
                ):
                    # Check for PERMANENT mapset existence
                    mapset_path = os.path.join(dir_path, "PERMANENT")
                    if os.path.isdir(mapset_path) and os.access(
                        mapset_path, os.R_OK & os.X_OK
                    ):
                        # Check access rights to the global database
                        # Super admin can see all projects
                        if (
                            self.has_superadmin_role
                            or dir
                            in self.user_credentials["permissions"][
                                "accessible_datasets"
                            ]
                        ):
                            projects.append(dir)
        # List all projects in the user database
        user_database = os.path.join(
            self.grass_user_data_base, self.user_group
        )
        if os.path.isdir(user_database):
            dirs = os.listdir(user_database)
            for dir in dirs:
                dir_path = os.path.join(user_database, dir)
                if os.path.isdir(dir_path) and os.access(
                    dir_path, os.R_OK & os.X_OK
                ):
                    # Check for PERMANENT mapset existence
                    mapset_path = os.path.join(dir_path, "PERMANENT")
                    if os.path.isdir(mapset_path) and os.access(
                        mapset_path, os.R_OK & os.X_OK
                    ):
                        projects.append(dir)
        if projects:
            param = {"status": "success"}
            grass_version_s = G_VERSION["version"]
            grass_version = [
                int(item) for item in grass_version_s.split(".")[:2]
            ]
            if grass_version >= [8, 4]:
                param["projects"] = projects
            else:
                param["locations"] = projects
            return make_response(
                jsonify(LocationListResponseModel(**param)),
                200,
            )
        else:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message="Unable to access GRASS database.",
                    )
                ),
                405,
            )


class ProjectManagementResourceUser(ResourceBase):
    """This class returns information about a specific project"""

    def __init__(self):
        ResourceBase.__init__(self)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", location_management.get_user_doc))
    def get(self, project_name):
        """
        Get the project projection and current computational region of the
        PERMANENT mapset
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
                read_current_region,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)


class ProjectManagementResourceAdminUser(ResourceBase):
    """This class manages the creation, deletion and modification of projects

    This is only allowed for administrators and users
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
    @swagger.doc(check_endpoint("delete", location_management.delete_user_doc))
    def delete(self, project_name):
        """
        Delete an existing project and everything inside from the user
        database.
        """
        # Delete only projects from the user database
        project = ensure_valid_path(
            [self.grass_user_data_base, self.user_group, project_name]
        )
        permanent_mapset = ensure_valid_path([project, "PERMANENT"])
        wind_file = ensure_valid_path([permanent_mapset, "WIND"])
        # Check the project path, only "valid" projects can be deleted
        if os.path.isdir(project):
            if os.path.isdir(permanent_mapset) and os.path.isfile(wind_file):
                try:
                    shutil.rmtree(project)
                    return make_response(
                        jsonify(
                            SimpleResponseModel(
                                status="success",
                                message="Project %s deleted" % project_name,
                            )
                        ),
                        200,
                    )
                except Exception as e:
                    return make_response(
                        jsonify(
                            SimpleResponseModel(
                                status="error",
                                message="Unable to delete project "
                                f"{project_name} Exception {e}",
                            )
                        ),
                        500,
                    )

        return make_response(
            jsonify(
                SimpleResponseModel(
                    status="error",
                    message="Project %s does not exists" % project_name,
                )
            ),
            400,
        )

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", location_management.post_user_doc))
    def post(self, project_name):
        """Create a new project based on EPSG code in the user database."""
        # Create only new projects if they did not exist in the global
        # database
        project = ensure_valid_path([self.grass_data_base, project_name])

        # Check the project path
        if os.path.isdir(project):
            return self.get_error_response(
                message="Unable to create project. "
                "Location <%s> exists in global database." % project_name
            )

        # Check also for the user database
        project = ensure_valid_path(
            [self.grass_user_data_base, self.user_group, project_name]
        )
        # Check the project path
        if os.path.isdir(project):
            return self.get_error_response(
                message="Unable to create project. "
                "Location <%s> exists in user database." % project_name
            )

        rdc = self.preprocess(
            has_json=True,
            has_xml=False,
            project_name=project_name,
            mapset_name="PERMANENT",
        )
        if rdc:
            enqueue_job(self.job_timeout, create_project, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)
