# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2018 Sören Gebbert and mundialis GmbH & Co. KG
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

"""The user specific resources

This module specifies all endpoints to manage user accounts
in the redis database via REST API calls.

TODO: Implement POST full permission creation
      Implement PUT to modify existing users
"""

from flask import jsonify, make_response, g
from flask_restful import reqparse
from flask_restful_swagger_2 import swagger
from actinia_api.swagger2.actinia_core.apidocs import user_management

from actinia_core.core.common.config import global_config
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.rest.base.base_login import LoginBase
from actinia_core.rest.base.user_auth import (
    check_admin_role,
    check_admin_role_or_own_userid,
)
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.core.common.app import auth
from actinia_core.core.common.user import ActiniaUser
from actinia_core.models.response_models import (
    UserListResponseModel,
    UserInfoResponseModel,
    SimpleResponseModel,
)


__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class UserListResource(LoginBase):
    """List all user in the database."""

    def __init__(self):
        LoginBase.__init__(self)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", user_management.user_list_get_doc))
    def get(self):
        """List all users in the database

        These methods work only if the
        authorized user has an admin role.

        Returns:
            flask.Response: A HTTP response with
                            JSON payload containing a list of users
        """
        if global_config.KEYCLOAK_CONFIG_PATH:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message="The keycloak authentication does not allow "
                        "to request all users",
                    )
                ),
                400,
            )

        user = ActiniaUser(None)
        user_list = user.list_all_users()

        return make_response(
            jsonify(
                UserListResponseModel(status="success", user_list=user_list)
            ),
            200,
        )


class UserManagementResource(LoginBase):
    """Get, Create and Delete a single user

    These methods work only if the
    authorized user has an admin role.

    Only normal users (role=user) can be created with this class.

    """

    # Authorization is required for all resources
    # API logging is required for all resources
    decorators = [log_api_call, auth.login_required]

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", user_management.user_get_doc))
    @check_admin_role_or_own_userid
    def get(self, user_id):
        """Return the credentials of a single user

        These methods work only if the
        authorized user has an admin role or requests the own user ID.

        Args:
            user_id (str): The unique name of the user

        Returns:
            flask.Response: A HTTP response with
                            JSON payload containing the credentials
                            of the user
        """
        if global_config.KEYCLOAK_CONFIG_PATH:
            user = g.user
            if user.user_id != user_id:
                return make_response(
                    jsonify(
                        SimpleResponseModel(
                            status="error",
                            message="The keycloak authentication does not "
                            "allow to request another user.",
                        )
                    ),
                    400,
                )
        else:
            user = ActiniaUser(user_id)
            if user.exists() != 1:
                return make_response(
                    jsonify(
                        SimpleResponseModel(
                            status="error",
                            message="User <%s> does not exist" % user_id,
                        )
                    ),
                    400,
                )

        credentials = user.get_credentials()

        return make_response(
            jsonify(
                UserInfoResponseModel(
                    status="success",
                    permissions=credentials["permissions"],
                    user_id=credentials["user_id"],
                    user_role=credentials["user_role"],
                    user_group=credentials["user_group"],
                )
            ),
            200,
        )

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", user_management.user_post_doc))
    @check_admin_role
    def post(self, user_id):
        """Create a user in the database

        These methods work only if the
        authorized user has an admin role.

        Args:
            user_id (str): The unique name of the user

        Returns:
            flask.Response: A HTTP response with
                            JSON payload containing
                            the status and messages
        """
        if global_config.KEYCLOAK_CONFIG_PATH:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message="The keycloak authentication does not allow "
                        "to create a new user",
                    )
                ),
                400,
            )

        user = ActiniaUser(user_id)

        if user.exists() == 1:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message="User <%s> already exists" % user_id,
                    )
                ),
                400,
            )

        # Password parser
        password_parser = reqparse.RequestParser()
        password_parser.add_argument(
            "password",
            required=True,
            type=str,
            location="args",
            dest="password",
            help="The password of the new user cannot be converted.",
        )
        password_parser.add_argument(
            "group",
            required=True,
            type=str,
            location="args",
            dest="group",
            help="The group of the new user cannot be converted.",
        )
        args = password_parser.parse_args()
        password = args["password"]
        group = args["group"]

        user = ActiniaUser.create_user(user_id, group, password, "user", {})
        if user is not None:
            if user.exists():
                return make_response(
                    jsonify(
                        SimpleResponseModel(
                            status="success",
                            message="User %s created" % user_id,
                        )
                    ),
                    201,
                )

        return make_response(
            jsonify(
                SimpleResponseModel(
                    status="error",
                    message="Unable to create user %s" % user_id,
                )
            ),
            400,
        )

    @endpoint_decorator()
    @swagger.doc(check_endpoint("delete", user_management.user_delete_doc))
    @check_admin_role
    def delete(self, user_id):
        """Delete a specific user

        These methods work only if the
        authorized user has an admin role.

        Args:
            user_id (str): The unique name of the user

        Returns:
            flask.Response: A HTTP response with
                            JSON payload containing
                            the status and messages
        """
        if global_config.KEYCLOAK_CONFIG_PATH:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message="The keycloak authentication does not allow "
                        "to delete a user",
                    )
                ),
                400,
            )

        user = ActiniaUser(user_id)

        if user.exists() != 1:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message=f"Unable to delete user {user_id}. User does "
                        "not exist.",
                    )
                ),
                400,
            )

        if user.delete() is True:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="success", message="User %s deleted" % user_id
                    )
                ),
                200,
            )

        return make_response(
            jsonify(
                SimpleResponseModel(
                    status="error",
                    message="Unable to delete user %s" % user_id,
                )
            ),
            400,
        )
