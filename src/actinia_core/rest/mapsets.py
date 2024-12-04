# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2021-2024 mundialis GmbH & Co. KG
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
Mapset resources for information across all projects

* List all mapset locks
* List all mapsets in all projects available to a user
"""

from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
from flask import request
from actinia_api.swagger2.actinia_core.apidocs import mapsets

from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.rest.base.user_auth import check_user_permissions

# from actinia_core.rest.base.user_auth import check_admin_role
from actinia_core.core.common.app import auth
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.core.common.config import global_config
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.core.redis_lock import RedisLockingInterface
from actinia_core.core.redis_user import RedisUserInterface
from actinia_core.models.response_models import (
    SimpleResponseModel,
    MapsetListResponseModel,
    LockedMapsetListResponseModel,
)


__license__ = "GPLv3"
__author__ = "Julia Haas, Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2021-2024 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class AllMapsetsListingResourceAdmin(ResourceBase):
    """Get all locked mapsets"""

    decorators = [log_api_call, check_user_permissions, auth.login_required]

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", mapsets.get_doc))
    def get(self):
        if "status" in request.args:
            if request.args["status"] == "locked":
                if self.user.has_superadmin_role() is False:
                    return make_response(
                        jsonify(
                            SimpleResponseModel(
                                status="error",
                                message=(
                                    "Unable to list locked mapsets You are not"
                                    " authorized for this request. "
                                    "Minimum required user role: superadmin"
                                ),
                            )
                        ),
                        401,
                    )
                redis_interface = RedisLockingInterface()
                kwargs = dict()
                kwargs["host"] = global_config.REDIS_SERVER_URL
                kwargs["port"] = global_config.REDIS_SERVER_PORT
                if (
                    global_config.REDIS_SERVER_PW
                    and global_config.REDIS_SERVER_PW is not None
                ):
                    kwargs["password"] = global_config.REDIS_SERVER_PW

                redis_interface.connect(**kwargs)
                redis_connection = redis_interface.redis_server
                keys_locked = redis_connection.keys("RESOURCE-LOCK*")
                redis_interface.disconnect()
                keys_locked_dec = [key.decode() for key in keys_locked]
                mapsets_locked = [
                    "/".join(key.split("/")[-2:]) for key in keys_locked_dec
                ]
                try:
                    return make_response(
                        jsonify(
                            LockedMapsetListResponseModel(
                                status="success",
                                message="number of locked mapsets: %s"
                                % len(mapsets_locked),
                                locked_mapsets_list=mapsets_locked,
                            )
                        ),
                        200,
                    )

                except Exception as e:
                    return make_response(
                        jsonify(
                            SimpleResponseModel(
                                status="error",
                                message="Unable to list locked mapsets: "
                                f"Exception {e}",
                            )
                        ),
                        500,
                    )
        else:
            redis_interface = RedisUserInterface()
            kwargs = dict()
            kwargs["host"] = global_config.REDIS_SERVER_URL
            kwargs["port"] = global_config.REDIS_SERVER_PORT
            if (
                global_config.REDIS_SERVER_PW
                and global_config.REDIS_SERVER_PW is not None
            ):
                kwargs["password"] = global_config.REDIS_SERVER_PW
            redis_interface.connect(**kwargs)
            if "user" in request.args:
                user = request.args["user"]
                if self.user.has_superadmin_role() is False:
                    redis_interface.disconnect()
                    return make_response(
                        jsonify(
                            SimpleResponseModel(
                                status="error",
                                message=(
                                    f"Unable to list mapsets for user {user}: "
                                    "You are not authorized for this request. "
                                    "Minimum required user role: superadmin"
                                ),
                            )
                        ),
                        401,
                    )
            else:
                user = self.user.get_id()
            projects_mapsets = redis_interface.get_credentials(user)[
                "permissions"
            ]["accessible_datasets"]
            redis_interface.disconnect()
            mapsets = []
            for project in projects_mapsets:
                for mapset in projects_mapsets[project]:
                    mapsets.append(f"{project}/{mapset}")
            try:
                return make_response(
                    jsonify(
                        MapsetListResponseModel(
                            status="success",
                            available_mapsets=mapsets,
                        )
                    ),
                    200,
                )

            except Exception as e:
                return make_response(
                    jsonify(
                        SimpleResponseModel(
                            status="error",
                            message=f"Unable to list mapsets: Exception {e}",
                        )
                    ),
                    500,
                )
