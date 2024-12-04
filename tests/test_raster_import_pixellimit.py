# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2023-2024 mundialis GmbH & Co. KG
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
Tests: Import raster with pixellimit check
"""
import unittest
from flask.json import dumps as json_dumps

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
__author__ = "Lina Krisztian, Anika Weinmann"
__copyright__ = "Copyright 2023 - 2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"


class ImportRasterLayerPixellimitTestCase(ActiniaResourceTestCaseBase):
    project = "nc_spm_08"
    tmp_mapset = "mapset_rasterimport_pixellimit"
    endpoint = f"{project}/mapsets/{tmp_mapset}/processing_async"
    rimport_inp = "elevation"
    # import resolution with which the process should fail:
    rimport_res_fail = 0.1

    def setUp(self):
        # create new temp mapset
        super(ImportRasterLayerPixellimitTestCase, self).setUp()
        self.create_new_mapset(self.tmp_mapset, project_name=self.project)

    def tearDown(self):
        # delete mapset
        self.delete_mapset(self.tmp_mapset, project_name=self.project)
        super(ImportRasterLayerPixellimitTestCase, self).tearDown()

    def test_pixellimit_allowed(self):
        """
        Test import of raster, for which pixellimit is not reached
        and therefore allowed
        """
        raster_url = additional_external_data[self.rimport_inp]
        raster = self.rimport_inp
        process_chain = {
            "version": 1,
            "list": [
                {
                    "id": "1",
                    "module": "r.import",
                    "inputs": [
                        {
                            "param": "input",
                            "value": raster_url,
                        },
                        {
                            "param": "output",
                            "value": raster,
                        },
                    ],
                },
            ],
        }
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain),
            content_type="application/json",
        )
        # Import should succeed
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    def test_pixellimit_not_allowed(self):
        """
        Test import of raster, for which pixellimit is reached
        and therefore not allowed
        """
        raster_url = additional_external_data[self.rimport_inp]
        raster = self.rimport_inp
        process_chain = {
            "version": 1,
            "list": [
                {
                    "id": "1",
                    "module": "r.import",
                    "inputs": [
                        {
                            "param": "input",
                            "value": raster_url,
                        },
                        {
                            "param": "output",
                            "value": raster,
                        },
                        {
                            "param": "resolution",
                            "value": "value",
                        },
                        {
                            "param": "resolution_value",
                            "value": f"{self.rimport_res_fail}",
                        },
                    ],
                },
            ],
        }
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain),
            content_type="application/json",
        )
        # Import should fail with certain message (due too high resolution)
        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
        )
        self.assertTrue(
            "Processing pixel limit exceeded for raster import"
            in resp["exception"]["message"]
        )

    def test_pixellimit_importer(self):
        """
        Test import of raster with the importer
        with pixellimit not reached and therefore allowed
        """
        raster_url = additional_external_data[self.rimport_inp]
        raster = self.rimport_inp
        process_chain = {
            "version": 1,
            "list": [
                {
                    "id": "1",
                    "module": "importer",
                    "inputs": [
                        {
                            "import_descr": {
                                "source": raster_url,
                                "type": "raster",
                            },
                            "param": "map",
                            "value": raster,
                        },
                    ],
                },
            ],
        }
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain),
            content_type="application/json",
        )
        # Import should succeed
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )


if __name__ == "__main__":
    unittest.main()
