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

from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.core.common.process_object import Process
from actinia_core.core.common.app import URL_PREFIX


class STAImporter(object):

    def stac_import(self, stac_collecition_id, stac_name, semantic_label, bbox, filter):

        try:
            stac_name = stac_collecition_id.split(".")[3]
        except NameError:
            raise AssertionError("The sourcs has not the right structure")

        stac_root = self.get_search_root(stac_collecition_id)

        stac_filtered = self.apply_filter(stac_root, stac_name, bbox, filter)

        stac_result = self.get_filtered_bands(stac_filtered, semantic_label)

        exec_params = ["input=%s" % stac_result[0], "output=%s" % stac_collecition_id]

        p = Process(
            exec_type="grass",
            executable="r.in.gdal",
            executable_params=exec_params,
            id=f"r_gdal_{os.path.basename(stac_collecition_id)}",
            skip_permission_check=True
        )

        return p

    def get_search_root(self, stac_collecition_id):
        stac_from_actinia = requests.get(
            URL_PREFIX + "/stac/" + stac_collecition_id)

        stac_json = stac_from_actinia.json()

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

    def apply_filter(self, stac_root_search, stac_name, bbox, filter):

        search_body = {
            "collections": [stac_name],
        }
        search_body["query"] = filter

        search_body["bbox"] = bbox

        stac_search = requests.post(
            stac_root_search,
            json=search_body
        )

        full_filtered_result = stac_search.json()

        return full_filtered_result

    def get_filtered_bands(self, stac_items, semantic_label):
        band_roots = {}
        for feature in stac_items["features"]:
            for key, value in feature["assets"].items():
                if "eo:bands" in value:
                    if "common_name" in value["eo:bands"][0]:
                        if value["eo:bands"][0]["common_name"] in semantic_label:
                            band_name = value["eo:bands"][0]["name"]
                            if band_name not in band_roots:
                                band_roots[band_name] = []
                            band_roots[band_name].append(
                                feature["assets"][band_name]["href"])
        return band_roots

    def _get_stac_import_download_commands(self, entry):

        """Helper method to get the stac import and download commands.

            Args:
                entry (dict): Entry of the import description list

            Returns:
                stac_commands: The stac download and import commands
        """
        # Check for band information

        stac_source = entry["import_descr"]["source"]

        if "semantic_label" in entry["import_descr"]:
            stac_semantic_label = entry["import_descr"]["semantic_label"]

        if "extent" in entry["import_descr"]:
            if "spatial" and "temporal" not in entry["import_descr"]["extent"]:
                raise AsyncProcessError("Unknown spatial or/and temporal parameters"
                                        "in the process chain definition")

            if "spatial" in entry["import_descr"]["extent"]:
                if "bbox" in entry["import_descr"]["extent"]["spatial"]:
                    stac_extent = entry["import_descr"]["extent"]

                if "temporal" in entry["import_descr"]["extent"]:
                    if "interval" in entry["import_descr"]["extent"]["temporal"]:
                        stac_extent = entry["import_descr"]["extent"]

                if "filter" in entry["import_descr"]:
                    stac_filter = entry["import_descr"]["filter"]

            stac_command = \
                self.stac_import(
                    stac_source=stac_source,
                    semantic_label=stac_semantic_label,
                    extent=stac_extent,
                    filter=stac_filter)
            stac_command
            raise AsyncProcessError("STAC import is comming soon")
