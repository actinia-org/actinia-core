# -*- coding: utf-8 -*-
import unittest
from .test_resource_base import ActiniaResourceTestCaseBase
import time

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class RasterAsyncExport(ActiniaResourceTestCaseBase):

    def test_export(self):

        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/geotiff_async',
                             headers=self.user_auth_header)
        resp = self.waitAsyncStatusAssertHTTP(rv, headers=self.user_auth_header)

        # Get the exported results
        urls = resp["urls"]["resources"]

        for url in urls:
            print(url)
            rv = self.server.get(url, headers=self.user_auth_header)
            self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
            self.assertEqual(rv.mimetype, "image/tiff", "Wrong mimetype %s"%rv.mimetype)
            print(rv.headers)

        time.sleep(1)

    def test_export_region(self):

        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/geotiff_async_orig',
                             headers=self.user_auth_header)
        resp = self.waitAsyncStatusAssertHTTP(rv, headers=self.user_auth_header)

        # Get the exported results
        urls = resp["urls"]["resources"]

        for url in urls:
            print(url)
            rv = self.server.get(url, headers=self.user_auth_header)
            self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
            self.assertEqual(rv.mimetype, "image/tiff", "Wrong mimetype %s"%rv.mimetype)
            print(rv.headers)

        time.sleep(1)

    def test_export_error(self):

        rv = self.server.get('/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevationion/geotiff_async',
                             headers=self.user_auth_header)
        self.waitAsyncStatusAssertHTTP(rv, headers=self.user_auth_header, http_status=400, status="error",
                                       message_check="AsyncProcessError:")


if __name__ == '__main__':
    unittest.main()
