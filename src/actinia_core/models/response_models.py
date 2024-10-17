# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2024 Sören Gebbert and mundialis GmbH & Co. KG
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
Response models
"""
import pickle
import time
from datetime import datetime
from flask import jsonify
from flask_restful_swagger_2 import Schema
from copy import deepcopy
from actinia_api import URL_PREFIX

from actinia_core.core.common.process_chain import GrassModule

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Julia Haas, Guido Riembauer, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class ProgressInfoModel(Schema):
    """This class defines the model for progress information.

    Progress information is generated in case a process chain with at least one
    commands is processed.
    """

    type = "object"
    properties = {
        "step": {
            "type": "integer",
            "format": "int64",
            "description": "The current processing step",
        },
        "num_of_steps": {
            "type": "integer",
            "format": "int64",
            "description": "The total number of processing steps",
        },
        "sub_step": {
            "type": "integer",
            "format": "int64",
            "description": "The current sub step of the current processing "
            "step",
        },
        "num_of_sub_steps": {
            "type": "integer",
            "format": "int32",
            "description": "The total number of sub steps of the current "
            "processing step",
        },
    }
    required = ["step", "num_of_steps"]

    example = {"num_of_steps": 6, "step": 6}


class ProcessLogModel(Schema):
    """This class defines the model for Unix process information.

    Each time a Unix process
    is invoked, this model must be used to inform the user of the return
    process state. Each process has parameters, stdout/stderr output and a
    return value. This model is not designed to inform about running processes,
    but about finished processes. The return_code of 0 indicates that it ran
    successfully. A negative value -N indicates that the child was terminated
    by signal N (POSIX only; see also
    https://en.wikipedia.org/wiki/Signal_(IPC)#Default_action).
    """

    type = "object"
    properties = {
        "id": {"type": "string", "description": "The ID of the executable"},
        "executable": {
            "type": "string",
            "description": "The name of the executable",
        },
        "parameter": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The parameter of the executable",
        },
        "stdout": {
            "type": "string",
            "description": "The stdout output of the executable",
        },
        "stderr": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The stderr output of the executable as list of "
            "strings",
        },
        "return_code": {
            "type": "number",
            "format": "int32",
            "description": "The return code of the executable",
        },
        "run_time": {
            "type": "number",
            "format": "float",
            "description": "The runtime of the executable in seconds",
        },
        "mapset_size": {
            "type": "number",
            "format": "float",
            "description": "The size of the mapset in bytes",
        },
    }
    required = ["executable", "parameter", "stdout", "stderr", "return_code"]

    example = {
        "executable": "g.list",
        "parameter": ["type=raster", "mapset=PERMANENT"],
        "return_code": 0,
        "run_time": 0.05017662048339844,
        "stderr": [""],
        "stdout": "aspect\nbasin_50K\n",
    }


class UrlModel(Schema):
    """URL schema that points to the status URL
    of the resource and to all generated resources (files, images, ...).

    """

    type = "object"
    properties = {
        "status": {
            "type": "string",
            "description": "The URL to check the status of the resource",
        },
        "resources": {
            "type": "array",
            "items": {"type": "string"},
            "description": "A list of URLs to generated resources, that may "
            "be GeoTiff files, vector files, ASCII files or png images",
        },
    }
    required = ["status", "resources"]
    example = {
        "resources": [
            f"http://localhost{URL_PREFIX}/resource/user/resource_id-4846cbcc-"
            "3918-4654-bf4d-7e1ba2b59ce6/my_slope.tiff"
        ],
        "status": f"http://localhost{URL_PREFIX}/resources/user/resource_id-"
        "4846cbcc-3918-4654-bf4d-7e1ba2b59ce6",
    }


class SimpleResponseModel(Schema):
    """
    Response schema that is used in cases that no asynchronous run was
    performed and the generated information is very simple.

    """

    type = "object"
    properties = {
        "status": {
            "type": "string",
            "description": "The status of the resource, values: accepted, "
            "running, finished, terminated, error",
        },
        "message": {
            "type": "string",
            "description": "A simple message to describes the status of the "
            "resource",
        },
    }
    required = ["status", "message"]


class MapsetListResponseModel(Schema):
    """
    Response schema that is used to list all mapsets available to the user.
    """

    type = "object"
    properties = {
        "status": {
            "type": "string",
            "description": "The status of the request",
        },
        "available_mapsets": {
            "type": "array",
            "items": {"type": "string"},
            "description": (
                "The names of all available mapsets with"
                " corresponding projects in the global database"
            ),
        },
    }
    required = ["status", "available_mapsets"]
    example = {
        "status": "success",
        "available_mapsets": [
            "nc_spm_08/PERMANENT",
            "latlong_wgs84/PERMANENT",
        ],
    }


class LockedMapsetListResponseModel(Schema):
    """Response schema that is used to list all locked mapsets."""

    type = "object"
    properties = {
        "status": {
            "type": "string",
            "description": "The status of the request",
        },
        "locked_mapsets_list": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The names of all locked mapsets",
        },
        "message": {
            "type": "string",
            "description": "A simple message to describes the status of the "
            "resource",
        },
    }
    required = ["status", "locked_mapsets_list", "message"]
    example = {
        "status": "success",
        "locked_mapsets_list": ["utm32n/test_mapset"],
        "message": "number of locked mapsets: 1",
    }


class ApiInfoModel(Schema):
    """Response schema that contains API information of the called endpoint.

    This information is used in the ProcessResponseModel schema and
    important for the accounting system.

    """

    type = "object"
    properties = {
        "endpoint": {
            "type": "string",
            "description": "The endpoint of the API call",
        },
        "method": {
            "type": "string",
            "description": "The HTTP method of the request",
        },
        "path": {
            "type": "string",
            "description": "The path of the REST API call",
        },
        "request_url": {"type": "string", "description": "The request URL"},
        "post_url": {"type": "string", "description": "The post URL"},
    }
    required = ["endpoint", "method", "path", "request_url"]

    example = {
        "endpoint": "asyncephemeralresource",
        "method": "POST",
        "path": f"{URL_PREFIX}/projects/nc_spm_08/processing_async",
        "request_url": f"http://localhost{URL_PREFIX}/projects/nc_spm_08/"
        "processing_async",
    }


class ExceptionTracebackModel(Schema):
    """
    Response schema that contains python3 exception information of the called
    endpoint in case an exception was raised.

    This information is required to debug the REST API.
    """

    type = "object"
    properties = {
        "message": {
            "type": "string",
            "description": "The message that was send with the exception",
        },
        "type": {"type": "string", "description": "The type of the exception"},
        "traceback": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The full traceback of the exception",
        },
    }
    required = ["message", "type", "traceback"]

    example = {
        "message": "Error",
        "type": "exceptions.Exception",
        "traceback": 'File "main.py", line 2, in <module>\n    '
        'raise Exception("Error")\n',
    }


class ProcessingResponseModel(Schema):
    """This is the base class for ALL response models.

    This class or its derivatives must be used in all responses that run
    GRASS modules or Unix programs. Derivatives only differ in the
    *process_result* schema.
    """

    type = "object"
    properties = {
        "status": {
            "type": "string",
            "description": "The status of the response",
        },
        "user_id": {
            "type": "string",
            "description": "The id of the user that issued a request",
        },
        "resource_id": {
            "type": "string",
            "description": "The unique resource id",
        },
        "queue": {
            "type": "string",
            "description": "The name of the queue in which the job is queued",
        },
        "process_log": {
            "type": "array",
            "items": ProcessLogModel,
            "description": "A list of ProcessLogModels",
        },
        "process_chain_list": {
            "type": "array",
            "items": GrassModule,
            "description": "The list of GRASS modules that were used in the "
            "processing",
        },
        "process_results": {
            "type": "string",
            "description": "An arbitrary class that stores the processing "
            "results",
        },
        "progress": ProgressInfoModel,
        "message": {
            "type": "string",
            "description": "Message for the user, maybe status, finished or "
            "error message",
        },
        "exception": ExceptionTracebackModel,
        "accept_timestamp": {
            "type": "number",
            "format": "double",
            "description": "The acceptance timestamp in seconds of the "
            "response",
        },
        "accept_datetime": {
            "type": "string",
            "description": "The acceptance timestamp of the response in human "
            "readable format",
        },
        "timestamp": {
            "type": "number",
            "format": "double",
            "description": "The current timestamp in seconds of the response",
        },
        "time_delta": {
            "type": "number",
            "format": "double",
            "description": "The time delta of the processing in seconds",
        },
        "datetime": {
            "type": "string",
            "description": "The current timestamp of the response in human "
            "readable format",
        },
        "http_code": {
            "type": "number",
            "format": "int32",
            "description": "The HTTP code of the response",
        },
        "urls": UrlModel,
        "api_info": ApiInfoModel,
    }
    required = [
        "status",
        "user_id",
        "resource_id",
        "timestamp",
        "datetime",
        "accept_timestamp",
        "accept_datetime",
        "message",
    ]

    example = {
        "accept_datetime": "2017-05-24 22:37:21.607255",
        "accept_timestamp": 1495658241.607252,
        "api_info": {
            "endpoint": "asyncephemeralresource",
            "method": "POST",
            "path": "/projects/nc_spm_08/processing_async",
            "request_url": f"http://localhost{URL_PREFIX}/projects/nc_spm_08/"
            "processing_async",
        },
        "datetime": "2017-05-24 22:37:21.608717",
        "http_code": 200,
        "message": "Resource accepted",
        "process_results": {},
        "resource_id": "resource_id-2be8cafe-b451-46a0-be15-f61d95c5efa1",
        "status": "accepted",
        "timestamp": 1495658241.608716,
        "urls": {
            "resources": [],
            "status": f"http://localhost{URL_PREFIX}/resources/admin/"
            "resource_id-2be8cafe-b451-46a0-be15-f61d95c5efa1",
        },
        "user_id": "admin",
    }


class ProcessingErrorResponseModel(ProcessingResponseModel):
    """
    Response schema that returns error messages from a failed process execution
    that includes debug information (python traceback) and process logs.
    """

    type = "object"
    properties = deepcopy(ProcessingResponseModel.properties)
    required = deepcopy(ProcessingResponseModel.required)
    example = {
        "accept_datetime": "2018-05-06 22:02:14.323815",
        "accept_timestamp": 1525636934.3238132,
        "api_info": {
            "endpoint": "mapsetmanagementresourceuser",
            "method": "GET",
            "path": "/projects/nc_spm_08/mapsets/PERMANE/info",
            "request_url": f"http://localhost{URL_PREFIX}/projects/nc_spm_08/"
            "mapsets/PERMANENT/info",
        },
        "datetime": "2018-05-06 22:02:14.398927",
        "exception": {
            "message": "AsyncProcessError:  Error while running executable "
            "<g.region>",
            "traceback": [
                '  File "/home/soeren/src/GRaaS/actinia_venv/lib/python3.5/'
                "site-packages/actinia_core-0.0.post0.dev37+g216eeae.dirty-"
                'py3.5.egg/actinia_core/resources/ephemeral_processing.py", '
                "line 1063, in _run_executable\n    raise AsyncProcessError("
                '"Error while running executable <%s>" % process.executable)\n'
            ],
            "type": "<class 'actinia_core.core.common.exceptions."
            "AsyncProcessError'>",
        },
        "http_code": 400,
        "message": "AsyncProcessError:  Error while running executable "
        "<g.region>",
        "process_chain_list": [
            {
                "1": {"flags": "ug3", "module": "g.region"},
                "2": {"flags": "fw", "module": "g.proj"},
            }
        ],
        "process_log": [
            {
                "executable": "g.region",
                "parameter": ["-ug3"],
                "return_code": 1,
                "run_time": 0.05020904541015625,
                "stderr": [
                    "ERROR: MAPSET PERMANE not found at /home/soeren/actinia/"
                    "workspace/temp_db/gisdbase_5c4c13bce6e54207aea2e1705cba"
                    "0b8b/nc_spm_08",
                    "",
                ],
                "stdout": "",
            }
        ],
        "progress": {"num_of_steps": 2, "step": 1},
        "resource_id": "resource_id-79608249-521c-4a98-9e1f-9201f693870b",
        "status": "error",
        "time_delta": 0.07516026496887207,
        "timestamp": 1525636934.3989098,
        "urls": {
            "resources": [],
            "status": f"http://localhost{URL_PREFIX}/resources/user/"
            "resource_id-79608249-521c-4a98-9e1f-9201f693870b",
        },
        "user_id": "user",
    }


class ProcessingResponseListModel(Schema):
    """Response schema that represent a list of ProcessingResponseModel's"""

    type = "object"
    properties = {
        "resource_list": {
            "type": "array",
            "items": ProcessingResponseModel,
            "description": "A list of ProcessingResponseModel objects",
        }
    }
    required = ["resource_list"]


class StorageModel(Schema):
    """This class defines the model to inform about available storage
    that is used for caching or user specific resource storage.

    It is used as schema to define the *process_result* in a
    ProcessingResponseModel derivative.
    """

    type = "object"
    properties = {
        "used": {
            "type": "number",
            "format": "int64",
            "description": "The used storage in bytes",
        },
        "free": {
            "type": "number",
            "format": "int64",
            "description": "The free storage in bytes",
        },
        "quota": {
            "type": "number",
            "format": "int64",
            "description": "The current quota in bytes",
        },
        "free_percent": {
            "type": "number",
            "format": "int32",
            "description": "The free storage in percent",
        },
    }
    required = ["used", "free", "quota", "free_percent"]


class UnivarResultModel(Schema):
    """
    Response schema for the result of univariate computations of raster layers.

    It is used as schema to define the *process_result* in a
    ProcessingResponseModel derivative.
    """

    type = "object"
    properties = {
        "name": {
            "type": "string",
            "description": "The name of the raster resource",
        },
        "cells": {
            "type": "number",
            "format": "double",
        },
        "coeff_var": {
            "type": "number",
            "format": "double",
        },
        "max": {
            "type": "number",
            "format": "double",
        },
        "mean": {
            "type": "number",
            "format": "double",
        },
        "mean_of_abs": {
            "type": "number",
            "format": "double",
        },
        "min": {
            "type": "number",
            "format": "double",
        },
        "n": {
            "type": "number",
            "format": "double",
        },
        "null_cells": {
            "type": "number",
            "format": "double",
        },
        "range": {
            "type": "number",
            "format": "double",
        },
        "stddev": {
            "type": "number",
            "format": "double",
        },
        "sum": {
            "type": "number",
            "format": "double",
        },
        "variance": {
            "type": "number",
            "format": "double",
        },
    }
    # If a map is empty, r.univar will return nothing, hence no required
    # variables
    # required = ['name', 'cells', 'coeff_var', 'max', 'mean', 'mean_of_abs',
    #            'min','n', 'null_cells', 'range', 'stddev', 'sum', 'variance']


class CategoricalStatisticsResultModel(Schema):
    """Response schema for the result of r.stats computations of raster layers.

    It is used as schema to define the *process_result* in a
    ProcessingResponseModel derivative.
    """

    type = "object"
    properties = {
        "cat": {"type": "string", "description": "The raster category"},
        "name": {
            "type": "string",
            "description": "The name of raster category",
        },
        "area": {
            "type": "number",
            "format": "double",
            "description": "The size of the area in square meters",
        },
        "cell_count": {
            "type": "number",
            "format": "double",
            "description": "The number of cells that have the raster category",
        },
        "percent": {
            "type": "number",
            "format": "double",
            "description": "The percentage of the area",
        },
    }
    required = ["cat", "name", "area", "cell_count", "percent"]


class RegionModel(Schema):
    """Output of GRASS GIS module g.region -gu3

    It is used as schema to define the *process_result* in a
    ProcessingResponseModel derivative.

    GRASS 7.8.dev (latlong_wgs84):~ > g.region -gu3
    projection=3
    zone=0
    n=80
    s=0
    w=0
    e=120
    t=50
    b=0
    nsres=10
    nsres3=10
    ewres=10
    ewres3=10
    tbres=10
    rows=8
    rows3=8
    cols=12
    cols3=12
    depths=5
    cells=96
    cells3=480

    """

    type = "object"
    properties = {
        "projection": {
            "type": "number",
            "format": "integer",
        },
        "zone": {
            "type": "number",
            "format": "integer",
        },
        "n": {
            "type": "number",
            "format": "double",
        },
        "s": {
            "type": "number",
            "format": "double",
        },
        "w": {
            "type": "number",
            "format": "double",
        },
        "e": {
            "type": "number",
            "format": "double",
        },
        "t": {
            "type": "number",
            "format": "double",
        },
        "b": {
            "type": "number",
            "format": "double",
        },
        "nsres": {
            "type": "number",
            "format": "double",
        },
        "nsres3": {
            "type": "number",
            "format": "double",
        },
        "ewres": {
            "type": "number",
            "format": "double",
        },
        "ewres3": {
            "type": "number",
            "format": "double",
        },
        "tbres": {
            "type": "number",
            "format": "double",
        },
        "rows": {
            "type": "number",
            "format": "integer",
        },
        "rows3": {
            "type": "number",
            "format": "integer",
        },
        "cols": {
            "type": "number",
            "format": "integer",
        },
        "cols3": {
            "type": "number",
            "format": "integer",
        },
        "depths": {
            "type": "number",
            "format": "integer",
        },
        "cells": {
            "type": "number",
            "format": "integer",
        },
        "cells3": {
            "type": "number",
            "format": "integer",
        },
    }

    example = {
        "b": 0.0,
        "cells": 29535,
        "cells3": 29535,
        "cols": 179,
        "cols3": 179,
        "depths": 1,
        "e": 639530.0,
        "ewres": 10.0,
        "ewres3": 10.0,
        "n": 221230.0,
        "nsres": 10.0,
        "nsres3": 10.0,
        "projection": 99,
        "rows": 165,
        "rows3": 165,
        "s": 219580.0,
        "t": 1.0,
        "tbres": 1.0,
        "w": 637740.0,
        "zone": 0,
    }


class MapsetInfoModel(Schema):
    """Schema for projection and region information from a specific mapset.

    It is used as schema to define the *process_result* in a
    ProcessingResponseModel derivative.
    """

    type = "object"
    properties = {
        "projection": {
            "type": "string",
            "description": "The project projection WKT string",
        },
        "region": RegionModel,
    }
    required = ["projection", "region"]

    example = {
        "projection": 'PROJCS["NAD83(HARN) / North Carolina",GEOGCS['
        '"NAD83(HARN)",DATUM["NAD83_High_Accuracy_Reference_Network",'
        'SPHEROID["GRS1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],'
        'TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6152"]],PRIMEM['
        '"Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",'
        '0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY['
        '"EPSG","4152"]],PROJECTION["Lambert_Conformal_Conic_2SP"],'
        'PARAMETER["standard_parallel_1",36.16666666666666],'
        'PARAMETER["standard_parallel_2",34.33333333333334],'
        'PARAMETER["latitude_of_origin",33.75],PARAMETER['
        '"central_meridian",-79],PARAMETER["false_easting",'
        '609601.22],PARAMETER["false_northing",0],UNIT["metre",1,'
        'AUTHORITY["EPSG","9001"]],AXIS["X",EAST],'
        'AXIS["Y",NORTH],AUTHORITY["EPSG","3358"]]\n',
        "region": {
            "b": 0.0,
            "cells": 29535,
            "cells3": 29535,
            "cols": 179,
            "cols3": 179,
            "depths": 1,
            "e": 639530.0,
            "ewres": 10.0,
            "ewres3": 10.0,
            "n": 221230.0,
            "nsres": 10.0,
            "nsres3": 10.0,
            "projection": 99,
            "rows": 165,
            "rows3": 165,
            "s": 219580.0,
            "t": 1.0,
            "tbres": 1.0,
            "w": 637740.0,
            "zone": 0,
        },
    }


class MapsetInfoResponseModel(ProcessingResponseModel):
    """Response schema that includes projection and region information
    about a specific mapset as processing results.

    This schema is a derivative of the ProcessingResponseModel that defines a
    different *process_results* schema.
    """

    type = "object"
    properties = deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = MapsetInfoModel
    required = deepcopy(ProcessingResponseModel.required)
    example = {
        "accept_datetime": "2018-05-02 10:53:20.254387",
        "accept_timestamp": 1525258400.2543857,
        "api_info": {
            "endpoint": "mapsetmanagementresourceuser",
            "method": "GET",
            "path": f"{URL_PREFIX}/projects/ECAD/mapsets/PERMANENT/info",
            "request_url": f"http://localhost{URL_PREFIX}/projects/ECAD/"
            "mapsets/PERMANENT/info",
        },
        "datetime": "2018-05-02 10:53:20.392509",
        "http_code": 200,
        "message": "Processing successfully finished",
        "process_chain_list": [
            {
                "1": {"flags": "ug3", "module": "g.region"},
                "2": {"flags": "fw", "module": "g.proj"},
            }
        ],
        "process_log": [
            {
                "executable": "g.region",
                "parameter": ["-ug3"],
                "return_code": 0,
                "run_time": 0.05018115043640137,
                "stderr": [""],
                "stdout": "...",
            },
            {
                "executable": "g.proj",
                "parameter": ["-fw"],
                "return_code": 0,
                "run_time": 0.05016374588012695,
                "stderr": [""],
                "stdout": "...",
            },
        ],
        "process_results": {
            "projection": 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",'
            '6378137,298.257223563,AUTHORITY["EPSG","7030"]],'
            'AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,'
            'AUTHORITY["EPSG","8901"]],UNIT["degree",'
            '0.0174532925199433,AUTHORITY["EPSG","9122"]],'
            'AUTHORITY["EPSG","4326"]]\n',
            "region": {
                "b": 0.0,
                "cells": 1,
                "cells3": 1,
                "cols": 1,
                "cols3": 1,
                "depths": 1,
                "e": 1.0,
                "ewres": 1.0,
                "ewres3": 1.0,
                "n": 1.0,
                "nsres": 1.0,
                "nsres3": 1.0,
                "projection": 3,
                "rows": 1,
                "rows3": 1,
                "s": 0.0,
                "t": 1.0,
                "tbres": 1.0,
                "w": 0.0,
                "zone": 0,
            },
        },
        "progress": {"num_of_steps": 2, "step": 2},
        "resource_id": "resource_id-2222cdb7-06f5-460d-a38f-5745a3c3b518",
        "status": "finished",
        "time_delta": 0.13819408416748047,
        "timestamp": 1525258400.392495,
        "urls": {
            "resources": [],
            "status": f"http://localhost{URL_PREFIX}/resources/user/"
            "resource_id-2222cdb7-06f5-460d-a38f-5745a3c3b518",
        },
        "user_id": "user",
    }


class RasterAreaStatsResponseModel(ProcessingResponseModel):
    """Response schema for a list of categorical statistics.

    This schema is a derivative of the ProcessingResponseModel that defines a
    different *process_results* schema.
    """

    type = "object"
    properties = deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = {}
    properties["process_results"]["type"] = "array"
    properties["process_results"]["items"] = CategoricalStatisticsResultModel
    required = deepcopy(ProcessingResponseModel.required)
    example = {}


class AreaUnivarResultModel(Schema):
    """Response schema for the result of univariate computations of raster
    layers based on a vector area.

    It is used as schema to define the process_result in a
    ProcessingResponseModel.

    cat
    fid
    raster_number
    raster_minimum
    raster_maximum
    raster_range
    raster_average
    raster_median
    raster_stddev
    raster_sum
    raster_variance
    raster_coeff_var

    """

    type = "object"
    properties = {
        "fid": {
            "type": "string",
            "description": "Field id from the polygon of the vector map layer "
            "used for area stats computation",
        },
        "cat": {
            "type": "string",
            "description": "The category id from the polygon of the vector map"
            " layer used for area stats computation",
        },
        "raster_number": {
            "type": "number",
            "format": "double",
        },
        "raster_minimum": {
            "type": "number",
            "format": "double",
        },
        "raster_maximum": {
            "type": "number",
            "format": "double",
        },
        "raster_range": {
            "type": "number",
            "format": "double",
        },
        "raster_average": {
            "type": "number",
            "format": "double",
        },
        "raster_median": {
            "type": "number",
            "format": "double",
        },
        "raster_stddev": {
            "type": "number",
            "format": "double",
        },
        "raster_sum": {
            "type": "number",
            "format": "double",
        },
        "raster_variance": {
            "type": "number",
            "format": "double",
        },
        "raster_coeff_var": {
            "type": "number",
            "format": "double",
        },
    }


class RasterAreaUnivarStatsResponseModel(ProcessingResponseModel):
    """Response schema for resources that generate area univariate result lists
     as processing results.

    This schema is a derivative of the ProcessingResponseModel that defines a
    different *process_results* schema.
    """

    type = "object"
    properties = deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = {}
    properties["process_results"]["type"] = "array"
    properties["process_results"]["items"] = AreaUnivarResultModel
    required = deepcopy(ProcessingResponseModel.required)
    # required.append("process_results")
    example = {}


class StorageResponseModel(ProcessingResponseModel):
    """Response schema for storage management calls.

    This schema is a derivative of the ProcessingResponseModel that defines a
    different *process_results* schema.
    """

    type = "object"
    properties = deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = StorageModel
    required = deepcopy(ProcessingResponseModel.required)
    # required.append("process_results")
    example = {
        "accept_datetime": "2018-05-02 10:51:27.988969",
        "accept_timestamp": 1525258287.9889677,
        "api_info": {
            "endpoint": "syncresourcestorageresource",
            "method": "GET",
            "path": "/resource_storage",
            "request_url": "http://localhost:8080/resource_storage",
        },
        "datetime": "2018-05-02 10:51:28.100659",
        "http_code": 200,
        "message": "Resource storage size successfully computed",
        "process_chain_list": [],
        "process_log": [
            {
                "executable": "/usr/bin/du",
                "parameter": ["-sb", "/actinia/resources/superadmin"],
                "return_code": 0,
                "run_time": 0.05042886734008789,
                "stderr": [""],
                "stdout": "4096\t/actinia/resources/superadmin\n",
            }
        ],
        "process_results": {
            "free": 107374178304,
            "free_percent": 99,
            "quota": 107374182400,
            "used": 4096,
        },
        "progress": {"num_of_steps": 0, "step": 1},
        "resource_id": "resource_id-f9463d91-04a6-497c-b107-37c4ee013530",
        "status": "finished",
        "time_delta": 0.11174893379211426,
        "timestamp": 1525258288.1006439,
        "urls": {
            "resources": [],
            "status": "http://localhost:8080/resources/superadmin/resource_id-"
            "f9463d91-04a6-497c-b107-37c4ee013530",
        },
        "user_id": "superadmin",
    }


class StringListProcessingResultResponseModel(ProcessingResponseModel):
    """Response schema for resources that generate string list
     as processing results.

    This schema is a derivative of the ProcessingResponseModel that defines a
    different *process_results* schema.
    """

    type = "object"
    properties = deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = {}
    properties["process_results"]["type"] = "array"
    properties["process_results"]["items"] = {"type": "string"}
    required = deepcopy(ProcessingResponseModel.required)
    # required.append("process_results")
    example = {
        "accept_datetime": "2018-05-02 12:02:20.746845",
        "accept_timestamp": 1525255340.746844,
        "api_info": {
            "endpoint": "listmapsetsresource",
            "method": "GET",
            "path": "/projects/nc_spm_08/mapsets",
            "request_url": "http://localhost:5000/projects/nc_spm_08/mapsets",
        },
        "datetime": "2018-05-02 12:02:20.861017",
        "http_code": 200,
        "message": "Processing successfully finished",
        "process_chain_list": [
            {
                "1": {
                    "flags": "l",
                    "inputs": {"separator": "newline"},
                    "module": "g.mapsets",
                }
            }
        ],
        "process_log": [
            {
                "executable": "g.mapsets",
                "parameter": ["separator=newline", "-l"],
                "return_code": 0,
                "run_time": 0.0501406192779541,
                "stderr": ["Available mapsets:", ""],
                "stdout": "PERMANENT\nSource_A\nSource_B\nTarget\nlandsat\n"
                "raster_test_mapset\nuser1\n",
            }
        ],
        "process_results": [
            "PERMANENT",
            "Source_A",
            "Source_B",
            "Target",
            "landsat",
            "raster_test_mapset",
            "user1",
        ],
        "progress": {"num_of_steps": 1, "step": 1},
        "resource_id": "resource_id-715530fe-53e2-4b2b-87b2-3777c90fec7c",
        "status": "finished",
        "time_delta": 0.11421895027160645,
        "timestamp": 1525255340.8610027,
        "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/user/resource_id-"
            "715530fe-53e2-4b2b-87b2-3777c90fec7c",
        },
        "user_id": "user",
    }


