# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2022 Sören Gebbert and mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Tests: Sentinel2 processing library test case
"""
from actinia_core.core.common.sentinel_processing_library import (
    Sentinel2Processing,
)
from actinia_core.core.common.config import global_config
import os
import unittest
import pytest

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Guido Riembauer"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"


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

    tempdir = "/tmp"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    @pytest.mark.unittest
    def test_download_import_commands(self):
        gsqi = Sentinel2Processing(
            config=global_config,
            product_id="S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_"
            "20170212T104138",
            query_result=None,
            bands=["B12", "B08"],
            temp_file_path=self.tempdir,
            download_cache=self.tempdir,
            send_resource_update=update_dummy,
            message_logger=MessageDummy(),
        )
        # download commands
        result, _ = gsqi.get_sentinel2_download_process_list()
        print(len(result))
        for p in result:
            print(str(p))

        # self.assertTrue(len(result) == 4)

        # import commands
        result = gsqi.get_sentinel2_import_process_list()
        print(len(result))
        for p in result:
            print(str(p))

        # self.assertTrue(len(result) == 2 + 8 + 8)

        # r.mapclalc ndvi processing
        result = gsqi.get_ndvi_r_mapcalc_process_list(
            nir="nir", red="red", raster_result_name="ndvi"
        )
        print(len(result))
        for p in result:
            print(str(p))

        # self.assertTrue(len(result) == 2)

    @pytest.mark.unittest
    def test_download_import_commands_noquery(self):
        gsqi = Sentinel2Processing(
            product_id="S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_"
            "20170212T104138",
            bands=["B12", "B08"],
            download_cache=self.tempdir,
            send_resource_update=update_dummy,
            message_logger=MessageDummy(),
        )
        # download commands
        result, maps = gsqi.get_sentinel2_download_process_list_without_query()
        # there should be just one command (i.sentinel.download)
        self.assertTrue(
            len(result) == 1,
            ("Download process list consists of " "more than one processes"),
        )
        self.assertEqual(
            result[0].executable,
            "i.sentinel.download",
            ("Download process executable is not " "i.sentinel.download"),
        )
        ref_params = [
            "datasource=GCS",
            (
                "query=identifier=S2A_MSIL1C_20170212T104141"
                "_N0204_R008_T31TGJ_20170212T104138"
            ),
            "output=/tmp",
        ]
        self.assertEqual(
            result[0].executable_params,
            ref_params,
            (
                "Download process executable does not have the "
                "expected parameters"
            ),
        )

        # test if mapnames are created correctly
        refmaps = ["T31TGJ_20170212T104141_B12", "T31TGJ_20170212T104141_B08"]
        testmaps = [maps[map][1] for map in maps]
        self.assertEqual(
            refmaps,
            testmaps,
            ("Import maps " f"{','.join(refmaps)} are not created correctly."),
        )
        self.assertTrue("B12" in maps and "B08" in maps, ("Band"))

        # import commands
        result = gsqi.get_sentinel2_import_process_list_without_query()
        # there should be just one command (i.sentinel.import)
        self.assertTrue(
            len(result) == 1,
            ("Import process list consists of " "more than one processes"),
        )
        self.assertEqual(
            result[0].executable,
            "i.sentinel.import",
            ("Import process executable is not " "i.sentinel.import"),
        )
        params = result[0].executable_params
        self.assertTrue(
            "pattern=(B12|B08)" in params,
            ("Import band name " "pattern is incorrect"),
        )


if __name__ == "__main__":
    unittest.main()
