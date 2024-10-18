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
Tests: Resource storage test case
"""
from flask.json import loads as json_load
from datetime import datetime, timedelta
import unittest
import os

try:
    from .test_resource_base import (
        ActiniaResourceTestCaseBase,
        global_config,
        URL_PREFIX,
    )
except ModuleNotFoundError:
    from test_resource_base import (
        ActiniaResourceTestCaseBase,
        global_config,
        URL_PREFIX,
    )

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class ResourceStorageTestCase(ActiniaResourceTestCaseBase):
    def test_resource_storage(self):
        # global_config.GRASS_RESOURCE_DIR = "/tmp/rstorage_tmp"
        global_config.GRASS_RESOURCE_QUOTA = 1
        try:
            os.mkdir(global_config.GRASS_RESOURCE_DIR)
        except Exception:  # more precise exception gladly accepted
            pass

        try:
            os.mkdir(
                os.path.join(global_config.GRASS_RESOURCE_DIR, self.admin_id)
            )
        except Exception:  # more precise exception gladly accepted
            pass

        rv = self.server.get(
            URL_PREFIX + "/resource_storage", headers=self.admin_auth_header
        )
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        self.assertTrue("used" in json_load(rv.data)["process_results"])
        self.assertTrue("quota" in json_load(rv.data)["process_results"])
        self.assertTrue("free" in json_load(rv.data)["process_results"])
        self.assertTrue(
            "free_percent" in json_load(rv.data)["process_results"]
        )

        rv = self.server.delete(
            URL_PREFIX + "/resource_storage", headers=self.admin_auth_header
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        rv = self.server.get(
            URL_PREFIX + "/resource_storage", headers=self.admin_auth_header
        )
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        self.assertTrue("used" in json_load(rv.data)["process_results"])
        self.assertTrue("quota" in json_load(rv.data)["process_results"])
        self.assertTrue("free" in json_load(rv.data)["process_results"])
        self.assertTrue(
            "free_percent" in json_load(rv.data)["process_results"]
        )

    # TODO: configure wrong resource dir path differently (via config file)
    # see https://github.com/actinia-org/actinia-core/issues/422
    # def test_resource_storage_error_1(self):
    #     global_config.GRASS_RESOURCE_DIR = "/tmp/rstorage_tmp_nope"
    #     global_config.GRASS_RESOURCE_QUOTA = 1

    #     rv = self.server.get(
    #         URL_PREFIX + "/resource_storage", headers=self.admin_auth_header
    #     )
    #     import pdb; pdb.set_trace()
    #     self.assertEqual(
    #         rv.status_code,
    #         400,
    #         "HTML status code is wrong %i" % rv.status_code,
    #     )
    #     self.assertEqual(
    #         rv.mimetype,
    #         "application/json",
    #         "Wrong mimetype %s" % rv.mimetype
    #     )

    # TODO: configure wrong resource dir path differently (via config file)
    # see https://github.com/actinia-org/actinia-core/issues/422
    # def test_resource_storage_error_2(self):
    #     global_config.GRASS_RESOURCE_DIR = "/tmp/rstorage_tmp_nope"
    #     global_config.GRASS_RESOURCE_QUOTA = 1

    #     rv = self.server.delete(
    #         URL_PREFIX + "/resource_storage", headers=self.admin_auth_header
    #     )
    #     self.waitAsyncStatusAssertHTTP(
    #         rv,
    #         headers=self.admin_auth_header,
    #         http_status=400,
    #         status="error",
    #         message_check="AsyncProcessError:",
    #     )
    #     self.assertEqual(
    #         rv.mimetype,
    #         "application/json",
    #         "Wrong mimetype %s" % rv.mimetype
    #     )

    def test_resource_storage_delete_olderthan(self):
        # global_config.GRASS_RESOURCE_DIR = "/tmp/rstorage_tmp"
        global_config.GRASS_RESOURCE_QUOTA = 1
        try:
            os.mkdir(global_config.GRASS_RESOURCE_DIR)
        except Exception:  # more precise exception gladly accepted
            pass

        admin_resource_path = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            self.admin_id,
        )
        try:
            os.mkdir(admin_resource_path)
        except Exception:  # more precise exception gladly accepted
            pass

        # create files from specified date
        now = datetime.now()
        before_15days = now - timedelta(days=15)
        file1 = os.path.join(admin_resource_path, "file1.txt")
        file2 = os.path.join(admin_resource_path, "file2.txt")
        date1 = now.strftime("%Y-%m-%d %H:%M:%S")
        date2 = before_15days.strftime("%Y-%m-%d %H:%M:%S")
        cmd_touch_file1 = f"touch -d '{date1}' {file1}"
        cmd_touch_file2 = f"touch -d '{date2}' {file2}"
        os.system(cmd_touch_file1)
        os.system(cmd_touch_file2)
        created_files = os.listdir(admin_resource_path)
        self.assertIn(
            "file1.txt",
            created_files,
            "'file1.txt' not in resource path after creation",
        )
        self.assertIn(
            "file2.txt",
            created_files,
            "'file2.txt' not in resource path after creation",
        )

        # request resource storage
        rv = self.server.get(
            URL_PREFIX + "/resource_storage", headers=self.admin_auth_header
        )
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )

        # delete files older than 10 days
        rv = self.server.delete(
            URL_PREFIX + "/resource_storage?olderthan=10",
            headers=self.admin_auth_header,
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # check files
        files = os.listdir(admin_resource_path)
        self.assertIn("file1.txt", files, "'file1.txt' not in resource path")
        self.assertNotIn("file2.txt", files, "'file2.txt' in resource path")

        # clean up resource storage
        rv = self.server.delete(
            URL_PREFIX + "/resource_storage", headers=self.admin_auth_header
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )


if __name__ == "__main__":
    unittest.main()
