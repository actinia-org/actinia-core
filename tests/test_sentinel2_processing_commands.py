# -*- coding: utf-8 -*-
from actinia_core.resources.common.sentinel_processing_library import Sentinel2Processing
from actinia_core.resources.common.config import global_config
import unittest

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
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
