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
Tests: AsyncProcess test case
"""
import unittest
from flask.json import dumps as json_dumps

try:
    from .test_resource_base import (
        ActiniaResourceTestCaseBase,
        URL_PREFIX,
        additional_external_data,
    )
except ModuleNotFoundError:
    from test_resource_base import (
        ActiniaResourceTestCaseBase,
        URL_PREFIX,
        additional_external_data,
    )

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = "Copyright 2016-2024, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

vector_layer_export = {
    "list": [
        {
            "id": "exporter_1",
            "outputs": [
                {
                    "export": {"type": "vector", "format": "GML"},
                    "param": "map",
                    "value": "hospitals",
                },
                {
                    "export": {"type": "vector", "format": "GeoJSON"},
                    "param": "map",
                    "value": "nc_state",
                },
                {
                    "export": {"type": "vector", "format": "GPKG"},
                    "param": "map",
                    "value": "nc_state",
                },
                {
                    "export": {"type": "vector", "format": "SQLite"},
                    "param": "map",
                    "value": "nc_state",
                },
                {
                    "export": {"type": "vector", "format": "ESRI_Shapefile"},
                    "param": "map",
                    "value": "firestations",
                },
                {
                    "export": {"type": "vector", "format": "CSV"},
                    "param": "map",
                    "value": "poi_names_wake",
                },
            ],
            "module": "exporter",
        }
    ],
    "version": "1",
}


vector_layer_buffer = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data["rio_json"],
                        "type": "vector",
                    },
                    "param": "map",
                    "value": "input_point",
                }
            ],
        },
        {
            "id": "v_buffer",
            "module": "v.buffer",
            "inputs": [
                {"param": "input", "value": "input_point"},
                {"param": "output", "value": "buf_point"},
                {"param": "distance", "value": "0.001"},
            ],
        },
        {
            "id": "exporter_1",
            "module": "exporter",
            "outputs": [
                {
                    "export": {"type": "vector", "format": "GeoJSON"},
                    "param": "map",
                    "value": "buf_point",
                }
            ],
        },
    ],
    "version": "1",
}


vector_layer_clean = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data["rio_json"],
                        "type": "vector",
                    },
                    "param": "map",
                    "value": "map_to_clean",
                }
            ],
        },
        {
            "id": "v_clean",
            "module": "v.clean",
            "inputs": [
                {"param": "input", "value": "map_to_clean"},
                {"param": "output", "value": "map_cleaned"},
                {"param": "type", "value": "area"},
                {"param": "tool", "value": "rmarea"},
                {"param": "threshold", "value": "0.0000000001"},
            ],
        },
        {
            "id": "exporter_1",
            "module": "exporter",
            "outputs": [
                {
                    "export": {"type": "vector", "format": "GeoJSON"},
                    "param": "map",
                    "value": "map_cleaned",
                }
            ],
        },
    ],
    "version": "1",
}


class AsyncProcessTestCase(ActiniaResourceTestCaseBase):
    def test_vector_export(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(vector_layer_export),
            content_type="application/json",
        )

        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
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
                rv.mimetype,
                "application/zip",
                "Wrong mimetype %s" % rv.mimetype,
            )

    def test_vector_buffer(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/latlong_wgs84/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(vector_layer_buffer),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
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
                rv.mimetype,
                "application/zip",
                "Wrong mimetype %s" % rv.mimetype,
            )

            out_file = open("/tmp/bla.zip", "wb")
            out_file.write(rv.data)
            out_file.close()

    def test_vector_clean(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/latlong_wgs84/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(vector_layer_clean),
            content_type="application/json",
        )

        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
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
                rv.mimetype,
                "application/zip",
                "Wrong mimetype %s" % rv.mimetype,
            )

            out_file = open("/tmp/bla.zip", "wb")
            out_file.write(rv.data)
            out_file.close()


if __name__ == "__main__":
    unittest.main()
