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
Tests: Async process test case
"""
import unittest
import copy
from flask.json import loads as json_loads, dumps as json_dumps
import time

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

# Module change example for r.slope.aspect with g.region adjustment
process_chain = {
    1: {
        "module": "g.region",
        "inputs": {"raster": "elevation@PERMANENT"},
        "flags": "p",
        "verbose": True,
    },
    2: {
        "module": "r.slope.aspect",
        "inputs": {
            "elevation": "elevation@PERMANENT",
            "format": "degrees",
            "min_slope": "0.0",
        },
        "outputs": {
            "aspect": {"name": "my_aspect"},
            "slope": {
                "name": "my_slope",
                "export": {"format": "GTiff", "type": "raster"},
            },
        },
        "flags": "a",
        "overwrite": False,
        "verbose": True,
    },
    3: {
        "module": "r.watershed",
        "inputs": {"elevation": "elevation@PERMANENT"},
        "outputs": {
            "accumulation": {
                "name": "my_accumulation",
                "export": {"format": "GTiff", "type": "raster"},
            }
        },
    },
    4: {
        "module": "r.info",
        "inputs": {"map": "my_aspect"},
        "flags": "gr",
        "verbose": True,
    },
    5: {"executable": "/bin/true", "parameters": []},
    6: {"executable": "/bin/true"},
    7: {"executable": "/bin/sleep", "parameters": ["4"]},
}

# Module chains with errors
process_chain_error_1 = {
    1: {
        "module": "g.region",
        "inputs": {"raster": "elevation@PERMANENT"},
        "flags": "&p",
        "verbose": True,
    }
}

process_chain_error_2 = {
    1: {
        "module": "g.region_nopo",
        "inputs": {"raster": "elevation@PERMANENT"},
        "flags": "p",
        "verbose": True,
    }
}

process_chain_error_3 = {
    1: {
        "module": "g.region",
        "inputs": {"raster": "elevion@PANENT"},
        "flags": "p",
        "verbose": True,
    }
}

process_chain_error_4 = {
    1: {
        "module": "g.region",
        "inputs": {"faster": "elevion@PANENT"},
        "flags": "p",
        "verbose": True,
    }
}

process_chain_error_5 = {1: {}}

process_chain_error_6 = {
    2: {
        "module": "r.slope.aspect",
        "inputs": {
            "elevation": "elevation@PERMANENT",
            "format": "degrees",
            "min_slope": "0.0",
        },
        "outputs": {
            "aspect": {"name": "my_aspect"},
            "slope": {
                "name": "my_slope",
                "export": {"fromat": "GTiff", "type": "raster"},
            },
        },
        "flags": "a",
        "overwrite": False,
        "verbose": True,
    },
}

process_chain_region = {
    1: {
        "module": "g.region",
        "inputs": {"raster": "elevation@PERMANENT"},
        "flags": "p",
        "verbose": True,
    },
    2: {
        "module": "g.region",
        "inputs": {"res": "0.001"},
        "flags": "p",
        "verbose": True,
    },
    3: {
        "module": "r.info",
        "inputs": {"map": "elevation@PERMANENT"},
        "flags": "gr",
        "verbose": True,
    },
}


class AsyncProcessTestCase(ActiniaResourceTestCaseBase):
    def test_async_processing(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    def test_async_processing_termination(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain),
            content_type="application/json",
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

        resp = json_loads(rv.data)

        rv_user_id = resp["user_id"]
        rv_resource_id = resp["resource_id"]

        while True:
            rv = self.server.get(
                f"{URL_PREFIX}/resources/{rv_user_id}/{rv_resource_id}",
                headers=self.admin_auth_header,
            )
            print("Get", rv.data.decode())
            resp = json_loads(rv.data)
            if (
                resp["status"] == "finished"
                or resp["status"] == "error"
                or resp["status"] == "terminated"
            ):
                break

            time.sleep(0.2)

            # Send the termination request, again and again :)
            rv = self.server.delete(
                f"{URL_PREFIX}/resources/{rv_user_id}/{rv_resource_id}",
                headers=self.admin_auth_header,
            )
            print("Delete", rv.data.decode())

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )
        self.assertEqual(resp["status"], "terminated")

        time.sleep(1)

    def test_async_processing_large_region(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.user_auth_header,
            data=json_dumps(process_chain_region),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )

    def test_async_processing_error_1(self):
        """
        Wrong character in module description
        :return:
        """

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.user_auth_header,
            data=json_dumps(process_chain_error_1),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )

    def test_async_processing_error_2(self):
        """
        Wrong module error
        :return:
        """

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.user_auth_header,
            data=json_dumps(process_chain_error_2),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )

    def test_async_processing_error_3(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.user_auth_header,
            data=json_dumps(process_chain_error_3),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )

    def test_async_processing_error_4(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.user_auth_header,
            data=json_dumps(process_chain_error_4),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )

    def test_async_processing_error_5(self):
        """No JSON payload error"""

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.user_auth_header,
        )

        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_error_6(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.user_auth_header,
            data=json_dumps(process_chain_error_5),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )

    def test_async_processing_error_7(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.user_auth_header,
            data=json_dumps(process_chain_error_6),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )

    def test_async_processing_error_8(self):
        """Wrong mapset in input definitions as admin"""

        pc = copy.deepcopy(process_chain)
        pc[1]["inputs"]["raster"] = "elevation@NO_Mapset"
        pc[2]["inputs"]["elevation"] = "elevation@NO_Mapset"
        pc[3]["inputs"]["elevation"] = "elevation@NO_Mapset"

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.admin_auth_header,
            data=json_dumps(pc),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
            message_check="AsyncProcessError:",
        )

    def test_async_processing_error_9(self):
        """
        Wrong mapset in input definitions as user, hence authorization error
        """

        pc = copy.deepcopy(process_chain_error_1)
        pc[1]["inputs"]["raster"] = "elevation@NO_Mapset"
        pc[1]["flags"] = "p"

        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/processing_async",
            headers=self.user_auth_header,
            data=json_dumps(pc),
            content_type="application/json",
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
