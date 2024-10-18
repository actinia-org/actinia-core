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
Tests: User test case
"""
import unittest
from actinia_core.core.common.user import ActiniaUser
from actinia_core.core.common.app import flask_app

try:
    from .test_resource_base import ActiniaResourceTestCaseBase
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class UserTestCase(ActiniaResourceTestCaseBase):
    """
    This class tests the user interface, the creation and deletion
    of a user entry in a Redis database
    """

    def setUp(self):
        # We need to set the application context
        self.app_context = flask_app.app_context()
        self.app_context.push()

        # Create a test user
        self.user_id = "soeren"
        self.password = "1234"
        self.user_group = "test"

    def tearDown(self):
        self.app_context.pop()

    def test_create_delete_user(self):
        # Make sure the user database is empty
        user = ActiniaUser(self.user_id)
        if user.exists():
            print("Delete existing user")
            user.delete()

        # Create a new user
        user = ActiniaUser.create_user(
            self.user_id,
            self.user_group,
            self.password,
            user_role="admin",
            accessible_datasets={"nc_spm_08": ["PERMANENT", "user1"]},
            accessible_modules=["g.region", "g.mapset", "r.slope.aspect"],
            cell_limit=1000,
            process_num_limit=3,
            process_time_limit=30,
        )

        print(user)

        self.assertEqual(user.get_role(), "admin")
        self.assertEqual(user.get_id(), self.user_id)
        self.assertEqual(user.get_group(), self.user_group)
        self.assertEqual(user.get_cell_limit(), 1000)
        self.assertEqual(user.get_process_num_limit(), 3)
        self.assertEqual(user.get_process_time_limit(), 30)

        datasets = user.get_accessible_datasets()
        modules = user.get_accessible_modules()

        self.assertTrue("nc_spm_08" in datasets)
        self.assertTrue("PERMANENT" in datasets["nc_spm_08"])
        self.assertTrue("g.region" in modules)

        token = user.generate_auth_token()
        user_2 = ActiniaUser.verify_auth_token(token)

        print(user_2)

        self.assertTrue(user_2.exists())
        self.assertEqual(user_2.get_role(), "admin")
        self.assertEqual(user_2.get_id(), self.user_id)
        self.assertEqual(user.get_group(), self.user_group)
        self.assertEqual(user_2.get_cell_limit(), 1000)
        self.assertEqual(user_2.get_process_num_limit(), 3)
        self.assertEqual(user_2.get_process_time_limit(), 30)

        datasets = user_2.get_accessible_datasets()
        modules = user_2.get_accessible_modules()

        self.assertTrue("nc_spm_08" in datasets)
        self.assertTrue("PERMANENT" in datasets["nc_spm_08"])
        self.assertTrue("g.region" in modules)

        api_key = user.generate_api_key()
        user_3 = ActiniaUser.verify_api_key(api_key)

        print(user_3)

        self.assertTrue(user_3.exists())
        self.assertEqual(user_3.get_role(), "admin")
        self.assertEqual(user_3.get_id(), self.user_id)
        self.assertEqual(user.get_group(), self.user_group)
        self.assertEqual(user_3.get_cell_limit(), 1000)
        self.assertEqual(user_3.get_process_num_limit(), 3)
        self.assertEqual(user_3.get_process_time_limit(), 30)

        datasets = user_3.get_accessible_datasets()
        modules = user_3.get_accessible_modules()

        self.assertTrue("nc_spm_08" in datasets)
        self.assertTrue("PERMANENT" in datasets["nc_spm_08"])
        self.assertTrue("g.region" in modules)

        self.assertTrue(user.delete())
        self.assertFalse(user_2.delete())
        self.assertFalse(user_3.delete())

    def test_create_update_user(self):
        """Test the creation and update of a user in the redis database"""

        user = ActiniaUser(self.user_id)
        if user.exists():
            print("Delete existing user")
            user.delete()

        # Create a new user
        user = ActiniaUser.create_user(
            self.user_id,
            self.user_group,
            self.password,
            user_role="admin",
            accessible_datasets={"nc_spm_08": ["PERMANENT", "user1"]},
            accessible_modules=["g.region", "g.mapset", "r.slope.aspect"],
            cell_limit=1000,
            process_num_limit=3,
            process_time_limit=30,
        )

        print(user)

        self.assertEqual(user.get_role(), "admin")
        self.assertEqual(user.get_id(), self.user_id)
        self.assertEqual(user.get_group(), self.user_group)
        self.assertEqual(user.get_cell_limit(), 1000)
        self.assertEqual(user.get_process_num_limit(), 3)
        self.assertEqual(user.get_process_time_limit(), 30)

        datasets = user.get_accessible_datasets()

        self.assertTrue("nc_spm_08" in datasets)
        self.assertTrue("PERMANENT" in datasets["nc_spm_08"])

        user = ActiniaUser(user_id=self.user_id)
        user.read_from_db()
        user.set_role("user")
        user.set_cell_limit(1000000)
        user.set_process_num_limit(10)
        user.set_process_time_limit(50)
        user.update()

        print(user)

        self.assertEqual(user.get_role(), "user")
        self.assertEqual(user.get_cell_limit(), 1000000)
        self.assertEqual(user.get_process_num_limit(), 10)
        self.assertEqual(user.get_process_time_limit(), 50)

        user = ActiniaUser(user_id=self.user_id)
        user.read_from_db()
        user.add_accessible_dataset("utm32n", ["PERMANENT"])
        user.add_accessible_modules(
            [
                "i.vi",
            ]
        )
        user.update()

        print(user)

        datasets = user.get_accessible_datasets()
        modules = user.get_accessible_modules()

        self.assertTrue("nc_spm_08" in datasets)
        self.assertTrue("PERMANENT" in datasets["nc_spm_08"])
        self.assertTrue("g.region" in modules)
        self.assertTrue("utm32n" in datasets)
        self.assertTrue("PERMANENT" in datasets["utm32n"])
        self.assertTrue("i.vi" in modules)

        user = ActiniaUser(user_id=self.user_id)
        user.read_from_db()
        user.remove_project("utm32n")
        user.remove_mapsets_from_project(
            "nc_spm_08",
            [
                "user1",
            ],
        )
        user.remove_accessible_modules(
            [
                "i.vi",
            ]
        )
        user.update()

        print(user)

        datasets = user.get_accessible_datasets()
        modules = user.get_accessible_modules()

        self.assertTrue("nc_spm_08" in datasets)
        self.assertTrue("PERMANENT" in datasets["nc_spm_08"])
        self.assertFalse("user1" in datasets["nc_spm_08"])
        self.assertTrue("g.region" in modules)
        self.assertFalse("utm32n" in datasets)
        self.assertFalse("i.vi" in modules)


if __name__ == "__main__":
    unittest.main()
