# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2024 mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
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

__license__ = "GPL-3.0-or-later"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

PC_RUNIVAR = {
    "list": [
        {
            "id": "set_region_to_raster",
            "module": "g.region",
            "inputs": [{"param": "raster", "value": "landuse96_28m"}],
            "flags": "g",
        },
        {
            "id": "get_stats",
            "module": "r.univar",
            "inputs": [{"param": "map", "value": "landuse96_28m"}],
            "flags": "g",
        },
        {
            "id": "calculation_scalling",
            "module": "r.mapcalc",
            "inputs": [
                {
                    "param": "expression",
                    "value": "test = (landuse96_28m - get_stats::stdout::min) "
                    "/ (get_stats::stdout::max - get_stats::stdout::min)",
                }
            ],
        },
        {
            "id": "get_stats_result",
            "module": "r.univar",
            "inputs": [{"param": "map", "value": "test"}],
            "stdout": {
                "id": "stats_zonal",
                "format": "kv",
                "delimiter": "=",
            },
            "flags": "g",
        },
    ],
    "version": "1",
}

PC_GLIST = {
    "list": [
        {"id": "print_region", "module": "g.region", "flags": "p"},
        {
            "id": "g_list_rasterpattern",
            "module": "g.list",
            "inputs": [
                {"param": "type", "value": "raster"},
                {"param": "pattern", "value": "l*"},
                {"param": "separator", "value": "comma"},
            ],
        },
        {
            "id": "set_region",
            "module": "g.region",
            "inputs": [
                {"param": "raster", "value": "g_list_rasterpattern::stdout"}
            ],
            "flags": "g",
        },
    ],
    "version": "1",
}


class AsyncProcessStdinParameterParserTestCase(ActiniaResourceTestCaseBase):
    def test_glist_parsing(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(PC_GLIST),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )
        self.assertIn(
            "landuse96_28m,lsat7_2002_10",
            resp["process_log"][1]["stdout"],
            "Process log is wrong",
        )
        self.assertIn(
            "raster=landuse96_28m,lsat7_2002_10",
            resp["process_log"][2]["parameter"],
            "Process parameters are set incorrectly.",
        )

    def test_runivar_parsing(self):
        min, max = 0, 21
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(PC_RUNIVAR),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )
        self.assertIn(f"min={min}", resp["process_log"][1]["stdout"])
        self.assertIn(f"max={max}", resp["process_log"][1]["stdout"])
        self.assertIn(
            f"- {min}) / ({max} - {min})",
            resp["process_log"][2]["parameter"][0],
            "Process parameters (min and max) are set incorrectly.",
        )
        self.assertEqual(
            float(resp["process_results"]["stats_zonal"]["max"]), 1
        )
        self.assertEqual(
            float(resp["process_results"]["stats_zonal"]["min"]), 0
        )


if __name__ == "__main__":
    unittest.main()