def create_response_from_model(
    response_model_class=ProcessingResponseModel,
    status=None,
    user_id=None,
    resource_id=None,
    queue=None,
    iteration=None,
    process_log=None,
    progress=None,
    results=None,
    message=None,
    http_code=None,
    status_url=None,
    orig_time=None,
    orig_datetime=None,
    resource_urls=[],
    api_info=None,
    process_chain_list=[],
    exception=None,
    resp_type="pickle",
):
    """Create a dictionary and its pickle or JSON representation to represent
    response information

    This function is used to create almost all responses of Actinia Core

    Args:
        response_model_class (class): The response model class that must be
                                      applied. By default this is the
                                      ProcessingResponseModel class, that is
                                      the base for all responses that involve
                                      executables in Actinia Core. All classes
                                      that are accepted must be derived from
                                      ProcessingResponseModel and specify the
                                      "process_results" field. By default a
                                      string is required as data type for
                                      "process_results".
        status (str): One of: accepted, running, finished, error
        user_id (str): The user id
        resource_id (str): The resource id
        queue (str): The name of the queue
        iteration (int): The iteration of the job
        process_log (dict, str, list): The log from the running GRASS module
        progress (ProgressInfoModel): Progress information
        results (dict): The results of processing steps as Python data types
        message (str): The message from the running GRASS module or an error
                       message
        http_code (int): The HTTP status code
        status_url (str): The url of this request
        orig_time (time): The time of origin (seconds)
        orig_datetime (datetime): The datetime of origin (datetime format)
        resource_urls ([str]): The list of url of the new created resources
        api_info (ApiInfoModel): Information about the API call, important for
                                 accounting
        process_chain_list ([ProcessChainModel]): The list of process chains
        resp_type (str): What type of response, "pickle" or "json"

    Returns:
        A pickle string or json string

    """
    # if issubclass(response_model_class, ProcessingResponseModel) is False:
    #    raise IOError

    # if webhook auth is given set pw to XXX
    for i in range(len(process_chain_list)):
        if (
            "webhooks" in process_chain_list[i]
            and "auth" in process_chain_list[i]["webhooks"]
        ):
            webhook_auth = process_chain_list[i]["webhooks"]["auth"]
            process_chain_list[i]["webhooks"][
                "auth"
            ] = f"{webhook_auth.split(':')[0]}:XXX"

    resp_dict = response_model_class(
        status=status,
        user_id=user_id,
        resource_id=resource_id,
        queue=str(queue),
        # iteration=iteration,
        accept_timestamp=orig_time,
        accept_datetime=orig_datetime,
        timestamp=time.time(),
        datetime=str(datetime.now()),
        message=message,
        time_delta=time.time() - orig_time,
    )

    if process_log is not None:
        resp_dict["process_log"] = process_log
    if progress is not None:
        resp_dict["progress"] = progress
    if results is not None:
        resp_dict["process_results"] = results
    if process_chain_list is not None:
        resp_dict["process_chain_list"] = process_chain_list
    if http_code is not None:
        resp_dict["http_code"] = http_code
    if exception is not None:
        resp_dict["exception"] = exception
    if http_code is not None:
        resp_dict["urls"] = UrlModel(
            resources=resource_urls, status=str(status_url)
        )
    if api_info is not None:
        resp_dict["api_info"] = api_info
    if iteration is not None:
        resp_dict["iteration"] = iteration

    if resp_type == "pickle":
        return pickle.dumps([http_code, resp_dict])
    else:
        return jsonify(resp_dict)


