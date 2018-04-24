# -*- coding: utf-8 -*-

import pickle
import time
from datetime import datetime
from flask import jsonify
from flask_restful_swagger_2 import Schema
from copy import deepcopy
from .process_chain import ProcessChainModel

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class ProgressInfoModel(Schema):
    """This class defines the model for progress information.

    Progress information is generated in case a chain of several commands is processed.
    """
    type = 'object'
    properties = {
        'step': {
            'type': 'integer',
            'format': 'int64',
            'description': 'The current step of processing'
        },
        'num_of_steps': {
            'type': 'integer',
            'format': 'int64',
            'description': 'The total number of processing steps'
        },
        'sub_step': {
            'type': 'integer',
            'format': 'int64',
            'description': 'The current sub step of the current processing step'
        },
        'num_of_sub_steps': {
            'type': 'integer',
            'format': 'int32',
            'description': 'The total number of sub steps of the current processing step'
        },
    }
    required = ['step', 'num_of_steps']

    example = {
        "num_of_steps": 6,
        "step": 6
      }


class StorageModel(Schema):
    """This class defines the model to inform about available storage
    that is used for caching or user specific resource storage.
    """
    type = 'object'
    properties = {
        'used': {
            'type': 'number',
            'format': 'int64',
            'description': 'The used storage in bytes'
        },
        'free': {
            'type': 'number',
            'format': 'int64',
            'description': 'The free storage in bytes'
        },
        'quota': {
            'type': 'number',
            'format': 'int64',
            'description': 'The current quota in bytes'
        },
        'free_percent': {
            'type': 'number',
            'format': 'int32',
            'description': 'The free storage in percent'
        },
    }
    required = ['used', 'free', 'quota', 'free_percent']


class ProcessLogModel(Schema):
    """This class defines the model for Unix process information.

    Each time a Unix process
    is invoked, this model must be used to inform the user of the return process state. Each process
    has parameters, stdout/stderr output and a return value. This model is not designed to inform
    about running processes, but about finished processes.
    """
    type = 'object'
    properties = {
        'executable': {
            'type': 'string',
            'description': 'The name of the executable that was executed'
        },
        'parameter': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'The parameter of the executable that was executed'
        },
        'stdout': {
            'type': 'string',
            'description': 'The stdout output of the executable'
        },
        'stderr': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'The stderr output of the executable as list of strings'
        },
        'return_code': {
            'type': 'number',
            'format': 'int32',
            'description': 'The return code of the executable'
        },
        'run_time': {
            'type': 'number',
            'format': 'float',
            'description': 'The runtime of the executable in seconds'
        }
    }
    required = ['executable', 'parameter', 'stdout', 'stderr', 'return_code']

    example = {
      "executable": "g.region",
      "parameter": [
        "raster=elevation@PERMANENT",
        "res=10000",
        "-p",
        "--v"
      ],
      "return_code": 0,
      "stderr": [
        "NS resolution has been changed",
        "EW resolution has been changed",
        "NS and EW resolutions are different",
        ""
      ],
      "stdout": "projection: 99 (Lambert Conformal Conic)\nzone:       0\ndatum:      nad83\nellipsoid:  a=6378137 es=0.006694380022900787\nnorth:      228500\nsouth:      215000\nwest:       630000\neast:       645000\nnsres:      13500\newres:      7500\nrows:       1\ncols:       2\ncells:      2\n"
    }


class UrlModel(Schema):
    """URL schema that points to the status URL
    of the resource and to all generated resources (files, images, ...).

    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The URL to check the status of the resource'
        },
        'resources': {
            'type': 'array',
            'items': {'type': 'string'},
            'description': 'A list of URLs to generated resources'
        }
    }
    required = ["status", "resources"]


class SimpleResponseModel(Schema):
    """Response schema that is used in cases that no asynchronous run was performed.

    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The status of the resource, values: accepted, running, finished, terminated, error'
        },
        'message': {
            'type': 'string',
            'description': 'A simple message to describes the status of the resource'
        }
    }
    required = ["status", "message"]


class ApiInfoModel(Schema):
    """Response schema that contains API information of the called endpoint.

    This information is used in the ProcessResponseModel schema and
    important for the accounting system.

    """
    type = 'object'
    properties = {
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
        'request_url': {
            'type': 'string',
            'description': 'The request URL'
        }
    }
    required = ["endpoint", "method", "path", "request_url"]

    example = {
        "endpoint": "asyncephemeralresource",
        "method": "POST",
        "path": "/locations/nc_spm_08/processing_async",
        "request_url": "http://localhost/locations/nc_spm_08/processing_async"
      }


