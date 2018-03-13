# -*- coding: utf-8 -*-
from flask.json import loads as json_load
from werkzeug.datastructures import Headers
import unittest
import base64
from test_resource_base import ActiniaResourceTestCaseBase

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class GActiniaUserTestCase(ActiniaResourceTestCaseBase):
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
        rv = self.server.get('/users', headers=self.admin_auth_header)
        print ("GET /users", rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

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

        rv = self.server.post('/users/%s?password=%s&group=%s' % (new_user_id, new_password, new_group),
                              headers=self.admin_auth_header)
        print("POST /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 201, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Try to create the user again which should fail
        rv = self.server.post('/users/%s?password=%s&group=%s' % (new_user_id, new_password, new_group),
                              headers=self.admin_auth_header)
        print("POST /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        # Get the new user entry
        rv = self.server.get('/users/thomas', headers=self.admin_auth_header)
        #print("GET /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        self.assertEquals(json_load(rv.data)["User id"], new_user_id)
        self.assertEquals(json_load(rv.data)["User role"], "user")

        # Get the admin user entry
        rv = self.server.get('/users/admin', headers=self.admin_auth_header)
        #print("GET /users/admin", rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

        self.assertEquals(json_load(rv.data)["User id"], self.admin_id)
        self.assertEquals(json_load(rv.data)["User role"], "admin")

        # Delete the user as admin
        rv = self.server.delete('/users/%s' % new_user_id, headers=self.admin_auth_header)
        print("DELETE /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)

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
        new_auth_header.add('Authorization',
                            'Basic ' + base64.b64encode('%s:%s'%(new_user_id,
                                                                 new_password)))

        rv = self.server.post('/users/%s?password=%s&group=%s' % (new_user_id, new_password, new_group),
                              headers=new_auth_header)
        print("POST /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i"%rv.status_code)

        # Try to get the user credentials as non-admin which should fail!
        rv = self.server.get('/users/%s' % new_user_id,
                             headers=new_auth_header)
        print("GET /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i"%rv.status_code)

        # Try to delete the new user as non-admin which should fail!
        rv = self.server.delete('/users/%s' % new_user_id,
                                headers=new_auth_header)
        print("DELETE /users/thomas", rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i"%rv.status_code)

    def test_token_generation_admin(self):

        rv = self.server.get('/token', headers=self.admin_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_api_key_generation_admin(self):

        rv = self.server.get('/api_key', headers=self.admin_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_token_generation_user(self):

        rv = self.server.get('/token', headers=self.user_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_token_generation_user_expire(self):

        rv = self.server.get('/token?expiration_time=3600', headers=self.user_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_token_generation_guest(self):

        rv = self.server.get('/token', headers=self.guest_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_token_generation_wrong_no_auth(self):

        rv = self.server.get('/token')
        print (rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "text/html", "Wrong mimetype %s"%rv.mimetype)

    def test_api_key_generation_wrong_user(self):

        rv = self.server.get('/api_key', headers=self.user_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 401, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_token_generation_user_expire_error(self):

        rv = self.server.get('/token?expiration_time=1000000000', headers=self.user_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_token_generation_user_expire_wrong(self):

        rv = self.server.get('/token?expiration_time=blablub', headers=self.user_auth_header)
        print (rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)


if __name__ == '__main__':
    unittest.main()
