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
from flask.json import dumps as json_dumps
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

process_chain_short_1 = {
    1: {
        "module": "g.region",
        "inputs": {"raster": "elevation@PERMANENT", "res": "1000"},
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
            "aspect": {"name": "my_aspect_1"},
            "slope": {"name": "my_slope_1"},
        },
        "flags": "a",
        "overwrite": False,
        "verbose": True,
    },
}

process_chain_short_2 = {
    1: {
        "module": "g.region",
        "inputs": {"raster": "elevation@PERMANENT", "res": "1000"},
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

test_mapsets = ["Source_A", "Source_B", "Source_C", "Source_D", "Target"]


class AsyncProcessMapsetTestCaseAdmin(ActiniaResourceTestCaseBase):
    def check_remove_test_mapsets(self):
        """
        Check and remove test mapsets that have been created in the test-run
        Returns:

        """

        for mapset in test_mapsets:
            # Unlock mapset for deletion
            rv = self.server.delete(
                f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
                f"{mapset}/lock",
                headers=self.admin_auth_header,
            )
            print(rv.data)

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

        for mapset in test_mapsets:
            if mapset in mapsets:
                # Delete the mapset if it already exists
                rv = self.server.delete(
                    f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
                    f"mapsets/{mapset}",
                    headers=self.admin_auth_header,
                )
                print(rv.data)
                self.assertEqual(
                    rv.status_code,
                    200,
                    "HTML status code is wrong %i %s"
                    % (rv.status_code, mapset),
                )
                self.assertEqual(
                    rv.mimetype,
                    "application/json",
                    "Wrong mimetype %s" % rv.mimetype,
                )

    def test_1_merge_no_access_to_target_mapset_error(self):
        """No access to target mapset error test"""
        # Try merge source mapsets into target mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/user1/"
            "merging_async",
            headers=self.user_auth_header,
            data=json_dumps(["Source_A", "Source_B"]),
            content_type="application/json",
        )

        print(rv.data)
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError",
        )

    def test_2_merge_missing_target_mapset_error(self):
        """Missing target mapset test"""
        self.check_remove_test_mapsets()

        # Try merge source mapsets into target mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target/"
            "merging_async",
            headers=self.admin_auth_header,
            data=json_dumps(["Source_A", "Source_B"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError",
        )

    def test_3_merge_missing_source_mapsets_error(self):
        """Test error for missing source mapsets"""
        self.check_remove_test_mapsets()

        # Create target mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target",
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

        # Try merge source mapsets into target mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target/"
            "merging_async",
            headers=self.admin_auth_header,
            data=json_dumps(["Source_A", "Source_B"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError",
        )

    def test_4_merge_empty_mapset_list(self):
        """Test error for missing source mapsets"""
        self.check_remove_test_mapsets()

        # Create target mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target",
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

        # Try merge source mapsets into target mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target/"
            "merging_async",
            headers=self.admin_auth_header,
            data=json_dumps([]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError",
        )

    def test_5_merge_two_mapsets(self):
        """Test the merging of two mapsets into a target mapset"""
        self.check_remove_test_mapsets()

        # Create the source mapsets
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Source_A/"
            "processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_short_1),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Source_B/"
            "processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_short_2),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        # Create target mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target",
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

        # Merge source mapsets into target mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target/"
            "merging_async",
            headers=self.admin_auth_header,
            data=json_dumps(["Source_A", "Source_B"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        # Check copied raster
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target/"
            "raster_layers/my_aspect_1",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertTrue(
            "my_aspect_1", json_load(rv.data)["process_results"]["map"]
        )
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target/"
            "raster_layers/my_aspect_2",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertTrue(
            "my_aspect_2", json_load(rv.data)["process_results"]["map"]
        )
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target/"
            "raster_layers/my_slope_1",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertTrue(
            "my_slope_1", json_load(rv.data)["process_results"]["map"]
        )
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/Target/"
            "raster_layers/my_slope_2",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertTrue(
            "my_slope_2", json_load(rv.data)["process_results"]["map"]
        )
        time.sleep(1)


if __name__ == "__main__":
    unittest.main()
