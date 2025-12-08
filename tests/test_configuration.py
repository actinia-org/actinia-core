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
Tests: Configuration test case
"""
import unittest
from actinia_core.core.common.config import Configuration

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2023, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ConfigurationTestCase(unittest.TestCase):
    """
    This class tests the user interface, the creation and deletion
    of a user entry in a Kvdb database
    """

    file_name = "/tmp/actinia_test.cfg"

    def test_change_loglevel(self):
        c = Configuration()

        c.write(self.file_name)
        c.read(self.file_name)

        c.LOG_LEVEL = 1
        c.write(self.file_name)
        c.LOG_LEVEL = 4
        c.read(self.file_name)

        self.assertEqual(c.LOG_LEVEL, 1)

    def test_read_write_exceptions(self):
        c = Configuration()
        self.assertRaises(IOError, c.read, "/dk/l/K/D/V/l/d/g")
        self.assertRaises(IOError, c.write, "/dk/l/K/D/V/l/d/g")


if __name__ == "__main__":
    unittest.main()
