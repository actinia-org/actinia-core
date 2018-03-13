# -*- coding: utf-8 -*-
"""
Raster layer resources
"""

from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger

from actinia_core.resources.async_persistent_processing import AsyncPersistentProcessing
from actinia_core.resources.async_resource_base import AsyncEphemeralResourceBase
from actinia_core.resources.common.redis_interface import enqueue_job
from actinia_core.resources.common.request_parser import glist_parser, extract_glist_parameters
from actinia_core.resources.common.exceptions import AsyncProcessError
from actinia_core.resources.common.response_models import ProcessingResponseModel
from actinia_core.resources.common.response_models import StringListProcessingResultResponseModel

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class MapsetLayersResource(AsyncEphemeralResourceBase):
    """Manage layers of a mapset
    """
    def __init__(self, layer_type):
        AsyncEphemeralResourceBase.__init__(self)
        self.layer_type = layer_type

    def _get(self, location_name, mapset_name):
        """Return a collection of all available layers
        in the provided mapset.

        Optionally can g.list parameters be provided::

            http://<url>?pattern="*"

        Args:
            location_name (str): The name of the location
            mapset_name (str): The name of the mapset

        Return:
            flask.Response: HTTP 200 and a list of layers as JSON document in case of success, HTTP 400 otherwise

        Example::

            {"Process result":
              [ "lsat7_2002_10",
                "lsat7_2002_20",
                "lsat7_2002_30",
                "lsat7_2002_40",
                "lsat7_2002_50",
                "lsat7_2002_61",
                "lsat7_2002_62",
                "lsat7_2002_70",
                "lsat7_2002_80"
              ],
              "Status": "success"
            }

        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name, mapset_name=mapset_name)
        args = glist_parser.parse_args()
        rdc.set_user_data((args, self.layer_type))

        enqueue_job(self.job_timeout, list_raster_layers, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    def _delete(self, location_name, mapset_name):
        """Remove a list of layers identified by a pattern

        The g.remove "pattern" parameters must be provided::

            http://<url>?pattern="*"

        Args:
            location_name (str): The name of the location
            mapset_name (str): The name of the mapset

        Return:
            flask.Response: HTTP 200 in case of success, HTTP 400 otherwise

        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name)
        args = glist_parser.parse_args()
        rdc.set_user_data((args, self.layer_type))

        enqueue_job(self.job_timeout, remove_raster_layers, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    def _put(self, location_name, mapset_name):
        """Rename a list of layers

        The old names and new names must be provided as a
        list of tuples:

            [(a, a_new),(b, b_new),(c, c_new), ...]

        Args:
            location_name (str): The name of the location
            mapset_name (str): The name of the mapset

        Return:
            flask.Response: HTTP 200 in case of success, HTTP 400 otherwise

        """
        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name, mapset_name=mapset_name)
        args = glist_parser.parse_args()

        # Analyse the name list
        if isinstance(self.request_data, list) is False:
            self.raise_invalid_usage("Wrong format for layer list")

        if len(self.request_data) == 0:
            self.raise_invalid_usage("Empty layer list")

        for name_tuple in self.request_data:
            if isinstance(name_tuple, tuple) is False and isinstance(name_tuple, list) is False:
                self.raise_invalid_usage("List entry is not a tuple or list")

            if len(name_tuple) != 2:
                self.raise_invalid_usage("A tuple of layer names must have 2 entries")

        rdc.set_user_data((args, self.layer_type))

        enqueue_job(self.job_timeout, rename_raster_layers, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


class RasterLayersResource(MapsetLayersResource):
    """Manage raster layers of a mapset
    """

    def __init__(self):
        MapsetLayersResource.__init__(self, layer_type="raster")

    @swagger.doc({
        'tags': ['raster map layer management'],
        'description': 'Return a list of raster map layer names that are located in a specific location/mapset.'
                       ' Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location that should be accessed',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset from which the raster map layers should be listed',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            },
            {
                'name': 'pattern',
                'description': 'A parameter passed to g.list for raster map'
                               ' layer selection, eg.: http://<url>?pattern="*"',
                'required': False,
                'in': 'query',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns a list of raster map layers and the log '
                               'of the process chain that was used to create the response.',
                'schema':StringListProcessingResultResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why listing of '
                               'raster map layers did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name):
        """Return a list of raster map layer names that are located in a specific location/mapset
        """
        return self._get(location_name, mapset_name)

    @swagger.doc({
        'tags': ['raster map layer management'],
        'description': 'Rename a single raster map layer or a list of raster map layers that '
                       'are located in a specific location/mapset. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location that should be accessed',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset from which the raster map layers should be renamed',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'rename_list',
                'description': 'A list of raster name tuples [(a, a_new),(b, b_new),(c, c_new), ...]',
                'required': True,
                'in': 'body',
                'schema': {"type":"string"}
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns the log '
                               'of the process chain that was used to create the response.',
                'schema':ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why listing of '
                               'raster map layers did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def put(self, location_name, mapset_name):
        """Rename a single raster map layer or a list of raster map layers that are located in a specific location/mapset
        """
        return self._put(location_name, mapset_name)

    @swagger.doc({
        'tags': ['raster map layer management'],
        'description': 'Delete a single raster map layer or a list of raster map layer names that '
                       'are located in a specific location/mapset. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location that should be accessed',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset from which the raster map layers should be deleted',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'pattern',
                'description': 'A parameter passed for g.remove to remove a list of raster map '
                               'layers, to remove all eg.: http://<url>?pattern="*"',
                'required': False,
                'in': 'query',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns the log '
                               'of the process chain that was used to create the response.',
                'schema':ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why deletion of '
                               'raster map layers did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name):
        """Delete a single raster map layer or a list of raster map layer names that are located in a specific location/mapset
        """
        return self._delete(location_name, mapset_name)


class VectorLayersResource(MapsetLayersResource):
    """Manage vector layers of a mapset
    """
    def __init__(self):
        MapsetLayersResource.__init__(self, layer_type="vector")

    @swagger.doc({
        'tags': ['vector map layer management'],
        'description': 'Return a list of vector map layer names that are located in a specific location/mapset.'
                       ' Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location that should be accessed',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset from which the vector map layers should be listed',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            },
            {
                'name': 'pattern',
                'description': 'A parameter passed to g.list for vector map'
                               ' layer selection, eg.: http://<url>?pattern="*"',
                'required': False,
                'in': 'query',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns a list of vector map layers and the log '
                               'of the process chain that was used to create the response.',
                'schema':StringListProcessingResultResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why listing of '
                               'vector map layers did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name):
        """Return a list of vector map layer names that are located in a specific location/mapset
        """
        return self._get(location_name, mapset_name)

    @swagger.doc({
        'tags': ['vector map layer management'],
        'description': 'Rename a single vector map layer or a list of vector map layers that '
                       'are located in a specific location/mapset. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location that should be accessed',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset from which the vector map layers should be renamed',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'rename_list',
                'description': 'A list of vector name tuples [(a, a_new),(b, b_new),(c, c_new), ...]',
                'required': True,
                'in': 'body',
                'schema': {"type":"string"}
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns the log '
                               'of the process chain that was used to create the response.',
                'schema':ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why listing of '
                               'vector map layers did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def put(self, location_name, mapset_name):
        """Rename a single vector map layer or a list of vector map layers that are located in a specific location/mapset
        """
        return self._put(location_name, mapset_name)

    @swagger.doc({
        'tags': ['vector map layer management'],
        'description': 'Delete a single vector map layer or a list of vector map layer names that '
                       'are located in a specific location/mapset. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location that should be accessed',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset from which the vector map layers should be deleted',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'pattern',
                'description': 'A parameter passed for g.remove to remove a list of vector map '
                               'layers, to remove all eg.: http://<url>?pattern="*"',
                'required': False,
                'in': 'query',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns the log '
                               'of the process chain that was used to create the response.',
                'schema':ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why deletion of '
                               'vector map layers did not succeeded',
                'schema':ProcessingResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name):
        """Delete a single vector map layer or a list of vector map layer names that are located in a specific location/mapset
        """
        return self._delete(location_name, mapset_name)


def list_raster_layers(*args):
    processing = AsyncPersistentListLayers(*args)
    processing.run()


class AsyncPersistentListLayers(AsyncPersistentProcessing):
    """List all map layers (raster, vector) of a specific mapset,
     dependent on the provided type.
    """

    def __init__(self, *args):
        AsyncPersistentProcessing.__init__(self, *args)
        self.response_model_class = StringListProcessingResultResponseModel

    def _execute(self):

        self._setup()

        args, layer_type = self.data
        self.required_mapsets.append(self.target_mapset_name)

        options = extract_glist_parameters(args)

        pc = {"1":{"module":"g.list","inputs":{}}}

        for key in options:
            pc["1"]["inputs"][key] = options[key]

        pc["1"]["inputs"]["mapset"] = self.target_mapset_name
        pc["1"]["inputs"]["type"] = layer_type

        self.skip_region_check = True
        process_chain = self._validate_process_chain(skip_permission_check=True,
                                                     process_chain=pc)
        self._create_temp_database(self.required_mapsets)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_chain(process_chain)

        raster_layers_with_mapset = []
        raster_layers = self.module_output_log[0]["stdout"].split()

        for raster_layer in raster_layers:
            raster_layers_with_mapset.append(raster_layer.strip())

        self.module_results = raster_layers_with_mapset


def remove_raster_layers(*args):
    processing = AsyncPersistentRemoveLayers(*args)
    processing.run()


class AsyncPersistentRemoveLayers(AsyncPersistentProcessing):
    """Remove layers in a mapset
    """

    def __init__(self, *args):

        AsyncPersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()

        args, layer_type = self.data
        self.required_mapsets.append(self.target_mapset_name)

        options = extract_glist_parameters(args)

        pc = {"1":{"module":"g.remove","inputs":{}, "flags":"f"}}
        for key in options:
            pc["1"]["inputs"][key] = options[key]
        pc["1"]["inputs"]["type"] = layer_type

        self.skip_region_check = True
        process_chain = self._validate_process_chain(skip_permission_check=True,
                                                     process_chain=pc)
        self._create_temp_database(self.required_mapsets)
        self._check_lock_target_mapset()
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_chain(process_chain)

        if "WARNING: No data base element files found" in "\n".join(self.module_output_log[0]["stderr"]):
            raise AsyncProcessError("<%s> layer not found"%layer_type)

        self.finish_message = "Successfully removed %s layers."%layer_type

def rename_raster_layers(*args):
    processing = AsyncPersistentRenameLayers(*args)
    processing.run()


class AsyncPersistentRenameLayers(AsyncPersistentProcessing):
    """Rename raster layers in a mapset
    """

    def __init__(self, *args):

        AsyncPersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()

        args, layer_type = self.data
        self.required_mapsets.append(self.target_mapset_name)

        # List format must be
        # [(a, a_new),(b, b_new),(c, c_new), ...]
        name_list = list()
        for old_name, new_name in  self.request_data:
            name_list.append("%s,%s"%(old_name, new_name))
        name_string = ",".join(name_list)

        pc = {"1":{"module":"g.rename","inputs":{layer_type:name_string}}}

        self.skip_region_check = True
        process_chain = self._validate_process_chain(skip_permission_check=True,
                                                     process_chain=pc)
        self._create_temp_database(self.required_mapsets)
        self._check_lock_target_mapset()
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_chain(process_chain)

        if "WARNING: " in "\n".join(self.module_output_log[0]["stderr"]):
            if "not found" in "\n".join(self.module_output_log[0]["stderr"]):
                raise AsyncProcessError("Error while renaming map layers")

        self.finish_message = "Successfully renamed %s layers."%layer_type
