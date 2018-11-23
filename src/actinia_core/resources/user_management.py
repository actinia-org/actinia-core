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
from .base_login import LoginBase
from .common.user import ActiniaUser
from .common.app import auth
from .common.logging_interface import log_api_call

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class UserListResource(LoginBase):
    """List all user in the database.
    """

    def __init__(self):
        LoginBase.__init__(self)

    def get(self):
        """List all users in the database

        These methods work only if the
        authorized user has an admin role.

        Returns:
            flask.Response: A HTTP response with
                            JSON payload containing a list of users

            A HTTP status 200 response JSON content::

                {
                  "Status": "success",
                  "User list": [
                    "soeren"
                  ]
                }

        """
        user = ActiniaUser(None)
        user_list = user.list_all_users()

        return make_response(jsonify({"Status":"success",
                                      "User list":user_list}))

class UserManagementResource(LoginBase):
    """Get, Create and Delete a single user

    These methods work only if the
    authorized user has an admin role.

    Only normal users (role=user) can be created with this class.

    """

    def __init__(self):
        LoginBase.__init__(self)

    def get(self, user_id):
        """Return the credentials of a single user

        These methods work only if the
        authorized user has an admin role.

        Args:
            user_id (str): The unique name of the user

        Returns:
            flask.Response: A HTTP response with
                            JSON payload containing the credentials
                            of the user

            A HTTP status 200 response JSON content::

                {
                  "Permissions": {
                    "accessible_datasets": {
                      "nc_spm_08": [
                        "PERMANENT",
                        "user1",
                        "landsat"
                      ]
                    },
                    "accessible_modules": [
                      "r.blend",
                       ...
                      "g.findfile",
                      "g.gisenv"
                    ],
                    "cell_limit": 100000000,
                    "process_num_limit": 5,
                    "process_time_limit": 60
                  },
                  "Status": "success",
                  "User id": "soeren",
                  "User role": "admin"
                }

            A HTTP status 400 response JSON content::

                {
                  "Messages": "User <unknown_user_name> does not exist",
                  "Status": "error"
                }

        """
        user = ActiniaUser(user_id)

        if user.exists() is False:
            return make_response(jsonify({"Status":"error",
                                          "Messages":"User <%s> does not exist"%user_id}), 400)

        credentials = user.get_credentials()

        return make_response(jsonify({"Status":"success",
                                      "User id":credentials["user_id"],
                                      "User role":credentials["user_role"],
                                      "User group":credentials["user_group"],
                                      "Permissions":credentials["permissions"]}))

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

            A HTTP status 200 response JSON content::

                {
                  "Messages:": "User thomas created",
                  "Status": "success"
                }

            A HTTP status 400 response JSON content::

                {
                  "Messages": "Unable to create user thomas",
                  "Status": "error"
                }

        """
        # Password parser
        password_parser = reqparse.RequestParser()
        password_parser.add_argument('password', required=True,
                                     type=str, help='The password of the new user')
        password_parser.add_argument('group', required=True,
                                     type=str, help='The group of the new user')

        args = password_parser.parse_args()
        password = args["password"]
        group = args["group"]

        user = ActiniaUser.create_user(user_id, group, password, "user", {})

        if user is not None:
            if user.exists() is True:
                return make_response(jsonify({"Status":"success",
                                              "Messages:":"User %s created"%user_id}), 201)

        return make_response(jsonify({"Status":"error",
                                      "Messages":"Unable to create user %s"%user_id}), 400)

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

            A HTTP status 200 response JSON content::

                {
                  "Messages": "User thomas deleted",
                  "Status": "success"
                }

            A HTTP status 400 response JSON content::

                {
                  "Messages": "Unable to delete user thomas. User does not exist.",
                  "Status": "error"
                }

        """
        user = ActiniaUser(user_id)

        if user.exists() is False:
            return make_response(jsonify({"Status":"error",
                                          "Messages":"Unable to delete user %s. User does not exist."%user_id}), 400)

        if user.delete() is True:
            return make_response(jsonify({"Status":"success",
                                          "Messages":"User %s deleted"%user_id}))

        return make_response(jsonify({"Status":"error",
                                      "Messages":"Unable to delete user %s"%user_id}), 400)
