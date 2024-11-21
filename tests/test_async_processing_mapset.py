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
Tests: Async process mapset test case admin
"""
import unittest
from flask.json import loads as json_loads, dumps as json_dumps
from flask.json import loads as json_load
import time

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

# Module change example for r.slope.aspect with g.region adjustment
process_chain_long = {
    1: {
        "module": "g.region",
        "inputs": {"raster": "elevation@PERMANENT"},
        "flags": "p",
        "verbose": True,
    },
    2: {
        "module": "r.slope.aspect",
        "inputs": {
            "elevation": "elevation@PERMANENT",
            "format": "degrees",
            "min_slope": "0.0",
        },
        "outputs": {
            "aspect": {"name": "my_aspect"},
            "slope": {"name": "my_slope"},
        },
        "flags": "a",
        "overwrite": False,
        "verbose": True,
    },
    3: {
        "module": "r.watershed",
        "inputs": {"elevation": "elevation@PERMANENT"},
        "outputs": {"accumulation": {"name": "my_accumulation"}},
    },
    4: {
        "module": "r.info",
        "inputs": {"map": "my_aspect"},
        "flags": "gr",
        "verbose": True,
    },
}

process_chain_short = {
    1: {
        "module": "g.region",
        "inputs": {"raster": "elevation@PERMANENT"},
        "flags": "p",
        "verbose": True,
    },
    2: {
        "module": "r.slope.aspect",
        "inputs": {
            "elevation": "elevation@PERMANENT",
            "format": "degrees",
            "min_slope": "0.0",
        },
        "outputs": {
            "aspect": {"name": "my_aspect_2"},
            "slope": {"name": "my_slope_2"},
        },
        "flags": "a",
        "overwrite": False,
        "verbose": True,
    },
}


class AsyncProcessMapsetTestCaseAdmin(ActiniaResourceTestCaseBase):
    def check_remove_test_mapset(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets",
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

        mapsets = json_load(rv.data)["process_results"]

        if "test_mapset" in mapsets:
            # Delete the mapset if it already exists
            rv = self.server.delete(
                f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
                "test_mapset",
                headers=self.admin_auth_header,
            )
            print(rv.data)
            self.assertEqual(
                rv.status_code,
                200,
                "HTML status code is wrong %i" % rv.status_code,
            )
            self.assertEqual(
                rv.mimetype,
                "application/json",
                "Wrong mimetype %s" % rv.mimetype,
            )

    def test_1_new_mapset(self):
        """
        Create a new mapset and process
        :return:
        """
        self.check_remove_test_mapset()

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_long),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets",
            headers=self.admin_auth_header,
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

        mapsets = json_load(rv.data)["process_results"]

        self.assertTrue("test_mapset" in mapsets)

        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset/raster_layers",
            headers=self.admin_auth_header,
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

        map_list = json_load(rv.data)["process_results"]
        self.assertTrue("my_accumulation" in map_list)
        self.assertTrue("my_aspect" in map_list)
        self.assertTrue("my_slope" in map_list)

        # Remove the mapset
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset",
            headers=self.admin_auth_header,
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

    def test_2_existing_mapset(self):
        """
        An existing mapset and process
        :return:
        """
        self.check_remove_test_mapset()

        # Create new mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset",
            headers=self.admin_auth_header,
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

        # Run the processing using an existing mapset
        # Atemporary mapset will be created and merged in the existing
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_long),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset/raster_layers",
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

        map_list = json_load(rv.data)["process_results"]
        self.assertTrue("my_accumulation" in map_list)
        self.assertTrue("my_aspect" in map_list)
        self.assertTrue("my_slope" in map_list)

        # Remove the mapset
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset",
            headers=self.admin_auth_header,
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

    def test_3_existing_mapset_lock(self):
        """
        Try to run two request on a locked mapset
        :return:
        """

        self.check_remove_test_mapset()

        # Create new mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset",
            headers=self.admin_auth_header,
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

        # Run the processing inside the new mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_long),
            content_type="application/json",
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

        resp = json_loads(rv.data)

        rv_user_id = resp["user_id"]
        rv_resource_id = resp["resource_id"]

        time.sleep(0.5)

        # Try to lock again and again
        # Run the processing inside the new mapset
        # Second runner
        rv_lock_1 = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_short),
            content_type="application/json",
        )

        print(rv_lock_1.data)
        self.assertEqual(
            rv_lock_1.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv_lock_1.mimetype,
            "application/json",
            "Wrong mimetype %s" % rv.mimetype,
        )
        # Third runner
        rv_lock_2 = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_long),
            content_type="application/json",
        )

        print(rv_lock_2.data)
        self.assertEqual(
            rv_lock_2.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv_lock_2.mimetype,
            "application/json",
            "Wrong mimetype %s" % rv.mimetype,
        )

        # Check the first runner
        while True:
            rv = self.server.get(
                URL_PREFIX + "/resources/%s/%s" % (rv_user_id, rv_resource_id),
                headers=self.admin_auth_header,
            )
            print(rv.data)
            resp = json_loads(rv.data)
            if resp["status"] == "finished" or resp["status"] == "error":
                break
            time.sleep(0.2)

        self.assertEqual(resp["status"], "finished")
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )

        # Check the second runner
        resp = json_loads(rv_lock_1.data)
        rv_user_id = resp["user_id"]
        rv_resource_id = resp["resource_id"]
        while True:
            rv = self.server.get(
                URL_PREFIX + "/resources/%s/%s" % (rv_user_id, rv_resource_id),
                headers=self.admin_auth_header,
            )
            print(rv.data)
            resp = json_loads(rv.data)
            if resp["status"] == "finished" or resp["status"] == "error":
                break
            time.sleep(0.2)

        self.assertEqual(resp["status"], "error")
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )

        # Check the third runner
        resp = json_loads(rv_lock_2.data)
        rv_user_id = resp["user_id"]
        rv_resource_id = resp["resource_id"]
        # Check the first runner
        while True:
            rv = self.server.get(
                f"{URL_PREFIX}/resources/{rv_user_id}/{rv_resource_id}",
                headers=self.admin_auth_header,
            )
            print(rv.data)
            resp = json_loads(rv.data)
            if resp["status"] == "finished" or resp["status"] == "error":
                break
            time.sleep(0.2)

        self.assertEqual(resp["status"], "error")
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )

        # Remove the mapset
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset",
            headers=self.admin_auth_header,
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

    def test_4_create_global_mapset(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_long),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )


if __name__ == "__main__":
    unittest.main()
