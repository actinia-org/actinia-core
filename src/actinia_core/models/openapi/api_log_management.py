# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2021 Sören Gebbert and mundialis GmbH & Co. KG
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
Models for api_log_management
"""

from flask_restful_swagger_2 import Schema

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


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
