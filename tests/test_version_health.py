# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2021 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
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


__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Julia Haas"
__copyright__ = "Copyright 2016-2021, Sören Gebbert & mundialis GmbH & Co. KG"
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
