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
Tests: Async process mapset test case admin
"""
import unittest
from flask.json import dumps as json_dumps
from flask.json import loads as json_load
import time
try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2021, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"

# Module change example for r.slope.aspect with g.region adjustment

process_chain_create_strds = {
    "list": [
        {
            "module": "g.copy",
            "id": "g_copy_raster_1",
            "inputs": [
                {
                    "param": "raster",
                    "value": "MOD11B3.A2015001.h11v05.single_LST_Day_6km@modis_lst,MOD11B3.A2015001.h11v05.single_LST_Day_6km"
                }
            ]
        },
        {
            "module": "g.copy",
            "id": "g_copy_raster_2",
            "inputs": [
                {
                    "param": "raster",
                    "value": "MOD11B3.A2015032.h11v05.single_LST_Day_6km@modis_lst,MOD11B3.A2015032.h11v05.single_LST_Day_6km"
                }
            ]
        },
        {
            "module": "g.copy",
            "id": "g_copy_raster_2",
            "inputs": [
                {
                    "param": "raster",
                    "value": "MOD11B3.A2015060.h11v05.single_LST_Day_6km@modis_lst,MOD11B3.A2015060.h11v05.single_LST_Day_6km"
                }
            ]
        },
        {
            "module": "t.create",
            "id": "t.create_strds",
            "inputs": [
                {
                    "param": "output",
                    "value": "modis"
                },
                {
                    "param": "title",
                    "value": "modis"
                },
                {
                    "param": "description",
                    "value": "modis"
                }
            ]
        },
        {
            "module": "t.register",
            "id": "t.register_strds",
            "inputs": [
                {
                    "param": "input",
                    "value": "modis"
                },
                {
                    "param": "maps",
                    "value": "MOD11B3.A2015001.h11v05.single_LST_Day_6km,MOD11B3.A2015032.h11v05.single_LST_Day_6km,MOD11B3.A2015060.h11v05.single_LST_Day_6km"
                },
                {
                    "param": "start",
                    "value": "2015-01-01"
                },
                {
                    "param": "increment",
                    "value": "1 months"
                }
            ]
        }
    ],
    "version": "1"
}


class AsyncMapsetMergingSTRDS(ActiniaResourceTestCaseBase):

    user_mapset = "test_strds_merging"

    def tearDown(self):
        # unlock and delete the test mapsets
        rv = self.server.get(URL_PREFIX + '/locations/nc_spm_08/mapsets',
                             headers=self.user_auth_header)
        existing_mapsets = json_load(rv.data)["process_results"]
        if self.user_mapset in existing_mapsets:
            rvdellock = self.server.delete(
                URL_PREFIX + '/locations/nc_spm_08/mapsets/%s/lock' % self.user_mapset,
                headers=self.admin_auth_header)
            print(rvdellock.data.decode())

            rvdel = self.server.delete(
                URL_PREFIX + '/locations/nc_spm_08/mapsets/%s' % self.user_mapset,
                headers=self.admin_auth_header)
            print(rvdel.data.decode())

    def test_create_strds_in_persistent_user_db(self):
        raster_dict = {
            'MOD11B3.A2015001.h11v05.single_LST_Day_6km': '2015-01-01 00:00:00',
            'MOD11B3.A2015032.h11v05.single_LST_Day_6km': '2015-02-01 00:00:00',
            'MOD11B3.A2015060.h11v05.single_LST_Day_6km': '2015-03-01 00:00:00'
        }
        rv = self.server.post(URL_PREFIX + f'/locations/nc_spm_08/mapsets/{self.user_mapset}/processing_async',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_create_strds),
                              content_type="application/json")

        resp = self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                              http_status=200, status="finished")

        # check if strds 'modis' is in mapset
        rv2 = self.server.get(URL_PREFIX + f'/locations/nc_spm_08/mapsets/{self.user_mapset}/strds',
                              headers=self.user_auth_header)
        strds = json_load(rv2.data)["process_results"]
        self.assertIn('modis', strds, "STRDS 'modis' is not in test mapset")

        # check if correct maps are listed i strds 'modis'
        rv3 = self.server.get(URL_PREFIX + f'/locations/nc_spm_08/mapsets/{self.user_mapset}/strds/modis/raster_layers',
                              headers=self.user_auth_header)
        strds_rasters = json_load(rv3.data)["process_results"]
        raster_times = {rast['id'].split('@')[0]: rast['start_time'] for rast in strds_rasters}
        self.assertEqual(
            len(raster_times), len(raster_dict),
            f"Number of raster in STRDS are not {len(raster_dict)}")
        self.assertEqual(
            raster_times, raster_times,
            "STRDS times and raster names are not correct in test mapset")

if __name__ == '__main__':
    unittest.main()
