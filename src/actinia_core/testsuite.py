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
Base class for GRASS GIS REST API tests
"""
import base64
import os
import requests
import time
import unittest
from flask.json import loads as json_loads
from flask.json import dumps as json_dumps
from werkzeug.datastructures import Headers
from actinia_api import URL_PREFIX

from .version import init_versions
from .health_check import health_check
from actinia_core.core.common.app import flask_app
from actinia_core.core.common import redis_interface
from actinia_core.core.common.config import global_config
from actinia_core.core.common.user import ActiniaUser
from actinia_core.core.common.process_queue import create_process_queue

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class ActiniaRequests(object):
    """Requests to a actinia server are performed with this class

    The requests.Response object will be extended to imitate a flask Response
    object by adding data and mimetype.
    """

    # The default server is the localhost
    actinia_server = "http://127.0.0.1:5000"
    # Check for an environmental variable to set the hostname http://IP:PORT
    if "ACTINIA_SERVER" in os.environ:
        actinia_server = str(os.environ["ACTINIA_SERVER"])

    def _make_flask_response(self, resp):
        """Take care of the mimetype to avoid r.text to take forever to parse
        a binary file.

        Args:
            resp: The requests.Response object that needs to be extended to be
                  a flask Response object

        Returns: extended requests.Response object with mimetype and data
                 attributes

        """
        if "content-type" in resp.headers:
            resp.mimetype = resp.headers["content-type"].split(";")[0]
        if (
            "content-type" in resp.headers
            and "tif" in resp.headers["content-type"]
        ):
            resp.data = resp.raw
        elif (
            "content-type" in resp.headers
            and "png" in resp.headers["content-type"]
        ):
            resp.data = resp.raw
        else:
            resp.data = resp.text
        return resp

    def _request(self, url, method, **kargs):
        if "content_type" in kargs:
            del kargs["content_type"]

        if "http" not in url:
            server_url = self.actinia_server + url
        else:
            server_url = url

        if method == "post":
            resp = requests.post(server_url, **kargs)
        elif method == "get":
            if ".tif" in url:
                resp = requests.get(server_url, stream=True, **kargs)
            else:
                resp = requests.get(server_url, **kargs)
        elif method == "delete":
            resp = requests.delete(server_url, **kargs)
        else:
            resp = requests.put(server_url, **kargs)
        return self._make_flask_response(resp)

    def post(self, url, **kargs):
        return self._request(url=url, method="post", **kargs)

    def get(self, url, **kargs):
        return self._request(url=url, method="get", **kargs)

    def delete(self, url, **kargs):
        return self._request(url=url, method="delete", **kargs)

    def put(self, url, **kargs):
        return self._request(url=url, method="put", **kargs)


class ActiniaTestCaseBase(unittest.TestCase):
    """Base class for GRASS GIS REST API tests"""

    server_test = False
    guest = None
    user = None
    admin = None
    root = None
    auth_header = {}
    users_list = []
    project_url_part = "projects"

    # set project_url_part to "locations" if GRASS GIS version < 8.4
    init_versions()
    health_check = health_check
    from .version import G_VERSION

    grass_version_s = G_VERSION["version"]
    grass_version = [int(item) for item in grass_version_s.split(".")[:2]]
    if grass_version < [8, 4]:
        project_url_part = "locations"

    if "ACTINIA_SERVER_TEST" in os.environ:
        server_test = bool(os.environ["ACTINIA_SERVER_TEST"])

    @classmethod
    def setUpClass(cls):
        # create configured folders
        os.makedirs(global_config.GRASS_USER_DATABASE, exist_ok=True)
        os.makedirs(global_config.GRASS_TMP_DATABASE, exist_ok=True)
        os.makedirs(global_config.GRASS_RESOURCE_DIR, exist_ok=True)
        os.makedirs(global_config.TMP_WORKDIR, exist_ok=True)
        os.makedirs(global_config.DOWNLOAD_CACHE, exist_ok=True)

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

        # We create 4 user for all roles: guest, user, admin, root
        accessible_datasets = {
            "nc_spm_08": [
                "PERMANENT",
                "user1",
                "landsat",
                "modis_lst",
                "test_mapset",
            ],
            "ECAD": ["PERMANENT"],
            "latlong_wgs84": ["PERMANENT"],
        }

        # Create users
        cls.guest_id, cls.guest_group, cls.guest_auth_header = cls.create_user(
            name="guest",
            role="guest",
            process_num_limit=3,
            process_time_limit=2,
            accessible_datasets=accessible_datasets,
        )
        cls.user_id, cls.user_group, cls.user_auth_header = cls.create_user(
            name="user",
            role="user",
            process_num_limit=3,
            process_time_limit=4,
            accessible_datasets=accessible_datasets,
        )
        cls.admin_id, cls.admin_group, cls.admin_auth_header = cls.create_user(
            name="admin", role="admin", accessible_datasets=accessible_datasets
        )
        cls.root_id, cls.root_group, cls.root_auth_header = cls.create_user(
            name="superadmin",
            role="superadmin",
            accessible_datasets=accessible_datasets,
        )

    @classmethod
    def create_user(
        cls,
        name="guest",
        role="guest",
        group="group",
        password="abcdefgh",
        accessible_datasets=None,
        process_num_limit=1000,
        process_time_limit=6000,
    ):
        auth = bytes("%s:%s" % (name, password), "utf-8")

        # We need to create an HTML basic authorization header
        cls.auth_header[role] = Headers()
        cls.auth_header[role].add(
            "Authorization", "Basic " + base64.b64encode(auth).decode()
        )

        # Make sure the user database is empty
        user = ActiniaUser(name)
        if user.exists():
            user.delete()
        # Create a user in the database
        user = ActiniaUser.create_user(
            name,
            group,
            password,
            user_role=role,
            accessible_datasets=accessible_datasets,
            process_num_limit=process_num_limit,
            process_time_limit=process_time_limit,
        )
        user.add_accessible_modules(["uname", "sleep"])
        cls.users_list.append(user)

        return name, group, cls.auth_header[role]

    @classmethod
    def tearDownClass(cls):
        for user in cls.users_list:
            user.delete()

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
        headers,
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
        # Check if the resource was accepted
        self.assertEqual(
            response.status_code,
            200,
            "HTML status code is wrong %i" % response.status_code,
        )
        self.assertEqual(
            response.mimetype,
            "application/json",
            "Wrong mimetype %s" % response.mimetype,
        )

        resp_data = json_loads(response.data)

        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]

        while True:
            rv = self.server.get(
                URL_PREFIX + "/resources/%s/%s" % (rv_user_id, rv_resource_id),
                headers=headers,
            )
            resp_data = json_loads(rv.data)
            if (
                resp_data["status"] == "finished"
                or resp_data["status"] == "error"
                or resp_data["status"] == "terminated"
                or resp_data["status"] == "timeout"
            ):
                break
            time.sleep(0.2)

        self.assertEqual(resp_data["status"], status)
        self.assertEqual(
            rv.status_code,
            http_status,
            "HTML status code is wrong %i" % rv.status_code,
        )

        if message_check is not None:
            self.assertTrue(
                message_check in resp_data["message"],
                (f"Message is {resp_data['message']}"),
            )

        time.sleep(0.4)
        return resp_data

    def assertRasterInfo(self, project, mapset, raster, ref_info, header):
        url = (
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/{mapset}/"
            f"raster_layers/{raster}"
        )
        rv = self.server.get(url, headers=header)
        resp = json_loads(rv.data.decode())
        info = resp["process_results"]
        for key, val in ref_info.items():
            self.assertIn(
                key, info, f"RasterInfoAssertion failed: key {key} not found"
            )
            self.assertEqual(
                val,
                info[key],
                (
                    f"RasterInfoAssertion failed:"
                    f" value {key}:{val} does not match reference"
                ),
            )

    def assertVectorInfo(self, project, mapset, vector, ref_info, header):
        url = (
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/{mapset}/"
            f"vector_layers/{vector}"
        )
        rv = self.server.get(url, headers=header)
        resp = json_loads(rv.data.decode())
        info = resp["process_results"]
        for key, val in ref_info.items():
            self.assertIn(
                key, info, f"VectorInfoAssertion failed: key {key} not found"
            )
            self.assertEqual(
                val,
                info[key],
                (
                    f"VectorInfoAssertion failed:"
                    f" value {key}:{val} does not match reference"
                ),
            )

    def create_new_mapset(self, mapset_name, project_name="nc_spm_08"):
        get_url = (
            f"{URL_PREFIX}/{self.project_url_part}/{project_name}/mapsets"
        )
        rv_get = self.server.get(get_url, headers=self.user_auth_header)
        self.assertEqual(
            rv_get.status_code,
            200,
            "HTML status code is wrong %i" % rv_get.status_code,
        )
        resp = json_loads(rv_get.data.decode())
        if mapset_name in resp["process_results"]:
            self.delete_mapset(mapset_name, project_name)

        # Create new mapset
        self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{project_name}/"
            f"mapsets/{mapset_name}",
            headers=self.admin_auth_header,
        )

    def delete_mapset(self, mapset_name, project_name="nc_spm_08"):
        # Unlock mapset for deletion
        self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/{project_name}/mapsets/"
            f"{mapset_name}/lock",
            headers=self.admin_auth_header,
        )

        # Delete existing mapset
        self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/{project_name}/"
            f"mapsets/{mapset_name}",
            headers=self.admin_auth_header,
        )

    def create_vector_layer(self, project, mapset, vector, region, parameter):
        # Remove potentially existing vector layer
        vl_url = (
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/{mapset}/"
            f"vector_layers"
        )
        url = f"{vl_url}/{vector}"
        rv_get = self.server.get(vl_url, headers=self.user_auth_header)
        self.assertEqual(
            rv_get.status_code,
            200,
            "HTML status code is wrong %i" % rv_get.status_code,
        )
        resp = json_loads(rv_get.data.decode())
        if vector in resp["process_results"]:
            rv = self.server.delete(url, headers=self.user_auth_header)

        parameter["column"] = "z"
        region["res"] = 100000
        # Create processing chain for random vector creation
        postbody = {
            "list": [
                {
                    "id": "set_region",
                    "module": "g.region",
                    "inputs": [
                        {"param": key, "value": str(val)}
                        for key, val in region.items()
                    ],
                },
                {
                    "id": "create_vector",
                    "module": "v.random",
                    "inputs": [
                        {"param": key, "value": str(val)}
                        for key, val in parameter.items()
                    ],
                    "outputs": [{"param": "output", "value": vector}],
                    "flags": "z",
                },
            ],
            "version": "1",
        }
        url = (
            f"{URL_PREFIX}/{self.project_url_part}/{project}/mapsets/{mapset}/"
            "processing_async"
        )
        rv = self.server.post(
            url,
            headers=self.user_auth_header,
            data=json_dumps(postbody),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.user_auth_header,
            http_status=200,
            status="finished",
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )
