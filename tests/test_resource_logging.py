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
Tests: Resource logging test case
"""
import unittest
import pickle
import uuid
from actinia_core.core.resources_logger import ResourceLogger
from actinia_core.core.common.app import flask_app

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, global_config
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, global_config

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


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
        self.document = pickle.dumps(
            [200, {"Status": "running", "URL": "/bla/bla"}]
        )

        redis_args = (
            global_config.REDIS_SERVER_URL,
            global_config.REDIS_SERVER_PORT,
        )
        if global_config.REDIS_SERVER_PW is not None:
            redis_args = (*redis_args, global_config.REDIS_SERVER_PW)
        self.log = ResourceLogger(*redis_args)
        del redis_args

    def tearDown(self):
        self.app_context.pop()

    def test_logging(self):
        ret = self.log.commit(
            user_id=self.user_id,
            resource_id=self.resource_id,
            iteration=1,
            document=self.document,
        )

        self.assertTrue(ret)

        ret = self.log.commit(
            user_id=self.user_id,
            resource_id=self.resource_id,
            iteration=1,
            document=self.document,
        )

        self.assertTrue(ret)

        doc = self.log.get(
            user_id=self.user_id, resource_id=self.resource_id, iteration=1
        )
        print(doc)
        self.assertEqual(self.document, doc)

        ret = self.log.delete(
            user_id=self.user_id, resource_id=self.resource_id, iteration=1
        )

        self.assertTrue(ret)

        doc = self.log.get(user_id=self.user_id, resource_id=self.resource_id)

        self.assertEqual(None, doc)

        ret = self.log.delete(
            user_id=self.user_id, resource_id=self.resource_id
        )

        self.assertFalse(ret)

    def test_list(self):
        user = "lisa"
        resource = "a"
        ret = self.log.commit(
            user_id=user,
            resource_id=resource,
            iteration=1,
            document=self.document,
        )
        self.assertTrue(ret)

        user = "franky"
        resource = "a"
        ret = self.log.commit(
            user_id=user,
            resource_id=resource,
            iteration=1,
            document=self.document,
        )
        self.assertTrue(ret)

        resource = "b"
        ret = self.log.commit(
            user_id=user,
            resource_id=resource,
            iteration=1,
            document=self.document,
        )
        self.assertTrue(ret)

        user = "klaus"
        resource = "a"
        ret = self.log.commit(
            user_id=user,
            resource_id=resource,
            iteration=1,
            document=self.document,
        )
        self.assertTrue(ret)

        resource = "b"
        ret = self.log.commit(
            user_id=user,
            resource_id=resource,
            iteration=1,
            document=self.document,
        )
        self.assertTrue(ret)

        resource = "c"
        ret = self.log.commit(
            user_id=user,
            resource_id=resource,
            iteration=1,
            document=self.document,
        )
        self.assertTrue(ret)

        ret = self.log.get_user_resources("lisa")
        self.assertEqual(len(ret), 1)
        print(ret)

        ret = self.log.get_user_resources("franky")
        print(ret)

        ret = self.log.get_user_resources("klaus")
        print(ret)

    def test_termination(self):
        ret = self.log.commit_termination(
            user_id=self.user_id, resource_id=self.resource_id
        )

        self.assertTrue(ret)

        ret = self.log.get_termination(
            user_id=self.user_id, resource_id=self.resource_id
        )

        self.assertEqual(True, ret)

        ret = self.log.delete_termination(
            user_id=self.user_id, resource_id=self.resource_id
        )

        self.assertTrue(ret)

        ret = self.log.get_termination(
            user_id=self.user_id, resource_id=self.resource_id
        )

        self.assertEqual(False, ret)

        ret = self.log.delete_termination(
            user_id=self.user_id, resource_id=self.resource_id
        )

        self.assertFalse(ret)


if __name__ == "__main__":
    unittest.main()
