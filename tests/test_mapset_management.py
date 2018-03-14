# -*- coding: utf-8 -*-
from .test_resource_base import ActiniaResourceTestCaseBase
from flask.json import loads as json_load
import unittest

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class MapsetTestCase(ActiniaResourceTestCaseBase):

    def test_list_mapsets(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        mapsets = json_load(rv.data)["process_results"]

        self.assertTrue("PERMANENT" in  mapsets)
        self.assertTrue("user1" in  mapsets)

    def test_mapsets_region_1(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/info',
                             headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        region_settings = json_load(rv.data)["process_results"]["region"]

        self.assertTrue("depths" in  region_settings)
        self.assertTrue("ewres" in  region_settings)
        self.assertTrue("cols" in  region_settings)
        self.assertTrue("rows" in  region_settings)

    def test_mapsets_region_2(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/user1/info',
                             headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        region_settings = json_load(rv.data)["process_results"]["region"]

        self.assertTrue("depths" in  region_settings)
        self.assertTrue("ewres" in  region_settings)
        self.assertTrue("cols" in  region_settings)
        self.assertTrue("rows" in  region_settings)

    def test_mapset_creation_and_deletion(self):
        self.create_new_mapset("test_mapset")

        # Mapset already exists
        rv = self.server.post('/locations/nc_spm_08/mapsets/test_mapset',
                              headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Delete mapset
        rv = self.server.delete('/locations/nc_spm_08/mapsets/test_mapset',
                                headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Delete should fail, since mapset does not exists
        rv = self.server.delete('/locations/nc_spm_08/mapsets/test_mapset',
                                headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_mapset_creation_and_deletion_unprivileged(self):
        # Create new mapsets as unprivileged user
        rv = self.server.post('/locations/nc_spm_08/mapsets/test_mapset',
                              headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i"%rv.status_code)

        # Delete mapset as unprivileged user
        rv = self.server.delete('/locations/nc_spm_08/mapsets/test_mapset',
                                headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i"%rv.status_code)

    def test_mapset_deletion_permanent_error(self):
        # Delete PERMANENT
        rv = self.server.delete('/locations/nc_spm_08/mapsets/PERMANENT',
                                headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)

    def test_mapset_deletion_global_db_error(self):
        # Delete PERMANENT
        rv = self.server.delete('/locations/nc_spm_08/mapsets/user1',
                                headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)

    def test_mapset_creation_and_locking(self):
        # Unlock mapset for deletion
        rv = self.server.delete('/locations/nc_spm_08/mapsets/test_mapset_2/lock',
                              headers=self.admin_auth_header)
        print(rv.data)

        # Delete any existing mapsets
        rv = self.server.delete('/locations/nc_spm_08/mapsets/test_mapset_2',
                                headers=self.admin_auth_header)
        print(rv.data)

        # Create new mapsets
        rv = self.server.post('/locations/nc_spm_08/mapsets/test_mapset_2',
                              headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Lock mapset
        rv = self.server.post('/locations/nc_spm_08/mapsets/test_mapset_2/lock',
                              headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # get mapset lock(False)
        rv = self.server.get('/locations/nc_spm_08/mapsets/test_mapset_2/lock',
                              headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        lock_status = json_load(rv.data)["process_results"]
        self.assertTrue(lock_status)

        # Unlock mapset
        rv = self.server.delete('/locations/nc_spm_08/mapsets/test_mapset_2/lock',
                              headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # get mapset lock (False)
        rv = self.server.get('/locations/nc_spm_08/mapsets/test_mapset_2/lock',
                              headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        lock_status = json_load(rv.data)["process_results"]
        self.assertFalse(lock_status)

        # Delete mapset
        rv = self.server.delete('/locations/nc_spm_08/mapsets/test_mapset_2',
                                headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # get mapset lock (False)
        rv = self.server.get('/locations/nc_spm_08/mapsets/test_mapset_2/lock',
                              headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        lock_status = json_load(rv.data)["process_results"]
        self.assertFalse(lock_status)

        # Lock mapset
        rv = self.server.post('/locations/nc_spm_08/mapsets/test_mapset_2/lock',
                              headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Unlock mapset
        rv = self.server.delete('/locations/nc_spm_08/mapsets/test_mapset_2/lock',
                              headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

if __name__ == '__main__':
    unittest.main()
