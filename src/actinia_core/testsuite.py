# -*- coding: utf-8 -*-
import base64
import os
import requests
import time
import unittest
from flask.json import loads as json_loads
from werkzeug.datastructures import Headers
from actinia_core import main as main
from actinia_core.resources.common import redis_interface
from actinia_core.resources.common.config import global_config
from actinia_core.resources.common.user import ActiniaUser

__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ActiniaRequests(object):
    """Requests to a actinia server are performed with this class

    The requests.Response object will be extended to imitate a flask Response object
    by adding data and mimetype.
    """
    # The default server is the localhost
    graas_server = "http://127.0.0.1:5000"
    # Check for an environmental variable to set the hostname http://IP:PORT
    if "GRAAS_SERVER" in os.environ:
        graas_server = str(os.environ["GRAAS_SERVER"])

    def _make_flask_response(self, resp):
        """Take care of the mimetype to avoid r.text to take forever to parse
        a binary file.

        Args:
            resp: The requests.Response object that needs to be extended to be a flask Response object

        Returns: extended requests.Response object with mimetype and data attributes

        """
        if "content-type" in resp.headers:
            resp.mimetype = resp.headers["content-type"].split(";")[0]
        if "content-type" in resp.headers and "tif" in resp.headers["content-type"]:
            resp.data = resp.raw
        elif "content-type" in resp.headers and "png" in resp.headers["content-type"]:
            resp.data = resp.raw
        else:
            resp.data = resp.text
        return resp

    def post(self, url, **kargs):
        if "content_type" in kargs:
            del kargs["content_type"]

        if "http" not in url:
            server_url = self.graas_server + url
        else:
            server_url = url

        resp = requests.post(server_url, **kargs)
        return self._make_flask_response(resp)

    def get(self, url, **kargs):

        if "http" not in url:
            server_url = self.graas_server + url
        else:
            server_url = url

        if ".tif" in url:
            resp = requests.get(server_url, stream=True, **kargs)
        else:
            resp = requests.get(server_url, **kargs)

        return self._make_flask_response(resp)

    def delete(self, url, **kargs):
        if "content_type" in kargs:
            del kargs["content_type"]

        if "http" not in url:
            server_url = self.graas_server + url
        else:
            server_url = url

        resp = requests.delete(server_url, **kargs)
        return self._make_flask_response(resp)

    def put(self, url, **kargs):
        if "content_type" in kargs:
            del kargs["content_type"]

        if "http" not in url:
            server_url = self.graas_server + url
        else:
            server_url = url

        resp = requests.put(server_url, **kargs)
        return self._make_flask_response(resp)


