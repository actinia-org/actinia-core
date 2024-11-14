# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2024 Sören Gebbert and mundialis GmbH & Co. KG
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
Tests: test list vector layers
"""
import unittest
from flask.json import loads as json_load

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class VectorLayersTestCase(ActiniaResourceTestCaseBase):
    def test_list_vector_layers(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/vector_layers",
            headers=self.user_auth_header,
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

        map_list = json_load(rv.data)["process_results"]
        self.assertTrue("boundary_county" in map_list)
        self.assertTrue("firestations" in map_list)
        self.assertTrue("geology" in map_list)
        self.assertTrue("hospitals" in map_list)

    def test_list_vector_layers_pattern(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/vector_layers?pattern=elev_*",
            headers=self.user_auth_header,
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

        map_list = json_load(rv.data)["process_results"]
        self.assertFalse("boundary_county" in map_list)
        self.assertTrue("elev_lid792_bepts" in map_list)
        self.assertTrue("elev_lid792_cont1m" in map_list)
        self.assertTrue("elev_lid792_randpts" in map_list)
        self.assertTrue("elev_lidrural_mrpts" in map_list)
        self.assertTrue("elev_lidrural_mrptsft" in map_list)

    def test_list_vector_layers_empty_list(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/vector_layers?pattern=NONE",
            headers=self.user_auth_header,
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

        map_list = json_load(rv.data)["process_results"]
        self.assertTrue(len(map_list) == 0)


if __name__ == "__main__":
    unittest.main()
