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
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Julia Haas, Guido Riembauer"
__copyright__ = "Copyright 2021 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class MapsetsTestCase(ActiniaResourceTestCaseBase):
    test_mapsets = [str(uuid.uuid4()), str(uuid.uuid4())]
    test_user = f"test_user_{str(uuid.uuid4())}"
    accessible_datasets = {
        "nc_spm_08": ["PERMANENT"],
        "latlong_wgs84": ["PERMANENT"],
    }
    ref_mapsets = []
    for location in accessible_datasets:
        for mapset in accessible_datasets[location]:
            ref_mapsets.append(f"{location}/{mapset}")

    @classmethod
    def setUpClass(cls):
        super(ActiniaResourceTestCaseBase, cls).setUpClass()

        # Create test_user
        (
            cls.test_user_id,
            cls.test_user_group,
            cls.test_user_auth_header,
        ) = cls.create_user(
            name=cls.test_user,
            role="user",
            accessible_datasets=cls.accessible_datasets,
        )

    def tearDown(self):
        # unlock and delete the test mapsets
        rv = self.server.get(
            URL_PREFIX + "/locations/nc_spm_08/mapsets",
            headers=self.user_auth_header,
        )
        existing_mapsets = json_load(rv.data)["process_results"]
        for mapset in self.test_mapsets:
            if mapset in existing_mapsets:
                rvdellock = self.server.delete(
                    URL_PREFIX
                    + "/locations/nc_spm_08/mapsets/%s/lock" % mapset,
                    headers=self.admin_auth_header,
                )
                print(rvdellock.data.decode())

                rvdel = self.server.delete(
                    URL_PREFIX + "/locations/nc_spm_08/mapsets/%s" % mapset,
                    headers=self.admin_auth_header,
                )
                print(rvdel.data.decode())

    def test_two_locked_mapsets(self):
        # Test correct behaviour if two mapsets are locked
        for mapset in self.test_mapsets:
            self.create_new_mapset(mapset)
            self.server.post(
                URL_PREFIX + "/locations/nc_spm_08/mapsets/%s/lock" % mapset,
                headers=self.root_auth_header,
            )
        rv = self.server.get(
            URL_PREFIX + "/mapsets?status=locked",
            headers=self.root_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )
        rvdata = json_load(rv.data)
        mapset_list = rvdata["locked_mapsets_list"]
        ref_list = ["nc_spm_08/{}".format(ms) for ms in self.test_mapsets]
        for ref_mapset in ref_list:
            self.assertIn(
                ref_mapset,
                mapset_list,
                "%s is not in the list of locked mapsets" % ref_mapset,
            )

        message = rvdata["message"]
        mapsets_no = int(message.split(":")[-1])
        self.assertGreaterEqual(
            mapsets_no, 2, "Number of locked mapsets is smaller than 2"
        )

        print(
            "Currently there are %s locked mapsets:\n %s"
            % (str(mapsets_no), "\n".join(mapset_list))
        )

    def test_user_error(self):
        # Test correct behaviour if user role is not admin
        rv = self.server.get(
            URL_PREFIX + "/mapsets?status=locked",
            headers=self.user_auth_header,
        )
        self.assertEqual(
            rv.status_code, 401, "Status code is not 401: %s" % rv.status_code
        )

    def test_user_own_mapsets(self):
        """Test if user can list available mapsets"""
        rv = self.server.get(
            URL_PREFIX + "/mapsets", headers=self.test_user_auth_header
        )
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        rvdata = json_load(rv.data)
        mapsets = rvdata["available_mapsets"]
        self.assertEqual(
            mapsets,
            self.ref_mapsets,
            "Mapset list is not equal to reference mapset list",
        )

    def test_superadmin_user_mapsets(self):
        """Test if superadmin can list available mapsets from test_user"""
        rv = self.server.get(
            URL_PREFIX + f"/mapsets?user={self.test_user}",
            headers=self.root_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        rvdata = json_load(rv.data)
        mapsets = rvdata["available_mapsets"]
        self.assertEqual(
            mapsets,
            self.ref_mapsets,
            "Mapset list is not equal to reference mapset list",
        )

    def test_user_user_mapsets(self):
        # Test if test_user can list available mapsets from user
        rv = self.server.get(
            URL_PREFIX + f"/mapsets?user={self.test_user}",
            headers=self.user_auth_header,
        )
        self.assertEqual(
            rv.status_code, 401, "Status code is not 401: %s" % rv.status_code
        )


if __name__ == "__main__":
    unittest.main()
