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


class RasterLegendTestCase(ActiniaResourceTestCaseBase):


    #################### IMAGE ################################################

    def test_raster_legend_no_args(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_legend_args_1(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             'at=0,100,0,20',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_legend_args_2(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             'range=100,120',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_legend_args_3(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             '&use=100,110,120',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_legend_args_4(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             '&fontsize=100',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_legend_args_5(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             'width=100&heigth=100',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_legend_args_6(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             'width=100&heigth=100&range=100,120&use=105,110,115&at=0,100,0,30',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_legend_args_7(self):
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             'labelnum=4',
                             headers=self.user_auth_header)

        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

    def test_raster_legend_args_error_1(self):
        # Wrong "at" parameter
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             'at=-0,-0',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)
        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)

    def test_raster_legend_args_error_2(self):
        # Wrong witdth
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             'width=-20&at=20,40,20,40',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)
        log = json_load(rv.data)["message"]
        self.assertFalse("AsyncProcessError:" in log)

    def test_raster_legend_args_error_3(self):
        # Wrong range and use
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             'range=100,120&use=90,130,115',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)
        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)

    def test_raster_legend_args_error_4(self):
        # Wrong labelnum
        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/legend?'
                             'labelnum=-4',
                             headers=self.user_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)
        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)

if __name__ == '__main__':
    unittest.main()
