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
App configuration of flask, flask_restful, redis server connection
and global settings
"""
actinia_string = """Actinia"""

actinia_description = """
================================
Actinia - The GRASS GIS REST API
================================

**Actinia** is an open source REST API for scalable, distributed, high performance
processing of geographical data that uses GRASS GIS for computational tasks.

It provides a REST API to process satellite images, time series of satellite images,
arbitrary raster data with geographical relations and vector data.

The REST interface allows to access, manage and manipulate the GRASS GIS
database via HTTP GET,PUT,POST and DELETE requests and to process raster, vector and
time series data located in a persistent GRASS GIS database.
**Actinia** allows the processing of cloud based data, for example all Landsat 4-8 scenes as well as all
Sentinel2A scenes in an ephemeral databases. The computational results of ephemeral processing
are available via object storage as GeoTIFF files.

The full API documentation is available here: https://redocly.github.io/redoc/?url=https://actinia.mundialis.de/latest/swagger.json


Examples:
---------

To execute the examples, first setup login information, IP address and port:

        export ACTINIA_URL=https://actinia.mundialis.de/latest
        export AUTH='-u demouser:gu3st!pa55w0rd'

**Data management**

- List all locations that are available in the actinia persistent database:

        curl ${AUTH} -X GET "${ACTINIA_URL}/locations"

- List all mapsets in the location latlong_wgs84:

        curl ${AUTH} -X GET "${ACTINIA_URL}/locations/latlong_wgs84/mapsets"

- List all raster layers in location latlong_wgs84 and mapset Sentinel2A

        curl ${AUTH} -X GET "${ACTINIA_URL}/locations/latlong_wgs84/mapsets/Sentinel2A/raster_layers"

- List all space-time raster datasets (STRDS) in location ECAD and mapset PERMANENT:

        curl ${AUTH} -X GET "${ACTINIA_URL}/locations/ECAD/mapsets/PERMANENT/raster_layers"

- List all raster map layers of the STRDS precipitation_1950_2013_yearly_mm:

        curl ${AUTH} -X GET "${ACTINIA_URL}/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm/raster_layers"

**Landsat and Sentinel2A NDVI computation**

This API call will compute the NDVI of the top of atmosphere (TOAR)
corrected Landsat4 scene LC80440342016259LGN00:

    curl ${AUTH} -X POST "${ACTINIA_URL}/landsat_process/LC80440342016259LGN00/TOAR/NDVI"

NDVI computation of Sentinel2A scene S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138:

    curl ${AUTH} -X POST "${ACTINIA_URL}/sentinel2_process/ndvi/S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138"

The results of the asynchronous computations are available as GeoTIFF file in a cloud storage for download.
"""

from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from flask import Flask
from flask_restful_swagger_2 import Api

from actinia_api import API_VERSION, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Julia Haas"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


flask_app = Flask(__name__)
# allows endpoints with and without trailing slashes
flask_app.url_map.strict_slashes = False
CORS(flask_app)

flask_api = Api(flask_app, prefix=URL_PREFIX,
                api_version=API_VERSION,
                api_spec_url='/swagger',
                title=actinia_string,
                description=actinia_description, schemes=['https'],
                consumes=['application/gml+xml', 'application/json'])

# Set the security definition in an unconventional way
flask_api._swagger_object["securityDefinitions"] = {"basicAuth": {"type": "basic"}}
flask_api._swagger_object["security"] = [{"basicAuth": []}]

auth = HTTPBasicAuth()
