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
Model for Base layer resources
"""

from flask_restful_swagger_2 import Schema

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class SetRegionModel(Schema):
    """This schema represents the computational region definition for raster
     and vector map layers.

        n : for north
        s : for south
        e : for east
        w : for west
        res : resolution of the region
        ewres: east-west resolution
        nsres: north-south resolution
        raster: Raster layer name with mapset to set the region from
        align: Raster layer name with mapset to align the region to
        zoom: Raster layer name with mapset to zoom the region to
        vector: Vector layer name with mapset to set the region from

    """
    type = 'object'
    properties = {
        'region': {
            'type': 'string',
            'description': 'Set current region from named region'
        },
        'raster': {
            'type': 'string',
            'description': 'Raster layer name with mapset to set the region from'
        },
        'align': {
            'type': 'string',
            'description': 'Raster layer name with mapset to align the region to'
        },
        'zoom': {
            'type': 'string',
            'description': 'Raster layer name with mapset to zoom the region to'
        },
        'vector': {
            'type': 'string',
            'description': 'Vector layer name with mapset to set the region from'
        },
        'n': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the northern edge'
        },
        's': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the southern edge'
        },
        'w': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the western edge'
        },
        'e': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the eastern edge'
        },
        't': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the top edge'
        },
        'b': {
            'type': 'number',
            'format': 'double',
            'description': 'Value for the bottom edge'
        },
        'nsres': {
            'type': 'number',
            'format': 'double',
            'description': 'North-south 2D grid resolution'
        },
        'res': {
            'type': 'number',
            'format': 'double',
            'description': '2D grid resolution (north-south and east-west)'
        },
        'ewres': {
            'type': 'number',
            'format': 'double',
            'description': 'East-west 2D grid resolution'
        },
        'res3': {
            'type': 'number',
            'format': 'double',
            'description': '3D grid resolution (north-south, east-west and top-bottom)'
        },
        'tbres': {
            'type': 'number',
            'format': 'double',
            'description': 'Top-bottom 3D grid resolution'
        }
    }
