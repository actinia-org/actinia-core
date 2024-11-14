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
Tests: Raster layer test
"""
import unittest
from pprint import pprint
from flask.json import loads as json_load
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


class RasterLayerTestCase(ActiniaResourceTestCaseBase):
    def test_raster_layer_get_colors(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/colors",
            headers=self.user_auth_header,
        )
        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        colors = json_load(rv.data)["process_results"]
        self.assertTrue(len(colors) == 8)

    def test_raster_layer_set_colors(self):
        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        # Create
        postbody = {
            "list": [
                {
                    "id": "set_region",
                    "module": "g.region",
                    "inputs": [
                        {"param": "n", "value": "228500"},
                        {"param": "s", "value": "215000"},
                        {"param": "e", "value": "645000"},
                        {"param": "w", "value": "630000"},
                        {"param": "ewres", "value": "50"},
                        {"param": "nsres", "value": "50"},
                    ],
                },
                {
                    "id": "create_raster",
                    "module": "r.mapcalc",
                    "inputs": [
                        {"param": "expression", "value": "test_layer = 1"}
                    ],
                },
            ],
            "version": "1",
        }
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/processing_async",
            headers=self.user_auth_header,
            data=json_dumps(postbody),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=200,
            status="finished",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        rules = {
            "rules": [
                "1 0:0:0",
            ]
        }

        # Set the color table
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer/colors",
            headers=self.user_auth_header,
            data=json_dumps(rules),
            content_type="application/json",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        rules = {"color": "elevation"}

        # Set the color table
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer/colors",
            headers=self.user_auth_header,
            data=json_dumps(rules),
            content_type="application/json",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        rules = {"raster": "elevation@PERMANENT"}

        # Set the color table
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer/colors",
            headers=self.user_auth_header,
            data=json_dumps(rules),
            content_type="application/json",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Delete
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer",
            headers=self.user_auth_header,
        )
        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_1_raster_layer_set_colors_errors(self):
        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        # Create
        postbody = {
            "list": [
                {
                    "id": "set_region",
                    "module": "g.region",
                    "inputs": [
                        {"param": "n", "value": "228500"},
                        {"param": "s", "value": "215000"},
                        {"param": "e", "value": "645000"},
                        {"param": "w", "value": "630000"},
                        {"param": "ewres", "value": "50"},
                        {"param": "nsres", "value": "50"},
                    ],
                },
                {
                    "id": "create_raster",
                    "module": "r.mapcalc",
                    "inputs": [
                        {"param": "expression", "value": "test_layer = 1"}
                    ],
                },
            ],
            "version": "1",
        }
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/processing_async",
            headers=self.user_auth_header,
            data=json_dumps(postbody),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )
        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        rules = {
            "rules": [
                "wrong format",
            ]
        }

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer/colors",
            headers=self.user_auth_header,
            data=json_dumps(rules),
            content_type="application/json",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)

        rules = {"rules": "blub"}

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer/colors",
            headers=self.user_auth_header,
            data=json_dumps(rules),
            content_type="application/json",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Two rules
        rules = {"color": "elevation", "raster": "elevation@PERMANENT"}

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer/colors",
            headers=self.user_auth_header,
            data=json_dumps(rules),
            content_type="application/json",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Wrong format
        rules = {"nonsense": "bla"}

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer/colors",
            headers=self.user_auth_header,
            data=json_dumps(rules),
            content_type="application/json",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Wrong format
        rules = [1, 2, 3]

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer/colors",
            headers=self.user_auth_header,
            data=json_dumps(rules),
            content_type="application/json",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Raster layer not found
        rules = {"raster": "elevation_nope@PERMANENT"}

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer/colors",
            headers=self.user_auth_header,
            data=json_dumps(rules),
            content_type="application/json",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)

        # No mapset in name
        rules = {"raster": "elevation"}

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer/colors",
            headers=self.user_auth_header,
            data=json_dumps(rules),
            content_type="application/json",
        )

        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Delete
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers/test_layer",
            headers=self.user_auth_header,
        )
        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_raster_layer_colors_error_1(self):
        # Raster does not exist
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevat/colors",
            headers=self.user_auth_header,
        )
        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)
        self.assertTrue("Error while running executable <r.colors.out" in log)


if __name__ == "__main__":
    unittest.main()
