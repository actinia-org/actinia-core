# -*- coding: utf-8 -*-
import unittest
from pprint import pprint
from flask.json import loads as json_load
from flask.json import dumps as json_dumps
try:
    from .test_resource_base import ActiniaResourceTestCaseBase
except:
    from test_resource_base import ActiniaResourceTestCaseBase


__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Soeren Gebbert"
__email__      = "soerengebbert@googlemail.com"


class RasterLayerTestCase(ActiniaResourceTestCaseBase):

    #################### COLORS ###############################################

    def test_raster_layer_get_colors(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/colors',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        colors = json_load(rv.data)["process_results"]
        self.assertTrue(len(colors) == 8)

    def test_raster_layer_set_colors(self):

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
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        rules = {"rules":["1 0:0:0",]}

        # Set the color table
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer/colors'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps(rules),
                              content_type="application/json")

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        rules = {"color":"elevation"}

        # Set the color table
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer/colors'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps(rules),
                              content_type="application/json")

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        rules = {"raster":"elevation@PERMANENT"}

        # Set the color table
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer/colors'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps(rules),
                              content_type="application/json")

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Delete
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                                headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_1_raster_layer_set_colors_errors(self):
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

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        #######################################################################
        rules = {"rules":["wrong format",]}

        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer/colors'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps(rules),
                              content_type="application/json")

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)

        #######################################################################
        rules = {"rules":"blub"}

        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer/colors'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps(rules),
                              content_type="application/json")

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        #######################################################################
        # Two rules
        rules = {"color":"elevation", "raster":"elevation@PERMANENT"}

        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer/colors'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps(rules),
                              content_type="application/json")

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        #######################################################################
        # Wrong format
        rules = {"nonsense":"bla"}

        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer/colors'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps(rules),
                              content_type="application/json")

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        #######################################################################
        # Wrong format
        rules = [1,2,3]

        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer/colors'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps(rules),
                              content_type="application/json")

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        #######################################################################
        # Raster layer not found
        rules = {"raster":"elevation_nope@PERMANENT"}

        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer/colors'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps(rules),
                              content_type="application/json")

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)

        #######################################################################
        # No mapset in name
        rules = {"raster":"elevation"}

        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer/colors'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps(rules),
                              content_type="application/json")

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        #######################################################################
        # Delete
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/raster_layers/test_layer'%new_mapset,
                                headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_colors_error_1(self):
        # Raster does not exist
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevat/colors',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)
        self.assertTrue("Error while running executable <r.colors.out" in log)

if __name__ == '__main__':
    unittest.main()
