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
Tests: List raster layers test case
"""
from flask.json import loads as json_loads, dumps as json_dumps
import unittest

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


class ListRasterLayersTestCase(ActiniaResourceTestCaseBase):
    def create_raster_layer(self, mapset_name, raster_name):
        # Remove potentially existing raster layer
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{mapset_name}/raster_layers/{raster_name}",
            headers=self.user_auth_header,
        )
        # print(rv.data)
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
                        {
                            "param": "expression",
                            "value": "%s = 1" % raster_name,
                        }
                    ],
                },
            ],
            "version": "1",
        }
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{mapset_name}/processing_async",
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
        # print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_list_raster_layers(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers",
            headers=self.user_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        map_list = json_loads(rv.data)["process_results"]
        self.assertTrue("elevation" in map_list)
        self.assertTrue("aspect" in map_list)
        self.assertTrue("lsat7_2002_10" in map_list)
        self.assertTrue("slope" in map_list)

    def test_list_raster_layers_pattern(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers?pattern=lsat*",
            headers=self.user_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        map_list = json_loads(rv.data)["process_results"]
        self.assertFalse("elevation" in map_list)
        self.assertFalse("aspect" in map_list)
        self.assertTrue("lsat7_2002_10" in map_list)
        self.assertFalse("slope" in map_list)

    def test_list_raster_layers_empty_list(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers?pattern=NONE",
            headers=self.user_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        map_list = json_loads(rv.data)["process_results"]
        self.assertTrue(len(map_list) == 0)

    def test_remove_raster_layers_pattern(self):
        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        map_list = ["test_delete_layer_1", "test_delete_layer_2"]

        # Create raster layers
        for map_name in map_list:
            self.create_raster_layer(new_mapset, map_name)

        # # Delete raster layers
        # rv = self.server.delete(
        #     f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/user1/raster_layers?"
        #     "pattern=test_delete_layer_*",
        #     headers=self.user_auth_header
        # )
        # print(rv.data)
        # self.assertEqual(
        #     rv.status_code,
        #     200, "HTML status code is wrong %i" % rv.status_code
        # )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        # List raster layer
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers?pattern=test_delete_layer_*",
            headers=self.user_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )
        # Check
        map_list_result = json_loads(rv.data)["process_results"]
        for map_name in map_list_result:
            self.assertTrue(map_name in map_list)

        # Delete raster layers
        for map_name in map_list:
            rv = self.server.delete(
                f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
                f"{new_mapset}/raster_layers/{map_name}",
                headers=self.user_auth_header,
            )
            print(rv.data.decode())

    def test_rename_raster_layers(self):
        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        map_list = ["test_rename_layer_1", "test_rename_layer_2"]
        new_map_list = ["test_rename_layer_1_new", "test_rename_layer_2_new"]
        rename_map_list = [
            ("test_rename_layer_1", "test_rename_layer_1_new"),
            ("test_rename_layer_2", "test_rename_layer_2_new"),
        ]

        # Create raster layers
        for map_name in map_list:
            self.create_raster_layer(new_mapset, map_name)

        # Rename raster layer
        rv = self.server.put(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers",
            headers=self.user_auth_header,
            data=json_dumps(rename_map_list),
            content_type="application/json",
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Rename raster layer
        rv = self.server.put(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/raster_layers",
            headers=self.user_auth_header,
            data=json_dumps(rename_map_list),
            content_type="application/json",
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Delete raster layers
        for map_name in new_map_list:
            rv = self.server.delete(
                f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
                f"{new_mapset}/raster_layers/{map_name}",
                headers=self.user_auth_header,
            )
            print(rv.data.decode())
            self.assertEqual(
                rv.status_code,
                200,
                "HTML status code is wrong %i" % rv.status_code,
            )


if __name__ == "__main__":
    unittest.main()
