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
Tests: version health
"""
import unittest

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Julia Haas"
__copyright__ = (
    "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class VersionHealthTestCase(ActiniaResourceTestCaseBase):
    def test_version(self):
        """test version endpoint"""
        rv = self.server.get(URL_PREFIX + "/version")
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )

    def test_version_slash(self):
        """test version endpoint with trailing slash"""
        rv = self.server.get(URL_PREFIX + "/version/")
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )

    def test_health_check(self):
        """test health_check endpoint"""
        rv = self.server.get(URL_PREFIX + "/health_check")
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )

    def test_health_check_slash(self):
        """test health_check endpoint with trailing slash"""
        rv = self.server.get(URL_PREFIX + "/health_check/")
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )


if __name__ == "__main__":
    unittest.main()
