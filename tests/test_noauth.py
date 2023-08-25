# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2018 Sören Gebbert and mundialis GmbH & Co. KG
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
Tests: Location test case
"""
import configparser
from flask.json import loads as json_loads, dumps as json_dumps
import os
import pytest
import requests
import unittest
from actinia_core.core.common.app import flask_app
from actinia_core.core.common.config import global_config
from actinia_core.core.common import redis_interface
from actinia_core.core.common.process_queue import create_process_queue
from actinia_core.testsuite import ActiniaRequests # ActiniaTestCaseBase, URL_PREFIX,


try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = (
    "Copyright 2023, mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis"


class ActiniaWithoutAuthentication(ActiniaResourceTestCaseBase):
    """Test bsae class to test actinia without autentication"""
    server_test = False
    cfg_file = os.environ.get(
        "ACTINIA_CUSTOM_TEST_CFG", "/etc/default/actinia"
    )
    auth_value = None
    tmp_cfg_file = "%s_tmp" % cfg_file
    auth = "False"

    if "ACTINIA_SERVER_TEST" in os.environ:
        server_test = bool(os.environ["ACTINIA_SERVER_TEST"])

    @classmethod
    def save_config(cls, src, dest, value):
        config = configparser.ConfigParser()
        config.read(src)
        if value:
            config["API"]["authentication"] = value
        else:
            del config["API"]["authentication"]
        with open(dest, "w") as configfile:
            config.write(configfile)

    @classmethod
    def setUpClass(cls):
        cls.auth_value = global_config.AUTHENTICATION
        if cls.auth_value is True:
            os.replace(cls.cfg_file, cls.tmp_cfg_file)
            cls.save_config(
                cls.tmp_cfg_file,
                cls.cfg_file,
                cls.auth,
            )

        if cls.server_test is False and cls.custom_actinia_cfg is False:
            global_config.REDIS_SERVER_SERVER = "localhost"
            global_config.REDIS_SERVER_PORT = 7000
            global_config.GRASS_RESOURCE_DIR = "/tmp"
            global_config.DOWNLOAD_CACHE = "/tmp/download_cache"
            global_config.REDIS_QUEUE_SERVER_URL = "localhost"
            global_config.REDIS_QUEUE_SERVER_PORT = 6379
            global_config.NUMBER_OF_WORKERS = 3

        # If the custom_actinia_cfg variable is set, then the actinia config
        # file will be read to configure Redis queue
        if cls.server_test is False and cls.custom_actinia_cfg is not False:
            global_config.read(cls.custom_actinia_cfg)
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
        # reset config
        if cls.auth is True:
            cls.save_config(cls.tmp_cfg_file, cls.cfg_file, "True")
            os.remove(cls.tmp_cfg_file)
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

    def test_version(self):
        rv = self.server.get(
            URL_PREFIX + "/version"
        )
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        data = json_loads(rv.data)
        self.assertIn("api_version", data)
        self.assertIn("version", data)
        self.assertIn("grass_version", data)

    def test_list_locations(self):
        rv = self.server.get(
            URL_PREFIX + "/locations"
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
        self.assertIn(
            "locations", json_loads(rv.data), "No locations in response"
        )
        locations = json_loads(rv.data)["locations"]
        self.assertIn("nc_spm_08", locations, "Wrong location listed")

#     def test_location_info(self):
#         rv = self.server.get(
#             URL_PREFIX + "/locations/nc_spm_08/info",
#             headers=self.admin_auth_header,
#         )
#         print(rv.data)
#         self.assertEqual(
#             rv.status_code,
#             200,
#             "HTML status code is wrong %i" % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
#         )
#
#         region_settings = json_loads(rv.data)["process_results"]["region"]
#         json_loads(rv.data)["process_results"]["projection"]
#
#         self.assertTrue("depths" in region_settings)
#         self.assertTrue("ewres" in region_settings)
#         self.assertTrue("cols" in region_settings)
#         self.assertTrue("rows" in region_settings)
#
#     def test_location_global_db_error(self):
#         # ERROR: Try to create a location as admin that exists in the global
#         # database
#         rv = self.server.post(
#             URL_PREFIX + "/locations/nc_spm_08",
#             data=json_dumps({"epsg": "4326"}),
#             content_type="application/json",
#             headers=self.admin_auth_header,
#         )
#         print(rv.data)
#         self.assertEqual(
#             rv.status_code,
#             400,
#             "HTML status code is wrong %i" % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
#         )
#
#     def test_location_creation_and_deletion(self):
#         # Delete a potentially existing location
#         rv = self.server.delete(
#             URL_PREFIX + "/locations/test_location",
#             headers=self.admin_auth_header,
#         )
#
#         # Create new location as admin
#         rv = self.server.post(
#             URL_PREFIX + "/locations/test_location",
#             data=json_dumps({"epsg": "4326"}),
#             content_type="application/json",
#             headers=self.admin_auth_header,
#         )
#         print(rv.data)
#         self.assertEqual(
#             rv.status_code,
#             200,
#             "HTML status code is wrong %i" % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
#         )
#
#         # ERROR: Try to create a location as admin that already exists
#         rv = self.server.post(
#             URL_PREFIX + "/locations/test_location",
#             data=json_dumps({"epsg": "4326"}),
#             content_type="application/json",
#             headers=self.admin_auth_header,
#         )
#         print(rv.data)
#         self.assertEqual(
#             rv.status_code,
#             400,
#             "HTML status code is wrong %i" % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
#         )
#
#         # Delete location
#         rv = self.server.delete(
#             URL_PREFIX + "/locations/test_location",
#             headers=self.admin_auth_header,
#         )
#         print(rv.data)
#         self.assertEqual(
#             rv.status_code,
#             200,
#             "HTML status code is wrong %i" % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
#         )
#
#         # ERROR: Delete should fail, since location does not exists
#         rv = self.server.delete(
#             URL_PREFIX + "/locations/test_location",
#             headers=self.admin_auth_header,
#         )
#         print(rv.data)
#         self.assertEqual(
#             rv.status_code,
#             400,
#             "HTML status code is wrong %i" % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
#         )
#
#     def test_location_creation_and_deletion_as_user(self):
#         # Delete a potentially existing location
#         rv = self.server.delete(
#             URL_PREFIX + "/locations/test_location",
#             headers=self.user_auth_header,
#         )
#
#         # Create new location as user
#         rv = self.server.post(
#             URL_PREFIX + "/locations/test_location",
#             data=json_dumps({"epsg": "4326"}),
#             content_type="application/json",
#             headers=self.user_auth_header,
#         )
#         self.assertEqual(
#             rv.status_code,
#             200,
#             "Location creation by user: HTML status code is wrong %i"
#             % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype,
#             "application/json",
#             "Location creation by user: Wrong mimetype %s" % rv.mimetype,
#         )
#
#         # ERROR: Try to create a location as user that already exists
#         rv = self.server.post(
#             URL_PREFIX + "/locations/test_location",
#             data=json_dumps({"epsg": "4326"}),
#             content_type="application/json",
#             headers=self.user_auth_header,
#         )
#         self.assertEqual(
#             rv.status_code,
#             400,
#             "Location recreation by user: HTML status code is wrong %i"
#             % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype,
#             "application/json",
#             "Location recreation by user: Wrong mimetype %s" % rv.mimetype,
#         )
#
#         # Delete location
#         rv = self.server.delete(
#             URL_PREFIX + "/locations/test_location",
#             headers=self.user_auth_header,
#         )
#         self.assertEqual(
#             rv.status_code,
#             200,
#             "Location deletion by user: HTML status code is wrong %i"
#             % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype,
#             "application/json",
#             "Location deletion by user: Wrong mimetype %s" % rv.mimetype,
#         )
#
#         # ERROR: Delete should fail, since location does not exists
#         rv = self.server.delete(
#             URL_PREFIX + "/locations/test_location",
#             headers=self.user_auth_header,
#         )
#         self.assertEqual(
#             rv.status_code,
#             400,
#             "Location redeletion by user: HTML status code is wrong %i"
#             % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype,
#             "application/json",
#             "Location redeletion by user: Wrong mimetype %s" % rv.mimetype,
#         )
#
#     def test_location_creation_and_deletion_as_guest(self):
#         # ERROR: Try to create a location as guest
#         rv = self.server.post(
#             URL_PREFIX + "/locations/test_location_user",
#             data=json_dumps({"epsg": "4326"}),
#             content_type="application/json",
#             headers=self.guest_auth_header,
#         )
#         print(rv.data)
#         self.assertEqual(
#             rv.status_code,
#             401,
#             "HTML status code is wrong %i" % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
#         )
#
#         # ERROR: Delete should fail since the guest user is not authorized
#         rv = self.server.delete(
#             URL_PREFIX + "/locations/test_location_user",
#             headers=self.guest_auth_header,
#         )
#         print(rv.data)
#         self.assertEqual(
#             rv.status_code,
#             401,
#             "HTML status code is wrong %i" % rv.status_code,
#         )
#         self.assertEqual(
#             rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
#         )


if __name__ == "__main__":
    unittest.main()
