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
Tests: Google Big Query interface test case
"""
from actinia_core.core.common.google_satellite_bigquery_interface import (
    GoogleSatelliteBigQueryInterface,
)
from actinia_core.core.common.config import global_config
import os
import unittest
from pprint import pprint

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"


class GoogleBigQueryInterfaceTestCase(unittest.TestCase):
    """This class tests the BigQuery google interface to collect download
    urls of landsat and sentinel data
    """

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
    def test_query_for_landsat_scene_time(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)

        start = "2017-01-01T10:45:00"
        end = "2017-01-01T10:55:00"

        result = gsqi.query_landsat_archive(start_time=start, end_time=end)
        pprint(result)
        self.assertTrue(len(result) >= 1)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_query_for_landsat_scene_time_coords(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)

        start = "2016-11-01T00:00:00"
        end = "2016-11-03T00:00:00"

        result = gsqi.query_landsat_archive(
            start_time=start, end_time=end, lon=-45.0, lat=-7.0
        )
        pprint(result)
        self.assertTrue(len(result) >= 1)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_query_for_sentinel2_scene_time(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)

        start = "2017-01-01T10:05:00"
        end = "2017-01-01T11:00:00"

        result = gsqi.query_sentinel2_archive(start_time=start, end_time=end)
        pprint(result)
        self.assertEqual(len(result), 154)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_query_for_sentinel2_scene_time_coords(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)

        start = "2016-11-01T00:00:00"
        end = "2016-11-30T00:00:00"

        result = gsqi.query_sentinel2_archive(
            start_time=start, end_time=end, lon=-45.0, lat=-7.0
        )
        pprint(result)
        self.assertTrue(len(result) >= 1)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_query_for_sentinel_scene_sinlge(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)
        # A very small scene
        result = gsqi.get_sentinel_urls(
            [
                "S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138",
            ],
            ["B12", "B08"],
        )
        pprint(result)
        self.assertTrue(len(result) == 1)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_query_for_sentinel_scene_four(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)
        result = gsqi.get_sentinel_urls(
            [
                "S2A_MSIL1C_20170202T090201_N0204_R007_T36TVT_20170202T090155",
                "S2A_MSIL1C_20170221T093031_N0204_R136_T34UGV_20170221T093310",
                "S2A_MSIL1C_20170211T060951_N0204_R134_T44WPT_20170211T060950",
                "S2A_MSIL1C_20170218T143751_N0204_R096_T20PRT_20170218T143931",
            ],
            ["B04", "B08"],
        )
        pprint(result)
        self.assertTrue(len(result) == 4)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_query_for_sentinel_scene_two_missing(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)
        result = gsqi.get_sentinel_urls(
            [
                "S2A_MSIL1C_20170301T225331_N0204_R115_T56DNG_20170301T225347",
                "S2A_MSIL1C_20170221T093031_N0204_R136_T34UGV_20170221T093310",
                "S2A_MSIL1C_NOPE",
                "S2A_MSIL1C_POPE",
            ],
            ["B04", "B08"],
        )
        pprint(result)
        self.assertTrue(len(result) == 2)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_query_for_sentinel_scene_empty_query(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)
        result = gsqi.get_sentinel_urls(
            [
                "S2A_MSIL1C_20170208T092131_N0204_R093_T35TLF_NOPENOPENOPE",
            ],
            ["B04", "B08"],
        )
        pprint(result)
        self.assertTrue(not result)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_query_for_landsat_scene(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)
        result = gsqi.get_landsat_urls(
            [
                "LC80440342016259LGN00",
                "LC80440342013106LGN01",
                "LC80440342013154LGN00",
            ],
            ["B1", "MTL"],
        )
        pprint(result)
        self.assertTrue(len(result) == 3)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_query_for_landsat_scene_one_missing(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)
        result = gsqi.get_landsat_urls(
            [
                "LC80440342016259LGN00",
                "LC80440342013106LGN01",
                "LC80440342013154LGN00_WRONG",
            ],
            ["B1", "MTL"],
        )
        pprint(result)
        self.assertTrue(len(result) == 2)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_query_for_landsat_scene_empty_query(self):
        gsqi = GoogleSatelliteBigQueryInterface(global_config)
        result = gsqi.get_landsat_urls(
            [
                "LE72_NOPENOPENOPE",
            ],
            ["B1", "MTL"],
        )
        pprint(result)
        self.assertTrue(not result)


if __name__ == "__main__":
    unittest.main()
