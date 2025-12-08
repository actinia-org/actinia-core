# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2024 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Tests: Raster async export test case
"""
import unittest
import time

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = "Copyright 2016-2024, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class RasterAsyncExport(ActiniaResourceTestCaseBase):
    def test_export(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/geotiff_async",
            headers=self.user_auth_header,
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.user_auth_header
        )

        # Get the exported results
        urls = resp["urls"]["resources"]

        for url in urls:
            print(url)
            rv = self.server.get(url, headers=self.user_auth_header)
            self.assertEqual(
                rv.status_code,
                200,
                "HTML status code is wrong %i" % rv.status_code,
            )
            self.assertEqual(
                rv.mimetype, "image/tiff", "Wrong mimetype %s" % rv.mimetype
            )
            print(rv.headers)

        time.sleep(1)

    def test_export_region(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/geotiff_async_orig",
            headers=self.user_auth_header,
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.user_auth_header
        )

        # Get the exported results
        urls = resp["urls"]["resources"]

        for url in urls:
            print(url)
            rv = self.server.get(url, headers=self.user_auth_header)
            self.assertEqual(
                rv.status_code,
                200,
                "HTML status code is wrong %i" % rv.status_code,
            )
            self.assertEqual(
                rv.mimetype, "image/tiff", "Wrong mimetype %s" % rv.mimetype
            )
            print(rv.headers)

        time.sleep(1)

    def test_export_error(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevationion/geotiff_async",
            headers=self.user_auth_header,
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )


if __name__ == "__main__":
    unittest.main()
