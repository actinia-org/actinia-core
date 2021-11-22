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
This code shows the STACImporter model which help actinia core
to save and manage the STAC collections stored through the actinia STAC plugin

"""

# from PyQt4.QtCore import *
# from PyQt4.QtXml import *
# from config import global_config

__license__ = "GPLv3"
__author__ = "Jorge Herrera"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "__mundialis__"
__email__ = "info@mundialis.de"


import requests
import os
import json

from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.core.common.process_object import Process
try:
    from actinia_stac_plugin.core.stac_collection_id import callStacCollection
    has_plugin = True
except Exception:
    has_plugin = False


class STACImporter:

    @classmethod
    def stac_import(self, stac_collecition_id, semantic_label, interval, bbox, filter):

        if has_plugin:
            try:
                stac_name = stac_collecition_id.split(".")[3]
            except Exception:
                raise AsyncProcessError("The source has not the right structure")

            stac_root = self.get_search_root(stac_collecition_id)

            stac_filtered = self.apply_filter(stac_root, stac_name,
                                              interval, bbox, filter)

            stac_result = self.get_filtered_bands(stac_filtered, semantic_label)

            stac_processes = []

            for key, value in stac_result.items():

                for name_id, url in value.items():

                    output_name = stac_name + "_" + key + "_" + name_id

                    # From Here Onwards, the Process build starts
                    exec_params = ["input=%s" % "/vsicurl/"+url,
                                   "output=%s" % output_name,
                                   "-o"]

                    p = Process(
                        exec_type="grass",
                        executable="r.in.gdal",
                        executable_params=exec_params,
                        id=f"r_gdal_{os.path.basename(output_name)}",
                        skip_permission_check=True
                    )

                    stac_processes.append(p)
        else:
            raise AsyncProcessError("Actinia STAC plugin is not installed")

        return stac_processes

    @classmethod
    def get_search_root(self, stac_collecition_id):

        stac_from_actinia = callStacCollection(stac_collecition_id)

        stac_json = json.loads(stac_from_actinia)

        for item in stac_json["links"]:
            if item["rel"] == "root":
                stac_url = item["href"]

                if "?" in stac_url:
                    stac_url = stac_url.split("?")[0]

                if stac_url.endswith("/"):
                    stac_root_search = stac_url + "search"
                else:
                    stac_root_search = stac_url + "/search"

        return stac_root_search

    @classmethod
    def apply_filter(self, stac_root_search, stac_name, interval, bbox, filter):

        search_body = {
            "collections": [stac_name],
        }
        search_body["query"] = filter

        search_body["bbox"] = bbox

        search_body["interval"] = interval

        stac_search = requests.post(
            stac_root_search,
            json=search_body
        )

        full_filtered_result = stac_search.json()

        if "features" in full_filtered_result:
            return full_filtered_result
        else:
            raise AsyncProcessError(full_filtered_result)

    @classmethod
    def get_filtered_bands(self, stac_items, semantic_label):
        band_roots = {}

        for feature in stac_items["features"]:
            for key, value in feature["assets"].items():
                if "eo:bands" in value:
                    if "common_name" in value["eo:bands"][0]:
                        if value["eo:bands"][0]["common_name"] in semantic_label:
                            band_name = value["eo:bands"][0]["name"]
                            if band_name not in band_roots:
                                band_roots[band_name] = {}
                            feature_id = feature["id"]
                            item_link = feature["assets"][band_name]["href"]
                            band_roots[band_name][feature_id] = item_link
                        elif value["eo:bands"][0]["name"] in semantic_label:
                            band_name = value["eo:bands"][0]["name"]
                            if band_name not in band_roots:
                                band_roots[band_name] = {}
                            feature_id = feature["id"]
                            item_link = feature["assets"][band_name]["href"]
                            band_roots[band_name][feature_id] = item_link
        return band_roots

    @classmethod
    def get_stac_import_download_commands(self,
                                          entry,
                                          config=None,
                                          temp_file_path=None,
                                          message_logger=None,
                                          send_resource_update=None):

        """Helper method to get the stac import and download commands.

            Args:
                entry (dict): Entry of the import description list

            Returns:
                stac_commands: The stac download and import commands
        """
        # Check for band information
        # TODO check config, temp_file_path, message_logger, send_resource_update
        stac_entry_source = entry["import_descr"]["source"]

        if "semantic_label" in entry["import_descr"]:
            stac_semantic_label = entry["import_descr"]["semantic_label"]

        if "extent" in entry["import_descr"]:
            if "spatial" and "temporal" not in entry["import_descr"]["extent"]:
                raise AsyncProcessError("Unknown spatial or/and temporal parameters"
                                        "in the process chain definition")

            if "bbox" in entry["import_descr"]["extent"]["spatial"]:
                stac_extent = entry["import_descr"]["extent"]["spatial"]["bbox"][0]

            if "interval" in entry["import_descr"]["extent"]["temporal"]:
                interval = entry["import_descr"]["extent"]["temporal"]["interval"][0]
                stac_interval = interval

            if "filter" in entry["import_descr"]:
                stac_filter = entry["import_descr"]["filter"]

            stac_command = \
                self.stac_import(
                    stac_collecition_id=stac_entry_source,
                    semantic_label=stac_semantic_label,
                    interval=stac_interval,
                    bbox=stac_extent,
                    filter=stac_filter)
            return stac_command
            # raise AsyncProcessError("STAC import is comming soon")
