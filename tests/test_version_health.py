# -*- coding: utf-8 -*-
import unittest
try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX


__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class VersionHealthTestCase(ActiniaResourceTestCaseBase):

    def test_version(self):
        rv = self.server.get(URL_PREFIX + '/version')
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)

    def test_health_check(self):
        rv = self.server.get(URL_PREFIX + '/health_check')
        print(rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)


if __name__ == '__main__':
    unittest.main()
