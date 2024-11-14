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
Tests: Project test case
"""
from flask.json import loads as json_loads, dumps as json_dumps
import unittest

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ProjectTestCase(ActiniaResourceTestCaseBase):
    def test_list_projects(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}",
            headers=self.user_auth_header,
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

        if "nc_spm_08" in json_loads(rv.data)[self.project_url_part]:
            project = "nc_spm_08"

        self.assertEqual(project, "nc_spm_08", "Wrong project listed")

    def test_project_info(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/info",
            headers=self.admin_auth_header,
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

        region_settings = json_loads(rv.data)["process_results"]["region"]
        json_loads(rv.data)["process_results"]["projection"]

        self.assertTrue("depths" in region_settings)
        self.assertTrue("ewres" in region_settings)
        self.assertTrue("cols" in region_settings)
        self.assertTrue("rows" in region_settings)

    def test_project_global_db_error(self):
        # ERROR: Try to create a project as admin that exists in the global
        # database
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_project_creation_and_deletion(self):
        # Delete a potentially existing project
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/test_project",
            headers=self.admin_auth_header,
        )

        # Create new project as admin
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/test_project",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.admin_auth_header,
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

        # ERROR: Try to create a project as admin that already exists
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/test_project",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # Delete project
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/test_project",
            headers=self.admin_auth_header,
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

        # ERROR: Delete should fail, since project does not exists
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/test_project",
            headers=self.admin_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_project_creation_and_deletion_as_user(self):
        # Delete a potentially existing project
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/test_project",
            headers=self.user_auth_header,
        )

        # Create new project as user
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/test_project",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.user_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            200,
            "Project creation by user: HTML status code is wrong %i"
            % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype,
            "application/json",
            "Project creation by user: Wrong mimetype %s" % rv.mimetype,
        )

        # ERROR: Try to create a project as user that already exists
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/test_project",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.user_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            400,
            "Project recreation by user: HTML status code is wrong %i"
            % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype,
            "application/json",
            "Project recreation by user: Wrong mimetype %s" % rv.mimetype,
        )

        # Delete project
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/test_project",
            headers=self.user_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            200,
            "Project deletion by user: HTML status code is wrong %i"
            % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype,
            "application/json",
            "Project deletion by user: Wrong mimetype %s" % rv.mimetype,
        )

        # ERROR: Delete should fail, since project does not exists
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/test_project",
            headers=self.user_auth_header,
        )
        self.assertEqual(
            rv.status_code,
            400,
            "Project redeletion by user: HTML status code is wrong %i"
            % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype,
            "application/json",
            "Project redeletion by user: Wrong mimetype %s" % rv.mimetype,
        )

    def test_project_creation_and_deletion_as_guest(self):
        # ERROR: Try to create a project as guest
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/test_project_user",
            data=json_dumps({"epsg": "4326"}),
            content_type="application/json",
            headers=self.guest_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

        # ERROR: Delete should fail since the guest user is not authorized
        rv = self.server.delete(
            f"{URL_PREFIX}/{self.project_url_part}/test_project_user",
            headers=self.guest_auth_header,
        )
        print(rv.data)
        self.assertEqual(
            rv.status_code,
            401,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )


if __name__ == "__main__":
    unittest.main()
