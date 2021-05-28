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
Models for location_management
"""

from flask_restful_swagger_2 import Schema

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class LocationListResponseModel(Schema):
    """Response schema for location lists
    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The status of the resource, values: accepted, '
                           'running, finished, terminated, error'
        },
        'locations': {
            'type': 'array',
            'items': {"type": "string"},
            'description': 'The list of locations in the GRASS database'
        }
    }
    example = {"locations": ["nc_spm_08", "latlong_wgs84", "ECAD"], "status": "success"}
    required = ["status", "locations"]


class ProjectionInfoModel(Schema):
    """Schema to define projection information as JSON input in POST requests
    """
    type = 'object'
    properties = {
        'epsg': {
            'type': 'string',
            'description': 'The EPSG code of the projection that should be used '
                           'to create a location'
        }
    }
    example = {"epsg": "4326"}
    required = ["epsg"]
