# -*- coding: utf-8 -*-from graas_api.resources.common.config import Configuration
from __future__ import print_function
import unittest
from actinia_core.resources.common.config import Configuration

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class ConfigurationTestCase(unittest.TestCase):
    """
    This class tests the user interface, the creation and deletion
    of a user entry in a Redis database
    """

    file_name = "/tmp/graas_test.cfg"

    def test_change_loglevel(self):

        c = Configuration()

        c.write(self.file_name)
        c.read(self.file_name)

        c.LOG_LEVEL = 1
        c.write(self.file_name)
        c.LOG_LEVEL = 4
        c.read(self.file_name)

        self.assertEquals(c.LOG_LEVEL, 1)

        print(c)

    def test_read_write_exceptions(self):

        c = Configuration()
        self.assertRaises(IOError, c.read, "/dk/l/K/D/V/l/d/g")
        self.assertRaises(IOError, c.write, "/dk/l/K/D/V/l/d/g")

if __name__ == '__main__':
    unittest.main()
