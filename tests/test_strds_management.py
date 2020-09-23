# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2018 Sören Gebbert and mundialis GmbH & Co. KG
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#######

"""
Tests: STRDS test case
"""
from flask.json import loads as json_loads, dumps as json_dumps
import unittest
try:
    from .test_resource_base import ActiniaResourceTestCaseBase, global_config, URL_PREFIX
except:
    from test_resource_base import ActiniaResourceTestCaseBase, global_config, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class STRDSTestCase(ActiniaResourceTestCaseBase):

    #################### LIST RASTER ##########################################

    def test_list_strds(self):
        rv = self.server.get(URL_PREFIX + '/locations/ECAD/mapsets/PERMANENT/strds',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        strds_list = json_loads(rv.data)["process_results"]
        self.assertTrue("precipitation_1950_2013_yearly_mm" in strds_list)
        self.assertTrue("temperature_mean_1950_2013_yearly_celsius" in strds_list)

    def test_list_strds_where_1(self):
        rv = self.server.get(URL_PREFIX + "/locations/ECAD/mapsets/PERMANENT/strds?where=start_time > '1900-01-01'",
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        strds_list = json_loads(rv.data)["process_results"]
        self.assertTrue("precipitation_1950_2013_yearly_mm" in strds_list)
        self.assertTrue("temperature_mean_1950_2013_yearly_celsius" in strds_list)

    def test_list_strds_where_2(self):
        rv = self.server.get(URL_PREFIX + "/locations/ECAD/mapsets/PERMANENT/strds?where=start_time > '2000-01-01'",
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        strds_list = json_loads(rv.data)["process_results"]

        self.assertEqual(len(strds_list), 0)

    #################### INFO #################################################

    def test_strds_info(self):
        rv = self.server.get(URL_PREFIX + '/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        start_time = json_loads(rv.data)["process_results"]["start_time"]

        self.assertEqual(start_time, "'1950-01-01 00:00:00'")

    #################### CREATE REMOVE ########################################

    def test_strds_create_remove(self):

        new_mapset = "strds_test"
        self.create_new_mapset(mapset_name=new_mapset, location_name="ECAD")

        # Create success
        rv = self.server.post(URL_PREFIX + '/locations/ECAD/mapsets/%s/strds/test_strds' %new_mapset,
                              headers=self.admin_auth_header,
                              data=json_dumps({"temporaltype": "absolute",
                                               "title": "A nice title",
                                               "description": "A nice description"}),
                              content_type="application/json")
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        # Create failure since the strds already exists
        rv = self.server.post(URL_PREFIX + '/locations/ECAD/mapsets/%s/strds/test_strds' %new_mapset,
                              headers=self.admin_auth_header,
                              data=json_dumps({"temporaltype": "absolute",
                                               "title": "A nice title",
                                               "description": "A nice description"}),
                              content_type="application/json")
        # print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)
        # Read/check information of the new strds
        rv = self.server.get(URL_PREFIX + '/locations/ECAD/mapsets/%s/strds/test_strds' %new_mapset,
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        start_time = json_loads(rv.data)["process_results"]["start_time"]

        self.assertEquals(start_time, "'None'")
        # Delete the strds
        rv = self.server.delete(URL_PREFIX + '/locations/ECAD/mapsets/%s/strds/test_strds' %new_mapset,
                                headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)
        # Try to delete the strds again to produce an error
        rv = self.server.delete(URL_PREFIX + '/locations/ECAD/mapsets/%s/strds/test_strds' %new_mapset,
                                headers=self.admin_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        rv = self.server.get(URL_PREFIX + '/locations/ECAD/mapsets/%s/strds/test_strds' %new_mapset,
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

    #################### ERROR ################################################

    def test_strds_info_error_1(self):
        # Raster does not exist
        rv = self.server.get(URL_PREFIX + '/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm_nope',
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

    def test_list_strds_where_error_1(self):
        # Wrong where statement
        rv = self.server.get(URL_PREFIX + "/locations/ECAD/mapsets/PERMANENT/strds?where=start_timing > '2000-01-01'",
                             headers=self.user_auth_header)
        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

if __name__ == '__main__':
    unittest.main()
