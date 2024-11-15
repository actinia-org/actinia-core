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
Tests: STRDS render test case
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
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"

project = "nc_spm_08"
strds_mapset = "modis_lst"
strds_data = "LST_Day_monthly"


class STRDSRenderTestCase(ActiniaResourceTestCaseBase):
    def create_raster_layer(self, project_name, mapset_name, raster_name, val):
        # Remove potentially existing raster layer
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/{project_name}/mapsets/"
            f"{mapset_name}/raster_layers/{raster_name}",
            headers=self.admin_auth_header,
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
                            "value": "%s = %d" % (raster_name, val),
                        }
                    ],
                },
            ],
            "version": "1",
        }
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{project_name}/mapsets/"
            f"{mapset_name}/processing_async",
            headers=self.admin_auth_header,
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

    def test_strds_render_1(self):
        new_mapset = "strds_render_test"
        self.create_new_mapset(new_mapset, project)

        # Create success
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/"
            f"{new_mapset}/strds/test_strds_register",
            headers=self.admin_auth_header,
            data=json_dumps(
                {
                    "temporaltype": "absolute",
                    "title": "A nice title",
                    "description": "A nice description",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Create the raster layer
        self.create_raster_layer(project, new_mapset, "test_layer_1", 1)
        self.create_raster_layer(project, new_mapset, "test_layer_2", 2)
        self.create_raster_layer(project, new_mapset, "test_layer_3", 3)

        raster_layers = [
            {
                "name": "test_layer_1",
                "start_time": "2000-01-01",
                "end_time": "2000-01-02",
            },
            {
                "name": "test_layer_2",
                "start_time": "2000-01-02",
                "end_time": "2000-01-03",
            },
            {
                "name": "test_layer_3",
                "start_time": "2000-01-03",
                "end_time": "2000-01-04",
            },
        ]

        rv = self.server.put(
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/"
            f"{new_mapset}/strds/test_strds_register/raster_layers",
            data=json_dumps(raster_layers),
            content_type="application/json",
            headers=self.admin_auth_header,
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Check strds
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/"
            f"{new_mapset}/strds/test_strds_register/render?width=100&"
            "height=100",
            headers=self.admin_auth_header,
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype
        )

        # Check strds
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/"
            f"{new_mapset}/strds/test_strds_register/render?"
            "width=100&height=100&"
            "start_time=2000-01-01 00:00:00&end_time=2000-01-02 00:00:00",
            headers=self.admin_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype
        )


if __name__ == "__main__":
    unittest.main()
