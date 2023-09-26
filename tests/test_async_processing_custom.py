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
Tests: Async process custom test case admin
"""
import unittest
from flask.json import dumps as json_dumps

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
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
