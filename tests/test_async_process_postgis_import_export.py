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
Tests: Async processing PostGIS test case
"""
import unittest

# from flask.json import dumps as json_dumps
from random import randint

try:
    from .test_resource_base import ActiniaResourceTestCaseBase  # , URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase  # , URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

process_chain_postgis = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "PG:dbname=gis user=postgres host=localhost "
                        "port=5432 password=postgres",
                        "type": "postgis",
                        "vector_layer": "poly",
                    },
                    "param": "map",
                    "value": "poly",
                }
            ],
        },
        {
            "id": "exporter_1",
            "module": "exporter",
            "outputs": [
                {
                    "export": {
                        "dbstring": "PG:dbname=gis user=postgres "
                        "host=localhost port=5432 password=postgres",
                        "format": "PostgreSQL",
                        "type": "vector",
                        "output_layer": "poly_2",
                    },
                    "param": "map",
                    "value": "poly",
                }
            ],
        },
    ],
    "webhooks": {
        "finished": "http://0.0.0.0:5005/webhook/finished",
        "update": "http://0.0.0.0:5005/webhook/update",
    },
    "version": "1",
}


class AsyncProcessingPostGISTestCase(ActiniaResourceTestCaseBase):
    def gen_output_layer_name(self):
        process_chain_postgis["list"][1]["outputs"][0]["export"][
            "output_layer"
        ] = "poly_%i" % randint(0, 1000000000)

    # # TODO fix test and comment the test in (postgres DB is needed)
    # def test_1_async_processing_postgis_validation(self):
    #     rv = self.server.post(
    #         f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
    #         "process_chain_validation_async",
    #         headers=self.admin_auth_header,
    #         data=json_dumps(process_chain_postgis),
    #         content_type="application/json",
    #     )
    #
    #     resp = self.waitAsyncStatusAssertHTTP(
    #         rv,
    #         headers=self.admin_auth_header,
    #         http_status=200,
    #         status="finished",
    #     )
    #     self.assertEqual(len(resp["process_results"]), 1)
    #
    # # TODO fix test and comment the test in (postgres DB is needed)
    # def test_2_async_processing_postgis_run(self):
    #     # Don't overwrite an existing layer
    #     self.gen_output_layer_name()
    #
    #     rv = self.server.post(
    #         f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
    #         "processing_async_export",
    #         headers=self.admin_auth_header,
    #         data=json_dumps(process_chain_postgis),
    #         content_type="application/json",
    #     )
    #
    #     resp = self.waitAsyncStatusAssertHTTP(
    #         rv,
    #         headers=self.admin_auth_header,
    #         http_status=200,
    #         status="finished",
    #     )
    #     self.assertEqual(len(resp["process_log"]), 2)


if __name__ == "__main__":
    unittest.main()
