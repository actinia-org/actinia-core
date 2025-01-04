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
Tests: STRDS test case
"""
from pprint import pprint
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
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

project = "nc_spm_08"
strds_mapset = "modis_lst"
strds_endpoint = f"{project}/mapsets/{strds_mapset}/strds"
strds_data = "LST_Day_monthly"
new_mapset = "raster_test_mapset"


class STRDSTestCase(ActiniaResourceTestCaseBase):
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

    def test_strds_creation_error(self):
        # This must fail, global mapsets are not allowed to modify
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/"
            f"{strds_mapset}/strds/test_strds_register",
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
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_strds_create_register_unregister_1(self):
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
        pprint(json_loads(rv.data))
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
                "start_time": "2000-01-01 00:00:00",
                "end_time": "2000-01-02 00:00:00",
            },
            {
                "name": "test_layer_2",
                "start_time": "2000-01-02 00:00:00",
                "end_time": "2000-01-03 00:00:00",
            },
            {
                "name": "test_layer_3",
                "start_time": "2000-01-03 00:00:00",
                "end_time": "2000-01-04 00:00:00",
            },
        ]

        rv = self.server.put(
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/"
            f"{new_mapset}/strds/test_strds_register/raster_layers",
            data=json_dumps(raster_layers),
            content_type="application/json",
            headers=self.admin_auth_header,
        )
        pprint(json_loads(rv.data))
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
            f"{new_mapset}/strds/test_strds_register",
            headers=self.admin_auth_header,
        )
        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        min_min = json_loads(rv.data)["process_results"]["min_min"]
        max_max = json_loads(rv.data)["process_results"]["max_max"]
        num_maps = json_loads(rv.data)["process_results"]["number_of_maps"]
        self.assertEqual(min_min, "1.0")
        self.assertEqual(max_max, "3.0")
        self.assertEqual(num_maps, "3")

        # Unregister the raster layers
        raster_layers = ["test_layer_1", "test_layer_2", "test_layer_3"]

        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/"
            f"{new_mapset}/strds/test_strds_register/raster_layers",
            data=json_dumps(raster_layers),
            content_type="application/json",
            headers=self.user_auth_header,
        )
        pprint(json_loads(rv.data))
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
            f"{new_mapset}/strds/test_strds_register",
            headers=self.user_auth_header,
        )
        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        min_min = json_loads(rv.data)["process_results"]["min_min"]
        max_max = json_loads(rv.data)["process_results"]["max_max"]
        num_maps = json_loads(rv.data)["process_results"]["number_of_maps"]
        self.assertEqual(min_min, "None")
        self.assertEqual(max_max, "None")
        self.assertEqual(num_maps, "0")

        # Delete the strds
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/"
            f"{new_mapset}/strds/test_strds_register",
            headers=self.user_auth_header,
        )
        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_strds_raster_layer_1(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/{strds_endpoint}/"
            f"{strds_data}/raster_layers",
            headers=self.user_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        map_list = json_loads(rv.data)["process_results"]
        self.assertEqual(len(map_list), 24)

    def test_strds_raster_layer_2(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/{strds_endpoint}/"
            f"{strds_data}/raster_layers?where=start_time >= '2016-01-01'",
            headers=self.user_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        map_list = json_loads(rv.data)["process_results"]
        self.assertEqual(len(map_list), 12)

    def test_strds_info_error_1(self):
        # Raster does not exist
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/{strds_endpoint}/"
            "precipitation_1950_2013_yearly_mm_nope",
            headers=self.user_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_list_strds_where_error_1(self):
        # Wrong where statement
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/{strds_endpoint}/"
            f"{strds_data}/raster_layers?where=start_timing < '2015-01-01'",
            headers=self.user_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )


if __name__ == "__main__":
    unittest.main()