class ExceptionTracebackModel(Schema):
    """Response schema that contains Exception information of the called endpoint
    in case an Exception was raised.

    This information is required to debug the REST API.
    """
    type = 'object'
    properties = {
        'message': {
            'type': 'string',
            'description': 'The message that was send with the Exception'
        },
        'type': {
            'type': 'string',
            'description': 'The type of the Exception'
        },
        'traceback': {
            'type': 'string',
            'description': 'The full traceback of the Exception'
        }
    }
    required = ["message", "type", "traceback"]

    example = {
        "message": "Error",
        "type": "exceptions.Exception",
        "traceback": "File \"main.py\", line 2, in <module>\n    raise Exception(\"Error\")\n"
      }


class ProcessingResponseModel(Schema):
    """This is the base class for all asynchronous response models. This class must
    or a derivative must be used in all asynchronous responses. Usually
    specify derivatives different process_result schemas.

    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The status of the response'
        },
        'user_id': {
            'type': 'string',
            'description': 'The id of the user that issued a request'
        },
        'resource_id': {
            'type': 'string',
            'description': 'The unique resource id'
        },
        'process_log': {
            'type': 'array',
            'items': ProcessLogModel,
            'description': 'A list of ProcessLogModels'
        },
        'process_chain_list': {
            'type': 'array',
            'items': ProcessChainModel,
            'description': 'A list of ProcessChainModels that were used in the processing'
        },
        'process_results': {
            'type': 'string',
            'description': 'An arbitrary class that stores the processing results'
        },
        'progress': ProgressInfoModel,
        'message': {
            'type': 'string',
            'description': 'Message for the user, maybe status, finished or error message'
        },
        'exception': ExceptionTracebackModel,
        'accept_timestamp': {
            'type': 'number',
            'format': 'double',
            'description': 'The acceptance timestamp in seconds of the response'
        },
        'accept_datetime': {
            'type': 'string',
            'description': 'The acceptance timestamp of the response in human readable format'
        },
        'timestamp': {
            'type': 'number',
            'format': 'double',
            'description': 'The current timestamp in seconds of the response'
        },
        'time_delta': {
            'type': 'number',
            'format': 'double',
            'description': 'The time delta of the processing in seconds'
        },
        'datetime': {
            'type': 'string',
            'description': 'The current timestamp of the response in human readable format'
        },
        'http_code': {
            'type': 'number',
            'format': 'int32',
            'description': 'The HTTP code of the response'
        },
        'urls': UrlModel,
        'api_info': ApiInfoModel
    }
    required = ['status', 'user_id', 'resource_id', 'timestamp', 'datetime', 'accept_timestamp',
                'accept_datetime', 'message']

    example = {
      "accept_datetime": "2017-05-24 22:37:21.607255",
      "accept_timestamp": 1495658241.607252,
      "api_info": {
        "endpoint": "asyncephemeralresource",
        "method": "POST",
        "path": "/locations/nc_spm_08/processing_async",
        "request_url": "http://localhost/locations/nc_spm_08/processing_async"
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
        "status": "http://localhost/resources/admin/resource_id-2be8cafe-b451-46a0-be15-f61d95c5efa1"
      },
      "user_id": "admin"
    }


class ProcessingResponseListModel(Schema):
    """Response schema that represent a list of ProcessingResponseModel's
    """
    type = 'object'
    properties = {
        'resource_list': {
            'type': 'array',
            'items': ProcessingResponseModel,
            'description': 'A list of ProcessingResponseModel objects'
        }
    }
    required = ["resource_list"]


class UnivarResultModel(Schema):
    """Response schema for the result of univariate computations of raster layers.

    It is used as schema to define the process_result in a  ProcessingResponseModel.
    """
    type = 'object'
    properties = {
        'name': {
            'type': 'string',
            'description': 'The name of the raster resource'
        },
        'cells': {
            'type': 'number',
            'format': 'double',
        },
        'coeff_var': {
            'type': 'number',
            'format': 'double',
        },
        'max': {
            'type': 'number',
            'format': 'double',
        },
        'mean': {
            'type': 'number',
            'format': 'double',
        },
        'mean_of_abs': {
            'type': 'number',
            'format': 'double',
        },
        'min': {
            'type': 'number',
            'format': 'double',
        },
        'n': {
            'type': 'number',
            'format': 'double',
        },
        'null_cells': {
            'type': 'number',
            'format': 'double',
        },
        'range': {
            'type': 'number',
            'format': 'double',
        },
        'stddev': {
            'type': 'number',
            'format': 'double',
        },
        'sum': {
            'type': 'number',
            'format': 'double',
        },
        'variance': {
            'type': 'number',
            'format': 'double',
        }
    }
    # If a map is empty, r.univar will return nothing, hence no required variables
    # required = ['name', 'cells', 'coeff_var', 'max', 'mean', 'mean_of_abs',
    #            'min', 'n', 'null_cells', 'range', 'stddev', 'sum', 'variance']


class CategoricalStatisticsResultModel(Schema):
    """Response schema for the result of r.stats computations of raster layers.

    It is used as schema to define the process_result in a  ProcessingResponseModel.
    """
    type = 'object'
    properties = {
        'cat': {
            'type': 'string',
            'description': 'The raster category'
        },
        'name': {
            'type': 'string',
            'description': 'The name of raster category'
        },
        'area': {
            'type': 'number',
            'format': 'double',
            'description': 'The size of the area in square meters'
        },
        'cell_count': {
            'type': 'number',
            'format': 'double',
            'description': 'The number of cells that have the raster category'
        },
        'percent': {
            'type': 'number',
            'format': 'double',
            'description': 'The percentage of the area'
        }
    }
    required = ['cat', 'name', 'area', 'cell_count', 'percent']


class RegionModel(Schema):
    """Output og GRASS module g.region -gu3

    It is used as schema to define the process_result in a  ProcessingResponseModel.

    GRASS 7.3.svn (LL):~ > g.region -gu3
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
    type = 'object'
    properties = {
        'projection': {
            'type': 'number',
            'format': 'integer',
        },
        'zone': {
            'type': 'number',
            'format': 'integer',
        },
        'n': {
            'type': 'number',
            'format': 'double',
        },
        's': {
            'type': 'number',
            'format': 'double',
        },
        'w': {
            'type': 'number',
            'format': 'double',
        },
        'e': {
            'type': 'number',
            'format': 'double',
        },
        't': {
            'type': 'number',
            'format': 'double',
        },
        'b': {
            'type': 'number',
            'format': 'double',
        },
        'nsres': {
            'type': 'number',
            'format': 'double',
        },
        'nsres3': {
            'type': 'number',
            'format': 'double',
        },
        'ewres': {
            'type': 'number',
            'format': 'double',
        },
        'ewres3': {
            'type': 'number',
            'format': 'double',
        },
        'tbres': {
            'type': 'number',
            'format': 'double',
        },
        'rows': {
            'type': 'number',
            'format': 'integer',
        },
        'rows3': {
            'type': 'number',
            'format': 'integer',
        },
        'cols': {
            'type': 'number',
            'format': 'integer',
        },
        'cols3': {
            'type': 'number',
            'format': 'integer',
        },
        'depths': {
            'type': 'number',
            'format': 'integer',
        },
        'cells': {
            'type': 'number',
            'format': 'integer',
        },
        'cells3': {
            'type': 'number',
            'format': 'integer',
        }
    }


