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
Tests: Actinia user test case
"""
from flask.json import loads as json_load
from werkzeug.datastructures import Headers
import unittest
import base64
try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ActiniaUserTestCase(ActiniaResourceTestCaseBase):
    """
    Test the REST User credentials, creation, deletion API

    User can only be received, created and deleted
    as user with an admin role.
    """

    def test_list_users(self):
        """
        List all users in the database
        :return:
        """
        rv = self.server.get(URL_PREFIX + '/users', headers=self.admin_auth_header)
        print ("GET /users", rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        users = ""
        if "guest" in json_load(rv.data)["User list"]:
            users = "guest"

        self.assertEqual(users, "guest", "Wrong user listed")

    def test_create_get_delete_user(self):
        """
        Create a new user, access it as admin and as normal user and delete it
        :return:
        """

        # Create a new user
        new_user_id = "thomas"
        new_group = "test"
        new_password = "12345"

        rv = self.server.post(URL_PREFIX + '/users/%s?password=%s&group=%s' % (new_user_id, new_password, new_group),
                              headers=self.admin_auth_header)
        print("POST /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 201, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        # Try to create the user again which should fail
        rv = self.server.post(URL_PREFIX + '/users/%s?password=%s&group=%s' % (new_user_id, new_password, new_group),
                              headers=self.admin_auth_header)
        print("POST /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        # Get the new user entry
        rv = self.server.get(URL_PREFIX + '/users/thomas', headers=self.admin_auth_header)
        #print("GET /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        self.assertEquals(json_load(rv.data)["User id"], new_user_id)
        self.assertEquals(json_load(rv.data)["User role"], "user")

        # Get the admin user entry
        rv = self.server.get(URL_PREFIX + '/users/admin', headers=self.admin_auth_header)
        #print("GET /users/admin", rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

        self.assertEquals(json_load(rv.data)["User id"], "admin")
        self.assertEquals(json_load(rv.data)["User role"], "admin")

        # Delete the user as admin
        rv = self.server.delete(URL_PREFIX + '/users/%s' % new_user_id, headers=self.admin_auth_header)
        print("DELETE /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)

    def test_create_get_delete_user_unprivileged(self):
        """
        Create, get and delete as normal user
        :return:
        """

        # Create a new user
        new_user_id = "thomas"
        new_group = "test"
        new_password = "12345"

        # Now try to create a new user with the thomas account which should fail!
        new_auth_header = Headers()
        auth = bytes('%s:%s' % (new_user_id, new_password), "utf-8")
        new_auth_header.add('Authorization', 'Basic ' + base64.b64encode(auth).decode())

        rv = self.server.post(URL_PREFIX + '/users/%s?password=%s&group=%s' % (new_user_id, new_password, new_group),
                              headers=new_auth_header)
        print("POST /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i" %rv.status_code)

        # Try to get the user credentials as non-admin which should fail!
        rv = self.server.get(URL_PREFIX + '/users/%s' % new_user_id,
                             headers=new_auth_header)
        print("GET /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i" %rv.status_code)

        # Try to delete the new user as non-admin which should fail!
        rv = self.server.delete(URL_PREFIX + '/users/%s' % new_user_id,
                                headers=new_auth_header)
        print("DELETE /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i" %rv.status_code)

    def test_token_generation_admin(self):

        rv = self.server.get(URL_PREFIX + '/token', headers=self.admin_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

    def test_api_key_generation_admin(self):

        rv = self.server.get(URL_PREFIX + '/api_key', headers=self.admin_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

    def test_token_generation_user(self):

        rv = self.server.get(URL_PREFIX + '/token', headers=self.user_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

    def test_token_generation_user_expire(self):

        rv = self.server.get(URL_PREFIX + '/token?expiration_time=3600', headers=self.user_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

    def test_token_generation_guest(self):

        rv = self.server.get(URL_PREFIX + '/token', headers=self.guest_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

    def test_token_generation_wrong_no_auth(self):

        rv = self.server.get(URL_PREFIX + '/token')
        print (rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "text/html", "Wrong mimetype %s" %rv.mimetype)

    def test_api_key_generation_wrong_user(self):

        rv = self.server.get(URL_PREFIX + '/api_key', headers=self.user_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

    def test_token_generation_user_expire_error(self):

        rv = self.server.get(URL_PREFIX + '/token?expiration_time=1000000000', headers=self.user_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)

    def test_token_generation_user_expire_wrong(self):

        rv = self.server.get(URL_PREFIX + '/token?expiration_time=blablub', headers=self.user_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i" %rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" %rv.mimetype)


if __name__ == '__main__':
    unittest.main()
