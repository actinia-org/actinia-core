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
Tests: Vector Layer test case

TODO: fix below raster --> vector
"""
from flask.json import loads as json_load
import unittest

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann, Guido Riembauer"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class RasterLayerTestCase(ActiniaResourceTestCaseBase):
    def test_creation_1(self):
        # Remove potentially existing raster layer
        new_mapset = "raster_test_mapset"
        self.create_new_mapset(new_mapset)

        # Create
        region = {"n": 228500, "s": 215000, "e": 645000, "w": 630000}
        parameter = {"npoints": 1, "zmin": 1, "zmax": 1, "seed": 1}
        self.create_vector_layer(
            "nc_spm_08", new_mapset, "test_layer", region, parameter
        )

        # Check
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/vector_layers/test_layer",
            headers=self.user_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        areas = json_load(rv.data)["process_results"]["areas"]
        points = json_load(rv.data)["process_results"]["points"]
        centroids = json_load(rv.data)["process_results"]["centroids"]

        self.assertEqual(areas, "0")
        self.assertEqual(points, "1")
        self.assertEqual(centroids, "0")

        # Delete
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/vector_layers/test_layer",
            headers=self.user_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Delete fail
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            f"{new_mapset}/vector_layers/test_layer",
            headers=self.user_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_layer_info(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/vector_layers/boundary_county",
            headers=self.user_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        areas = json_load(rv.data)["process_results"]["areas"]
        nodes = json_load(rv.data)["process_results"]["nodes"]
        centroids = json_load(rv.data)["process_results"]["centroids"]

        self.assertEqual(areas, "926")
        self.assertEqual(nodes, "1114")
        self.assertEqual(centroids, "926")

    def test_layer_info_error_1(self):
        # Raster does not exist
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/vector_layers/boundary_county_nope",
            headers=self.user_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )


if __name__ == "__main__":
    unittest.main()
