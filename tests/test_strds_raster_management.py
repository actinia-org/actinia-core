# -*- coding: utf-8 -*-
from flask.json import loads as json_loads, dumps as json_dumps
import unittest
try:
    from .test_resource_base import ActiniaResourceTestCaseBase
except:
    from test_resource_base import ActiniaResourceTestCaseBase

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class STRDSTestCase(ActiniaResourceTestCaseBase):

    #################### CREATE REGISTER ######################################

    def test_strds_creation_error(self):

        # This must fail, global mapsets are not allowed to modify
        rv = self.server.post('/locations/ECAD/mapsets/PERMANENT/strds/test_strds_register',
                              headers=self.admin_auth_header,
                              data=json_dumps({"temporaltype": "absolute",
                                               "title": "A nice title",
                                               "description": "A nice description"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)


    def test_strds_create_register_unregister_1(self):

        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset, "ECAD")

        # Create success
        rv = self.server.post('/locations/ECAD/mapsets/%s/strds/test_strds_register'%new_mapset,
                              headers=self.admin_auth_header,
                              data=json_dumps({"temporaltype": "absolute",
                                               "title": "A nice title",
                                               "description": "A nice description"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Create the raster layer
        rv = self.server.post('/locations/ECAD/mapsets/%s/raster_layers/test_layer_1'%new_mapset,
                              headers=self.admin_auth_header,
                              data=json_dumps({"expression": "1"}),
                              content_type="application/json")
        print(rv.data)
        rv = self.server.post('/locations/ECAD/mapsets/%s/raster_layers/test_layer_2'%new_mapset,
                              headers=self.admin_auth_header,
                              data=json_dumps({"expression": "2"}),
                              content_type="application/json")
        print(rv.data)
        rv = self.server.post('/locations/ECAD/mapsets/%s/raster_layers/test_layer_3'%new_mapset,
                              headers=self.admin_auth_header,
                              data=json_dumps({"expression": "3"}),
                              content_type="application/json")
        print(rv.data)

        raster_layers = [{"name": "test_layer_1", "start_time": "2000-01-01", "end_time": "2000-01-02"},
                         {"name": "test_layer_2", "start_time": "2000-01-02", "end_time": "2000-01-03"},
                         {"name": "test_layer_3", "start_time": "2000-01-03", "end_time": "2000-01-04"}]

        rv = self.server.put("/locations/ECAD/mapsets/%s/strds/test_strds_register/raster_layers"%new_mapset,
                             data=json_dumps(raster_layers),
                             content_type="application/json",
                             headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Check strds
        rv = self.server.get("/locations/ECAD/mapsets/%s/strds/test_strds_register"%new_mapset,
                             headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        min_min = json_loads(rv.data)["process_results"]["min_min"]
        max_max = json_loads(rv.data)["process_results"]["max_max"]
        num_maps = json_loads(rv.data)["process_results"]["number_of_maps"]
        self.assertEqual(min_min, "1.0")
        self.assertEqual(max_max, "3.0")
        self.assertEqual(num_maps, "3")

        # Unregister the raster layers
        raster_layers = ["test_layer_1", "test_layer_2", "test_layer_3"]

        rv = self.server.delete("/locations/ECAD/mapsets/%s/strds/test_strds_register/raster_layers"%new_mapset,
                                data=json_dumps(raster_layers),
                                content_type="application/json",
                                headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Check strds
        rv = self.server.get("/locations/ECAD/mapsets/%s/strds/test_strds_register"%new_mapset,
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        min_min = json_loads(rv.data)["process_results"]["min_min"]
        max_max = json_loads(rv.data)["process_results"]["max_max"]
        num_maps = json_loads(rv.data)["process_results"]["number_of_maps"]
        self.assertEqual(min_min, "None")
        self.assertEqual(max_max, "None")
        self.assertEqual(num_maps, "0")

        # Delete the strds
        rv = self.server.delete('/locations/ECAD/mapsets/%s/strds/test_strds_register'%new_mapset,
                                headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    #################### LIST RASTER FROM STRDS ###############################

    def test_strds_raster_layer_1(self):
        rv = self.server.get('/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm/raster_layers',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        map_list = json_loads(rv.data)["process_results"]
        self.assertEqual(len(map_list), 63)

    def test_strds_raster_layer_2(self):
        rv = self.server.get("/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm/raster_layers?"
                          "where=start_time > '2000-01-01'",
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        map_list = json_loads(rv.data)["process_results"]
        self.assertEqual(len(map_list), 13)

    #################### ERROR ################################################

    def test_strds_info_error_1(self):
        # Raster does not exist
        rv = self.server.get('/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm_nope',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_list_strds_where_error_1(self):
        # Wrong where statement
        rv = self.server.get("/locations/ECAD/mapsets/PERMANENT/strds?where=start_timing > '2000-01-01'",
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

if __name__ == '__main__':
    unittest.main()
