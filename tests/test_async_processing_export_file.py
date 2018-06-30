# -*- coding: utf-8 -*-
import unittest
from flask.json import loads as json_loads, dumps as json_dumps
import requests
try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

# Module  example for r.out.ascii output file export
file_export = {
    "version":1,
    "webhook": "http://0.0.0.0:5005/webhook",
    "list": [
        {
            "id": "1",
            "exe": "/bin/sleep",
            "params": ["1"]
        },
        {
            "id": "2",
            "module": "g.region",
            "inputs": [
                {"param": "raster",
                 "value": "elevation@PERMANENT"},
                {"param":"res",
                 "value": "10000"}
            ],
            "flags": "p",
            "verbose": True
        },
        {
            "id": "3",
            "module": "r.out.ascii",
            "inputs": [{"param":"input",
                        "value": "elevation@PERMANENT"}],
            "outputs": [
                {"export": {"type": "file", "format": "TXT"},
                 "param":"output",
                 "value": "$file::out1"}
            ]
        },
        {
            "id": "4",
            "module": "r.out.ascii",
            "inputs": [{"param": "input",
                       "value": "elevation@PERMANENT"}],
            "outputs": [
                {"export": {"type": "file", "format": "TXT"},
                 "param": "output",
                 "value": "$file::out2"}
            ]
        }
    ]
}


class AsyncProcessFileExportTestCase(ActiniaResourceTestCaseBase):

    def test_async_processing_file_export(self):
        rv = self.server.post(URL_PREFIX + '/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(file_export),
                              content_type="application/json")

        resp = self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        # Get the exported results
        urls = resp["urls"]["resources"]

        for url in urls:
            print(url)
            rv = self.server.get(url, headers=self.user_auth_header)
            self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
            self.assertEqual(rv.mimetype, "application/zip", "Wrong mimetype %s"%rv.mimetype)
            print(rv.headers)
            print(rv.iter_encoded())

    def test_termination(self):

        rv = self.server.post(URL_PREFIX + '/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(file_export),
                              content_type="application/json")
        resp = json_loads(rv.data)
        # Send the termination request
        delinfo = self.server.delete(URL_PREFIX + "/resources/%s/%s" % (resp["user_id"], resp["resource_id"]),
                                     headers=self.admin_auth_header)

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="terminated",
                                       message_check="AsyncProcessTermination:")


class AsyncProcessExportTestCaseAdminS3(ActiniaResourceTestCaseBase):
    """Test the S3 storage support

    Deactivated due to credential exposition problem
    """

    def test_async_processing_export(self):

        rv = self.server.post(URL_PREFIX + '/locations/nc_spm_08/processing_async_export_s3',
                              headers=self.admin_auth_header,
                              data=json_dumps(file_export),
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

        rv = self.server.post(URL_PREFIX + '/locations/nc_spm_08/processing_async_export_s3',
                              headers=self.admin_auth_header,
                              data=json_dumps(file_export),
                              content_type="application/json")
        resp = json_loads(rv.data)
        # Send the termination request
        self.server.delete(URL_PREFIX + "/resources/%s/%s" % (resp["user_id"], resp["resource_id"]),
                           headers=self.admin_auth_header)

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="terminated",
                                       message_check="AsyncProcessTermination:")


class AsyncProcessExportTestCaseAdminGCS(ActiniaResourceTestCaseBase):
    """Test the GCS storage support

    Deactivated due to credential exposition problem
    """

    def test_async_processing_export(self):

        rv = self.server.post(URL_PREFIX + '/locations/nc_spm_08/processing_async_export_gcs',
                              headers=self.admin_auth_header,
                              data=json_dumps(file_export),
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

        rv = self.server.post(URL_PREFIX + '/locations/nc_spm_08/processing_async_export_gcs',
                              headers=self.admin_auth_header,
                              data=json_dumps(file_export),
                              content_type="application/json")
        resp = json_loads(rv.data)
        # Send the termination request
        self.server.delete(URL_PREFIX + "/resources/%s/%s" % (resp["user_id"], resp["resource_id"]),
                           headers=self.admin_auth_header)

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="terminated",
                                       message_check="AsyncProcessTermination:")

if __name__ == '__main__':
    unittest.main()
