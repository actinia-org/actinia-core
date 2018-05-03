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


class RasterLayerRendererTestCase(ActiniaResourceTestCaseBase):

    #################### IMAGE ################################################

    def test_raster_layer_image_no_args(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/render',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_args_1(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/render?'
                             'n=228500&s=215000&w=630000&e=645000',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_args_2(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/render?'
                             'n=228500&s=215000&w=630000&e=645000&width=100&height=100',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_args_3(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/render?'
                             'width=100&height=100',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_args_error_1(self):
        # North is smaller then south
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/render?'
                             'n=-228500&s=215000',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_args_error_2(self):
        # Negative size
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/'
                             'render?&width=-100&height=-100',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_args_error_3(self):
        # Raster does not exist
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevat/render?',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    #################### RGB IMAGE ############################################

    def test_raster_layer_image_rgb_1(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/landsat/render_rgb?'
                             'red=lsat5_1987_10&blue=lsat5_1987_20&green=lsat5_1987_30',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_rgb_2(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/landsat/render_rgb?'
                          'n=228513&s=214975.5&w=629992.5&e=645012&width=100&height=100'
                          '&red=lsat5_1987_30&blue=lsat5_1987_20&green=lsat5_1987_10',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_rgb_3(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/landsat/render_rgb?'
                          'width=100&height=100'
                          '&red=lsat5_1987_30&blue=lsat5_1987_20&green=lsat5_1987_10',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_rgb_error_green(self):
        # No green raster layer
        rv = self.server.get('/locations/nc_spm_08/mapsets/landsat/render_rgb?'
                          'n=228513&s=214975.5&w=629992.5&e=645012'
                          '&red=lsat5_1987_30&blue=lsat5_1987_20',
                             headers=self.user_auth_header)

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_rgb_error_blue(self):
        # No blue raster layer
        rv = self.server.get('/locations/nc_spm_08/mapsets/landsat/render_rgb?'
                          'n=228513&s=214975.5&w=629992.5&e=645012'
                          '&red=lsat5_1987_30&green=lsat5_1987_20',
                             headers=self.user_auth_header)

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_rgb_error_red(self):
        # No red raster layer
        rv = self.server.get('/locations/nc_spm_08/mapsets/landsat/render_rgb?'
                          'n=228513&s=214975.5&w=629992.5&e=645012'
                          '&blue=lsat5_1987_30&green=lsat5_1987_20',
                             headers=self.user_auth_header)

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_rgb_error_wrong_raster(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/landsat/render_rgb?'
                          'n=228513&s=214975.5&w=629992.5&e=645012'
                          '&red=lsat5_1987_30_1&blue=lsat5_1987_20&green=lsat5_1987_10',
                             headers=self.user_auth_header)

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_rgb_error_mapset_in_name_1(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/landsat/render_rgb?'
                             'red=lsat5_1987_10@landsat&blue=lsat5_1987_20&green=lsat5_1987_30',
                             headers=self.user_auth_header)

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_rgb_error_mapset_in_name_2(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/landsat/render_rgb?'
                             'red=lsat5_1987_10&blue=lsat5_1987_20@landsat&green=lsat5_1987_30',
                             headers=self.user_auth_header)

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_rgb_error_mapset_in_name_3(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/landsat/render_rgb?'
                             'red=lsat5_1987_10&blue=lsat5_1987_20&green=lsat5_1987_30@landsat',
                             headers=self.user_auth_header)

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    #################### SHADE IMAGE ##########################################

    def test_raster_layer_image_shade_1(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/render_shade?'
                             'shade=aspect&color=elevation',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_shade_2(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/render_shade?'
                             'width=100&height=100'
                             '&shade=aspect&color=elevation',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_error_mapset_in_name_1(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/render_shade?'
                             '&shade=aspect@PERMANENT&color=elevation',
                             headers=self.user_auth_header)

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_error_mapset_in_name_2(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/render_shade?'
                             '&shade=aspect&color=elevation@PERMANENT',
                             headers=self.user_auth_header)

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_layer_image_error_missing_color_1(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/render_shade?'
                             '&shade=aspect',
                             headers=self.user_auth_header)

        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)


if __name__ == '__main__':
    unittest.main()
