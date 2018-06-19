# -*- coding: utf-8 -*-
from flask.json import loads as json_load
import unittest
import os
try:
    from .test_resource_base import ActiniaResourceTestCaseBase, global_config, URL_PREFIX
except:
    from test_resource_base import ActiniaResourceTestCaseBase, global_config, URL_PREFIX

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class DownloadCacheTestCase(ActiniaResourceTestCaseBase):

    def test_download_cache(self):

        global_config.DOWNLOAD_CACHE = "/tmp/dcache_tmp"
        global_config.DOWNLOAD_CACHE_QUOTA = 1
        try:
            os.mkdir(global_config.DOWNLOAD_CACHE)
        except:
            pass

        try:
            os.mkdir(os.path.join(global_config.DOWNLOAD_CACHE, self.admin_id))
        except:
            pass

        rv = self.server.get(URL_PREFIX + '/download_cache',
                             headers=self.admin_auth_header)
        print(rv.data.decode())
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        self.assertTrue("used" in json_load(rv.data)["process_results"])
        self.assertTrue("quota" in json_load(rv.data)["process_results"])
        self.assertTrue("free" in json_load(rv.data)["process_results"])
        self.assertTrue("free_percent" in json_load(rv.data)["process_results"])

        rv = self.server.delete(URL_PREFIX + '/download_cache',
                                headers=self.admin_auth_header)
        print(rv.data.decode())
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        rv = self.server.get(URL_PREFIX + '/download_cache',
                             headers=self.admin_auth_header)
        print(rv.data.decode())
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        self.assertTrue("used" in json_load(rv.data)["process_results"])
        self.assertTrue("quota" in json_load(rv.data)["process_results"])
        self.assertTrue("free" in json_load(rv.data)["process_results"])
        self.assertTrue("free_percent" in json_load(rv.data)["process_results"])

    def test_download_cache_error_1(self):

        if os.path.isdir("/tmp/dcache_tmp_nope") is True:
            os.rmdir("/tmp/dcache_tmp_nope")

        global_config.DOWNLOAD_CACHE = "/tmp/dcache_tmp_nope"
        global_config.DOWNLOAD_CACHE_QUOTA = 1

        rv = self.server.get(URL_PREFIX + '/download_cache',
                             headers=self.admin_auth_header)
        print(rv.data.decode())
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_download_cache_error_2(self):

        if os.path.isdir("/tmp/dcache_tmp_nope") is True:
            os.rmdir("/tmp/dcache_tmp_nope")

        global_config.DOWNLOAD_CACHE = "/tmp/dcache_tmp_nope"
        global_config.DOWNLOAD_CACHE_QUOTA = 1

        rv = self.server.delete(URL_PREFIX + '/download_cache',
                                headers=self.admin_auth_header)
        print(rv.data.decode())
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

if __name__ == '__main__':
    unittest.main()
