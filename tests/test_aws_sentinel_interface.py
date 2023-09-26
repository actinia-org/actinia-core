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
Tests: AWS Sentinel interface test case
"""
from actinia_core.core.common.aws_sentinel_interface import (
    AWSSentinel2AInterface,
)
from actinia_core.core.common.config import global_config
import unittest
from pprint import pprint
import magic
import os
from urllib.request import urlopen

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"


class AWSSentinelInterfaceTestCase(unittest.TestCase):
    """This class tests theAWS interface to collect download
    urls of sentinel data
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def validate_result(self, result, bands):
        for scene in result:
            for tile in scene["tiles"]:
                url = tile["info"]
                response = urlopen(url)
                mime_type = magic.from_buffer(
                    response.read(256), mime=True
                ).lower()
                print(mime_type)
                self.assertTrue(mime_type in ["text/plain"])

                url = tile["metadata"]
                response = urlopen(url)
                mime_type = magic.from_buffer(
                    response.read(256), mime=True
                ).lower()
                print(mime_type)
                self.assertTrue(
                    mime_type in ["application/xml"]
                    or mime_type in ["text/xml"]
                )

                url = tile["preview"]
                response = urlopen(url)
                mime_type = magic.from_buffer(
                    response.read(256), mime=True
                ).lower()
                print(mime_type)
                self.assertTrue(mime_type in ["image/jpeg"])

                for band in bands:
                    url = tile[band]["public_url"]

                    # Download 256 bytes from the url and check its mimetype
                    response = urlopen(url)
                    mime_type = magic.from_buffer(
                        response.read(256), mime=True
                    ).lower()
                    print(mime_type)

                    self.assertTrue(mime_type in ["image/jp2"])

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def otest_query_for_sentinel_scenes_single_old(self):
        aws = AWSSentinel2AInterface(global_config)
        result = aws.get_sentinel_urls(
            [
                "S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_"
                "V20151207T003302_20151207T003302",
            ],
            ["B12", "B08"],
        )
        pprint(result)

        self.assertTrue(
            "S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_V20151207T003302_"
            "20151207T003302" in result[0]["product_id"]
        )
        self.validate_result(result, ["B12", "B08"])

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def otest_query_for_sentinel_scenes_single_old_geojson(self):
        aws = AWSSentinel2AInterface(global_config)
        result = aws.get_sentinel_urls(
            [
                "S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_V20151207"
                "T003302_20151207T003302",
            ],
            ["B12", "B08"],
        )
        pprint(result)

        self.assertTrue(
            "S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_V20151207"
            "T003302_20151207T003302" in result[0]["product_id"]
        )

        for tile in result[0]["tiles"]:
            geojson = aws.get_sentinel_tile_footprint(tile)
            print(geojson)

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def otest_query_for_sentinel_scenes_single_new(self):
        aws = AWSSentinel2AInterface(global_config)
        result = aws.get_sentinel_urls(
            [
                "S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138",
            ],
            ["B12", "B08"],
        )
        pprint(result)

        self.assertTrue(
            "S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138"
            in result[0]["product_id"]
        )
        self.validate_result(result, ["B12", "B08"])

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def otest_query_for_sentinel_scenes_single_new_safe(self):
        aws = AWSSentinel2AInterface(global_config)
        result = aws.get_sentinel_urls(
            [
                "S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212"
                "T104138.SAFE",
            ],
            ["B12", "B08"],
        )
        pprint(result)

        self.assertTrue(
            "S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138"
            in result[0]["product_id"]
        )
        self.validate_result(result, ["B12", "B08"])

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def otest_query_for_sentinel_scenes_singler_eplacement_bug(self):
        aws = AWSSentinel2AInterface(global_config)
        result = aws.get_sentinel_urls(
            [
                "S2A_MSIL1C_20171210T020751_N0206_R017_T50HPG_20171210T052001",
            ],
            ["B12", "B08"],
        )
        pprint(result)

        self.assertTrue(
            "S2A_MSIL1C_20171210T020751_N0206_R017_T50HPG_20171210T052001"
            in result[0]["product_id"]
        )
        self.validate_result(result, ["B12", "B08"])

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def otest_query_for_sentinel_scenes_singler_eplacement_bug_2(self):
        aws = AWSSentinel2AInterface(global_config)
        result = aws.get_sentinel_urls(
            [
                "S2A_OPER_PRD_MSIL1C_PDMC_20161031T014722_R087_V20161030"
                "T235752_20161030T235752",
            ],
            ["B12", "B08"],
        )
        pprint(result)

        self.assertTrue(
            "S2A_OPER_PRD_MSIL1C_PDMC_20161031T014722_R087_V20161030"
            "T235752_20161030T235752" in result[0]["product_id"]
        )
        self.validate_result(result, ["B12", "B08"])

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def otest_query_for_sentinel_scenes_mutli_mixed(self):
        aws = AWSSentinel2AInterface(global_config)
        result = aws.get_sentinel_urls(
            [
                "S2A_MSIL1C_20170202T090201_N0204_R007_T36TVT_20170202T090155",
                "S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_V20151207"
                "T003302_20151207T003302",
                "S2A_MSIL1C_20170218T143751_N0204_R096_T20PRT_20170218T143931",
            ],
            ["B04", "B08"],
        )
        pprint(result)

        self.assertTrue(
            "S2A_MSIL1C_20170202T090201_N0204_R007_T36TVT_20170202T090155"
            in result[0]["product_id"]
        )
        self.assertTrue(
            "S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_V20151207T003302_"
            "20151207T003302" in result[1]["product_id"]
        )
        self.assertTrue(
            "S2A_MSIL1C_20170218T143751_N0204_R096_T20PRT_20170218T143931"
            in result[2]["product_id"]
        )
        self.validate_result(result, ["B04", "B08"])

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def otest_query_for_sentinel_scenes_single_error(self):
        aws = AWSSentinel2AInterface(global_config)

        try:
            result = aws.get_sentinel_urls(
                [
                    "S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212"
                    "T104138_NOPE",
                ],
                ["B12", "B08"],
            )
            pprint(result)
            self.assertTrue(False, "The error was not found")
        except Exception as e:
            self.assertTrue(
                True,
                "An exception was raised for the correct reason: %s" % str(e),
            )

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def otest_query_for_sentinel_scenes_multi_error(self):
        aws = AWSSentinel2AInterface(global_config)

        try:
            result = aws.get_sentinel_urls(
                [
                    "S2A_MSIL1C_20170202T090201_N0204_R007_T36TVT_"
                    "20170202T090155",
                    "S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_"
                    "V20151207T003302_20151207T003302",
                    "S2A_MSIL1C_20170218T143751_N0204_R096_T20PRT_"
                    "20170218T143931_NOPE",
                ],
                ["B04", "B08"],
            )
            pprint(result)
            self.assertTrue(False, "The error was not found")
        except Exception as e:
            self.assertTrue(
                True,
                "An exception was raised for the correct reason: %s" % str(e),
            )

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def otest_query_for_sentinel_scenes_band_error(self):
        aws = AWSSentinel2AInterface(global_config)

        try:
            aws.get_sentinel_urls(
                [
                    "S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_"
                    "20170212T104138_NOPE",
                ],
                ["B120", "B080"],
            )
            # pprint(result)
            self.assertTrue(False, "The error was not found")
        except Exception as e:
            self.assertTrue(
                True,
                "An exception was raised for the correct reason: %s" % str(e),
            )


if __name__ == "__main__":
    unittest.main()
