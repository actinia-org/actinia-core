# -*- coding: utf-8 -*-
import unittest
from flask.json import loads as json_load
try:
    from .test_resource_base import ActiniaResourceTestCaseBase
except:
    from test_resource_base import ActiniaResourceTestCaseBase

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class VectorLayersTestCase(ActiniaResourceTestCaseBase):

    #################### LIST RASTER ##########################################

    def test_list_vector_layers(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        map_list = json_load(rv.data)["process_results"]
        self.assertTrue("boundary_county" in map_list)
        self.assertTrue("firestations" in map_list)
        self.assertTrue("geology" in map_list)
        self.assertTrue("hospitals" in map_list)

    def test_list_vector_layers_pattern(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers?pattern=elev_*',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        map_list = json_load(rv.data)["process_results"]
        self.assertFalse("boundary_county" in map_list)
        self.assertTrue("elev_lid792_bepts" in map_list)
        self.assertTrue("elev_lid792_cont1m" in map_list)
        self.assertTrue("elev_lid792_randpts" in map_list)
        self.assertTrue("elev_lidrural_mrpts" in map_list)
        self.assertTrue("elev_lidrural_mrptsft" in map_list)

    def test_list_vector_layers_empty_list(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers?pattern=NONE',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        map_list = json_load(rv.data)["process_results"]
        self.assertTrue(len(map_list) == 0)

if __name__ == '__main__':
    unittest.main()
