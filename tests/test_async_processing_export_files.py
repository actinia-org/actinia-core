# -*- coding: utf-8 -*-
import unittest
from test_resource_base import ActiniaResourceTestCaseBase
from flask.json import loads as json_loads, dumps as json_dumps
import requests

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"

# Module change example for r.slope.aspect with g.region adjustment
process_chain_long = {
   1:{
        "module":"g.region",
        "inputs":{
            "raster":"elevation@PERMANENT",
            "res":"1000"
        },
        "flags":"p",
        "verbose":True
   },
   2:{
        "module":"r.slope.aspect",
        "inputs":{
            "elevation":"elevation@PERMANENT",
            "format":"degrees",
            "min_slope":"0.0"
        },
        "outputs":{
            "aspect":{
                "name":"my_aspect",
                "export":{
                    "format":"GTiff",
                    "type":"raster"
                }
            },
            "slope":{
                "name":"my_slope",
                "export":{
                    "format":"GTiff",
                    "type":"raster"
                }
            }
        },
        "flags":"a",
        "overwrite":True,
        "verbose":True
   },
   3:{
        "module":"r.watershed",
        "inputs":{
            "elevation":"elevation@PERMANENT"
        },
        "outputs":{
            "accumulation":{
                "name":"my_accumulation",
                "export":{
                    "format":"GTiff",
                    "type":"raster"
                }
            }
        }
   }
}


class AsyncProcessExport2TestCaseAdmin(ActiniaResourceTestCaseBase):

    def test_async_processing_export(self):

        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_long),
                              content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        # Get the exported results
        urls = resp["urls"]["resources"]

        for url in urls:
            print(url)
            rv = self.server.get(url, headers=self.user_auth_header)
            self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
            self.assertEqual(rv.mimetype, "image/tiff", "Wrong mimetype %s"%rv.mimetype)
            print(rv.headers)
            print(rv.iter_encoded())


class AsyncProcessExportTestCaseAdminS3(ActiniaResourceTestCaseBase):
    """Test the S3 storage support"""

    def test_async_processing_export(self):

        rv = self.server.post('/locations/nc_spm_08/processing_async_export_s3',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_long),
                              content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        # Get the exported results
        urls = resp["urls"]["resources"]

        for url in urls:
            print(url)
            rv = requests.get(url)
            print(rv)
            self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)

    def test_termination(self):

        rv = self.server.post('/locations/nc_spm_08/processing_async_export_s3',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_long),
                              content_type="application/json")
        resp = json_loads(rv.data)
        # Send the termination request
        self.server.delete("/status/%s/%s" % (resp["user_id"], resp["resource_id"]),
                           headers=self.admin_auth_header)

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="terminated",
                                       message_check="AsyncProcessTermination:")


class AsyncProcessExportTestCaseAdminGCS(ActiniaResourceTestCaseBase):
    """Test the GCS storage support"""

    def test_async_processing_export(self):

        rv = self.server.post('/locations/nc_spm_08/processing_async_export_gcs',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_long),
                              content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        # Get the exported results
        urls = resp["urls"]["resources"]

        for url in urls:
            print(url)
            rv = requests.get(url)
            print(rv)
            self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)

    def test_termination(self):

        rv = self.server.post('/locations/nc_spm_08/processing_async_export_gcs',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_long),
                              content_type="application/json")
        resp = json_loads(rv.data)
        # Send the termination request
        self.server.delete("/status/%s/%s" % (resp["user_id"], resp["resource_id"]),
                           headers=self.admin_auth_header)

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="terminated",
                                       message_check="AsyncProcessTermination:")


if __name__ == '__main__':
    unittest.main()
