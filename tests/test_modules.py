# -*- coding: utf-8 -*-
from .test_resource_base import ActiniaResourceTestCaseBase
import unittest

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class GrassModuleTestCase(ActiniaResourceTestCaseBase):

    def test_module_dict(self):

        rv = self.server.get('/modules',
                             headers=self.user_auth_header)
        #print(rv.data)
        print(rv.mimetype)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

if __name__ == '__main__':
    unittest.main()
