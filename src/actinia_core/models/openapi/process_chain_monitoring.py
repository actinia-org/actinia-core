# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2021 mundialis GmbH & Co. KG
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
Process Chain Monitoring
"""
from flask_restful_swagger_2 import Schema

__license__ = "GPLv3"
__author__ = "Anika Weinmann, Carmen Tawalika"
__copyright__ = "Copyright 2021, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class MapsetSizeResponseModel(Schema):
    """Response schema for mapset sizes of a resource
    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The status of the resource, values: success, error'
        },
        'mapset_sizes': {
            'type': 'array',
            'items': {"type": "integer"},
            'description': 'The list of mapset sizes of a resource in bytes'
        }
    }
    example = {"mapset_sizes": [29946, 29946], "status": "success"}
    required = ["status", "mapset_sizes"]


class MaxMapsetSizeResponseModel(Schema):
    """Response schema for maximum mapset size of a resoucre
    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The status of the resource, values: success, error'
        },
        'max_mapset_size': {
            'type': 'integer',
            'description': 'The maximum mapset size of a resource in bytes'
        }
    }
    example = {"max_mapset_size": 29949, "status": "success"}
    required = ["status", "max_mapset_size"]
