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
Tests: Async process custom test case admin
"""
import unittest
from flask.json import dumps as json_dumps

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2023, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class AsyncProcessCustomTestCaseAdmin(ActiniaResourceTestCaseBase):
    def test_async_processing(self):
        rv = self.server.post(
            URL_PREFIX + "/custom_process/uname",
            headers=self.admin_auth_header,
            data=json_dumps(["-a"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

    def test_async_processing_error_1(self):
        """
        Test the error handling in case the program was not found
        Returns:

        """
        rv = self.server.post(
            URL_PREFIX + "/custom_process/uname_nopo",
            headers=self.admin_auth_header,
            data=json_dumps(["-a"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

    def test_async_processing_error_2(self):
        """
        Test the error handling in case the program was not found
        Returns:

        """
        rv = self.server.post(
            URL_PREFIX + "/custom_process/cat",
            headers=self.admin_auth_header,
            data=json_dumps(["non_existing_file"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )

    def test_async_processing_user(self):
        """
        Sleep for one secnond
        Returns:

        """
        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=self.user_auth_header,
            data=json_dumps(["1"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

    def test_async_processing_error_to_long(self):
        """
        Test the error handling in case the program is running too long
        Returns:

        """
        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=self.user_auth_header,
            data=json_dumps(["10"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=400,
            status="terminated",
            message_check="AsyncProcessTimeLimit:",
        )

    def test_async_processing_unauthorized_access(self):
        """
        Test the error handling in case the program is is not in access list
        Returns:

        """
        rv = self.server.post(
            URL_PREFIX + "/custom_process/ps",
            headers=self.user_auth_header,
            data=json_dumps(["-rf"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )


if __name__ == "__main__":
    unittest.main()
