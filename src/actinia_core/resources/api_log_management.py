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

"""
This module is designed to deliver the API calls of a specific user
"""
from flask import g
from flask import jsonify, make_response
from flask_restful import Resource

from flask_restful_swagger_2 import swagger
from flask_restful_swagger_2 import Schema

from actinia_core.common.app import auth
from actinia_core.common.api_logger import ApiLogger
from actinia_core.common.api_logger import log_api_call
from actinia_core.common.response_models import SimpleResponseModel
from .user_auth import check_user_permissions

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ApiLogEntryModel(Schema):
    """Response schema for a single API log entry that is used to track all API
    calls of a user.
    """
    type = 'object'
    properties = {
        'time_stamp': {
            'type': 'string',
            'description': 'The time stamp of the API call'
        },
        'node': {
            'type': 'string',
            'description': 'The node that executed the API call'
        },
        'endpoint': {
            'type': 'string',
            'description': 'The endpoint of the API call'
        },
        'method': {
            'type': 'string',
            'description': 'The HTTP method of the request'
        },
        'path': {
            'type': 'string',
            'description': 'The path of the REST API call'
        },
        'url': {
            'type': 'string',
            'description': 'The request URL'
        },
        'request_str': {
            'type': 'string',
            'description': 'The request string'
        }
    }
    required = ["time_stamp", "node", "endpoint",
                "method", "path", "url", "request_str"]


class ApiLogListModel(Schema):
    """Response schema that represents a list of API log entries.
    """
    type = 'object'
    properties = {
        'api_log_list': {
            'type': 'array',
            'items': ApiLogEntryModel,
            'description': 'A list of ApiLogEntryModel objects'
        }
    }
    required = ["api_log_list"]


class APILogResource(Resource):
    """API logg management
    """

    decorators = [log_api_call, check_user_permissions,
                  auth.login_required]

    def __init__(self):

        # Configuration
        Resource.__init__(self)

        self.api_logger = ApiLogger()

        # Store the user id and user role of the current user
        self.user_id = g.user.get_id()
        self.user_role = g.user.get_role()

    @swagger.doc({
        'tags': ['API Log'],
        'description': 'Get a list of all API calls that have been called by the '
                       'provided user. Admin and superadmin roles can list API '
                       'calls from any user. A user role can only list API calls '
                       'from itself. '
                       'Minimum required user role: user.',

        'parameters': [
            {
                'name': 'user_id',
                'description': 'The unique user name/id',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'Returned a list of all API calls that have been '
                               'called by the provided user.',
                'schema': ApiLogListModel
            },
            '400': {
                'description': 'The error message why API log gathering did not '
                               'succeeded',
                'schema': SimpleResponseModel
            }
        }
    })
    def get(self, user_id):
        """Get a list of all API calls that have been called by the provided user."""

        if self.user_role not in ["admin", "superadmin"] and user_id != self.user_id:
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="You do not have the permission "
                        "to list the API calls of the user")), 401)

        api_log_list = self.api_logger.list(user_id, 0, -1)
        return make_response(jsonify(ApiLogListModel(api_log_list=api_log_list)), 200)
