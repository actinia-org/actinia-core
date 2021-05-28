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
Models for Raster colors management
"""

from flask_restful_swagger_2 import Schema

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class RasterColorModel(Schema):
    """Response schema that is used in cases that no asynchronous run was performed.

    """
    description = "Set the color table for an existing raster map layer with a " \
                  "set of rules, a specific color or an other raster map layer"
    type = 'object'
    properties = {
        'rules': {
            'type': 'array',
            'description': 'A list of rules to set the color table of a raster '
                           'map layer',
            'items': {'type': "string"}
        },
        'color': {
            'type': 'string',
            'description': 'The name of a color to be set for a raster map layer'
        },
        'raster': {
            'type': 'string',
            'description': 'The name of an existing raster map layer to copy '
                           'the color table from'
        }
    }
    example = {
        "rules": ["1 0:0:0",
                  "default 255:255:255"],
        "color": "ndvi",
        "raster": "elevation@PERMANENT"
    }
