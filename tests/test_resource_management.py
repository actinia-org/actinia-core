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
Tests: User requests test case
"""
from pprint import pprint
from flask.json import dumps as json_dumps
from werkzeug.datastructures import Headers
from flask.json import loads as json_loads
import unittest
import time
import base64
from random import randint

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
from actinia_core.core.common.user import ActiniaUser

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class UserRequestsTestCase(ActiniaResourceTestCaseBase):
    def test_user_status_requests_1(self):
        """Resource list with 3 finished resources"""

        # Create a random test user id that are used for login as admin
        user_id = "heinz" + str(randint(0, 10000000))
        user_group = self.user_group
        password = "1234"

        # We need to create an HTML basic authorization header
        auth_header = Headers()
        auth = bytes("%s:%s" % (user_id, password), "utf-8")
        auth_header.add(
            "Authorization", "Basic " + base64.b64encode(auth).decode()
        )

        # Make sure the user database is empty
        user = ActiniaUser(user_id)
        if user.exists():
            user.delete()
        # Create a user in the database and reduce its credentials
        self.user = ActiniaUser.create_user(
            user_id,
            user_group,
            password,
            user_role="user",
            accessible_datasets={
                "nc_spm_08": [
                    "PERMANENT",
                    "user1",
                    "landsat",
                    "modis_lst",
                    "test_mapset",
                ],
                "ECAD": ["PERMANENT"],
            },
            process_num_limit=3,
            process_time_limit=2,
        )

        # Create three successfully run resources
        rv = self.server.post(
            URL_PREFIX + "/custom_process/uname",
            headers=auth_header,
            data=json_dumps(["-a"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        rv = self.server.post(
            URL_PREFIX + "/custom_process/uname",
            headers=auth_header,
            data=json_dumps(["-a"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        rv = self.server.post(
            URL_PREFIX + "/custom_process/uname",
            headers=auth_header,
            data=json_dumps(["-a"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id, headers=auth_header
        )
        # print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        resource_list = json_loads(rv.data)["resource_list"]

        pprint(resource_list)

        self.assertTrue(len(resource_list) == 3)

        # Count return stats
        finished = 0
        for resource in resource_list:
            finished += int(resource["status"] == "finished")
            # print(resource["status"])

        self.assertTrue(finished == 3)

        # Check the different resource list parameters
        rv = self.server.get(
            URL_PREFIX + "/resources/%s?num=1" % user_id, headers=auth_header
        )
        self.assertTrue(len(json_loads(rv.data)["resource_list"]) == 1)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s?num=2" % user_id, headers=auth_header
        )
        self.assertTrue(len(json_loads(rv.data)["resource_list"]) == 2)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s?num=2&type=finished" % user_id,
            headers=auth_header,
        )
        self.assertTrue(len(json_loads(rv.data)["resource_list"]) == 2)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s?num=2&type=all" % user_id,
            headers=auth_header,
        )
        self.assertTrue(len(json_loads(rv.data)["resource_list"]) == 2)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s?type=all" % user_id,
            headers=auth_header,
        )
        self.assertTrue(len(json_loads(rv.data)["resource_list"]) == 3)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s?type=finished" % user_id,
            headers=auth_header,
        )
        self.assertTrue(len(json_loads(rv.data)["resource_list"]) == 3)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s?type=terminated" % user_id,
            headers=auth_header,
        )
        self.assertTrue(len(json_loads(rv.data)["resource_list"]) == 0)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s?type=unknown" % user_id,
            headers=auth_header,
        )
        self.assertTrue(len(json_loads(rv.data)["resource_list"]) == 0)

        # Check permission access using the default users

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.guest_auth_header,
        )
        # print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.user_auth_header,
        )
        # print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.admin_auth_header,
        )
        # print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.root_auth_header,
        )
        # print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

    def test_user_status_requests_2(self):
        """Resource list with 2 finished, 1 terminated and 2 error resources"""

        # Create a random test user id that are used for login as admin
        user_id = "heinz" + str(randint(0, 10000000))
        user_group = self.user_group
        password = "1234"

        # We need to create an HTML basic authorization header
        auth_header = Headers()
        auth = bytes("%s:%s" % (user_id, password), "utf-8")
        auth_header.add(
            "Authorization", "Basic " + base64.b64encode(auth).decode()
        )

        # Make sure the user database is empty
        user = ActiniaUser(user_id)
        if user.exists():
            user.delete()
        # Create a user in the database and reduce its credentials
        self.user = ActiniaUser.create_user(
            user_id,
            user_group,
            password,
            user_role="admin",
            accessible_datasets={
                "nc_spm_08": ["PERMANENT", "user1", "landsat", "test_mapset"],
                "ECAD": ["PERMANENT"],
            },
            process_num_limit=3,
            process_time_limit=5,
        )

        rv = self.server.post(
            URL_PREFIX + "/custom_process/uname",
            headers=auth_header,
            data=json_dumps(["-a"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=auth_header)

        rv = self.server.post(
            URL_PREFIX + "/custom_process/uname",
            headers=auth_header,
            data=json_dumps(["-a"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(rv, headers=auth_header)

        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=auth_header,
            data=json_dumps(["10"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv, headers=auth_header, http_status=400, status="terminated"
        )

        rv = self.server.post(
            URL_PREFIX + "/custom_process/uname_Fail",
            headers=auth_header,
            data=json_dumps(["-a"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv, headers=auth_header, http_status=400, status="error"
        )

        rv = self.server.post(
            URL_PREFIX + "/custom_process/uname_Fail",
            headers=auth_header,
            data=json_dumps(["-a"]),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv, headers=auth_header, http_status=400, status="error"
        )

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id, headers=auth_header
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        resource_list = json_loads(rv.data)["resource_list"]
        self.assertTrue(len(resource_list) == 5)

        # Count return stats
        error = 0
        finished = 0
        terminated = 0
        for resource in resource_list:
            print(resource["status"])
            finished += int(resource["status"] == "finished")
            error += int(resource["status"] == "error")
            terminated += int(resource["status"] == "terminated")

        self.assertTrue(finished == 2)
        self.assertTrue(terminated == 1)
        self.assertTrue(error == 2)

        # Check permission access using the default users

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.guest_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.user_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.admin_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.root_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_user_status_requests_3(self):
        """Empty resource list test"""

        # Create a random test user id that are used for login as admin
        user_id = "heinz" + str(randint(0, 10000000))
        user_group = "test"
        password = "1234"

        # We need to create an HTML basic authorization header
        auth_header = Headers()
        auth = bytes("%s:%s" % (user_id, password), "utf-8")
        auth_header.add(
            "Authorization", "Basic " + base64.b64encode(auth).decode()
        )

        # Make sure the user database is empty
        user = ActiniaUser(user_id)
        if user.exists():
            user.delete()
        # Create a user in the database and reduce its credentials
        self.user = ActiniaUser.create_user(user_id, user_group, password)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id, headers=auth_header
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        resource_list = json_loads(rv.data)["resource_list"]
        self.assertTrue(len(resource_list) == 0)

        # Check permission access using the default users

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.guest_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.user_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.admin_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.root_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_time_termination(self):
        """Test the time dependent termination of three running resources"""

        # Create a random test user id that are used for login as admin
        user_id = "heinz" + str(randint(0, 10000000))
        user_group = "test"
        password = "1234"

        # We need to create an HTML basic authorization header
        auth_header = Headers()
        auth = bytes("%s:%s" % (user_id, password), "utf-8")
        auth_header.add(
            "Authorization", "Basic " + base64.b64encode(auth).decode()
        )

        # Make sure the user database is empty
        user = ActiniaUser(user_id)
        if user.exists():
            user.delete()
        # Create a user in the database and reduce its credentials
        self.user = ActiniaUser.create_user(
            user_id,
            user_group,
            password,
            user_role="user",
            accessible_datasets={
                "nc_spm_08": ["PERMANENT", "user1", "landsat", "test_mapset"],
                "ECAD": ["PERMANENT"],
            },
            process_num_limit=3,
            process_time_limit=2,
        )

        # Start three processes that exceeds the time limit
        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=auth_header,
            data=json_dumps(["20"]),
            content_type="application/json",
        )

        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=auth_header,
            data=json_dumps(["20"]),
            content_type="application/json",
        )

        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=auth_header,
            data=json_dumps(["20"]),
            content_type="application/json",
        )

        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id, headers=auth_header
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Wait for termination
        time.sleep(5)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id, headers=auth_header
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        resource_list = json_loads(rv.data)["resource_list"]
        self.assertTrue(len(resource_list) == 3)

        # Count return stats
        terminated = 0
        for resource in resource_list:
            terminated += int(resource["status"] == "terminated")
            print(resource["status"])

        self.assertTrue(terminated == 3)

    def test_user_termination(self):
        """Test the termination of three running resources"""

        # Create a random test user id that are used for login as admin
        user_id = "heinz" + str(randint(0, 10000000))
        user_group = "test"
        password = "1234"

        # We need to create an HTML basic authorization header
        auth_header = Headers()
        auth = bytes("%s:%s" % (user_id, password), "utf-8")
        auth_header.add(
            "Authorization", "Basic " + base64.b64encode(auth).decode()
        )

        # Make sure the user database is empty
        user = ActiniaUser(user_id)
        if user.exists():
            user.delete()
        # Create a user in the database and reduce its credentials
        self.user = ActiniaUser.create_user(
            user_id,
            user_group,
            password,
            user_role="user",
            accessible_datasets={
                "nc_spm_08": ["PERMANENT", "user1", "landsat", "test_mapset"],
                "ECAD": ["PERMANENT"],
            },
            process_num_limit=3,
            process_time_limit=100,
        )

        # Start three processes that will be terminated
        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=auth_header,
            data=json_dumps(["20"]),
            content_type="application/json",
        )

        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=auth_header,
            data=json_dumps(["20"]),
            content_type="application/json",
        )

        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=auth_header,
            data=json_dumps(["20"]),
            content_type="application/json",
        )

        # Test guest termination error
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.guest_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        # Test user termination error
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.user_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        # Test admin termination error
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.admin_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        # Delete the resources
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id, headers=auth_header
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Wait for termination
        time.sleep(5)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id, headers=auth_header
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        resource_list = json_loads(rv.data)["resource_list"]
        self.assertTrue(len(resource_list) == 3)

        # Count return stats
        terminated = 0
        for resource in resource_list:
            terminated += int(resource["status"] == "terminated")
            print(resource["status"])

        self.assertTrue(terminated == 3)

    def test_admin_termination(self):
        """Test the termination of one running resources from admin user"""

        # Create a random test user id that are used for login as admin
        user_id = "horst" + str(randint(0, 10000000))
        user_group = self.user_group
        password = "1234"

        # We need to create an HTML basic authorization header
        auth_header = Headers()
        auth = bytes("%s:%s" % (user_id, password), "utf-8")
        auth_header.add(
            "Authorization", "Basic " + base64.b64encode(auth).decode()
        )

        # Make sure the user database is empty
        user = ActiniaUser(user_id)
        if user.exists():
            user.delete()
        # Create a user in the database and reduce its credentials
        self.user = ActiniaUser.create_user(
            user_id,
            user_group,
            password,
            user_role="admin",
            accessible_datasets={
                "nc_spm_08": ["PERMANENT", "user1", "landsat", "test_mapset"],
                "ECAD": ["PERMANENT"],
            },
            process_num_limit=3,
            process_time_limit=100,
        )

        # Start three processes that will be terminated
        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=auth_header,
            data=json_dumps(["20"]),
            content_type="application/json",
        )

        # Test guest termination error
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.guest_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        # Test user termination error
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.user_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        # Test admin termination success
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.admin_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Test superadmin termination success
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.root_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Wait for termination
        time.sleep(5)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id, headers=auth_header
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        resource_list = json_loads(rv.data)["resource_list"]
        self.assertTrue(len(resource_list) == 1)

        # Count return stats
        terminated = 0
        for resource in resource_list:
            terminated += int(resource["status"] == "terminated")
            print(resource["status"])

        self.assertTrue(terminated == 1)

    def test_superadmin_termination(self):
        """
        Test the termination of one running resources from superadmin user
        """

        # Create a random test user id that are used for login as admin
        user_id = "horst" + str(randint(0, 10000000))
        user_group = self.user_group
        password = "1234"

        # We need to create an HTML basic authorization header
        auth_header = Headers()
        auth = bytes("%s:%s" % (user_id, password), "utf-8")
        auth_header.add(
            "Authorization", "Basic " + base64.b64encode(auth).decode()
        )

        # Make sure the user database is empty
        user = ActiniaUser(user_id)
        if user.exists():
            user.delete()
        # Create a user in the database and reduce its credentials
        self.user = ActiniaUser.create_user(
            user_id,
            user_group,
            password,
            user_role="superadmin",
            accessible_datasets={
                "nc_spm_08": ["PERMANENT", "user1", "landsat", "test_mapset"],
                "ECAD": ["PERMANENT"],
            },
            process_num_limit=3,
            process_time_limit=100,
        )

        # Start three processes that will be terminated
        rv = self.server.post(
            URL_PREFIX + "/custom_process/sleep",
            headers=auth_header,
            data=json_dumps(["20"]),
            content_type="application/json",
        )

        # Test guest termination error
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.guest_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        # Test user termination error
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.user_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        # Test admin termination error
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.admin_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        # self.assertEqual(
        #     rv.mimetype,
        #     "application/json",
        #     "Wrong mimetype %s" % rv.mimetype
        # )

        # Test superadmin termination success
        rv = self.server.delete(
            URL_PREFIX + "/resources/%s" % user_id,
            headers=self.root_auth_header,
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Wait for termination
        time.sleep(5)

        rv = self.server.get(
            URL_PREFIX + "/resources/%s" % user_id, headers=auth_header
        )
        print(rv.data.decode())
        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        resource_list = json_loads(rv.data)["resource_list"]
        self.assertTrue(len(resource_list) == 1)

        # Count return stats
        terminated = 0
        for resource in resource_list:
            terminated += int(resource["status"] == "terminated")
            print(resource["status"])

        self.assertTrue(terminated == 1)


if __name__ == "__main__":
    unittest.main()
