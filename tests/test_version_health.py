# -*- coding: utf-8 -*-
from .test_resource_base import ActiniaResourceTestCaseBase
import unittest

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class VersionHealthTestCase(ActiniaResourceTestCaseBase):

    def test_version(self):
        rv = self.server.get('/version')
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)

    def test_health_check(self):
        rv = self.server.get('/health_check')
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)

if __name__ == '__main__':
    unittest.main()
