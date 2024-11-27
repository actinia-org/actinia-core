# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2023-2024 Sören Gebbert and mundialis GmbH & Co. KG
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
Tests: No authentication test case
"""
import os
from flask.json import dumps as json_dumps
from flask.json import loads as json_loads
import pytest
import unittest
from actinia_core.core.common.app import flask_app
from actinia_core.core.common.config import global_config
from actinia_core.core.common import redis_interface
from actinia_core.core.common.process_queue import create_process_queue
from actinia_core.testsuite import ActiniaRequests

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except Exception:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2023-2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


PC = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [{"param": "raster", "value": "elevation@PERMANENT"}],
            "flags": "p",
        },
        {
            "id": "2",
            "module": "r.colors.out_sld",
            "inputs": [
                {"param": "map", "value": "elevation@PERMANENT"},
                {"param": "style_name", "value": "elevation"},
            ],
            "stdout": {"id": "sld", "format": "list", "delimiter": "\n"},
        },
        {
            "id": "3",
            "module": "r.mapcalc",
            "inputs": [{"param": "expression", "value": "baum = 5"}],
        },
        {
            "id": "4",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "elevation@PERMANENT"}],
            "flags": "g",
            "stdout": {"id": "r_info_map1", "format": "kv", "delimiter": "="},
        },
        {
            "id": "5",
            "module": "g.list",
            "inputs": [{"param": "type", "value": "raster"}],
        },
        {
            "id": "6",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "baum"}],
            "flags": "g",
            "stdout": {"id": "r_info_map2", "format": "kv", "delimiter": "="},
        },
    ],
}


class ActiniaWithoutAuthentication(ActiniaResourceTestCaseBase):
    """Test base class to test actinia without autentication"""

    server_test = False

    if "ACTINIA_SERVER_TEST" in os.environ:
        server_test = bool(os.environ["ACTINIA_SERVER_TEST"])

    @classmethod
    def setUpClass(cls):
        # Start the redis interface
        redis_args = (
            global_config.REDIS_SERVER_URL,
            global_config.REDIS_SERVER_PORT,
        )
        if (
            global_config.REDIS_SERVER_PW
            and global_config.REDIS_SERVER_PW is not None
        ):
            redis_args = (*redis_args, global_config.REDIS_SERVER_PW)

        redis_interface.connect(*redis_args)

        # Process queue
        create_process_queue(config=global_config)

    @classmethod
    def tearDownClass(cls):
        if cls.server_test is False:
            redis_interface.disconnect()

    def setUp(self):
        # We need to set the application context
        self.app_context = flask_app.app_context()
        self.app_context.push()

        # Check if the local or server site tests should be performed
        if self.server_test is False:
            flask_app.config["TESTING"] = True

            self.server = flask_app.test_client()
        else:
            self.server = ActiniaRequests()

    def tearDown(self):
        self.app_context.pop()

    def waitAsyncStatusAssertHTTP(
        self,
        response,
        http_status=200,
        status="finished",
        message_check=None,
    ):
        """Poll the status of a resource and assert its finished HTTP status

        The response will be checked if the resource was accepted. Hence it
        must always be HTTP 200 status.

        The status URL from the response is then polled until status: finished,
        error or terminated.
        The result of the poll can be checked against its HTTP status and its
        actinia status message.

        Args:
            response: The accept response
            http_status (int): The HTTP status that should be checked
            status (str): The return status of the response
            message_check (str): A string that must be in the message field

        Returns: response

        """
        resp_data = super().waitAsyncStatusAssertHTTP(
            response, None, http_status, status, message_check
        )
        return resp_data


@pytest.mark.noauth
class TestActiniaWithoutAuthentication(ActiniaWithoutAuthentication):
    def test_01_version(self):
        """Test version endpoint"""
        rv = self.server.get(f"{URL_PREFIX}/version")
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        data = json_loads(rv.data)
        self.assertIn("api_version", data)
        self.assertIn("version", data)
        self.assertIn("grass_version", data)

    def test_02_list_projects(self):
        """Test list project endpoint"""
        rv = self.server.get(f"{URL_PREFIX}/{self.project_url_part}")
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )
        self.assertIn(
            self.project_url_part,
            json_loads(rv.data),
            f"No {self.project_url_part} in response",
        )
        projects = json_loads(rv.data)[self.project_url_part]
        self.assertIn("nc_spm_08", projects, "Wrong project listed")

    def test_03_processing_ephemeral(self):
        """Test job resumption with processing_async endpoint and stdout"""
        endpoint = f"{self.project_url_part}/nc_spm_08/processing_async"
        rv = self.server.post(
            f"{URL_PREFIX}/{endpoint}",
            data=json_dumps(PC),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            http_status=200,
            status="finished",
        )
        self.compare_stdout(resp)

    def test_04_processing_persistent(self):
        """Test job resumption with persistent processing_async endpoint and
        stdout
        """
        endpoint = (
            f"{self.project_url_part}/nc_spm_08/mapsets/test/processing_async"
        )
        rv = self.server.post(
            f"{URL_PREFIX}/{endpoint}",
            data=json_dumps(PC),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv,
            http_status=200,
            status="finished",
        )
        self.compare_stdout(resp)
        # check processing mapset
        rv2 = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets"
        )
        self.assertEqual(
            rv2.status_code,
            200,
            f"HTML status code is wrong {rv2.status_code}",
        )
        data = json_loads(rv2.data)
        self.assertIn(
            "test", data["process_results"], "Mapset 'test' does not exists"
        )
        # check created raster
        rv3 = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/test/"
            "raster_layers"
        )
        self.assertEqual(
            rv3.status_code,
            200,
            f"HTML status code is wrong {rv3.status_code}",
        )
        data = json_loads(rv3.data)
        self.assertIn(
            "baum", data["process_results"], "Raster 'baum' does not exists"
        )
        # delete test mapset
        self.admin_auth_header = None
        self.delete_mapset("test", "nc_spm_08")
        rv4 = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets"
        )
        self.assertEqual(
            rv4.status_code,
            200,
            f"HTML status code is wrong {rv4.status_code}",
        )
        data = json_loads(rv4.data)
        self.assertNotIn(
            "test", data["process_results"], "Mapset 'test' exists"
        )

    def compare_stdout(self, resp):
        proc_results = resp["process_results"]
        self.assertIn(
            "sld", proc_results, "'sld' not saved in process results"
        )
        self.assertIn(
            "r_info_map1",
            proc_results,
            "'r_info_map1' not saved in process results",
        )
        self.assertIn(
            "r_info_map2",
            proc_results,
            "'r_info_map2' not saved in process results",
        )
        self.assertIsInstance(
            proc_results["sld"], list, "'sld' result is not of type list"
        )
        self.assertIsInstance(
            proc_results["r_info_map1"],
            dict,
            "'r_info_map1' result is not of type dict",
        )
        self.assertIsInstance(
            proc_results["r_info_map2"],
            dict,
            "'r_info_map2' result is not of type dict",
        )
        r_info_map1 = {
            "cells": "2025000",
            "cols": "1500",
            "datatype": "FCELL",
            "east": "645000",
            "ewres": "10",
            "ncats": "255",
            "north": "228500",
            "nsres": "10",
            "rows": "1350",
            "south": "215000",
            "west": "630000",
        }
        self.assertEqual(
            proc_results["r_info_map1"],
            r_info_map1,
            "'r_info_map1' is not equal to the region",
        )
        r_info_map2 = {
            "cells": "2025000",
            "cols": "1500",
            "datatype": "CELL",
            "east": "645000",
            "ewres": "10",
            "ncats": "0",
            "north": "228500",
            "nsres": "10",
            "rows": "1350",
            "south": "215000",
            "west": "630000",
        }
        self.assertEqual(
            proc_results["r_info_map2"],
            r_info_map2,
            "'r_info_map2' is not equal to the region",
        )


if __name__ == "__main__":
    unittest.main()
