# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2021-present mundialis GmbH & Co. KG
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
Tests: Upload vector via endpoint test case
"""
import os
import unittest

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except Exception:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Anika Weinmann, Guido Riembauer"
__copyright__ = "Copyright 2016-2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"

geojson_data = """{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -78.64837646484375,
              35.820040281161
            ],
            [
              -78.71429443359375,
              35.75765724051559
            ],
            [
              -78.63739013671874,
              35.71752800693265
            ],
            [
              -78.54400634765624,
              35.737595151747826
            ],
            [
              -78.55499267578125,
              35.808904044068626
            ],
            [
              -78.64837646484375,
              35.820040281161
            ]
          ]
        ]
      }
    }
  ]
}"""


class UploadVectorLayerTestCase(ActiniaResourceTestCaseBase):
    project = "nc_spm_08"
    mapset = "PERMANENT"
    tmp_mapset = "mapset_upload"
    vector = "testvector"
    local_geojson = f"/tmp/{vector}.geojson"
    gpkg_file = "/src/actinia_core/tests/data/nc_test_poly.gpkg"
    zipped_shp_file = "/src/actinia_core/tests/data/nc_test_poly.zip"

    ref_info = {
        "Attributes": [{"column": "cat", "type": "INTEGER"}],
        "areas": "1",
        "islands": "1",
        "boundaries": "1",
        "centroids": "1",
        "lines": "0",
        "map3d": "0",
        "nodes": "1",
        "points": "0",
        "primitives": "2",
        "attribute_layer_number": "1",
        "attribute_primary_key": "cat",
        "bottom": "0.000000",
        "top": "0.000000",
        "east": "650847.36413895",
        "north": "229689.570968999",
        "south": "218319.98552841",
        "west": "635437.976534827",
    }

    @classmethod
    def setUpClass(cls):
        # download a vector to re-upload it
        super(UploadVectorLayerTestCase, cls).setUpClass()

        # write GeoJSON
        with open(cls.local_geojson, "w") as geojson:
            geojson.write(geojson_data)

    @classmethod
    def tearDownClass(cls):
        # remove GeoJSON
        os.remove(cls.local_geojson)

    def setUp(self):
        # create new temp mapset
        super(UploadVectorLayerTestCase, self).setUp()
        self.create_new_mapset(self.tmp_mapset, project_name=self.project)

    def tearDown(self):
        # delete mapset
        self.delete_mapset(self.tmp_mapset, project_name=self.project)
        super(UploadVectorLayerTestCase, self).tearDown()

    def test_upload_vector_geojson_userdb(self):
        """
        Test successful GeoJSON upload and check against reference vector info
        """
        url = (
            f"{URL_PREFIX}/{self.project_url_part}/{self.project}/"
            f"mapsets/{self.tmp_mapset}/vector_layers/{self.vector}"
        )
        multipart_form_data = {"file": open(self.local_geojson, "rb")}
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

        self.assertVectorInfo(
            self.project,
            self.tmp_mapset,
            self.vector,
            self.ref_info,
            self.user_auth_header,
        )

    def test_upload_vector_gpkg_userdb(self):
        """
        Test successful GPKG upload and check against reference vector info
        """
        url = (
            f"{URL_PREFIX}/{self.project_url_part}/{self.project}/"
            f"mapsets/{self.tmp_mapset}/vector_layers/{self.vector}"
        )
        multipart_form_data = {"file": open(self.gpkg_file, "rb")}
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

        self.assertVectorInfo(
            self.project,
            self.tmp_mapset,
            self.vector,
            self.ref_info,
            self.user_auth_header,
        )

    def test_upload_vector_zipped_shp_userdb(self):
        """
        Test successful zipped Shapefile upload and check against reference
        vector info
        """
        url = (
            f"{URL_PREFIX}/{self.project_url_part}/{self.project}/"
            f"mapsets/{self.tmp_mapset}/vector_layers/{self.vector}"
        )
        multipart_form_data = {"file": open(self.zipped_shp_file, "rb")}
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

        shp_ref_info = self.ref_info.copy()
        shp_ref_info["Attributes"] = [
            {"column": "cat", "type": "INTEGER"},
            {"column": "fid", "type": "DOUBLE PRECISION"},
        ]
        self.assertVectorInfo(
            self.project,
            self.tmp_mapset,
            self.vector,
            shp_ref_info,
            self.user_auth_header,
        )

    def test_upload_vector_globaldb_error(self):
        """Test Error if vector (GPKG) is uploaded to global DB"""
        url = (
            f"{URL_PREFIX}/{self.project_url_part}/{self.project}/"
            f"mapsets/{self.mapset}/vector_layers/{self.vector}"
        )
        multipart_form_data = {"file": open(self.gpkg_file, "rb")}
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