class MapsetInfoModel(Schema):
    """Schema for projection and region information from a specific mapset
    """
    type = 'object'
    properties = {
        'projection': {
            'type': 'string',
            'description': 'The location projection WKT string'
        },
        'region': RegionModel
    }
    required = ["projection", "region"]


class MapsetInfoResponseModel(ProcessingResponseModel):
    """Response schema that includes projection and region information
    about a specific mapset as processing results
    """
    type = 'object'
    properties =  deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = MapsetInfoModel
    required =  deepcopy(ProcessingResponseModel.required)


class RasterAreaStatsResponseModel(ProcessingResponseModel):
    """Response schema for a list of categorical statistics
    """
    type = 'object'
    properties =  deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = {}
    properties["process_results"]["type"] = "array"
    properties["process_results"]["items"] = CategoricalStatisticsResultModel
    required =  deepcopy(ProcessingResponseModel.required)


class AreaUnivarResultModel(Schema):
    """Response schema for the result of univariate computations of raster layers
    based on a vector area.

    It is used as schema to define the process_result in a  ProcessingResponseModel.

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
    type = 'object'
    properties = {
        'fid': {
            'type': 'string',
            'description': 'Field id from the polygon of the vector map layer used for area stats computation'
        },
        'cat': {
            'type': 'string',
            'description': 'The category id from the polygon of the vector map layer used for area stats computation'
        },
        'raster_number': {
            'type': 'number',
            'format': 'double',
        },
        'raster_minimum': {
            'type': 'number',
            'format': 'double',
        },
        'raster_maximum': {
            'type': 'number',
            'format': 'double',
        },
        'raster_range': {
            'type': 'number',
            'format': 'double',
        },
        'raster_average': {
            'type': 'number',
            'format': 'double',
        },
        'raster_median': {
            'type': 'number',
            'format': 'double',
        },
        'raster_stddev': {
            'type': 'number',
            'format': 'double',
        },
        'raster_sum': {
            'type': 'number',
            'format': 'double',
        },
        'raster_variance': {
            'type': 'number',
            'format': 'double',
        },
        'raster_coeff_var': {
            'type': 'number',
            'format': 'double',
        }
    }


class RasterAreaUnivarStatsResponseModel(ProcessingResponseModel):
    """Response schema for resources that generate area univariate result lists
     as processing results.
    """
    type = 'object'
    properties =  deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = {}
    properties["process_results"]["type"] = "array"
    properties["process_results"]["items"] = AreaUnivarResultModel
    required =  deepcopy(ProcessingResponseModel.required)
    # required.append("process_results")


class StorageResponseModel(ProcessingResponseModel):
    """Response schema for storage management calls.
    """
    type = 'object'
    properties = deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = StorageModel
    required = deepcopy(ProcessingResponseModel.required)
    # required.append("process_results")


class StringListProcessingResultResponseModel(ProcessingResponseModel):
    """Response schema for resources that generate string list
     as processing results.
    """
    type = 'object'
    properties =  deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = {}
    properties["process_results"]["type"] = "array"
    properties["process_results"]["items"] = {'type':"string"}
    required = deepcopy(ProcessingResponseModel.required)
    # required.append("process_results")


def create_response_from_model(response_model_class=ProcessingResponseModel,
                               status=None,
                               user_id=None,
                               resource_id=None,
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
                               resp_type="pickle"):
    """Create a dictionary and its pickle or JSON representation to represent response information

    This function is used to create almost all responses of Actinia Core

    Args:
        response_model_class (class): The response model class that must be applied. By default
                                      this is the ProcessingResponseModel class, that is the base
                                      for all responses that involve executables in Actinia Core. All
                                      classes that are accepted must be derived from ProcessingResponseModel
                                      and specify the "process_results" field. By default a string
                                      is required as data type for "process_results".
        status (str): One of: accepted, running, finished, error
        user_id (str): The user id
        resource_id (str): The resource id
        process_log (dict, str, list): The log from the running GRASS module
        progress (ProgressInfoModel): Progress information
        results (dict): The results of processing steps as Python data types
        message (str): The message from the running GRASS module or an error message
        http_code (int): The HTTP status code
        status_url (str): The url of this request
        orig_time (time): The time of origin (seconds)
        orig_datetime (datetime): The datetime of origin (datetime format)
        resource_urls ([str]): The list of url of the new created resources
        api_info (ApiInfoModel): Information about the API call, important for accounting
        process_chain_list ([ProcessChainModel]): The list of process chains
        resp_type (str): What type of response, "pickle" or "json"

    Returns:
        A pickle string or json string

    """
    #if issubclass(response_model_class, ProcessingResponseModel) is False:
    #    raise IOError

    resp_dict = response_model_class(status=status,
                                     user_id=user_id,
                                     resource_id=resource_id,
                                     accept_timestamp=orig_time,
                                     accept_datetime=orig_datetime,
                                     timestamp=time.time(),
                                     datetime=str(datetime.now()),
                                     message=message,
                                     time_delta=time.time() - orig_time)

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
        resp_dict["urls"] = UrlModel(resources=resource_urls,
                                     status=str(status_url))
    if api_info is not None:
        resp_dict["api_info"] = api_info

    if resp_type == "pickle":
        return pickle.dumps([http_code, resp_dict])
    else:
        return jsonify(resp_dict)
