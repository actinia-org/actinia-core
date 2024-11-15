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
Tests: Webhook
"""
import unittest

# import pytest
from flask.json import loads as json_loads, dumps as json_dumps
import requests
from jinja2 import Template
import os
import time

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

port = "5006"

pc = {
    "version": 1,
    "webhooks": {
        "finished": f"http://0.0.0.0:{port}/webhook/finished",
        "update": f"http://0.0.0.0:{port}/webhook/update",
    },
    "list": [
        {"id": "1", "exe": "/bin/sleep", "params": ["{{ sleep }}"]},
        {
            "id": "2",
            "module": "g.region",
            "inputs": [
                {"param": "raster", "value": "elevation@PERMANENT"},
                {"param": "res", "value": "10000"},
            ],
            "flags": "p",
            "verbose": True,
        },
    ],
}


def startWebhook(sleeptime=10):
    """
    Starts a webhook server which returns status code 200 for /webhook/update
    and /webhook/finished endpoints and can be shutdown by endpoint /shutdown.
    """
    inputlist = [
        "webhook-server",
        "--host",
        "0.0.0.0",
        "--port",
        port,
        "&",
    ]
    os.system(" ".join(inputlist))
    time.sleep(sleeptime)
    resp = requests.get(f"http://0.0.0.0:{port}/webhook/finished")
    return resp.status_code


def startBrokenWebhook(sleeptime=10):
    """
    Starts a webhook server which returns status code 200 for /webhook/update
    endpoint and by endpoint /webhook/finished it shuts down itself to test the
    etries if the webhook server can not be reached or return a server error
    code (500 - 599).
    """
    inputlist = [
        "webhook-server-broken",
        "--host",
        "0.0.0.0",
        "--port",
        port,
        "&",
    ]
    os.system(" ".join(inputlist))
    time.sleep(sleeptime)
    resp = requests.get(f"http://0.0.0.0:{port}/webhook/update")
    return resp.status_code


class WebhookTestCase(ActiniaResourceTestCaseBase):
    def setUp(self):
        # start a webhook server before the normal setUp
        status_code = startWebhook(10)
        self.assertEqual(status_code, 200, "Webhook server is not running")
        super().setUp()

    def tearDown(self):
        # shutting down the webhook server
        resp = requests.get(f"http://0.0.0.0:{port}/shutdown")
        self.assertEqual(
            resp.status_code, 200, "Webhook server is not shutting down"
        )

    def poll_job(self, resp_data):
        # poll an actinia job
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        time.sleep(10)
        rv2 = self.server.get(
            URL_PREFIX + "/resources/%s/%s" % (rv_user_id, rv_resource_id),
            headers=self.admin_auth_header,
        )
        resp_data2 = json_loads(rv2.data)
        return resp_data2

    # @pytest.mark.dev
    # def test_started_webhook(self):
    #     """Test the started webhook via a actinia process."""
    #     # time.sleep(10)
    #     # import pdb; pdb.set_trace()
    #     resp = None
    #     while resp is None or resp.status_code != 200:
    #         resp = requests.get(f"http://0.0.0.0:{port}/webhook/finished")
    #         time.sleep(3)
    #     tm = Template(json_dumps(pc))
    #     rv = self.server.post(
    #         f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
    #         "processing_async_export",
    #         headers=self.admin_auth_header,
    #         data=tm.render(sleep=1),
    #         content_type="application/json",
    #     )
    #     self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

    def test_finished_webhook_retries(self):
        """Test the retry if the webhook can not be reached or returns a server
        error.
        """
        tm = Template(json_dumps(pc))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=tm.render(sleep=30),
            content_type="application/json",
        )

        # poll job and check if it is running
        resp_data = json_loads(rv.data)
        status = resp_data["status"]
        while status == "accepted":
            resp_data2 = self.poll_job(resp_data)
            status = resp_data2["status"]
        self.assertEqual(status, "running", "Actinia job is not 'running'!")

        # shutdown webhook and start broken finished webhook
        webhook_resp = requests.get(f"http://0.0.0.0:{port}/shutdown")
        self.assertEqual(
            webhook_resp.status_code, 200, "Shutdown of webhook failed!"
        )
        time.sleep(2)
        status_code = startBrokenWebhook(10)
        self.assertEqual(
            status_code, 200, "Broken webhook server is not running"
        )

        broken_server_is_running = True
        while broken_server_is_running is True:
            try:
                resp = requests.get(f"http://0.0.0.0:{port}/webhook/update")
                if resp.status_code == 500:
                    broken_server_is_running = False
            except Exception:
                broken_server_is_running = False

        # restart webhook server
        status_code = startWebhook(10)
        self.assertEqual(status_code, 200, "Webhook server restart failed")

        # check if job is finished
        resp_data2 = self.poll_job(resp_data)
        status = resp_data2["status"]
        self.assertEqual(status, "finished", "Actinia job is not finished")


if __name__ == "__main__":
    unittest.main()
