# -*- coding: utf-8 -*-
from flask.json import loads as json_load
import unittest
from flask.json import dumps as json_dumps
try:
    from .test_resource_base import ActiniaResourceTestCaseBase
except:
    from test_resource_base import ActiniaResourceTestCaseBase


__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class RasterLayerTestCase(ActiniaResourceTestCaseBase):

    #################### CREATION #############################################

    def test_creation_1(self):
        # Remove potentially existing raster layer
        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        # Create
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/vector_layers/test_layer'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps({"region":{"n":228500, "s":215000,
                                                         "e":645000,"w":630000},
                                               "parameter": { "npoints":1, "zmin":1,
                                                              "zmax":1, "seed":1}}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Create fail
        rv = self.server.post('/locations/nc_spm_08/mapsets/%s/vector_layers/test_layer'%new_mapset,
                              headers=self.user_auth_header,
                              data=json_dumps({"npoints":1, "zmin":1, "zmax":1, "seed":1}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Check
        rv = self.server.get('/locations/nc_spm_08/mapsets/%s/vector_layers/test_layer'%new_mapset,
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        areas = json_load(rv.data)["process_results"]["areas"]
        points = json_load(rv.data)["process_results"]["points"]
        centroids = json_load(rv.data)["process_results"]["centroids"]

        self.assertEqual(areas, "0")
        self.assertEqual(points, "1")
        self.assertEqual(centroids, "0")

        # Delete
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/vector_layers/test_layer'%new_mapset,
                                headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Delete fail
        rv = self.server.delete('/locations/nc_spm_08/mapsets/%s/vector_layers/test_layer'%new_mapset,
                                headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_layer_info(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers/boundary_county',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        areas = json_load(rv.data)["process_results"]["areas"]
        nodes = json_load(rv.data)["process_results"]["nodes"]
        centroids = json_load(rv.data)["process_results"]["centroids"]

        self.assertEqual(areas, "926")
        self.assertEqual(nodes, "1114")
        self.assertEqual(centroids, "926")

    def test_layer_info_error_1(self):
        # Raster does not exist
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers/boundary_county_nope',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

if __name__ == '__main__':
    unittest.main()
