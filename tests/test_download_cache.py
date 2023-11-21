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
Tests: Download cache test case
"""
from flask.json import loads as json_load
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
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class DownloadCacheTestCase(ActiniaResourceTestCaseBase):
    def test_download_cache(self):
        # global_config.DOWNLOAD_CACHE = "/tmp/dcache_tmp"
        global_config.DOWNLOAD_CACHE_QUOTA = 1
        try:
            os.mkdir(global_config.DOWNLOAD_CACHE)
        except Exception:  # more precise exception gladly accepted
            pass

        try:
            os.mkdir(os.path.join(global_config.DOWNLOAD_CACHE, self.admin_id))
        except Exception:  # more precise exception gladly accepted
            pass

        rv = self.server.get(
            URL_PREFIX + "/download_cache", headers=self.admin_auth_header
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

        self.assertTrue("used" in json_load(rv.data)["process_results"])
        self.assertTrue("quota" in json_load(rv.data)["process_results"])
        self.assertTrue("free" in json_load(rv.data)["process_results"])
        self.assertTrue(
            "free_percent" in json_load(rv.data)["process_results"]
        )

        rv = self.server.delete(
            URL_PREFIX + "/download_cache", headers=self.admin_auth_header
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

        rv = self.server.get(
            URL_PREFIX + "/download_cache", headers=self.admin_auth_header
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

        self.assertTrue("used" in json_load(rv.data)["process_results"])
        self.assertTrue("quota" in json_load(rv.data)["process_results"])
        self.assertTrue("free" in json_load(rv.data)["process_results"])
        self.assertTrue(
            "free_percent" in json_load(rv.data)["process_results"]
        )

    # TODO: configure wrong download cache path differently (via config file)
    # see https://github.com/actinia-org/actinia-core/issues/422
    # def test_download_cache_error_1(self):
    #     if os.path.isdir("/tmp/dcache_tmp_nope") is True:
    #         os.rmdir("/tmp/dcache_tmp_nope")

    #     global_config.DOWNLOAD_CACHE = "/tmp/dcache_tmp_nope"
    #     global_config.DOWNLOAD_CACHE_QUOTA = 1

    #     rv = self.server.get(
    #         URL_PREFIX + "/download_cache", headers=self.admin_auth_header
    #     )
    #     print(rv.data.decode())
    #     self.assertEqual(
    #         rv.status_code,
    #         400,
    #         "HTML status code is wrong %i" % rv.status_code,
    #     )
    #     self.assertEqual(
    #        rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
    #     )

    # TODO: configure wrong download cache path differently (via config file)
    # see https://github.com/actinia-org/actinia-core/issues/422
    # def test_download_cache_error_2(self):
    #     if os.path.isdir("/tmp/dcache_tmp_nope") is True:
    #         os.rmdir("/tmp/dcache_tmp_nope")

    #     global_config.DOWNLOAD_CACHE = "/tmp/dcache_tmp_nope"
    #     global_config.DOWNLOAD_CACHE_QUOTA = 1

    #     rv = self.server.delete(
    #         URL_PREFIX + "/download_cache", headers=self.admin_auth_header
    #     )
    #     print(rv.data.decode())
    #     self.assertEqual(
    #         rv.status_code,
    #         400,
    #         "HTML status code is wrong %i" % rv.status_code,
    #     )
    #     self.assertEqual(
    #        rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
    #     )


if __name__ == "__main__":
    unittest.main()
