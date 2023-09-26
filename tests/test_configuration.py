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
Tests: Configuration test case
"""
import unittest
from actinia_core.core.common.config import Configuration

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ConfigurationTestCase(unittest.TestCase):
    """
    This class tests the user interface, the creation and deletion
    of a user entry in a Redis database
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
