# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2024 Sören Gebbert and mundialis GmbH & Co. KG
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
Tests: Upload raster via endpoint test case
"""
import os
import unittest
import requests

try:
    from .test_resource_base import (
        ActiniaResourceTestCaseBase,
        URL_PREFIX,
        additional_external_data,
    )
except Exception:
    from test_resource_base import (
        ActiniaResourceTestCaseBase,
        URL_PREFIX,
        additional_external_data,
    )

__license__ = "GPLv3"
__author__ = "Anika Weinmann, Guido Riembauer"
__copyright__ = "Copyright 2016-2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"


class UploadRasterLayerTestCase(ActiniaResourceTestCaseBase):
    project = "nc_spm_08"
    mapset = "PERMANENT"
    tmp_mapset = "mapset_upload"
    raster = "elev_ned_30m"
    raster_url = additional_external_data["elev_ned_30m_tif"]
    local_raster = f"/tmp/{raster}.tif"

    ref_info = {
        "cells": "225000",
        "cols": "500",
        "east": "645000",
        "ewres": "30",
        "maptype": "raster",
        "max": "156.3865",
        "min": "55.1736",
        "ncats": "0",
        "north": "228500",
        "nsres": "30",
        "rows": "450",
        "south": "215000",
        "west": "630000",
    }

    @classmethod
    def setUpClass(cls):
        # download a raster to re-upload it
        super(UploadRasterLayerTestCase, cls).setUpClass()

        resp_download = requests.get(cls.raster_url)
        if resp_download.status_code == 200:
            with open(cls.local_raster, "wb") as out:
                for bits in resp_download.iter_content():
                    out.write(bits)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.local_raster)

    def setUp(self):
        # create new temp mapset
        super(UploadRasterLayerTestCase, self).setUp()
        self.create_new_mapset(self.tmp_mapset, project_name=self.project)

    def tearDown(self):
        # delete mapset
        self.delete_mapset(self.tmp_mapset, project_name=self.project)
        super(UploadRasterLayerTestCase, self).tearDown()

    def test_upload_raster_userdb(self):
        """
        Test successful GeoTIFF upload and check against reference raster info
        """
        url = (
            f"{URL_PREFIX}/{self.project_url_part}/{self.project}/mapsets/"
            f"{self.tmp_mapset}/raster_layers/{self.raster}"
        )
        multipart_form_data = {"file": open(self.local_raster, "rb")}
        rv = self.server.post(
            url,
            content_type="multipart/form-data",
            headers=self.user_auth_header,
            data=multipart_form_data,
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=200,
            status="finished",
        )

        self.assertRasterInfo(
            self.project,
            self.tmp_mapset,
            self.raster,
            self.ref_info,
            self.user_auth_header,
        )

    def test_upload_raster_globaldb_error(self):
        """Test Error if raster is uploaded to global DB"""
        url = (
            f"{URL_PREFIX}/{self.project_url_part}/{self.project}/mapsets/"
            f"{self.mapset}/raster_layers/{self.raster}"
        )
        multipart_form_data = {"file": open(self.local_raster, "rb")}
        rv = self.server.post(
            url,
            content_type="multipart/form-data",
            headers=self.user_auth_header,
            data=multipart_form_data,
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=400,
            status="error",
            message_check=(
                f"Mapset <{self.mapset}> exists in the global "
                "dataset and can not be modified."
            ),
        )


if __name__ == "__main__":
    unittest.main()
