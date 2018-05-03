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


class STRDSRenderTestCase(ActiniaResourceTestCaseBase):

    def test_strds_render_1(self):

        new_mapset = "strds_render_test"
        self.create_new_mapset(new_mapset, "ECAD")

        # Create success
        rv = self.server.post('/locations/ECAD/mapsets/%s/strds/test_strds_register'%new_mapset,
                              headers=self.admin_auth_header,
                              data=json_dumps({"temporaltype": "absolute",
                                               "title": "A nice title",
                                               "description": "A nice description"}),
                              content_type="application/json")
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Create the raster layer
        rv = self.server.post('/locations/ECAD/mapsets/%s/raster_layers/test_layer_1'%new_mapset,
                              headers=self.admin_auth_header,
                              data=json_dumps({"expression": "1"}),
                              content_type="application/json")
        pprint(json_load(rv.data))
        rv = self.server.post('/locations/ECAD/mapsets/%s/raster_layers/test_layer_2'%new_mapset,
                              headers=self.admin_auth_header,
                              data=json_dumps({"expression": "2"}),
                              content_type="application/json")
        pprint(json_load(rv.data))
        rv = self.server.post('/locations/ECAD/mapsets/%s/raster_layers/test_layer_3'%new_mapset,
                              headers=self.admin_auth_header,
                              data=json_dumps({"expression": "3"}),
                              content_type="application/json")
        pprint(json_load(rv.data))

        raster_layers = [{"name": "test_layer_1", "start_time": "2000-01-01", "end_time": "2000-01-02"},
                         {"name": "test_layer_2", "start_time": "2000-01-02", "end_time": "2000-01-03"},
                         {"name": "test_layer_3", "start_time": "2000-01-03", "end_time": "2000-01-04"}]

        rv = self.server.put("/locations/ECAD/mapsets/%s/strds/test_strds_register/raster_layers"%new_mapset,
                             data=json_dumps(raster_layers),
                             content_type="application/json",
                             headers=self.admin_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Check strds
        rv = self.server.get("/locations/ECAD/mapsets/%s/strds/test_strds_register/render?"
                             "width=100&height=100"%new_mapset,
                             headers=self.admin_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

        # Check strds
        rv = self.server.get("/locations/ECAD/mapsets/%s/strds/test_strds_register/render?"
                             "width=100&height=100&start_time=2000-01-01&end_time=2000-01-02"%new_mapset,
                             headers=self.admin_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s"%rv.mimetype)

if __name__ == '__main__':
    unittest.main()
