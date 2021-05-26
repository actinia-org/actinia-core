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

from flask import jsonify, make_response
from flask_restful import reqparse
from flask_restful_swagger_2 import swagger
from .base_login import LoginBase
from actinia_core.common.user import ActiniaUser
from actinia_core.common.response_models import \
    UserListResponseModel, UserInfoResponseModel, SimpleResponseModel


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

    @swagger.doc({
        'tags': ['User Management'],
        'description': 'Get a list of all users. '
                       'Minimum required user role: admin.',
        'responses': {
            '200': {
                'description': 'This response returns a list of user names.',
                'schema': UserListResponseModel
            }
        }
    })
    def get(self):
        """List all users in the database

        These methods work only if the
        authorized user has an admin role.

        Returns:
            flask.Response: A HTTP response with
                            JSON payload containing a list of users
        """
        user = ActiniaUser(None)
        user_list = user.list_all_users()

        return make_response(jsonify(UserListResponseModel(
            status="success",
            user_list=user_list
        )), 200)


class UserManagementResource(LoginBase):
    """Get, Create and Delete a single user

    These methods work only if the
    authorized user has an admin role.

    Only normal users (role=user) can be created with this class.

    """

    def __init__(self):
        LoginBase.__init__(self)

    @swagger.doc({
        'tags': ['User Management'],
        'description': 'Get information about the group, role and permissions '
                       'of a certain user. '
                       'Minimum required user role: admin.',
        'parameters': [
            {
                'name': 'user',
                'description': 'The unique name of the user',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns information about a '
                               'certain user.',
                'schema': UserInfoResponseModel
            },
            '400': {
                'description': 'The error message',
                'schema': SimpleResponseModel
            }
        }
    })
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
        """
        user = ActiniaUser(user_id)

        if user.exists() is False:
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="User <%s> does not exist" % user_id
            )), 400)

        credentials = user.get_credentials()

        return make_response(jsonify(UserInfoResponseModel(
            status="success",
            permissions=credentials["permissions"],
            user_id=credentials["user_id"],
            user_role=credentials["user_role"],
            user_group=credentials["user_group"]
        )), 200)

    @swagger.doc({
        'tags': ['User Management'],
        'description': 'Creates a new user in the database. '
                       'Minimum required user role: admin.',
        'parameters': [
            {
                'name': 'user_id',
                'description': 'The unique name of the user',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'password',
                'description': 'The password of the new user',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'group',
                'description': 'The group of the new user',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns the status of user creation.',
                'schema': SimpleResponseModel
            },
            '400': {
                'description': 'The error message',
                'schema': SimpleResponseModel
            }
        }
    })
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
                return make_response(jsonify(SimpleResponseModel(
                    status="success",
                    message="User %s created" % user_id
                )), 201)

        return make_response(jsonify(SimpleResponseModel(
            status="error",
            message="Unable to create user %s" % user_id
        )), 400)

    @swagger.doc({
        'tags': ['User Management'],
        'description': 'Deletes a user. '
                       'Minimum required user role: admin.',
        'parameters': [
            {
                'name': 'user_id',
                'description': 'The unique name of the user',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns the status of user deletion.',
                'schema': SimpleResponseModel
            },
            '400': {
                'description': 'The error message',
                'schema': SimpleResponseModel
            }
        }
    })
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
        user = ActiniaUser(user_id)

        if user.exists() is False:
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="Unable to delete user %s. User does not exist." % user_id
            )), 400)

        if user.delete() is True:
            return make_response(jsonify(SimpleResponseModel(
                status="success",
                message="User %s deleted" % user_id
            )), 200)

        return make_response(jsonify(SimpleResponseModel(
            status="error",
            message="Unable to delete user %s" % user_id
        )), 400)
