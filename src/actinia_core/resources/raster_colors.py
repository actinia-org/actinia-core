# -*- coding: utf-8 -*-
"""
Raster colors management

TODO: Tests required
"""

from flask import jsonify, make_response
from .async_ephemeral_processing import AsyncEphemeralProcessing
from .async_persistent_processing import AsyncPersistentProcessing
from .async_resource_base import AsyncEphemeralResourceBase
from .common.redis_interface import enqueue_job
import tempfile
import os
import atexit

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class SyncPersistentRasterColorsResource(AsyncEphemeralResourceBase):
    """Manage the color table
    """

    def get(self, location_name, mapset_name, raster_name):
        """Prepare and enqueue

        Args:
            location_name: Name of the location
            mapset_name: Name of the mapset
            raster_name: name of the raster map

        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=raster_name)

        enqueue_job(self.job_timeout, start_job_colors_out, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    def post(self, location_name, mapset_name, raster_name):
        """Set the color table from JSON definition

        The JSON input should contain the color rules, a predefined color table
        or a raster layer:

            {"rules":["1 0:0:0", "default 255:255:255"]}
            {"color":"gbr"}
            {"raster":"elevation"}

        Args:
            location_name: Name of the location
            mapset_name: Name of the mapset
            raster_name: name of the raster map

        Raises:
            InvalidUsage in case the color definition is false

        """
        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=raster_name)

        if isinstance(self.request_data, dict) is False:
            return self.get_error_response(message="Missing raster color definition in JSON content")

        if len(self.request_data) > 1:
            return self.get_error_response(message="The color settings expect a single entry")

        if "rules" in self.request_data:
            if isinstance(self.request_data["rules"], list) is False:
                return self.get_error_response(message="Wrong rules definitions in JSON content")
        elif "color" in self.request_data:
            pass
        elif "raster" in self.request_data:
            if "@" not in self.request_data["raster"]:
                return self.get_error_response(message="Missing mapset definition in raster name")
        else:
            return self.get_error_response(message="Missing raster color definitions in JSON content")

        enqueue_job(self.job_timeout, start_job_from_rules, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


def start_job_colors_out(*args):
    processing = AsyncEphemeralRasterColorsOutput(*args)
    processing.run()


class AsyncEphemeralRasterColorsOutput(AsyncEphemeralProcessing):

    def __init__(self, *args):
        AsyncEphemeralProcessing.__init__(self, *args)

    def _execute(self, skip_permission_check=True):

        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.mapset_name)

        result_file = tempfile.mktemp(suffix=".color", dir=self.temp_file_path)

        self.request_data = {"1":{"module":"r.colors.out","inputs":{"map":"", "rules":""}}}
        self.request_data["1"]["inputs"]["map"] = raster_name + "@" + self.mapset_name
        self.request_data["1"]["inputs"]["rules"] = result_file

        # Run the selected modules
        process_list = self._create_temporary_grass_environment_and_process_list(skip_permission_check=True)
        self._execute_process_list(process_list)

        result = open(result_file, "r").read().strip().split("\n")

        self.module_results = result


def start_job_from_rules(*args):
    processing = AsyncPersistentRasterColorsRules(*args)
    processing.run()


class AsyncPersistentRasterColorsRules(AsyncPersistentProcessing):
    """Set the color table of a raster map from color rules

    Perform the processing in the original mapset
    """

    def __init__(self, *args):

        AsyncPersistentProcessing.__init__(self, *args)

    def _execute(self, skip_permission_check=True):

        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        options = self.request_data

        pc = {"1":{"module":"r.colors","inputs":{}}}
        pc["1"]["inputs"]["map"] = raster_name + "@" + self.target_mapset_name

        if "rules" in options:
            rules_file = tempfile.mktemp(suffix=".color")
            rules = open(rules_file, "w")

            for line in options["rules"]:
                rules.write(line + "\n")
            rules.close()

            pc["1"]["inputs"]["rules"] = rules_file
            atexit.register(remove_rules_file, rules_file)
        else:
            for option in options:
                pc["1"]["inputs"][option] = options[option]

        process_list = self._validate_process_chain(process_chain=pc,
                                                    skip_permission_check=True)
        self._check_lock_target_mapset()
        self._create_temp_database(self.required_mapsets)
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_list(process_list)


def remove_rules_file(rules_file):
    os.remove(rules_file)
