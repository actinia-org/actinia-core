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
Tests: Location test case
"""
from flask.json import loads as json_loads, dumps as json_dumps
import unittest

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class LocationTestCase(ActiniaResourceTestCaseBase):
    def test_list_locations(self):
        rv = self.server.get(
            URL_PREFIX + "/locations", headers=self.user_auth_header
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        if "nc_spm_08" in json_loads(rv.data)["locations"]:
            location = "nc_spm_08"

        self.assertEqual(location, "nc_spm_08", "Wrong location listed")

    def test_location_info(self):
        rv = self.server.get(
            URL_PREFIX + "/locations/nc_spm_08/info",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        region_settings = json_loads(rv.data)["process_results"]["region"]
        json_loads(rv.data)["process_results"]["projection"]

        self.assertTrue("depths" in region_settings)
        self.assertTrue("ewres" in region_settings)
        self.assertTrue("cols" in region_settings)
        self.assertTrue("rows" in region_settings)

    def test_location_global_db_error(self):
        # ERROR: Try to create a location as admin that exists in the global
        # database
        rv = self.server.post(
            URL_PREFIX + "/locations/nc_spm_08",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_location_creation_and_deletion(self):
        # Delete a potentially existing location
        rv = self.server.delete(
            URL_PREFIX + "/locations/test_location",
            headers=self.admin_auth_header,
        )

        # Create new location as admin
        rv = self.server.post(
            URL_PREFIX + "/locations/test_location",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # ERROR: Try to create a location as admin that already exists
        rv = self.server.post(
            URL_PREFIX + "/locations/test_location",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Delete location
        rv = self.server.delete(
            URL_PREFIX + "/locations/test_location",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # ERROR: Delete should fail, since location does not exists
        rv = self.server.delete(
            URL_PREFIX + "/locations/test_location",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_location_creation_and_deletion_as_user(self):
        # Delete a potentially existing location
        rv = self.server.delete(
            URL_PREFIX + "/locations/test_location",
            headers=self.user_auth_header,
        )

        # Create new location as user
        rv = self.server.post(
            URL_PREFIX + "/locations/test_location",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.user_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            200,
            "Location creation by user: HTML status code is wrong %i"
            % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype,
            "application/json",
            "Location creation by user: Wrong mimetype %s" % rv.mimetype,
        )

        # ERROR: Try to create a location as user that already exists
        rv = self.server.post(
            URL_PREFIX + "/locations/test_location",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.user_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            400,
            "Location recreation by user: HTML status code is wrong %i"
            % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype,
            "application/json",
            "Location recreation by user: Wrong mimetype %s" % rv.mimetype,
        )

        # Delete location
        rv = self.server.delete(
            URL_PREFIX + "/locations/test_location",
            headers=self.user_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            200,
            "Location deletion by user: HTML status code is wrong %i"
            % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype,
            "application/json",
            "Location deletion by user: Wrong mimetype %s" % rv.mimetype,
        )

        # ERROR: Delete should fail, since location does not exists
        rv = self.server.delete(
            URL_PREFIX + "/locations/test_location",
            headers=self.user_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            400,
            "Location redeletion by user: HTML status code is wrong %i"
            % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype,
            "application/json",
            "Location redeletion by user: Wrong mimetype %s" % rv.mimetype,
        )

    def test_location_creation_and_deletion_as_guest(self):
        # ERROR: Try to create a location as guest
        rv = self.server.post(
            URL_PREFIX + "/locations/test_location_user",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.guest_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # ERROR: Delete should fail since the guest user is not authorized
        rv = self.server.delete(
            URL_PREFIX + "/locations/test_location_user",
            headers=self.guest_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )


if __name__ == "__main__":
    unittest.main()
