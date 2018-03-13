# -*- coding: utf-8 -*-
import unittest
from test_resource_base import ActiniaResourceTestCaseBase
from flask.json import dumps as json_dumps

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class AsyncProcessCustomTestCaseAdmin(ActiniaResourceTestCaseBase):

    def test_async_processing(self):

        rv = self.server.post('/custom_process/uname',
                              headers=self.admin_auth_header,
                              data=json_dumps(["-a"]),
                              content_type="application/json")
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

    def test_async_processing_error_1(self):
        """
        Test the error handling in case the program was not found
        Returns:

        """
        rv = self.server.post('/custom_process/uname_nopo',
                              headers=self.admin_auth_header,
                              data=json_dumps(["-a"]),
                              content_type="application/json")
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header, http_status=400, status="error")

    def test_async_processing_error_2(self):
        """
        Test the error handling in case the program was not found
        Returns:

        """
        rv = self.server.post('/custom_process/cat',
                              headers=self.admin_auth_header,
                              data=json_dumps(["non_existing_file"]),
                              content_type="application/json")
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header, http_status=400, status="error",
                                       message_check="AsyncProcessError:")

    def test_async_processing_user(self):
        """
        Sleep for one secnond
        Returns:

        """
        rv = self.server.post('/custom_process/sleep',
                              headers=self.user_auth_header,
                              data=json_dumps(["1"]),
                              content_type="application/json")
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

    def test_async_processing_error_to_long(self):
        """
        Test the error handling in case the program is running too long
        Returns:

        """
        rv = self.server.post('/custom_process/sleep',
                              headers=self.user_auth_header,
                              data=json_dumps(["5"]),
                              content_type="application/json")
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header, http_status=400, status="terminated",
                                       message_check="AsyncProcessTimeLimit:")

    def test_async_processing_unauthorized_access(self):
        """
        Test the error handling in case the program is is not in access list
        Returns:

        """
        rv = self.server.post('/custom_process/ps',
                              headers=self.user_auth_header,
                              data=json_dumps(["-rf"]),
                              content_type="application/json")
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header, http_status=400, status="error",
                                       message_check="AsyncProcessError:")


if __name__ == '__main__':
    unittest.main()
