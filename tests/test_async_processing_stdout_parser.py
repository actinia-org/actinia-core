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
Tests: Async Process stdout parser test case
"""
import unittest
from flask.json import dumps as json_dumps

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

process_chain = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster", "value": "elevation@PERMANENT"},
                {"param": "res", "value": "5000"},
            ],
            "stdout": {"id": "region", "format": "kv", "delimiter": "="},
            "flags": "g",
        },
        {
            "id": "2",
            "module": "r.out.ascii",
            "inputs": [
                {"param": "input", "value": "elevation@PERMANENT"},
                {"param": "precision", "value": "0"},
            ],
            "stdout": {"id": "elevation", "format": "table", "delimiter": " "},
            "flags": "h",
        },
        {
            "id": "3",
            "module": "g.list",
            "inputs": [{"param": "type", "value": "raster"}],
            "stdout": {"id": "map_list", "format": "list", "delimiter": "\n"},
        },
        {
            "id": "4",
            "module": "r.univar",
            "inputs": [{"param": "map", "value": "elevation@PERMANENT"}],
            "stdout": {"id": "stats", "format": "kv", "delimiter": "="},
            "flags": "g",
        },
        {
            "id": "5",
            "module": "r.univar",
            "inputs": [
                {"param": "map", "value": "elevation@PERMANENT"},
                {"param": "zones", "value": "basin_50K@PERMANENT"},
                {"param": "separator", "value": "pipe"},
            ],
            "stdout": {
                "id": "stats_zonal",
                "format": "table",
                "delimiter": "|",
            },
            "flags": "t",
        },
    ],
}

r_what = {
    "list": [
        {
            "module": "g.region",
            "id": "g_region_1",
            "inputs": [
                {"param": "raster", "value": "landuse96_28m@PERMANENT"}
            ],
            "stdout": {"id": "region", "format": "kv", "delimiter": "="},
            "flags": "ga",
        },
        {
            "module": "r.what",
            "id": "r_what_1",
            "verbose": True,
            "flags": "nfic",
            "inputs": [
                {"param": "map", "value": "landuse96_28m@PERMANENT"},
                {
                    "param": "coordinates",
                    "value": "633614.08,224125.12,632972.36,225382.87",
                },
                {"param": "null_value", "value": "null"},
                {"param": "separator", "value": "pipe"},
            ],
            "stdout": {"id": "sample", "format": "table", "delimiter": "|"},
        },
    ],
    "version": "1",
}


class AsyncProcessStdoutParserTestCase(ActiniaResourceTestCaseBase):
    def test_output_parsing(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain),
            content_type="application/json",
        )

        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        self.assertTrue("region" in resp["process_results"])
        self.assertTrue("elevation" in resp["process_results"])
        self.assertTrue("map_list" in resp["process_results"])
        self.assertTrue("stats" in resp["process_results"])
        self.assertTrue("stats_zonal" in resp["process_results"])
        self.assertTrue("elevation" in resp["process_results"]["map_list"])
        self.assertEqual(resp["process_results"]["stats"]["cells"], "9")
        self.assertEqual(len(resp["process_results"]["elevation"]), 3)
        self.assertEqual(len(resp["process_results"]["region"]), 11)
        self.assertEqual(len(resp["process_results"]["stats_zonal"]), 7)
        self.assertEqual(len(resp["process_results"]["stats_zonal"][0]), 14)

    def test_output_parsing_r_what(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(r_what),
            content_type="application/json",
        )

        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        process_results = {
            "region": {
                "cells": "249324",
                "cols": "526",
                "e": "644971",
                "ewres": "28.5",
                "n": "228527.25",
                "nsres": "28.5",
                "projection": "99",
                "rows": "474",
                "s": "215018.25",
                "w": "629980",
                "zone": "0",
            },
            "sample": [
                [
                    "easting",
                    "northing",
                    "site_name",
                    "landuse96_28m@PERMANENT",
                    "landuse96_28m@PERMANENT_label",
                ],
                ["633614.08", "224125.12", "", "15", "Southern Yellow Pine"],
                [
                    "632972.36",
                    "225382.87",
                    "",
                    "4",
                    "Managed Herbaceous Cover",
                ],
            ],
        }

        self.assertEqual(resp["process_results"], process_results)


if __name__ == "__main__":
    unittest.main()
