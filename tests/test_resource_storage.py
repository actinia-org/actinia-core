# -*- coding: utf-8 -*-
from flask.json import loads as json_load
import unittest
import os
try:
    from .test_resource_base import ActiniaResourceTestCaseBase, global_config
except:
    from test_resource_base import ActiniaResourceTestCaseBase, global_config

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class ResourceStorageTestCase(ActiniaResourceTestCaseBase):

    def test_resource_storage(self):

        global_config.GRASS_RESOURCE_DIR = "/tmp/rstorage_tmp"
        global_config.GRASS_RESOURCE_QUOTA = 1
        try:
            os.mkdir(global_config.GRASS_RESOURCE_DIR)
        except:
            pass

        try:
            os.mkdir(os.path.join(global_config.GRASS_RESOURCE_DIR, self.admin_id))
        except:
            pass

        rv = self.server.get('/resource_storage',
                             headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        self.assertTrue("used" in json_load(rv.data)["process_results"])
        self.assertTrue("quota" in json_load(rv.data)["process_results"])
        self.assertTrue("free" in json_load(rv.data)["process_results"])
        self.assertTrue("free_percent" in json_load(rv.data)["process_results"])

        rv = self.server.delete('/resource_storage',
                                headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        rv = self.server.get('/resource_storage',
                             headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        self.assertTrue("used" in json_load(rv.data)["process_results"])
        self.assertTrue("quota" in json_load(rv.data)["process_results"])
        self.assertTrue("free" in json_load(rv.data)["process_results"])
        self.assertTrue("free_percent" in json_load(rv.data)["process_results"])

    def test_resource_storage_error_1(self):

        global_config.GRASS_RESOURCE_DIR = "/tmp/rstorage_tmp_nope"
        global_config.GRASS_RESOURCE_QUOTA = 1

        rv = self.server.get('/resource_storage',
                             headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_resource_storage_error_2(self):

        global_config.GRASS_RESOURCE_DIR = "/tmp/rstorage_tmp_nope"
        global_config.GRASS_RESOURCE_QUOTA = 1

        rv = self.server.delete('/resource_storage',
                                headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

if __name__ == '__main__':
    unittest.main()
