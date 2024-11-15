# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2021-2024 Sören Gebbert and mundialis GmbH & Co. KG
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
Tests: Async process2 test case
"""
import configparser
import os
import unittest
from flask.json import dumps as json_dumps
from flask.json import loads as json_loads
from jinja2 import Template
from time import sleep

from actinia_core.core.common.config import global_config

try:
    from .test_resource_base import (
        ActiniaResourceTestCaseBase,
        URL_PREFIX,
        additional_external_data,
    )
except ModuleNotFoundError:
    from test_resource_base import (
        ActiniaResourceTestCaseBase,
        URL_PREFIX,
        additional_external_data,
    )

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2021-2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


process_chain_1 = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [{"param": "raster", "value": "elevation@PERMANENT"}],
            "flags": "p",
        },
        {
            "id": "2",
            "module": "r.mapcalc",
            "inputs": [{"param": "expression", "value": "baum = 5"}],
        },
        {
            "id": "3",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "{{ map1 }}"}],
        },
        {
            "id": "4",
            "module": "g.list",
            "inputs": [{"param": "type", "value": "raster"}],
        },
        {
            "id": "5",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "{{ map2 }}"}],
        },
    ],
}

process_chain_2_error = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [{"param": "raster", "value": "elevation@PERMANENT"}],
            "flags": "p",
        },
        {"id": "2", "exe": "sleep", "params": ["{{ seconds }}"]},
        {
            "id": "3",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "elevation2@PERMANENT"}],
        },
    ],
}

process_chain_3_importer = {
    "version": 1,
    "list": [
        {
            "module": "g.region",
            "id": "1",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data["elev_ned_30m_tif"],
                        "type": "raster",
                    },
                    "param": "raster",
                    "value": "elev_ned_30m_new",
                }
            ],
            "flags": "p",
        },
        {
            "id": "2",
            "module": "r.mapcalc",
            "inputs": [{"param": "expression", "value": "baum = 5"}],
        },
        {
            "id": "3",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "{{ map1 }}"}],
        },
        {
            "id": "4",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data["pointInBonn"],
                        "type": "vector",
                    },
                    "param": "map",
                    "value": "point",
                },
                {
                    "import_descr": {
                        "source": additional_external_data["geology_30m_tif"],
                        "type": "raster",
                    },
                    "param": "map",
                    "value": "geology_30m_new",
                },
            ],
        },
        {
            "id": "5",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "{{ map2 }}"}],
        },
        {
            "id": "6",
            "module": "g.list",
            "inputs": [{"param": "type", "value": "raster"}],
        },
        {
            "id": "7",
            "module": "v.info",
            "inputs": [{"param": "map", "value": "point"}],
        },
        {
            "id": "8",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "geology_30m_new"}],
        },
    ],
}


process_chain_4_exporter = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [{"param": "raster", "value": "elevation@PERMANENT"}],
            "flags": "p",
        },
        {
            "id": "2",
            "module": "r.colors.out_sld",
            "inputs": [{"param": "map", "value": "elevation@PERMANENT"}],
            "outputs": [
                {
                    "param": "output",
                    "value": "$file::export_of_2",
                    "export": {"type": "file", "format": "TXT"},
                }
            ],
        },
        {
            "id": "3",
            "module": "r.mapcalc",
            "inputs": [{"param": "expression", "value": "baum = 5*elevation"}],
        },
        {
            "id": "4",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "{{ map1 }}"}],
        },
        {
            "id": "5",
            "module": "g.list",
            "inputs": [{"param": "type", "value": "raster"}],
        },
        {
            "id": "6",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "{{ map2 }}"}],
        },
        {
            "id": "7",
            "module": "exporter",
            "comment": "Export indices as COG",
            "outputs": [
                {
                    "export": {"type": "raster", "format": "COG"},
                    "param": "map",
                    "value": "baum",
                },
                {
                    "export": {"type": "raster", "format": "COG"},
                    "param": "map",
                    "value": "elevation@PERMANENT",
                },
            ],
        },
    ],
}

process_chain_5_stdout = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [{"param": "raster", "value": "elevation@PERMANENT"}],
            "flags": "p",
        },
        {
            "id": "2",
            "module": "r.colors.out_sld",
            "inputs": [
                {"param": "map", "value": "elevation@PERMANENT"},
                {"param": "style_name", "value": "elevation"},
            ],
            "stdout": {"id": "sld", "format": "list", "delimiter": "\n"},
        },
        {
            "id": "3",
            "module": "r.mapcalc",
            "inputs": [{"param": "expression", "value": "baum = 5"}],
        },
        {
            "id": "4",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "{{ map1 }}"}],
            "flags": "g",
            "stdout": {"id": "r_info_map1", "format": "kv", "delimiter": "="},
        },
        {
            "id": "5",
            "module": "g.list",
            "inputs": [{"param": "type", "value": "raster"}],
        },
        {
            "id": "6",
            "module": "r.info",
            "inputs": [{"param": "map", "value": "{{ map2 }}"}],
            "flags": "g",
            "stdout": {"id": "r_info_map2", "format": "kv", "delimiter": "="},
        },
    ],
}


class JobResumptionProcessingTestCase(ActiniaResourceTestCaseBase):
    cfg_file = os.environ.get("DEFAULT_CONFIG_PATH", "/etc/default/actinia")
    tmp_cfg_file = "%s_tmp" % cfg_file
    endpoint = "nc_spm_08/processing_async"
    save_interim_results_value = None
    resource_user_id = None
    resource_resource_id = None
    sleep_time = 15
    save_interim_results = "True"

    @classmethod
    def save_config(cls, src, dest, value):
        config = configparser.ConfigParser()
        config.read(src)
        config["MISC"]["save_interim_results"] = value
        with open(dest, "w") as configfile:
            config.write(configfile)

    @classmethod
    def setUpClass(cls):
        # change save_interim_results in config to True
        cls.save_interim_results_value = global_config.SAVE_INTERIM_RESULTS
        if cls.save_interim_results_value is False:
            os.replace(cls.cfg_file, cls.tmp_cfg_file)
            cls.save_config(
                cls.tmp_cfg_file,
                cls.cfg_file,
                cls.save_interim_results,
            )

        super(JobResumptionProcessingTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        # reset config
        if cls.save_interim_results_value is False:
            cls.save_config(cls.tmp_cfg_file, cls.cfg_file, "False")
            os.remove(cls.tmp_cfg_file)
        global_config.read(cls.cfg_file)

        super(JobResumptionProcessingTestCase, cls).tearDownClass()

    def test_notsaved_interim_results_by_success(self):
        """Test if the interim results are not saved if process ends
        successfully
        """
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        # check if interim results are not saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertFalse(
            os.path.isdir(interim_dir),
            "Interim results are stored",
        )

    def test_saved_interim_results(self):
        """Test if the interim results are not saved correctly"""
        step = 4
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum555"),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertTrue(
            os.path.isdir(interim_dir),
            "Interim results are not stored in the expected folder",
        )
        self.assertTrue(
            os.path.isdir(os.path.join(interim_dir, f"step{step}")),
            "Interim results mapset is not stored in the expected folder",
        )
        self.assertIn(
            "baum",
            os.listdir(os.path.join(interim_dir, f"step{step}", "cellhd")),
            "Raster map 'baum' not in interim results mapset",
        )
        self.assertTrue(
            os.path.isdir(os.path.join(interim_dir, f"tmpdir{step}")),
            "Interim results temporary file path is not stored in the expected"
            " folder",
        )

    def test_job_resumption(self):
        """Test job resumption with processing_async endpoint"""
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertTrue(
            os.path.isdir(interim_dir),
            "Interim results are not stored in the expected folder",
        )

        # resumption of the job
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv2,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    def test_job_2_times_resumption(self):
        """Test job 2 times resumption with processing_async endpoint"""
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # first job resumption
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum1"),
            content_type="application/json",
        )
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
        )
        status_url = resp2["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv2.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertTrue(
            os.path.isdir(interim_dir),
            "Interim results are not stored in the expected folder",
        )

        # second job resumption
        rv3 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv3,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )
        self.__class__.resource_user_id = rv_user_id
        self.__class__.resource_resource_id = rv_resource_id

    def test_job_resumption_error_by_running(self):
        """Test job resumption error by running process with processing_async
        endpoint
        """
        tpl = Template(json_dumps(process_chain_2_error))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(seconds=self.sleep_time),
            content_type="application/json",
        )
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        waiting_for_running = True
        while waiting_for_running:
            rv_pull = self.server.get(
                URL_PREFIX + "/resources/%s/%s" % (rv_user_id, rv_resource_id),
                headers=self.admin_auth_header,
            )
            resp_data_pull = json_loads(rv_pull.data)
            if resp_data_pull["status"] == "running":
                waiting_for_running = False
            elif resp_data_pull["status"] in [
                "error",
                "terminated",
                "timeout",
            ]:
                self.assertTrue(
                    False,
                    "Process is not running it is %s"
                    % resp_data_pull["status"],
                )
        status_url = resp_data_pull["urls"]["status"].split(URL_PREFIX)[-1]

        # job resumption by running job
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_2_error),
            content_type="application/json",
        )
        self.assertEqual(rv2.status_code, 404)
        resp_data2 = json_loads(rv2.data)
        self.assertEqual(resp_data2["status"], "error")
        self.assertEqual(
            resp_data2["message"], "Resource is running no restart possible"
        )

    def test_job_resumption_importer(self):
        """Test job resumption with processing_async endpoint and importer"""
        tpl = Template(json_dumps(process_chain_3_importer))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertTrue(
            os.path.isdir(interim_dir),
            "Interim results are not stored in the expected folder",
        )

        # resumption of the job
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elev_ned_30m_new", map2="baum"),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv2,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    def test_job_2_times_resumption_importer(self):
        """Test job 2 times resumption with processing_async endpoint and
        importer
        """
        tpl = Template(json_dumps(process_chain_3_importer))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # first job resumption
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elev_ned_30m_new", map2="baum1"),
            content_type="application/json",
        )
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
        )
        status_url = resp2["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv2.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertTrue(
            os.path.isdir(interim_dir),
            "Interim results are not stored in the expected folder",
        )

        # second job resumption
        rv3 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elev_ned_30m_new", map2="baum"),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv3,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )
        self.__class__.resource_user_id = rv_user_id
        self.__class__.resource_resource_id = rv_resource_id

    def compare_stdout(self, resp):
        proc_results = resp["process_results"]
        self.assertIn(
            "sld", proc_results, "'sld' not saved in process results"
        )
        self.assertIn(
            "r_info_map1",
            proc_results,
            "'r_info_map1' not saved in process results",
        )
        self.assertIn(
            "r_info_map2",
            proc_results,
            "'r_info_map2' not saved in process results",
        )
        self.assertIsInstance(
            proc_results["sld"], list, "'sld' result is not of type list"
        )
        self.assertIsInstance(
            proc_results["r_info_map1"],
            dict,
            "'r_info_map1' result is not of type dict",
        )
        self.assertIsInstance(
            proc_results["r_info_map2"],
            dict,
            "'r_info_map2' result is not of type dict",
        )
        r_info_map1 = {
            "cells": "2025000",
            "cols": "1500",
            "datatype": "FCELL",
            "east": "645000",
            "ewres": "10",
            "ncats": "255",
            "north": "228500",
            "nsres": "10",
            "rows": "1350",
            "south": "215000",
            "west": "630000",
        }
        self.assertEqual(
            proc_results["r_info_map1"],
            r_info_map1,
            "'r_info_map1' is not equal to the region",
        )
        r_info_map2 = {
            "cells": "2025000",
            "cols": "1500",
            "datatype": "CELL",
            "east": "645000",
            "ewres": "10",
            "ncats": "0",
            "north": "228500",
            "nsres": "10",
            "rows": "1350",
            "south": "215000",
            "west": "630000",
        }
        self.assertEqual(
            proc_results["r_info_map2"],
            r_info_map2,
            "'r_info_map2' is not equal to the region",
        )

    def test_job_resumption_stdout(self):
        """Test job resumption with processing_async endpoint and stdout"""
        tpl = Template(json_dumps(process_chain_5_stdout))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertTrue(
            os.path.isdir(interim_dir),
            "Interim results are not stored in the expected folder",
        )

        # resumption of the job
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )
        self.compare_stdout(resp2)

    def test_job_2_times_resumption_stdout(self):
        """Test job 2 times resumption with processing_async endpoint and
        stdout
        """
        tpl = Template(json_dumps(process_chain_5_stdout))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # first job resumption
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum1"),
            content_type="application/json",
        )
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
        )
        status_url = resp2["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv2.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertTrue(
            os.path.isdir(interim_dir),
            "Interim results are not stored in the expected folder",
        )

        # second job resumption
        rv3 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp3 = self.waitAsyncStatusAssertHTTP(
            rv3,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )
        self.compare_stdout(resp3)

    def test_resource_endpoints(self):
        """Test resource endpoint with iterations"""
        self.assertIsNotNone(self.resource_user_id, "resource_user_id is None")
        self.assertIsNotNone(
            self.resource_resource_id, "resource_resource_id is None"
        )

        # get latest iteration by requesting /resources/{USER}/resource_id-{ID}
        rv1 = self.server.get(
            URL_PREFIX
            + "/resources/%s/%s"
            % (self.resource_user_id, self.resource_resource_id),
            headers=self.admin_auth_header,
        )
        resp_data1 = json_loads(rv1.data)
        self.assertEqual(
            resp_data1["status"],
            "finished",
            "Resource request 1 is not finished",
        )
        self.assertEqual(
            rv1.status_code, 200, "Resource request 1 status code is not 200"
        )
        self.assertEqual(
            resp_data1["iteration"], 3, "Iteration is not 3 (the latest)"
        )

        # get all iteration by requesting /resources/{USER}/{ID}
        rv2 = self.server.get(
            URL_PREFIX
            + "/resources/%s/%s"
            % (
                self.resource_user_id,
                self.resource_resource_id.replace("resource_id-", ""),
            ),
            headers=self.admin_auth_header,
        )
        resp_data2 = json_loads(rv2.data)
        self.assertEqual(
            rv2.status_code, 200, "Resource request 2 status code is not 200"
        )
        self.assertEqual(
            len(resp_data2.keys()), 3, "Not 3 iteration in request"
        )

        # get resource by iteration number requesting /resources/{USER}/{ID}/
        # {ITERATION}
        for iteration in range(1, 4):
            rv3 = self.server.get(
                URL_PREFIX
                + "/resources/%s/%s/%d"
                % (
                    self.resource_user_id,
                    self.resource_resource_id,
                    iteration,
                ),
                headers=self.admin_auth_header,
            )
            resp_data3 = json_loads(rv3.data)
            self.assertEqual(
                rv3.status_code,
                200,
                "Resource request for iteration %d status code is not 200"
                % iteration,
            )
            if iteration != 1:
                self.assertIn(
                    "iteration",
                    resp_data3[str(iteration)],
                    "'iteration' is not in response",
                )
                self.assertEqual(
                    resp_data3[str(iteration)]["iteration"],
                    iteration,
                    "Iteration is not %d" % iteration,
                )
            else:
                self.assertNotIn(
                    "iteration",
                    resp_data3[str(iteration)],
                    "'iteration' is in response",
                )
            del rv3, resp_data3


class JobResumptionProcessingExportTestCase(JobResumptionProcessingTestCase):
    endpoint = "nc_spm_08/processing_async_export"
    resource_user_id = None
    resource_resource_id = None

    def test_job_resumption_exporter(self):
        """
        Test job resumption with processing_async_export endpoint and exporter
        """
        tpl = Template(json_dumps(process_chain_4_exporter))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertTrue(
            os.path.isdir(interim_dir),
            "Interim results are not stored in the expected folder",
        )

        # resumption of the job
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        # Get the exported results
        urls = resp2["urls"]["resources"]
        for url in urls:
            rv = self.server.get(url, headers=self.admin_auth_header)
            self.assertEqual(
                rv.status_code,
                200,
                "HTML status code is wrong %i" % rv.status_code,
            )
            if url.endswith(".tif"):
                self.assertEqual(
                    rv.mimetype,
                    "image/tiff",
                    "Wrong mimetype %s" % rv.mimetype,
                )
            elif url.endswith(".zip"):
                self.assertEqual(
                    rv.mimetype,
                    "application/zip",
                    "Wrong mimetype %s" % rv.mimetype,
                )

    def test_job_2_times_resumption_exporter(self):
        """Test job 2 times resumption with processing_async_export endpoint
        and exporter
        """
        tpl = Template(json_dumps(process_chain_4_exporter))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # first job resumption
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum1"),
            content_type="application/json",
        )
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2,
            headers=self.admin_auth_header,
            http_status=400,
            status="error",
        )
        status_url = resp2["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv2.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertTrue(
            os.path.isdir(interim_dir),
            "Interim results are not stored in the expected folder",
        )

        # second job resumption
        rv3 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp3 = self.waitAsyncStatusAssertHTTP(
            rv3,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        # Get the exported results
        urls = resp3["urls"]["resources"]
        for url in urls:
            rv = self.server.get(url, headers=self.admin_auth_header)
            self.assertEqual(
                rv.status_code,
                200,
                "HTML status code is wrong %i" % rv.status_code,
            )
            if url.endswith(".tif"):
                self.assertEqual(
                    rv.mimetype,
                    "image/tiff",
                    "Wrong mimetype %s" % rv.mimetype,
                )
            elif url.endswith(".zip"):
                self.assertEqual(
                    rv.mimetype,
                    "application/zip",
                    "Wrong mimetype %s" % rv.mimetype,
                )
        self.__class__.resource_user_id = rv_user_id
        self.__class__.resource_resource_id = rv_resource_id


class JobResumptionPersistentProcessingTestCase(
    JobResumptionProcessingTestCase
):
    project = "nc_spm_08"
    mapset = "test_mapset"
    endpoint = f"{project}/mapsets/{mapset}/processing_async"
    resource_user_id = None
    resource_resource_id = None
    mapset_created = True

    def tearDown(self):
        if self.mapset_created is True:
            rv = self.server.delete(
                f"{URL_PREFIX}/{self.project_url_part}/{self.project}/mapsets/"
                f"{self.mapset}/lock",
                headers=self.admin_auth_header,
            )
            self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)
            rv2 = self.server.delete(
                f"{URL_PREFIX}/{self.project_url_part}/{self.project}/mapsets/"
                f"{self.mapset}",
                headers=self.admin_auth_header,
            )
            self.waitAsyncStatusAssertHTTP(rv2, headers=self.admin_auth_header)
        else:
            self.__class__.mapset_created = True
        self.app_context.pop()

    def test_saved_interim_results(self):
        """Test if the interim results are removed"""
        self.create_new_mapset(self.mapset, self.project)
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id,
            "interim",
            rv_resource_id,
        )
        self.assertTrue(
            not os.path.isdir(interim_dir),
            "Interim results are not stored in the expected folder",
        )

    def test_job_resumption_error_by_running(self):
        super(
            JobResumptionPersistentProcessingTestCase, self
        ).test_job_resumption_error_by_running()
        sleep(self.sleep_time)
        self.__class__.mapset_created = False
        print(self.resource_user_id)

    def test_resource_endpoints(self):
        super(
            JobResumptionPersistentProcessingTestCase, self
        ).test_resource_endpoints()
        self.__class__.mapset_created = False


class JobResumptionErrorTestCase(ActiniaResourceTestCaseBase):
    endpoint = "nc_spm_08/processing_async"

    def test_job_resumption_config_error(self):
        """Test if the job resumption fails if save_interim_results is set to
        False in the actinia.cfg
        """
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/{self.endpoint}",
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json",
        )
        self.assertEqual(rv2.status_code, 404)
        resp_data = json_loads(rv2.data)
        self.assertEqual(resp_data["status"], "error")
        self.assertEqual(
            resp_data["message"],
            "Interim results are not set in the configuration",
        )


class JobResumptionProcessingTestCaseOnError(JobResumptionProcessingTestCase):
    save_interim_results = "onError"


class JobResumptionProcessingExportTestCaseOnError(
    JobResumptionProcessingExportTestCase
):
    save_interim_results = "onError"


class JobResumptionPersistentProcessingTestCaseOnError(
    JobResumptionPersistentProcessingTestCase
):
    save_interim_results = "onError"


if __name__ == "__main__":
    unittest.main()
