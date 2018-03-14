# -*- coding: utf-8 -*-
from .test_resource_base import ActiniaResourceTestCaseBase
from flask.json import loads as json_load, dumps as json_dumps
import unittest

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class RasterLayerTestCase(ActiniaResourceTestCaseBase):

    #################### CREATION #############################################

    def test_creation_1(self):

        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        # Create
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps({"region":{"n":228500, "s":215000,
                                                         "e":645000,"w":630000,
                                                         "ewres": 50, "nsres": 50},
                                               "expression": "1"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)
        # Check
        rv = self.server.get('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                             headers=self.user_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        minimum = json_load(rv.data)["process_results"]["min"]
        maximum = json_load(rv.data)["process_results"]["max"]
        datatype = json_load(rv.data)["process_results"]["datatype"]

        self.assertEqual(minimum, "1")
        self.assertEqual(maximum, "1")
        self.assertEqual(datatype, "CELL")
        # Delete
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                                headers=self.user_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_creation_2(self):
        """Check integer point raster creation"""

        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        # Create
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps({"region":{"n":228500, "s":215000,
                                                         "e":645000,"w":630000,
                                                         "ewres": 50, "nsres": 50},
                                               "expression": "1"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)
        # Check
        rv = self.server.get('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                             headers=self.user_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        minimum = json_load(rv.data)["process_results"]["min"]
        maximum = json_load(rv.data)["process_results"]["max"]
        datatype = json_load(rv.data)["process_results"]["datatype"]

        self.assertEqual(minimum, "1")
        self.assertEqual(maximum, "1")
        self.assertEqual(datatype, "CELL")
        # Delete
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                                headers=self.user_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_creation_3(self):
        """Check floating point raster creation"""
        # Remove potentially existing raster layer
        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        # Create
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps({"region":{"n":228500, "s":215000,
                                                         "e":645000,"w":630000,
                                                         "ewres": 50, "nsres": 50},
                                               "expression": "1.5"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)
        # Check
        rv = self.server.get('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                             headers=self.user_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        minimum = json_load(rv.data)["process_results"]["min"]
        maximum = json_load(rv.data)["process_results"]["max"]
        datatype = json_load(rv.data)["process_results"]["datatype"]

        self.assertEqual(minimum, "1.5")
        self.assertEqual(maximum, "1.5")
        self.assertEqual(datatype, "DCELL")
        # Delete
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                                headers=self.user_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_creation_4(self):
        # Remove potentially existing raster layer
        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        # Create
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer_1'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps({"region":{"n":228500, "s":215000,
                                                         "e":645000,"w":630000,
                                                         "ewres": 50, "nsres": 50},
                                               "expression": "1.0"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Create
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer_2'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps({"region":{"n":228500, "s":215000,
                                                         "e":645000,"w":630000,
                                                         "ewres": 50, "nsres": 50},
                                               "expression": "2.0"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Create
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer_3'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps({"region":{"n":228500, "s":215000,
                                                         "e":645000,"w":630000,
                                                         "ewres": 50, "nsres": 50},
                                               "expression": "3.0"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Delete
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/raster_layers?pattern=test_layer_*'%new_mapset,
                                headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Delete is empty and fails
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/raster_layers?pattern=test_layer_*'%new_mapset,
                                headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_creation_error_1(self):
        # Remove potentially existing raster layer
        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        # Create
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps({"region":{"n":228500, "s":215000,
                                                         "e":645000,"w":630000,
                                                         "ewres": 50, "nsres": 50},
                                               "expression": "1"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)
        # Create fail
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps({"region":{"n":228500, "s":215000,
                                                         "e":645000,"w":630000,
                                                         "ewres": 50, "nsres": 50},
                                               "expression": "1"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Delete
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                                headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)
        # Delete fail
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                                headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    #################### INFO #################################################

    def test_raster_layer_info(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        cells = json_load(rv.data)["process_results"]["cells"]
        cols = json_load(rv.data)["process_results"]["cols"]
        datatype = json_load(rv.data)["process_results"]["datatype"]

        self.assertEqual(cells, "2025000")
        self.assertEqual(cols, "1500")
        self.assertEqual(datatype, "FCELL")

    def test_raster_layer_info_error_1(self):
        # Raster does not exist
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevat',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

if __name__ == '__main__':
    unittest.main()
