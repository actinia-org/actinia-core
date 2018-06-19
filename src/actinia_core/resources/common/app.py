# -*- coding: utf-8 -*-
"""
App configuration of flask, flask_restful, redis server connection
and global settings
"""
actinia_string="""Actinia"""

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

The full API documentation is available here: https://actinia.mundialis.de/api_docs/


Examples:
---------

**Data management**

- List all locations that are available in the actinia persistent database:

        curl -X GET "https://actinia.mundialis.de/api/v1/locations" -H  "authorization: Basic ..."

- List all mapsets in the location LL:

        curl -X GET "https://actinia.mundialis.de/api/v1/locations/LL/mapsets" -H  "authorization: Basic ..."

- List all space-time raster datasets (STRDS) in location LL and mapset Sentinel_timeseries:

        curl -X GET "https://actinia.mundialis.de/api/v1/locations/LL/mapsets/Sentinel_timeseries/strds" -H  "authorization: Basic ..."

- List all raster map layers of the STRDS:

        curl -X GET "https://actinia.mundialis.de/api/v1/locations/LL/mapsets/Sentinel_timeseries/strds/S2A_B04/raster_layers" -H  "authorization: Basic ..."

**Landsat and Sentinel2A NDVI computation**

This API call will compute the NDVI of the top of athmosphere (TOAR)
corrected Landsat4 scene LC80440342016259LGN00:

    curl -X POST "https://actinia.mundialis.de/api/v1/landsat_process/LC80440342016259LGN00/TOAR/NDVI" -H  "authorization: Basic ..."

NDVI computation of Sentinel2A scene S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138:

    curl -X POST "https://actinia.mundialis.de/api/v1/sentinel2_process/ndvi/S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138" -H  "authorization: Basic ..."

The results of the asynchronous computations are available as GeoTIFF file in a cloud storage for download.


"""

from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from flask import Flask
from flask_restful_swagger_2 import Api

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"

API_VERSION="v1"

# This is the URL prefix that must be used in the tests
URL_PREFIX="/api/%s"%API_VERSION


flask_app = Flask(__name__)
CORS(flask_app)

flask_api = Api(flask_app, prefix=URL_PREFIX,
                api_version=API_VERSION,
                api_spec_url='/swagger',
                title=actinia_string,
                description=actinia_description, schemes=['https'],
                consumes=['application/gml+xml', 'application/json'])

# Set the security definition in an unconventional way
flask_api._swagger_object["securityDefinitions"] = {"basicAuth":{"type": "basic"}}
flask_api._swagger_object["security"]=[{"basicAuth":[]}]

auth = HTTPBasicAuth()
