# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2021 mundialis GmbH & Co. KG
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
Tests: Mapset test case
"""
from flask.json import loads as json_load
import uuid
import unittest
try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Julia Haas, Guido Riembauer"
__copyright__ = "Copyright 2021 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class MapsetsTestCase(ActiniaResourceTestCaseBase):

    test_mapsets = [str(uuid.uuid4()), str(uuid.uuid4())]

    def tearDown(self):
        # unlock and delete the test mapsets
        rv = self.server.get(URL_PREFIX + '/locations/nc_spm_08/mapsets',
                             headers=self.user_auth_header)
        existing_mapsets = json_load(rv.data)["process_results"]
        for mapset in self.test_mapsets:
            if mapset in existing_mapsets:
                rvdellock = self.server.delete(
                    URL_PREFIX + '/locations/nc_spm_08/mapsets/%s/lock' % mapset,
                    headers=self.admin_auth_header)
                print(rvdellock.data.decode())

                rvdel = self.server.delete(
                    URL_PREFIX + '/locations/nc_spm_08/mapsets/%s' % mapset,
                    headers=self.admin_auth_header)
                print(rvdel.data.decode())

    def test_no_locked_mapsets(self):
        # Test correct behaviour if no mapsets are locked
        rv = self.server.get(URL_PREFIX + '/mapsets?status=locked',
                             headers=self.admin_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" % rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype)
        rvdata = json_load(rv.data)
        mapset_list = rvdata["locked_mapsets_list"]
        message = rvdata["message"]
        mapsets_no = int(message.split(":")[-1])
        self.assertEqual(mapsets_no, 0, "Number of locked mapsets is not 0")
        self.assertEqual(mapset_list, [], "locked_mapsets_list is not empty")

    def test_two_locked_mapsets(self):
        # Test correct behaviour if two mapsets are locked
        for mapset in self.test_mapsets:
            self.create_new_mapset(mapset)
            rvpost = self.server.post(URL_PREFIX + '/locations/nc_spm_08/mapsets/%s/lock' % mapset,
                                      headers=self.admin_auth_header)
        rv = self.server.get(URL_PREFIX + '/mapsets?status=locked',
                             headers=self.admin_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" % rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype)
        rvdata = json_load(rv.data)
        mapset_set = set(rvdata["locked_mapsets_list"])
        ref_set = set(["nc_spm_08/{}".format(ms) for ms in self.test_mapsets])
        message = rvdata["message"]
        mapsets_no = int(message.split(":")[-1])
        self.assertEqual(mapsets_no, 2, "Number of locked mapsets is not 2")
        self.assertEqual(mapset_set, ref_set,"Names of locked mapsets do not match reference")

    def test_user_error(self):
        # Test correct behaviour if user role is not admin
        rv = self.server.get(URL_PREFIX + '/mapsets?status=locked',
                             headers=self.user_auth_header)
        self.assertEqual(rv.status_code, 401, "Status code is not 401: %s" % rv.status_code)

if __name__ == '__main__':
    unittest.main()
