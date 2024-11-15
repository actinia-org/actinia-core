# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2021-2024 Sören Gebbert and mundialis GmbH & Co. KG
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
Tests: Async process mapset test case admin
"""
import unittest
from flask.json import dumps as json_dumps
from flask.json import loads as json_load

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2021-2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

mapset_name = "test_strds_merging"

process_chain_create_strds1 = {
    "list": [
        {
            "module": "g.copy",
            "id": "g_copy_raster_1",
            "inputs": [
                {
                    "param": "raster",
                    "value": "MOD11B3.A2015001.h11v05.single_LST_Day_6km@modis"
                    "_lst,MOD11B3.A2015001.h11v05.single_LST_Day_6km",
                }
            ],
        },
        {
            "module": "g.copy",
            "id": "g_copy_raster_2",
            "inputs": [
                {
                    "param": "raster",
                    "value": "MOD11B3.A2015032.h11v05.single_LST_Day_6km@modis"
                    "_lst,MOD11B3.A2015032.h11v05.single_LST_Day_6km",
                }
            ],
        },
        {
            "module": "g.copy",
            "id": "g_copy_raster_3",
            "inputs": [
                {
                    "param": "raster",
                    "value": "MOD11B3.A2015060.h11v05.single_LST_Day_6km@modis"
                    "_lst,MOD11B3.A2015060.h11v05.single_LST_Day_6km",
                }
            ],
        },
        {
            "module": "t.create",
            "id": "t.create_strds",
            "inputs": [
                {"param": "output", "value": "modis"},
                {"param": "title", "value": "modis"},
                {"param": "description", "value": "modis"},
            ],
        },
        {
            "module": "t.register",
            "id": "t.register_strds",
            "inputs": [
                {"param": "input", "value": "modis"},
                {
                    "param": "maps",
                    "value": "MOD11B3.A2015001.h11v05.single_LST_Day_6km,"
                    "MOD11B3.A2015032.h11v05.single_LST_Day_6km,MOD11B3."
                    "A2015060.h11v05.single_LST_Day_6km",
                },
                {"param": "start", "value": "2015-01-01"},
                {"param": "increment", "value": "1 months"},
            ],
        },
    ],
    "version": "1",
}
process_chain_create_strds2 = {
    "list": [
        {
            "module": "g.copy",
            "id": "g_copy_raster_1",
            "inputs": [
                {
                    "param": "raster",
                    "value": "MOD11B3.A2016001.h11v05.single_LST_Day_6km@modis"
                    "_lst,MOD11B3.A2016001.h11v05.single_LST_Day_6km",
                }
            ],
        },
        {
            "module": "g.copy",
            "id": "g_copy_raster_2",
            "inputs": [
                {
                    "param": "raster",
                    "value": "MOD11B3.A2016032.h11v05.single_LST_Day_6km@modis"
                    "_lst,MOD11B3.A2016032.h11v05.single_LST_Day_6km",
                }
            ],
        },
        {
            "module": "t.create",
            "id": "t.create_strds_modis",
            "inputs": [
                {"param": "output", "value": "modis2"},
                {"param": "title", "value": "modis2"},
                {"param": "description", "value": "modis2"},
            ],
        },
        {
            "module": "t.register",
            "id": "t.register_strds_modis",
            "inputs": [
                {"param": "input", "value": "modis2"},
                {
                    "param": "maps",
                    "value": "MOD11B3.A2016001.h11v05.single_LST_Day_6km,"
                    "MOD11B3.A2016032.h11v05.single_LST_Day_6km",
                },
                {"param": "start", "value": "2016-01-01"},
                {"param": "increment", "value": "1 months"},
            ],
        },
    ],
    "version": "1",
}
process_chain_create_strds3 = {
    "list": [
        {
            "module": "g.copy",
            "id": "g_copy_raster_1",
            "inputs": [
                {
                    "param": "raster",
                    "value": "MOD11B3.A2016001.h11v05.single_LST_Day_6km@modis"
                    "_lst,MOD11B3.A2016001.h11v05.single_LST_Day_6km",
                }
            ],
        },
        {
            "module": "g.copy",
            "id": "g_copy_raster_2",
            "inputs": [
                {
                    "param": "raster",
                    "value": "MOD11B3.A2016032.h11v05.single_LST_Day_6km@modis"
                    "_lst,MOD11B3.A2016032.h11v05.single_LST_Day_6km",
                }
            ],
        },
        {
            "module": "t.create",
            "id": "t.create_strds_modis2",
            "inputs": [
                {"param": "output", "value": "modis2"},
                {"param": "title", "value": "modis2"},
                {"param": "description", "value": "modis2"},
            ],
        },
        {
            "module": "t.register",
            "id": "t.register_strds_modis2",
            "inputs": [
                {"param": "input", "value": "modis2"},
                {
                    "param": "maps",
                    "value": "MOD11B3.A2016001.h11v05.single_LST_Day_6km,"
                    "MOD11B3.A2016032.h11v05.single_LST_Day_6km",
                },
                {"param": "start", "value": "2016-01-01"},
                {"param": "increment", "value": "1 months"},
            ],
        },
        {
            "module": "t.create",
            "id": "t.create_strds_modis_changed",
            "inputs": [
                {"param": "output", "value": "modis"},
                {"param": "title", "value": "modis"},
                {"param": "description", "value": "modis"},
            ],
        },
        {
            "module": "t.register",
            "id": "t.register_strds_modis_changed",
            "inputs": [
                {"param": "input", "value": "modis"},
                {
                    "param": "maps",
                    "value": "MOD11B3.A2016001.h11v05.single_LST_Day_6km,"
                    "MOD11B3.A2016032.h11v05.single_LST_Day_6km",
                },
                {"param": "start", "value": "2016-01-01"},
                {"param": "increment", "value": "1 months"},
            ],
        },
    ],
    "version": "1",
}
process_chain_list = {
    "list": [
        {
            "module": "t.list",
            "id": "t_list_1",
            "inputs": [{"param": "type", "value": "strds"}],
        },
        {
            "module": "t.rast.list",
            "id": "t.rast.list_1",
            "inputs": [{"param": "input", "value": f"modis@{mapset_name}"}],
        },
    ],
    "version": "1",
}


class AsyncMapsetMergingSTRDS(ActiniaResourceTestCaseBase):
    user_mapset = mapset_name
    raster_dict_modis = {
        "MOD11B3.A2015001.h11v05.single_LST_Day_6km": "2015-01-01 00:00:00",
        "MOD11B3.A2015032.h11v05.single_LST_Day_6km": "2015-02-01 00:00:00",
        "MOD11B3.A2015060.h11v05.single_LST_Day_6km": "2015-03-01 00:00:00",
    }
    raster_dict_modis2 = {
        "MOD11B3.A2016001.h11v05.single_LST_Day_6km": "2016-01-01 00:00:00",
        "MOD11B3.A2016032.h11v05.single_LST_Day_6km": "2016-02-01 00:00:00",
    }

    def tearDown(self):
        # unlock and delete the test mapsets
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets",
            headers=self.user_auth_header,
        )
        existing_mapsets = json_load(rv.data)["process_results"]
        if self.user_mapset in existing_mapsets:
            rvdellock = self.server.delete(
                f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
                f"{self.user_mapset}/lock",
                headers=self.admin_auth_header,
            )
            print(rvdellock.data.decode())

            rvdel = self.server.delete(
                f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
                f"mapsets/{self.user_mapset}",
                headers=self.admin_auth_header,
            )
            print(rvdel.data.decode())

    def check_strds_in_mapset(self, strds_names):
        # check if strds 'modis' is in mapset
        rv = dict()
        for strds_name in strds_names:
            rv[strds_name] = self.server.get(
                f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
                f"mapsets/{self.user_mapset}/strds",
                headers=self.user_auth_header,
            )
            strds = json_load(rv[strds_name].data)["process_results"]
            self.assertIn(
                strds_name,
                strds,
                f"STRDS '{strds_name}' is not in test mapset",
            )

    def check_modis_strds(self, raster_dict, strds_name):
        # check if correct maps are listed in strds strds
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{self.user_mapset}/strds/{strds_name}/raster_layers",
            headers=self.user_auth_header,
        )
        strds_rasters = json_load(rv.data)["process_results"]
        raster_times = {
            rast["id"].split("@")[0]: rast["start_time"]
            for rast in strds_rasters
        }
        self.assertEqual(
            len(raster_times),
            len(raster_dict),
            f"Number of raster in STRDS are not {len(raster_dict)}",
        )
        self.assertEqual(
            raster_times,
            raster_times,
            "STRDS times and raster names are not correct in test mapset",
        )

    def test_create_strds_in_persistent_user_db(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{self.user_mapset}/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_create_strds1),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        # check if strds 'modis' is in mapset
        self.check_strds_in_mapset(["modis"])
        # check if correct maps are listed i strds 'modis'
        self.check_modis_strds(self.raster_dict_modis, "modis")

    def test_create_strds_in_persistent_user_db_and_list_it(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{self.user_mapset}/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_create_strds1),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        rv2 = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{self.user_mapset}/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_list),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv2,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        # check if strds 'modis' is in mapset
        self.check_strds_in_mapset(["modis"])
        # check if correct maps are listed i strds 'modis'
        self.check_modis_strds(self.raster_dict_modis, "modis")

    def test_create_strds_in_persistent_user_db_2(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{self.user_mapset}/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_create_strds1),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{self.user_mapset}/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_create_strds2),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        # check if strds 'modis' and 'modis2' is in mapset
        self.check_strds_in_mapset(["modis", "modis2"])
        # check if correct maps are listed in strds 'modis' and 'modis2'
        self.check_modis_strds(self.raster_dict_modis, "modis")
        self.check_modis_strds(self.raster_dict_modis2, "modis2")

    def test_create_strds_in_persistent_user_db_3(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{self.user_mapset}/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_create_strds1),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        # check if strds 'modis' is in mapset
        self.check_strds_in_mapset(["modis"])
        # check if correct maps are listed in strds 'modis'
        self.check_modis_strds(self.raster_dict_modis, "modis")

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{self.user_mapset}/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_create_strds3),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        # check if strds 'modis' and 'modis2' is in mapset
        self.check_strds_in_mapset(["modis", "modis2"])
        # check if correct maps are listed in strds 'modis' and 'modis2'
        self.check_modis_strds(self.raster_dict_modis2, "modis")
        self.check_modis_strds(self.raster_dict_modis2, "modis2")


if __name__ == "__main__":
    unittest.main()