class UserListResponseModel(Schema):
    """Response schema that is used to list all users."""

    type = "object"
    properties = {
        "status": {
            "type": "string",
            "description": "The status of the request",
        },
        "user_list": {
            "type": "array",
            "items": {"type": "string"},
            "description": "The names of all users",
        },
    }
    required = ["status", "user_list"]
    example = {"status": "success", "user_list": ["actinia-gdi"]}


class UserInfoResponseModel(Schema):
    """Response schema that is used to show information about a user."""

    type = "object"
    properties = {
        "status": {
            "type": "string",
            "description": "The status of the request",
        },
        "permissions": {
            "type": "object",
            "properties": {
                "cell_limit": {
                    "type": "string",
                    "description": "The limit of number of raster cells the "
                    "user is allowed to process",
                },
                "process_num_limit": {
                    "type": "string",
                    "description": "The limit of number of processes the user "
                    "is allowed to integrate into one process chain",
                },
                "process_time_limit": {
                    "type": "string",
                    "description": "The time a process must not exceed",
                },
                "accessible_datasets": {
                    "type": "object",
                    "properties": {},
                    "description": "The persistent GRASS GIS databases the "
                    "user is allowed to use. Contains one object for each "
                    "project name with an array of strings containing "
                    "all allowed mapset names. See example for more "
                    "information.",
                },
                "accessible_modules": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The GRASS GIS modules the user is allowed"
                    " to use",
                },
            },
            "description": "The names of all users",
        },
        "user_id": {
            "type": "string",
            "description": "The identifier of the user",
        },
        "user_role": {"type": "string", "description": "The role of the user"},
        "user_group": {
            "type": "string",
            "description": "The group of the user",
        },
    }
    required = ["status"]
    example = {
        "Permissions": {
            "accessible_datasets": {
                "nc_spm_08": ["PERMANENT", "user1", "landsat"]
            },
            "accessible_modules": [
                "r.blend",
                "r.buffer",
                "...",
                "t.rast.univar",
                "importer",
                "exporter",
            ],
            "cell_limit": 100000000000,
            "process_num_limit": 1000,
            "process_time_limit": 31536000,
        },
        "Status": "success",
        "User group": "superadmin",
        "User id": "actinia-gdi",
        "User role": "superadmin",
    }


class LinkResponseModel(Schema):
    """Response schema that is used in cases that no asynchronous run was
    performed and the generated information is very simple.

    """

    type = "object"
    properties = {
        "status": {
            "type": "string",
            "description": "The status of the resource, values: accepted, "
            "running, finished, terminated, error",
        },
        "message": {
            "type": "string",
            "description": "A simple message to describes the status of the "
            "resource",
        },
        "links": {"type": "list", "description": "A list of related links"},
    }
    required = ["status", "message"]
