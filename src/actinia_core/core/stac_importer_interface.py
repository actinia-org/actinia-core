# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2021 mundialis GmbH & Co. KG
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
This code shows the STACImporter model which helps actinia core
to save and manage the STAC collections stored through the actinia STAC plugin
"""

# from PyQt4.QtCore import *
# from PyQt4.QtXml import *
# from config import global_config

__license__ = "GPLv3"
__author__ = "Jorge Herrera"
__copyright__ = "Copyright 2021, mundialis GmbH & Co. KG"
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
    @staticmethod
    def _get_search_root(stac_collection_id):
        stac_from_actinia = callStacCollection(stac_collection_id)
        try:
            stac_json = json.loads(stac_from_actinia)
        except Exception:
            stac_json = stac_from_actinia

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

    @staticmethod
    def _apply_filter(stac_root_search, stac_name, interval, bbox, filter):
        search_body = {
            "collections": [stac_name],
        }
        search_body["query"] = filter

        search_body["bbox"] = bbox

        search_body["interval"] = interval

        stac_search = requests.post(stac_root_search, json=search_body)

        full_filtered_result = stac_search.json()

        if (
            "features" in full_filtered_result
            and len(full_filtered_result["features"]) > 0
        ):
            return full_filtered_result
        else:
            stac_search = requests.get(stac_root_search, json=search_body)
            full_filtered_result = stac_search.json()

            if (
                "features" in full_filtered_result
                and len(full_filtered_result["features"]) > 0
            ):
                return full_filtered_result
            else:
                raise AsyncProcessError("Not matched found")

    @staticmethod
    def _get_filtered_bands(stac_items, semantic_label):
        band_roots = {}

        for feature in stac_items["features"]:
            item_date = feature["properties"]["datetime"]
            for key, value in feature["assets"].items():
                if "eo:bands" in value:
                    if "common_name" in value["eo:bands"][0]:
                        if (
                            value["eo:bands"][0]["common_name"]
                            in semantic_label
                            or value["eo:bands"][0]["name"] in semantic_label
                            or semantic_label == []
                        ):
                            band_name = value["eo:bands"][0]["name"]
                            if band_name not in band_roots:
                                band_roots[band_name] = {}
                            feature_id = feature["id"]
                            item_link = feature["assets"][band_name]["href"]
                            band_roots[band_name]["name_id"] = feature_id
                            band_roots[band_name]["url"] = item_link
                            band_roots[band_name]["datetime"] = item_date
        return band_roots

    def _stac_import(
        self,
        stac_collection_id=None,
        semantic_label=None,
        interval=None,
        bbox=None,
        filter=None,
        strd_name=None,
    ):
        if has_plugin:
            try:
                stac_name = stac_collection_id.split(".")[3]
            except Exception:
                raise AsyncProcessError(
                    "The source has not the right structure"
                )

            stac_root = self._get_search_root(stac_collection_id)

            stac_filtered = self._apply_filter(
                stac_root, stac_name, interval, bbox, filter
            )

            stac_result = self._get_filtered_bands(
                stac_filtered, semantic_label
            )

            stac_processes = []

            # Create the strds

            # dd/mm/YY H:M:S

            exec_params = [
                "type=strds",
                "temporaltype=absolute",
                "output=%s" % strd_name,
                "title=%s" % strd_name,
                "description=%s" % f"{stac_collection_id}",
            ]

            p = Process(
                exec_type="grass",
                executable="t.create",
                executable_params=exec_params,
                id=f"t_create_{os.path.basename(stac_name)}",
                skip_permission_check=True,
            )

            stac_processes.append(p)

            for key, value in stac_result.items():
                item_id = value["name_id"]
                output_name = f"{strd_name}_{item_id}_{key}"

                url_prefix = "/vsicurl/"
                # Checking if the URL belongs to S3
                if "s3:" in value["url"]:
                    url_prefix = "/vsis3/"

                # Upload the image to GRASS
                exec_params = [
                    "input=%s" % url_prefix + value["url"],
                    "output=%s" % output_name,
                    "extent=region",
                ]

                import_raster = Process(
                    exec_type="grass",
                    executable="r.import",
                    executable_params=exec_params,
                    id=f"r_import_{output_name}",
                    skip_permission_check=True,
                )

                stac_processes.append(import_raster)

                # Setting the Semantic Label
                exec_params_sl = [
                    "map=%s" % output_name,
                    "semantic_label=%s" % key,
                ]

                sem_lab = Process(
                    exec_type="grass",
                    executable="r.support",
                    executable_params=exec_params_sl,
                    id=f"r_semantic_label_{output_name}",
                    skip_permission_check=True,
                )

                stac_processes.append(sem_lab)

                # Register the raster to the STDR
                exec_params_stdr = [
                    "input=%s" % strd_name,
                    "type=raster",
                    "maps=%s" % output_name,
                    "start=%s" % value["datetime"],
                ]

                registration = Process(
                    exec_type="grass",
                    executable="t.register",
                    executable_params=exec_params_stdr,
                    id=f"t_register_{output_name}",
                    skip_permission_check=True,
                )

                stac_processes.append(registration)
        else:
            raise AsyncProcessError("Actinia STAC plugin is not installed")

        return stac_processes

    def get_stac_import_download_commands(
        self,
        stac_entry,
        config=None,
        temp_file_path=None,
        message_logger=None,
        send_resource_update=None,
    ):
        """Helper method to get the stac import and download commands.
        Args:
            stac_entry (dict): stac_entry of the import description list
        Returns:
            stac_commands: The stac download and import commands
        """
        # Check for band information
        # TODO check config, temp_file_path, message_logger,
        # send_resource_update
        stac_entry_source = stac_entry["import_descr"]["source"]

        if "semantic_label" in stac_entry["import_descr"]:
            stac_semantic_label = stac_entry["import_descr"]["semantic_label"]

        if "extent" in stac_entry["import_descr"]:
            if (
                "spatial"
                and "temporal" not in stac_entry["import_descr"]["extent"]
            ):
                raise AsyncProcessError(
                    "Unknown spatial or/and temporal parameters"
                    "in the process chain definition"
                )

            if "bbox" in stac_entry["import_descr"]["extent"]["spatial"]:
                stac_extent = stac_entry["import_descr"]["extent"]["spatial"][
                    "bbox"
                ][0]

            if "interval" in stac_entry["import_descr"]["extent"]["temporal"]:
                interval = stac_entry["import_descr"]["extent"]
                interval = interval["temporal"]["interval"][0]
                stac_interval = interval

        stac_filter = {}
        if "filter" in stac_entry["import_descr"]:
            stac_filter = stac_entry["import_descr"]["filter"]

        stac_name = stac_entry["value"]

        stac_command = self._stac_import(
            stac_collection_id=stac_entry_source,
            semantic_label=stac_semantic_label,
            interval=stac_interval,
            bbox=stac_extent,
            filter=stac_filter,
            strd_name=stac_name,
        )
        return stac_command
