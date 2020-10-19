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
Tests: Sentinel2 processing library test case
"""
from actinia_core.resources.common.sentinel_processing_library import Sentinel2Processing
from actinia_core.resources.common.config import global_config
import os
import unittest

__license__    = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Soeren Gebbert"
__email__      = "soerengebbert@googlemail.com"


class MessageDummy(object):

    def info(self, message):
        print(message)

    def warning(self, message):
        print(message)

    def debug(self, message):
        print(message)

    def error(self, message):
        print(message)


def update_dummy(message):
    print(message)


class Sentinel2ProcessingLibraryTestCase(unittest.TestCase):
    """This class tests the BigQuery google interface to collect download
    urls of landsat and sentinel data
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf('GOOGLE_APPLICATION_CREDENTIALS' not in os.environ and 'GOOGLE_CLOUD_PROJECT' not in os.environ,
                     "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and 'GOOGLE_CLOUD_PROJECT' not set")
    def test_download_import_commands(self):
        gsqi = Sentinel2Processing(global_config, "S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138",
                                   None, ["B12", "B08"], "/tmp", "/tmp/", update_dummy, MessageDummy())
        # download commands
        result, maps = gsqi.get_sentinel2_download_process_list()
        print(len(result))
        for p in result:
            print(str(p))

        #self.assertTrue(len(result) == 4)

        # import commands
        result = gsqi.get_sentinel2_import_process_list()
        print(len(result))
        for p in result:
            print(str(p))

        #self.assertTrue(len(result) == 2 + 8 + 8)

        # r.mapclalc ndvi processing
        result = gsqi.get_ndvi_r_mapcalc_process_list(nir="nir", red="red", raster_result_name="ndvi")
        print(len(result))
        for p in result:
            print(str(p))

        #self.assertTrue(len(result) == 2)


if __name__ == '__main__':
    unittest.main()
