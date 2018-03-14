# -*- coding: utf-8 -*-
import unittest
from .test_resource_base import ActiniaResourceTestCaseBase
from flask.json import dumps as json_dumps

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

vector_layer_export = {
    'list': [{'id': 'exporter_1',
              "outputs": [{"export": {'type': 'vector', 'format': 'GML'},
                           'param': 'map',
                           "value": "hospitals"},
                          {"export": {'type': 'vector', 'format': 'GeoJSON'},
                           'param': 'map',
                           "value": "nc_state"},
                          {"export": {'type': 'vector', 'format': 'ESRI_Shapefile'},
                           'param': 'map',
                           "value": "firestations"},
                          {"export": {'type': 'vector', 'format': 'CSV'},
                           'param': 'map',
                           "value": "poi_names_wake"}],
              'module': 'exporter'}],

    'version': '1'}


vector_layer_buffer = {
    "list": [{
        "id": "importer_1",
        "module": "importer",
        "inputs": [{
            "import_descr": {
                "source": "https://storage.googleapis.com/graas-geodata/rio.json",
                "type": "vector"
            },
            "param": "map",
            "value": "input_point"
        }]
    }, {
        "id": "v_buffer",
        "module": "v.buffer",
        "inputs": [{
            "param": "input",
            "value": "input_point"
        }, {
            "param": "output",
            "value": "buf_point"
        }, {
            "param": "distance",
            "value": "0.001"
        }]
    },
        {
            "id": "exporter_1",
            "module": "exporter",
            "outputs": [{
                "export": {
                    "type": "vector",
                    "format": "GeoJSON"
                },
                "param": "map",
                "value": "buf_point"
            }]
        },
    ],
    "version": "1"
}


class AsyncProcessTestCase(ActiniaResourceTestCaseBase):

    def test_vector_export(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(vector_layer_export),
                              content_type="application/json")

        resp = self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                              http_status=200, status="finished")

        # Get the exported results
        urls = resp["urls"]["resources"]

        for url in urls:
            print(url)
            rv = self.server.get(url, headers=self.user_auth_header)
            self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" % rv.status_code)
            self.assertEqual(rv.mimetype, "application/zip", "Wrong mimetype %s" % rv.mimetype)

    def test_vector_buffer(self):
        rv = self.server.post('/locations/LL/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(vector_layer_buffer),
                              content_type="application/json")

        resp = self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                              http_status=200, status="finished")

        # Get the exported results
        urls = resp["urls"]["resources"]

        for url in urls:
            print(url)
            rv = self.server.get(url, headers=self.user_auth_header)
            self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" % rv.status_code)
            self.assertEqual(rv.mimetype, "application/zip", "Wrong mimetype %s" % rv.mimetype)

            out_file = open("/tmp/bla.zip", "w")
            out_file.write(rv.data)
            out_file.close()


if __name__ == '__main__':
    unittest.main()
