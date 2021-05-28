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
The user specific resources

This module specifies all endpoints to manage user accounts
in the redis database via REST API calls.

TODO: Implement POST full permission creation
      Implement PUT to modify existing users
"""
from flask_restful_swagger_2 import Schema

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class TokenResponseModel(Schema):
    """Response schema that is used for authentication token generation.

    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The status of the resource, values: success, error'
        },
        'token': {
            'type': 'string',
            'description': 'The generated token for authentication'
        },
        'message': {
            'type': 'string',
            'description': 'The message of the token generation'
        }
    }
    required = ["status", "token"]
