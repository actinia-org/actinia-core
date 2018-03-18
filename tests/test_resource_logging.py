# -*- coding: utf-8 -*-
import unittest
import pickle
import uuid
from actinia_core.resources.common.resources_logger import ResourceLogger
from actinia_core.resources.common.app import flask_app
try:
    from .test_resource_base import ActiniaResourceTestCaseBase, global_config
except:
    from test_resource_base import ActiniaResourceTestCaseBase, global_config

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class ResourceLoggingTestCase(ActiniaResourceTestCaseBase):
    """
    This class tests the resource logging interface
    """

    def setUp(self):
        # We need to set the application context
        self.app_context = flask_app.app_context()
        self.app_context.push()
        # The test user
        self.user_id = "soeren"
        self.resource_id = uuid.uuid1()
        self.document = pickle.dumps({"Status":"running", "URL":"/bla/bla"})
        self.log = ResourceLogger(global_config.REDIS_SERVER_URL,
                                  global_config.REDIS_SERVER_PORT)

    def tearDown(self):
        self.app_context.pop()

    def test_logging(self):

        ret = self.log.commit(user_id=self.user_id,
                              resource_id=self.resource_id,
                              document=self.document)

        self.assertTrue(ret)

        ret = self.log.commit(user_id=self.user_id,
                              resource_id=self.resource_id,
                              document=self.document)

        self.assertTrue(ret)

        doc = self.log.get(user_id=self.user_id,
                           resource_id=self.resource_id)
        print(doc)
        self.assertEqual(self.document, doc)

        ret = self.log.delete(user_id=self.user_id,
                              resource_id=self.resource_id)

        self.assertTrue(ret)

        doc = self.log.get(user_id=self.user_id,
                           resource_id=self.resource_id)

        self.assertEqual(None, doc)

        ret = self.log.delete(user_id=self.user_id,
                              resource_id=self.resource_id)

        self.assertFalse(ret)

    def test_list(self):

        user = "lisa"
        resource = "a"
        ret = self.log.commit(user_id=user,
                              resource_id=resource,
                              document=self.document)
        self.assertTrue(ret)

        user = "franky"
        resource = "a"
        ret = self.log.commit(user_id=user,
                              resource_id=resource,
                              document=self.document)
        self.assertTrue(ret)

        resource = "b"
        ret = self.log.commit(user_id=user,
                              resource_id=resource,
                              document=self.document)
        self.assertTrue(ret)

        user = "klaus"
        resource = "a"
        ret = self.log.commit(user_id=user,
                              resource_id=resource,
                              document=self.document)
        self.assertTrue(ret)

        resource = "b"
        ret = self.log.commit(user_id=user,
                              resource_id=resource,
                              document=self.document)
        self.assertTrue(ret)

        resource = "c"
        ret = self.log.commit(user_id=user,
                              resource_id=resource,
                              document=self.document)
        self.assertTrue(ret)

        ret = self.log.get_user_resources("lisa")
        self.assertEqual(len(ret), 1)
        print(ret)

        ret = self.log.get_user_resources("franky")
        print(ret)

        ret = self.log.get_user_resources("klaus")
        print(ret)


    def test_termination(self):

        ret = self.log.commit_termination(user_id=self.user_id,
                                          resource_id=self.resource_id)

        self.assertTrue(ret)

        ret = self.log.get_termination(user_id=self.user_id,
                                       resource_id=self.resource_id)

        self.assertEqual(True, ret)

        ret = self.log.delete_termination(user_id=self.user_id,
                                          resource_id=self.resource_id)

        self.assertTrue(ret)

        ret = self.log.get_termination(user_id=self.user_id,
                           resource_id=self.resource_id)

        self.assertEqual(False, ret)

        ret = self.log.delete_termination(user_id=self.user_id,
                                          resource_id=self.resource_id)

        self.assertFalse(ret)

if __name__ == '__main__':
    unittest.main()
