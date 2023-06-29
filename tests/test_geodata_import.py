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
Tests: Geodata download import support test case
"""
from actinia_core.core.geodata_download_importer import (
    GeoDataDownloadImportSupport,
)
from actinia_core.core.common.landsat_processing_library import (
    LandsatProcessing,
)
from actinia_core.core.common.config import global_config
import unittest
import subprocess
import os
import shutil

try:
    from .test_resource_base import additional_external_data
except ModuleNotFoundError:
    from test_resource_base import additional_external_data


__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class MessageDummy(object):
    def info(self, message):
        print(message)

    def warning(self, message):
        print(message)

    def debug(self, message):
        print(message)

    def error(self, message):
        print(message)


def update_dummy(message):
    print(message)


class GeoDataDownloadImportSupportTestCase(unittest.TestCase):
    """This class tests the BigQuery google interface to collect download
    urls of landsat and sentinel data
    """

    cache_dir = "/tmp/temp_test_cache"

    def setUp(self):
        if os.path.isdir(self.cache_dir) is False:
            os.mkdir(self.cache_dir)

    def tearDown(self):
        if os.path.isdir(self.cache_dir) is True:
            shutil.rmtree(self.cache_dir)
        pass

    def _run_process(self, process):
        print("Run process: " + str(process))

        inputlist = list()
        inputlist.append(process.executable)
        inputlist.extend(process.executable_params)

        proc = subprocess.Popen(
            args=inputlist, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("Process id: %i" % proc.pid)

        (stdout_buff, stderr_buff) = proc.communicate()
        print(stdout_buff)
        print(stderr_buff)
        proc.wait()

        self.assertEqual(
            0, proc.returncode, "Error while running %s" % process.executable
        )

    def test_download_commands_gml(self):
        gml = additional_external_data["census_wake2000_gml"]

        gddl = GeoDataDownloadImportSupport(
            config=global_config,
            temp_file_path="/tmp",
            download_cache=self.cache_dir,
            send_resource_update=update_dummy,
            message_logger=MessageDummy(),
            url_list=[
                gml,
            ],
        )

        pl, import_file_info = gddl.get_download_process_list()
        self.assertTrue("xml" in import_file_info[0][0])
        self.assertTrue(len(pl) == 2)

        for p in pl:
            self._run_process(p)

        for url, file_path, file_name in import_file_info:
            gddl.perform_file_validation(filepath=file_name)

        for url, file_path, file_name in import_file_info:
            p = gddl.get_vector_import_command(file_name, "test")
            print(p)
            self.assertEqual("v.import", p.executable)

    def test_download_commands_gml_zip(self):
        url_list = []

        gml = additional_external_data["census_wake2000_gml"]
        gml_zip = additional_external_data["census_wake2000_zip"]
        tif = additional_external_data["geology_30m_tif"]
        tif_zip = additional_external_data["geology_30m_zip"]

        url_list.append(gml_zip)
        url_list.append(tif_zip)
        url_list.append(gml)
        url_list.append(tif)

        gddl = GeoDataDownloadImportSupport(
            config=global_config,
            temp_file_path="/tmp",
            download_cache=self.cache_dir,
            send_resource_update=update_dummy,
            message_logger=MessageDummy(),
            url_list=url_list,
        )

        pl, import_file_info = gddl.get_download_process_list()
        self.assertEqual("application/zip", import_file_info[0][0])
        self.assertTrue(len(pl) == 8)

        for p in pl:
            self._run_process(p)

        for url, file_path, file_name in import_file_info:
            gddl.perform_file_validation(filepath=file_name)

    def test_download_commands_tif(self):
        tif_list = []
        tif_list.append(additional_external_data["geology_30m_tif"])
        tif_list.append(additional_external_data["geology_30m_tif"])
        tif_list.append(additional_external_data["geology_30m_tif"])
        tif_list.append(additional_external_data["geology_30m_tif"])
        tif_list.append(additional_external_data["geology_30m_tif"])
        tif_list.append(additional_external_data["geology_30m_tif"])

        gddl = GeoDataDownloadImportSupport(
            config=global_config,
            temp_file_path="/tmp",
            download_cache=self.cache_dir,
            send_resource_update=update_dummy,
            message_logger=MessageDummy(),
            url_list=tif_list,
        )

        pl, import_file_info = gddl.get_download_process_list()
        self.assertEqual("image/tiff", import_file_info[0][0])
        self.assertEqual("image/tiff", import_file_info[1][0])
        self.assertEqual("image/tiff", import_file_info[2][0])
        self.assertEqual("image/tiff", import_file_info[3][0])
        self.assertEqual("image/tiff", import_file_info[4][0])
        self.assertTrue(len(pl) == 12)

        for p in pl:
            self._run_process(p)

        for url, file_path, file_name in import_file_info:
            gddl.perform_file_validation(filepath=file_name)

        for url, file_path, file_name in import_file_info:
            p = gddl.get_raster_import_command(file_name, "test")
            print(p)
            self.assertEqual("r.import", p.executable)

    def test_landsat_download_commands(self):
        lp = LandsatProcessing(
            config=global_config,
            temp_file_path="/tmp",
            scene_id="LC08_L1GT_001004_20130910_20170502_01_T2",
            download_cache=self.cache_dir,
            send_resource_update=update_dummy,
            message_logger=MessageDummy(),
        )

        pl, import_file_info = lp.get_download_process_list()

        print(import_file_info, len(pl))
        for p in pl:
            print(p)

        pl = lp.get_i_landsat_toar_process_list(atcor_method="DOS4")

        print(import_file_info, len(pl))
        for p in pl:
            print(p)

        pl = lp.get_i_vi_process_list(
            atcor_method="DOS4", processing_method="NDVI"
        )

        print(import_file_info, len(pl))
        for p in pl:
            print(p)

        print(lp.raster_names)


if __name__ == "__main__":
    unittest.main()
