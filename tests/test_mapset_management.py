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
Tests: Mapset test case
"""
from flask.json import loads as json_load
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


class MapsetTestCase(ActiniaResourceTestCaseBase):
    def test_list_mapsets(self):
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

        self.assertTrue("PERMANENT" in mapsets)
        self.assertTrue("user1" in mapsets)

    def test_mapsets_region_1(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/info",
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

        region_settings = json_load(rv.data)["process_results"]["region"]

        self.assertTrue("depths" in region_settings)
        self.assertTrue("ewres" in region_settings)
        self.assertTrue("cols" in region_settings)
        self.assertTrue("rows" in region_settings)

    def test_mapsets_region_2(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/user1/"
            "info",
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

        region_settings = json_load(rv.data)["process_results"]["region"]

        self.assertTrue("depths" in region_settings)
        self.assertTrue("ewres" in region_settings)
        self.assertTrue("cols" in region_settings)
        self.assertTrue("rows" in region_settings)

    def test_mapset_creation_and_deletion(self):
        self.create_new_mapset("test_mapset")

        # Mapset already exists
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset",
            headers=self.admin_auth_header,
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

        # Delete mapset
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

        # Delete should fail, since mapset does not exists
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset",
            headers=self.admin_auth_header,
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

    def test_mapset_creation_and_deletion_unprivileged(self):
        # Create new mapsets as unprivileged user
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset",
            headers=self.guest_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )

        # Delete mapset as unprivileged user
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset",
            headers=self.guest_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )

    def test_mapset_deletion_permanent_error(self):
        # Delete PERMANENT
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )

    def test_mapset_deletion_global_db_error(self):
        # Delete PERMANENT
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/user1",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )

    def test_mapset_creation_and_locking(self):
        # Unlock mapset for deletion
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset_2/lock",
            headers=self.admin_auth_header,
        )
        print(rv.data)

        # Delete any existing mapsets
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset_2",
            headers=self.admin_auth_header,
        )
        print(rv.data)

        # Create new mapsets
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset_2",
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

        # Lock mapset
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset_2/lock",
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

        # get mapset lock(False)
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset_2/lock",
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

        lock_status = json_load(rv.data)["process_results"]
        self.assertTrue(lock_status)

        # Unlock mapset
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset_2/lock",
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

        # get mapset lock (False)
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset_2/lock",
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

        lock_status = json_load(rv.data)["process_results"]
        self.assertFalse(lock_status)

        # Delete mapset
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset_2",
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

        # get mapset lock (False)
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset_2/lock",
            headers=self.admin_auth_header,
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

        # lock_status = json_load(rv.data)["process_results"]
        # self.assertFalse(lock_status)

        # Lock mapset
        # This locks the mapset even if it doesn't exist and even though an
        # error is logged. Skip until fixed. TODO reactivate
        # https://github.com/actinia-org/actinia-core/issues/487
        # rv = self.server.post(
        #     f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
        #     "test_mapset_2/lock",
        #     headers=self.admin_auth_header,
        # )
        # print(rv.data)
        # self.assertEqual(
        #     rv.status_code,
        #     400,
        #     "HTML status code is wrong %i" % rv.status_code,
        # )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        # Unlock mapset
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "test_mapset_2/lock",
            headers=self.admin_auth_header,
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
