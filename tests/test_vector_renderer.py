# -*- coding: utf-8 -*-
import unittest
from pprint import pprint
from flask.json import loads as json_load
try:
    from .test_resource_base import ActiniaResourceTestCaseBase
except:
    from test_resource_base import ActiniaResourceTestCaseBase


__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Soeren Gebbert"
__email__      = "soerengebbert@googlemail.com"


class VectorLayerRendererTestCase(ActiniaResourceTestCaseBase):

    #################### IMAGE ################################################

    def test_vectorlayer_image_no_args(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers/boundary_county/render',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_vectorlayer_image_args_1(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers/boundary_county/render?'
                             'n=228500&s=215000&w=630000&e=645000',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_vectorlayer_image_args_2(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers/boundary_county/render?'
                             'n=228500&s=215000&w=630000&e=645000&width=100&height=100',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_vectorlayer_image_args_3(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers/boundary_county/render?'
                             'width=100&height=100',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_vectorlayer_image_args_error_1(self):
        # North is smaller then south
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers/boundary_county/render?'
                             'n=-228500&s=215000',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_vectorlayer_image_args_error_2(self):
        # Negative size
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers/boundary_county/'
                             'render?&width=-100&height=-100',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_vectorlayer_image_args_error_3(self):
        # Raster does not exist
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/vector_layers/boundary_county_nomap/render?',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)


if __name__ == '__main__':
    unittest.main()
