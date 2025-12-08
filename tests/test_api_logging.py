# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2023 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Tests: API logging test case
"""
import unittest
from actinia_core.core.common.api_logger import ApiLogger
from actinia_core.core.common.app import flask_app

try:
    from .test_resource_base import ActiniaResourceTestCaseBase
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2023, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class DummyHTTPRequest(object):
    def __init__(self):
        self.path = "path"
        self.endpoint = "endpoint"
        self.url = "url"
        self.method = "GET"


class ApiLoggingTestCase(ActiniaResourceTestCaseBase):
    """
    This class tests the api logging interface
    """

    def setUp(self):
        # We need to set the application context
        self.app_context = flask_app.app_context()
        self.app_context.push()
        # The test user
        self.user_id = "soeren"
        self.log = ApiLogger()
        self.request_object = DummyHTTPRequest()

    def tearDown(self):
        self.app_context.pop()

    def test_logging(self):
        ret = self.log.add_entry(
            user_id=self.user_id, http_request=self.request_object
        )

        self.assertTrue(ret, "add_entry does not work")

        ret = self.log.add_entry(
            user_id=self.user_id, http_request=self.request_object
        )

        self.assertTrue(ret, "add_entry does not work")

        ret = self.log.add_entry(
            user_id=self.user_id, http_request=self.request_object
        )

        self.assertTrue(ret, "add_entry does not work")

        size = self.log.size(self.user_id)

        self.assertEqual(size, 3, "The size method does not work %i" % size)

        list_of_logs = self.log.list(self.user_id, start=0, end=-1)

        for entry in list_of_logs:
            self.assertEqual(entry["api_info"]["endpoint"], "endpoint")
            self.assertEqual(entry["api_info"]["method"], "GET")

        # Remove the first entry
        self.log.trim(self.user_id, 1, -1)

        size = self.log.size(self.user_id)

        self.assertEqual(size, 2, "The size method does not work %i" % size)

        list_of_logs = self.log.list(self.user_id, start=0, end=-1)

        for entry in list_of_logs:
            self.assertEqual(entry["api_info"]["endpoint"], "endpoint")
            self.assertEqual(entry["api_info"]["method"], "GET")

        self.assertTrue(self.log.delete(self.user_id))


if __name__ == "__main__":
    unittest.main()