class ActiniaTestCaseBase(unittest.TestCase):
    """Base class for Grass REST API tests
    """
    server_test = False
    custom_graas_cfg = False
    guest = None
    user = None
    admin = None
    root = None

    if "GRAAS_SERVER_TEST" in os.environ:
        server_test = bool(os.environ["GRAAS_SERVER_TEST"])

    if "GRAAS_CUSTOM_TEST_CFG" in os.environ:
        custom_graas_cfg = str(os.environ["GRAAS_CUSTOM_TEST_CFG"])

    @classmethod
    def setUpClass(cls):
        if cls.server_test is False and cls.custom_graas_cfg is False:
            global_config.REDIS_SERVER_SERVER = "localhost"
            global_config.REDIS_SERVER_PORT = 7000
            global_config.GRASS_RESOURCE_DIR = "/tmp"
            global_config.DOWNLOAD_CACHE = "/tmp/download_cache"
            # Start the redis interface
            redis_interface.connect(global_config.REDIS_SERVER_URL,
                                    global_config.REDIS_SERVER_PORT)

            global_config.REDIS_QUEUE_SERVER_URL = "localhost"
            global_config.REDIS_QUEUE_SERVER_PORT = 6379
            # Create the job queue
            redis_interface.create_job_queues(global_config.REDIS_QUEUE_SERVER_URL,
                                              global_config.REDIS_QUEUE_SERVER_PORT,
                                              global_config.NUMBER_OF_QUEUES)
        # If the custom_graas_cfg variable is set, then the graas config file will be read
        # to configure Redis queue
        if cls.server_test is False and cls.custom_graas_cfg is not False:
            global_config.read(cls.custom_graas_cfg)

            # Create the job queue
            redis_interface.create_job_queues(global_config.REDIS_QUEUE_SERVER_URL,
                                              global_config.REDIS_QUEUE_SERVER_PORT,
                                              global_config.NUMBER_OF_QUEUES)

            # Start the redis interface
            redis_interface.connect(global_config.REDIS_SERVER_URL,
                                    global_config.REDIS_SERVER_PORT)

        # We create 4 user for all roles: guest, user, admin, root
        accessible_datasets = {"nc_spm_08": ["PERMANENT",
                                             "user1",
                                             "landsat",
                                             "test_mapset"],
                               "ECAD": ["PERMANENT"],
                               "LL": ["PERMANENT"]}
        # Password is the same for all
        cls.password = "12345678"

        ################### GUEST USER ###################

        cls.guest_id = "guest"
        cls.user_group = "test_group"
        cls.auth = bytes('%s:%s'.format(cls.guest_id, cls.password), "utf-8")

        # We need to create an HTML basic authorization header
        cls.guest_auth_header = Headers()

        cls.guest_auth_header.add('Authorization',
                                  'Basic ' + base64.b64encode(cls.auth).decode())

        # Make sure the user database is empty
        user = ActiniaUser(cls.guest_id)
        if user.exists():
            user.delete()
        # Create a user in the database and reduce its credentials
        cls.guest = ActiniaUser.create_user(cls.guest_id,
                                            cls.user_group,
                                            cls.password,
                                            user_role="user",
                                            accessible_datasets=accessible_datasets,
                                            process_num_limit=3,
                                            process_time_limit=2)
        cls.guest.add_accessible_modules(["uname", "sleep"])
        cls.guest.update()

        ################### NORMAL USER ###################

        cls.user_id = "user"
        cls.auth = bytes('%s:%s' % (cls.user_id, cls.password), "utf-8")

        # We need to create an HTML basic authorization header
        cls.user_auth_header = Headers()
        cls.user_auth_header.add('Authorization',
                                  'Basic ' + base64.b64encode(cls.auth).decode())

        # Make sure the user database is empty
        user = ActiniaUser(cls.user_id)
        if user.exists():
            user.delete()
        # Create a user in the database and reduce its credentials
        cls.user = ActiniaUser.create_user(cls.user_id,
                                           cls.user_group,
                                           cls.password,
                                           user_role="user",
                                           accessible_datasets=accessible_datasets,
                                           process_num_limit=3,
                                           process_time_limit=2)
        cls.user.add_accessible_modules(["uname", "sleep"])
        cls.user.update()

        ################### ADMIN USER ###################

        cls.admin_id = "admin"
        cls.auth = bytes('%s:%s' % (cls.admin_id, cls.password), "utf-8")

        # We need to create an HTML basic authorization header
        cls.admin_auth_header = Headers()
        cls.admin_auth_header.add('Authorization',
                                  'Basic ' + base64.b64encode(cls.auth).decode())

        # Make sure the user database is empty
        user = ActiniaUser(cls.admin_id)
        if user.exists():
            user.delete()
        # Create a user in the database
        cls.admin = ActiniaUser.create_user(cls.admin_id,
                                            cls.user_group,
                                            cls.password,
                                            user_role="admin",
                                            accessible_datasets=accessible_datasets,
                                            process_num_limit=1000,
                                            process_time_limit=6000)

        ################### ROOT USER ###################

        cls.root_id = "superadmin"
        cls.auth = bytes('%s:%s' % (cls.root_id, cls.password), "utf-8")

        # We need to create an HTML basic authorization header
        cls.root_auth_header = Headers()
        cls.root_auth_header.add('Authorization',
                                  'Basic ' + base64.b64encode(cls.auth).decode())

        # Make sure the user database is empty
        user = ActiniaUser(cls.root_id)
        if user.exists():
            user.delete()
        # Create a user in the database
        cls.root = ActiniaUser.create_user(cls.root_id,
                                           cls.user_group,
                                           cls.password,
                                           user_role="superadmin",
                                           accessible_datasets=accessible_datasets,
                                           process_num_limit=1000,
                                           process_time_limit=6000)

    @classmethod
    def tearDownClass(cls):
        if cls.guest:
            cls.guest.delete()
        if cls.user:
            cls.user.delete()
        if cls.admin:
            cls.admin.delete()
        if cls.root:
            cls.root.delete()

        if cls.server_test is False:
            redis_interface.disconnect()

    def setUp(self):
        # We need to set the application context
        self.app_context = main.flask_app.app_context()
        self.app_context.push()

        # Check if the local or server site tests should be performed
        if self.server_test is False:
            main.flask_app.config['TESTING'] = True

            self.server = main.flask_app.test_client()
        else:
            self.server = ActiniaRequests()

    def tearDown(self):
        self.app_context.pop()

    def waitAsyncStatusAssertHTTP(self, response, headers, http_status=200, status="finished",
                                  message_check=None):
        """Poll the status of a resource and assert its finished HTTP status

        The response will be checked if the resource was accepted. Hence it must always be HTTP 200 status.

        The status URL from the response is then polled until status: finished, error or terminated.
        The result of the poll can be checked against its HTTP status and its GRaaS status message.

        Args:
            response: The accept response
            http_status (int): The HTTP status that should be checked
            status (str): The return status of the response
            message_check (str): A string that must be in the message field

        Returns: response

        """
        # Check if the resource was accepted
        print(response.data)
        self.assertEqual(response.status_code, 200, "HTML status code is wrong %i" % response.status_code)
        self.assertEqual(response.mimetype, "application/json", "Wrong mimetype %s" % response.mimetype)

        resp_data = json_loads(response.data)

        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]

        while True:
            rv = self.server.get("/status/%s/%s" % (rv_user_id, rv_resource_id),
                                 headers=headers)
            print(rv.data)
            resp_data = json_loads(rv.data)
            if resp_data["status"] == "finished" or resp_data["status"] == "error" or resp_data[
                "status"] == "terminated":
                break
            time.sleep(0.2)

        self.assertEquals(resp_data["status"], status)
        self.assertEqual(rv.status_code, http_status, "HTML status code is wrong %i" % rv.status_code)

        if message_check is not None:
            self.assertTrue(message_check in resp_data["message"])

        time.sleep(0.4)
        return resp_data
