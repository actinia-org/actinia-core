# -*- coding: utf-8 -*-
import unittest
from actinia_core.resources.common.user import ActiniaUser
from actinia_core import main as main
try:
    from .test_common_base import CommonTestCaseBase
except:
    from test_common_base import CommonTestCaseBase

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class UserTestCase(CommonTestCaseBase):
    """
    This class tests the user interface, the creation and deletion
    of a user entry in a Redis database
    """

    def setUp(self):
        # We need to set the application context
        self.app_context = main.flask_app.app_context()
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
        user = ActiniaUser.create_user(self.user_id,
                                       self.user_group,
                                       self.password,
                                       user_role="admin",
                                       accessible_datasets={"nc_spm_08": ["PERMANENT", "user1"]},
                                       accessible_modules=["g.region", "g.mapset", "r.slope.aspect"],
                                       cell_limit=1000,
                                       process_num_limit=3,
                                       process_time_limit=30)

        print(user)

        self.assertEqual(user.get_role(), "admin")
        self.assertEquals(user.get_id(), self.user_id)
        self.assertEquals(user.get_group(), self.user_group)
        self.assertEquals(user.get_cell_limit(), 1000)
        self.assertEquals(user.get_process_num_limit(), 3)
        self.assertEquals(user.get_process_time_limit(), 30)

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
        self.assertEquals(user_2.get_id(), self.user_id)
        self.assertEquals(user.get_group(), self.user_group)
        self.assertEquals(user_2.get_cell_limit(), 1000)
        self.assertEquals(user_2.get_process_num_limit(), 3)
        self.assertEquals(user_2.get_process_time_limit(), 30)

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
        self.assertEquals(user_3.get_id(), self.user_id)
        self.assertEquals(user.get_group(), self.user_group)
        self.assertEquals(user_3.get_cell_limit(), 1000)
        self.assertEquals(user_3.get_process_num_limit(), 3)
        self.assertEquals(user_3.get_process_time_limit(), 30)

        datasets = user_3.get_accessible_datasets()
        modules = user_3.get_accessible_modules()

        self.assertTrue("nc_spm_08" in datasets)
        self.assertTrue("PERMANENT" in datasets["nc_spm_08"])
        self.assertTrue("g.region" in modules)

        self.assertTrue(user.delete())
        self.assertFalse(user_2.delete())
        self.assertFalse(user_3.delete())

    def test_create_update_user(self):
        """Test the creation and update of a user in the redis database
        """

        user = ActiniaUser(self.user_id)
        if user.exists():
            print("Delete existing user")
            user.delete()

        # Create a new user
        user = ActiniaUser.create_user(self.user_id,
                                       self.user_group,
                                       self.password,
                                       user_role="admin",
                                       accessible_datasets={"nc_spm_08": ["PERMANENT", "user1"]},
                                       accessible_modules=["g.region", "g.mapset", "r.slope.aspect"],
                                       cell_limit=1000,
                                       process_num_limit=3,
                                       process_time_limit=30)

        print(user)

        self.assertEqual(user.get_role(), "admin")
        self.assertEquals(user.get_id(), self.user_id)
        self.assertEquals(user.get_group(), self.user_group)
        self.assertEquals(user.get_cell_limit(), 1000)
        self.assertEquals(user.get_process_num_limit(), 3)
        self.assertEquals(user.get_process_time_limit(), 30)

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
        self.assertEquals(user.get_cell_limit(), 1000000)
        self.assertEquals(user.get_process_num_limit(), 10)
        self.assertEquals(user.get_process_time_limit(), 50)

        user = ActiniaUser(user_id=self.user_id)
        user.read_from_db()
        user.add_accessible_dataset("utm32n", ["PERMANENT"])
        user.add_accessible_modules(["i.vi", ])
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
        user.remove_location("utm32n")
        user.remove_mapsets_from_location("nc_spm_08", ["user1", ])
        user.remove_accessible_modules(["i.vi", ])
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


if __name__ == '__main__':
    unittest.main()
