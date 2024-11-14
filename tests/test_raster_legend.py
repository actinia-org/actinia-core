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
Tests: Raster legend test case
"""
import unittest
from pprint import pprint
from flask.json import loads as json_load

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except ModuleNotFoundError:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class RasterLegendTestCase(ActiniaResourceTestCaseBase):
    def test_raster_legend_no_args(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/legend",
            headers=self.user_auth_header,
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype
        )

    def test_raster_legend_args_1(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/legend?at=0,100,0,20",
            headers=self.user_auth_header,
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype
        )

    def test_raster_legend_args_2(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/legend?range=100,120",
            headers=self.user_auth_header,
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype
        )

    def test_raster_legend_args_3(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/legend?&use=100,110,120",
            headers=self.user_auth_header,
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype
        )

    def test_raster_legend_args_4(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/legend?&fontsize=100",
            headers=self.user_auth_header,
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype
        )

    def test_raster_legend_args_5(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/legend?width=100&height=100",
            headers=self.user_auth_header,
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype
        )

    def test_raster_legend_args_6(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/legend?width=100&height=100&"
            "range=100,120&use=105,110,115&at=0,100,0,30",
            headers=self.user_auth_header,
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype
        )

    def test_raster_legend_args_7(self):
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/legend?labelnum=4",
            headers=self.user_auth_header,
        )

        self.assertEqual(
            rv.status_code,
            200,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype
        )

    def test_raster_legend_args_error_1(self):
        # Wrong "at" parameter
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/"
            "PERMANENT/raster_layers/elevation/legend?at=-0,-0",
            headers=self.user_auth_header,
        )
        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )
        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)

    def test_raster_legend_args_error_2(self):
        # Wrong witdth
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/PERMANENT"
            "/raster_layers/elevation/legend?width=-20&at=20,40,20,40",
            headers=self.user_auth_header,
        )
        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )
        log = json_load(rv.data)["message"]
        self.assertFalse("AsyncProcessError:" in log)

    def test_raster_legend_args_error_3(self):
        # Wrong range and use
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/PERMANENT"
            "/raster_layers/elevation/legend?range=100,120&use=90,130,115",
            headers=self.user_auth_header,
        )
        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )
        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)

    def test_raster_legend_args_error_4(self):
        # Wrong labelnum
        rv = self.server.get(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/mapsets/PERMANENT"
            "/raster_layers/elevation/legend?labelnum=-4",
            headers=self.user_auth_header,
        )
        pprint(json_load(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )
        log = json_load(rv.data)["message"]
        self.assertTrue("AsyncProcessError:" in log)


if __name__ == "__main__":
    unittest.main()
