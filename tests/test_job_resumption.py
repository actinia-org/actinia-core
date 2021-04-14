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
Tests: Async process2 test case
"""
import os
import unittest
from flask.json import dumps as json_dumps
from flask.json import loads as json_loads
from jinja2 import Template
from time import sleep
from actinia_core.resources.common import redis_interface
from actinia_core.resources.common.process_queue import create_process_queue

from actinia_core.resources.common.config import global_config

try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2021, mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


process_chain_1 = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster",
                 "value": "elevation@PERMANENT"}
            ],
            "flags": "p"
        },
        {
            "id": "2",
            "module": "r.mapcalc",
            "inputs": [{"param": "expression",
                        "value": "baum = 5"}]
        },
        {
            "id": "3",
            "module": "r.info",
            "inputs": [{"param": "map",
                        "value": "{{ map1 }}"}]
        },
        {
            "id": "4",
            "module": "g.list",
            "inputs": [{"param": "type",
                        "value": "raster"}]
        },
        {
            "id": "5",
            "module": "r.info",
            "inputs": [{"param": "map",
                        "value": "{{ map2 }}"}]
        }
    ]
}

process_chain_2_error = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster",
                 "value": "elevation@PERMANENT"}
            ],
            "flags": "p"
        },
        {
            "id": "2",
            "exe": "sleep",
            "params": ["{{ seconds }}"]
        },
        {
            "id": "3",
            "module": "r.info",
            "inputs": [{"param": "map",
                        "value": "elevation2@PERMANENT"}]
        }
    ]
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
                    "source": "https://storage.googleapis.com/graas-"
                              "geodata/elev_ned_30m.tif",
                    "type": "raster"
                },
                "param": "raster",
                "value": "elev_ned_30m_new"
              }
            ],
            "flags": "p"
        },
        {
            "id": "2",
            "module": "r.mapcalc",
            "inputs": [{"param": "expression",
                        "value": "baum = 5"}]
        },
        {
            "id": "3",
            "module": "r.info",
            "inputs": [{"param": "map",
                        "value": "{{ map1 }}"}]
        },
        {
            "id": "4",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "https://raw.githubusercontent.com/mmacata/"
                                  "pagestest/gh-pages/pointInBonn.geojson",
                        "type": "vector"
                    },
                    "param": "map",
                    "value": "point"
                },
                {
                    "import_descr": {
                        "source": "https://storage.googleapis.com/graas-"
                                  "geodata/geology_30m.tif",
                        "type": "raster"
                    },
                    "param": "map",
                    "value": "geology_30m_new"
                 }
            ]
        },
        {
            "id": "5",
            "module": "r.info",
            "inputs": [{"param": "map",
                        "value": "{{ map2 }}"}]
        },
        {
            "id": "6",
            "module": "g.list",
            "inputs": [{"param": "type",
                        "value": "raster"}]
        },
        {
            "id": "7",
            "module": "v.info",
            "inputs": [{"param": "map",
                        "value": "point"}]
        },
        {
            "id": "8",
            "module": "r.info",
            "inputs": [{"param": "map",
                        "value": "geology_30m_new"}]
        }
    ]
}


process_chain_4_exporter = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster",
                 "value": "elevation@PERMANENT"}
            ],
            "flags": "p"
        },
        {
            "id": "2",
            "module": "r.colors.out_sld",
            "inputs": [
                {
                    "param": "map",
                    "value": "elevation@PERMANENT"
                }
            ],
            "outputs":  [
                {
                    "param": "output",
                    "value": "$file::export_of_2",
                    "export": {"type": "file", "format": "TXT"}
                }
            ]
        },
        {
            "id": "3",
            "module": "r.mapcalc",
            "inputs": [{"param": "expression",
                        "value": "baum = 5*elevation"}]
        },
        {
            "id": "4",
            "module": "r.info",
            "inputs": [{"param": "map",
                        "value": "{{ map1 }}"}]
        },
        {
            "id": "5",
            "module": "g.list",
            "inputs": [{"param": "type",
                        "value": "raster"}]
        },
        {
            "id": "6",
            "module": "r.info",
            "inputs": [{"param": "map",
                        "value": "{{ map2 }}"}]
        },
        {
            "id": "7",
            "module": "exporter",
            "comment": "Export indices as COG",
            "outputs": [
                {
                    "export": {
                        "type": "raster",
                        "format": "COG"
                    },
                    "param": "map",
                    "value": "baum"
                },
                {
                    "export": {
                        "type": "raster",
                        "format": "COG"
                    },
                    "param": "map",
                    "value": "elevation@PERMANENT"
                }
            ]
        }
    ]
}

process_chain_5_stdout = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster",
                 "value": "elevation@PERMANENT"}
            ],
            "flags": "p"
        },
        {
            "id": "2",
            "module": "r.colors.out_sld",
            "inputs": [
                {
                    "param": "map",
                    "value": "elevation@PERMANENT"
                },
                {
                    "param": "style_name",
                    "value": "elevation"
                }
            ],
            "stdout": {"id": "sld", "format": "list", "delimiter": "\n"}
        },
        {
            "id": "3",
            "module": "r.mapcalc",
            "inputs": [{"param": "expression",
                        "value": "baum = 5"}]
        },
        {
            "id": "4",
            "module": "r.info",
            "inputs": [{"param": "map",
                        "value": "{{ map1 }}"}],
            "flags": "g",
            "stdout": {"id": "r_info_map1", "format": "kv", "delimiter": "="}
        },
        {
            "id": "5",
            "module": "g.list",
            "inputs": [{"param": "type",
                        "value": "raster"}]
        },
        {
            "id": "6",
            "module": "r.info",
            "inputs": [{"param": "map",
                        "value": "{{ map2 }}"}],
            "flags": "g",
            "stdout": {"id": "r_info_map2", "format": "kv", "delimiter": "="}
        }
    ]
}


class JobResumptionProcessingTestCase(ActiniaResourceTestCaseBase):

    endpoint = '/locations/nc_spm_08/processing_async'
    resource_user_id = None
    resource_resource_id = None
    sleep_time = 15

    @classmethod
    def setUpClass(cls):

        global_config.SAVE_INTERIM_RESULTS = True

        # Start the redis interface
        redis_args = (global_config.REDIS_SERVER_URL, global_config.REDIS_SERVER_PORT)
        if global_config.REDIS_SERVER_PW and global_config.REDIS_SERVER_PW is not None:
            redis_args = (*redis_args, global_config.REDIS_SERVER_PW)

        redis_interface.connect(*redis_args)

        # Process queue
        create_process_queue(config=global_config)

        # We create 4 user for all roles: guest, user, admin, root
        accessible_datasets = {"nc_spm_08": ["PERMANENT",
                                             "user1",
                                             "landsat",
                                             "modis_lst",
                                             "test_mapset"],
                               "ECAD": ["PERMANENT"],
                               "latlong_wgs84": ["PERMANENT"]}

        # Create users
        cls.guest_id, cls.guest_group, cls.guest_auth_header = cls.create_user(
            name="guest", role="guest", process_num_limit=3, process_time_limit=2,
            accessible_datasets=accessible_datasets)
        cls.user_id, cls.user_group, cls.user_auth_header = cls.create_user(
            name="user", role="user", process_num_limit=3, process_time_limit=4,
            accessible_datasets=accessible_datasets)
        cls.admin_id, cls.admin_group, cls.admin_auth_header = cls.create_user(
            name="admin", role="admin", accessible_datasets=accessible_datasets)
        cls.root_id, cls.root_group, cls.root_auth_header = cls.create_user(
            name="superadmin", role="superadmin",
            accessible_datasets=accessible_datasets)

    def test_saved_interim_results(self):
        """Test if the interim results are saved correctly
        """
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json")
        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=200, status="finished")

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id, "interim", rv_resource_id)
        self.assertTrue(os.path.isdir(interim_dir),
                        "Interim results are not stored in the expected folder")
        self.assertTrue(
            os.path.isdir(os.path.join(interim_dir, 'step5')),
            "Interim results mapset is not stored in the expected folder")
        self.assertIn(
            'baum', os.listdir(os.path.join(interim_dir, 'step5', 'cellhd')),
            "Raster map 'baum' not in interim results mapset")
        self.assertTrue(
            os.path.isdir(os.path.join(interim_dir, 'tmpdir5')),
            "Interim results temporary file path is not stored in the expected folder")

    def test_job_resumption(self):
        """Test job resumption with processing_async endpoint
        """
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id, "interim", rv_resource_id)
        self.assertTrue(os.path.isdir(interim_dir),
                        "Interim results are not stored in the expected folder")

        # resumption of the job
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json")
        self.waitAsyncStatusAssertHTTP(
            rv2, headers=self.admin_auth_header, http_status=200, status="finished")

    def test_job_2_times_resumption(self):
        """Test job 2 times resumption with processing_async endpoint
        """
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # first job resumption
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum1"),
            content_type="application/json")
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp2["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv2.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id, "interim", rv_resource_id)
        self.assertTrue(os.path.isdir(interim_dir),
                        "Interim results are not stored in the expected folder")

        # second job resumption
        rv3 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json")
        self.waitAsyncStatusAssertHTTP(
            rv3, headers=self.admin_auth_header, http_status=200, status="finished")
        self.__class__.resource_user_id = rv_user_id
        self.__class__.resource_resource_id = rv_resource_id

    def test_job_resumption_error_by_running(self):
        """Test job resumption error by running process with processing_async
        endpoint
        """
        tpl = Template(json_dumps(process_chain_2_error))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(seconds=self.sleep_time),
            content_type="application/json")
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        waiting_for_running = True
        while waiting_for_running:
            rv_pull = self.server.get(URL_PREFIX + "/resources/%s/%s"
                                      % (rv_user_id, rv_resource_id),
                                      headers=self.admin_auth_header)
            resp_data_pull = json_loads(rv_pull.data)
            if resp_data_pull["status"] == "running":
                waiting_for_running = False
            elif resp_data_pull["status"] in ["error", "terminated", "timeout"]:
                self.assertTrue(False, "Process is not running it is %s"
                                       % resp_data_pull["status"])
        status_url = resp_data_pull["urls"]["status"].split(URL_PREFIX)[-1]

        # job resumption by running job
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_2_error),
            content_type="application/json")
        self.assertEqual(rv2.status_code, 404)
        resp_data2 = json_loads(rv2.data)
        self.assertEqual(resp_data2['status'], 'error')
        self.assertEqual(
            resp_data2['message'], 'Resource is running no restart possible')

    def test_job_resumption_importer(self):
        """Test job resumption with processing_async endpoint and importer
        """
        tpl = Template(json_dumps(process_chain_3_importer))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id, "interim", rv_resource_id)
        self.assertTrue(os.path.isdir(interim_dir),
                        "Interim results are not stored in the expected folder")

        # resumption of the job
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elev_ned_30m_new", map2="baum"),
            content_type="application/json")
        self.waitAsyncStatusAssertHTTP(
            rv2, headers=self.admin_auth_header, http_status=200, status="finished")

    def test_job_2_times_resumption_importer(self):
        """Test job 2 times resumption with processing_async endpoint and
        importer
        """
        tpl = Template(json_dumps(process_chain_3_importer))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # first job resumption
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elev_ned_30m_new", map2="baum1"),
            content_type="application/json")
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp2["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv2.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id, "interim", rv_resource_id)
        self.assertTrue(os.path.isdir(interim_dir),
                        "Interim results are not stored in the expected folder")

        # second job resumption
        rv3 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elev_ned_30m_new", map2="baum"),
            content_type="application/json")
        self.waitAsyncStatusAssertHTTP(
            rv3, headers=self.admin_auth_header, http_status=200, status="finished")
        self.__class__.resource_user_id = rv_user_id
        self.__class__.resource_resource_id = rv_resource_id

    def compare_stdout(self, resp):
        proc_results = resp['process_results']
        self.assertIn('sld', proc_results, "'sld' not saved in process results")
        self.assertIn('r_info_map1', proc_results,
                      "'r_info_map1' not saved in process results")
        self.assertIn('r_info_map2', proc_results,
                      "'r_info_map2' not saved in process results")
        self.assertIsInstance(proc_results['sld'], list,
                              "'sld' result is not of type list")
        self.assertIsInstance(
            proc_results['r_info_map1'], dict,
            "'r_info_map1' result is not of type dict")
        self.assertIsInstance(
            proc_results['r_info_map2'], dict,
            "'r_info_map2' result is not of type dict")
        r_info_map1 = {
            'cells': '2025000', 'cols': '1500', 'datatype': 'FCELL',
            'east': '645000', 'ewres': '10', 'ncats': '255', 'north': '228500',
            'nsres': '10', 'rows': '1350', 'south': '215000', 'west': '630000'}
        self.assertEqual(
            proc_results['r_info_map1'], r_info_map1,
            "'r_info_map1' is not equal to the region")
        r_info_map2 = {
            'cells': '2025000', 'cols': '1500', 'datatype': 'CELL',
            'east': '645000', 'ewres': '10', 'ncats': '0', 'north': '228500',
            'nsres': '10', 'rows': '1350', 'south': '215000', 'west': '630000'}
        self.assertEqual(
            proc_results['r_info_map2'], r_info_map2,
            "'r_info_map2' is not equal to the region")

    def test_job_resumption_stdout(self):
        """Test job resumption with processing_async endpoint and stdout
        """
        tpl = Template(json_dumps(process_chain_5_stdout))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id, "interim", rv_resource_id)
        self.assertTrue(os.path.isdir(interim_dir),
                        "Interim results are not stored in the expected folder")

        # resumption of the job
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json")
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2, headers=self.admin_auth_header, http_status=200, status="finished")
        self.compare_stdout(resp2)

    def test_job_2_times_resumption_stdout(self):
        """Test job 2 times resumption with processing_async endpoint and
        stdout
        """
        tpl = Template(json_dumps(process_chain_5_stdout))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # first job resumption
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum1"),
            content_type="application/json")
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp2["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv2.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id, "interim", rv_resource_id)
        self.assertTrue(os.path.isdir(interim_dir),
                        "Interim results are not stored in the expected folder")

        # second job resumption
        rv3 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json")
        resp3 = self.waitAsyncStatusAssertHTTP(
            rv3, headers=self.admin_auth_header, http_status=200, status="finished")
        self.compare_stdout(resp3)

    def test_resource_endpoints(self):
        """Test resource endpoint with iterations
        """
        self.assertIsNotNone(self.resource_user_id, "resource_user_id is None")
        self.assertIsNotNone(self.resource_resource_id, "resource_resource_id is None")

        # get latest iteration by requesting /resources/{USER}/resource_id-{ID}
        rv1 = self.server.get(
            URL_PREFIX + "/resources/%s/%s"
            % (self.resource_user_id, self.resource_resource_id),
            headers=self.admin_auth_header)
        resp_data1 = json_loads(rv1.data)
        self.assertEqual(resp_data1["status"], "finished",
                         "Resource request 1 is not finished")
        self.assertEqual(rv1.status_code, 200,
                         "Resource request 1 status code is not 200")
        self.assertEqual(resp_data1['iteration'], 3, "Iteration is not 3 (the latest)")

        # get all iteration by requesting /resources/{USER}/{ID}
        rv2 = self.server.get(
            URL_PREFIX + "/resources/%s/%s"
            % (self.resource_user_id,
               self.resource_resource_id.replace('resource_id-', '')),
            headers=self.admin_auth_header)
        resp_data2 = json_loads(rv2.data)
        self.assertEqual(rv2.status_code, 200,
                         "Resource request 2 status code is not 200")
        self.assertEqual(len(resp_data2.keys()), 3, "Not 3 iteration in request")

        # get resource by iteration number requesting /resources/{USER}/{ID}/{ITERATION}
        for iteration in range(1, 4):
            rv3 = self.server.get(
                URL_PREFIX + "/resources/%s/%s/%d"
                % (self.resource_user_id,
                   self.resource_resource_id, iteration),
                headers=self.admin_auth_header)
            resp_data3 = json_loads(rv3.data)
            self.assertEqual(
                rv3.status_code, 200,
                "Resource request for iteration %d status code is not 200" % iteration)
            if iteration != 1:
                self.assertIn(
                    'iteration', resp_data3[str(iteration)],
                    "'iteration' is not in response")
                self.assertEqual(
                    resp_data3[str(iteration)]['iteration'], iteration,
                    "Iteration is not %d" % iteration)
            else:
                self.assertNotIn('iteration', resp_data3[str(iteration)],
                                 "'iteration' is in response")
            del rv3, resp_data3


class JobResumptionProcessingExportTestCase(JobResumptionProcessingTestCase):

    endpoint = '/locations/nc_spm_08/processing_async_export'
    resource_user_id = None
    resource_resource_id = None

    def test_job_resumption_exporter(self):
        """Test job resumption with processing_async_export endpoint and exporter
        """
        tpl = Template(json_dumps(process_chain_4_exporter))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id, "interim", rv_resource_id)
        self.assertTrue(os.path.isdir(interim_dir),
                        "Interim results are not stored in the expected folder")

        # resumption of the job
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json")
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2, headers=self.admin_auth_header, http_status=200, status="finished")

        # Get the exported results
        urls = resp2["urls"]["resources"]
        for url in urls:
            print(url)
            rv = self.server.get(url, headers=self.admin_auth_header)
            self.assertEqual(
                rv.status_code, 200, "HTML status code is wrong %i" % rv.status_code)
            if url.endswith('.tif'):
                self.assertEqual(
                    rv.mimetype, "image/tiff", "Wrong mimetype %s" % rv.mimetype)
            elif url.endswith('.zip'):
                self.assertEqual(
                    rv.mimetype, "application/zip", "Wrong mimetype %s" % rv.mimetype)

    def test_job_2_times_resumption_exporter(self):
        """Test job 2 times resumption with processing_async_export endpoint and
        exporter
        """
        tpl = Template(json_dumps(process_chain_4_exporter))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation2@PERMANENT", map2="baum"),
            content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]

        # first job resumption
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum1"),
            content_type="application/json")
        resp2 = self.waitAsyncStatusAssertHTTP(
            rv2, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp2["urls"]["status"].split(URL_PREFIX)[-1]

        # check if interim results are saved
        resp_data = json_loads(rv2.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id, "interim", rv_resource_id)
        self.assertTrue(os.path.isdir(interim_dir),
                        "Interim results are not stored in the expected folder")

        # second job resumption
        rv3 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json")
        resp3 = self.waitAsyncStatusAssertHTTP(
            rv3, headers=self.admin_auth_header, http_status=200, status="finished")

        # Get the exported results
        urls = resp3["urls"]["resources"]
        for url in urls:
            print(url)
            rv = self.server.get(url, headers=self.admin_auth_header)
            self.assertEqual(
                rv.status_code, 200, "HTML status code is wrong %i" % rv.status_code)
            if url.endswith('.tif'):
                self.assertEqual(
                    rv.mimetype, "image/tiff", "Wrong mimetype %s" % rv.mimetype)
            elif url.endswith('.zip'):
                self.assertEqual(
                    rv.mimetype, "application/zip", "Wrong mimetype %s" % rv.mimetype)
        self.__class__.resource_user_id = rv_user_id
        self.__class__.resource_resource_id = rv_resource_id


class JobResumptionPersistentProcessingTestCase(JobResumptionProcessingTestCase):

    location = 'nc_spm_08'
    mapset = 'test_mapset'
    endpoint = '/locations/%s/mapsets/%s/processing_async' % (location, mapset)
    resource_user_id = None
    resource_resource_id = None
    mapset_created = True

    def tearDown(self):
        if self.mapset_created is True:
            rv = self.server.delete(
                URL_PREFIX + '/locations/%s/mapsets/%s/lock'
                             % (self.location, self.mapset),
                headers=self.admin_auth_header)
            self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header)
            rv2 = self.server.delete(
                URL_PREFIX + '/locations/%s/mapsets/%s' % (self.location, self.mapset),
                headers=self.admin_auth_header)
            self.waitAsyncStatusAssertHTTP(rv2, headers=self.admin_auth_header)
        else:
            self.__class__.mapset_created = True
        self.app_context.pop()

    def test_saved_interim_results(self):
        """Test if the interim results are removed
        """
        self.create_new_mapset(self.mapset, self.location)
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map1="elevation@PERMANENT", map2="baum"),
            content_type="application/json")
        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=200, status="finished")

        # check if interim results are saved
        resp_data = json_loads(rv.data)
        rv_user_id = resp_data["user_id"]
        rv_resource_id = resp_data["resource_id"]
        interim_dir = os.path.join(
            global_config.GRASS_RESOURCE_DIR,
            rv_user_id, "interim", rv_resource_id)
        self.assertTrue(not os.path.isdir(interim_dir),
                        "Interim results are not stored in the expected folder")

    def test_job_resumption_error_by_running(self):
        super(JobResumptionPersistentProcessingTestCase, self).\
            test_job_resumption_error_by_running()
        sleep(self.sleep_time)
        self.__class__.mapset_created = False

    def test_resource_endpoints(self):
        super(JobResumptionPersistentProcessingTestCase, self).test_resource_endpoints()
        self.__class__.mapset_created = False


class JobResumptionErrorTestCase(ActiniaResourceTestCaseBase):

    endpoint = '/locations/nc_spm_08/processing_async'

    def test_job_resumption_config_error(self):
        """Test if the job resumption fails if save_interim_results is set to
        False in the actinia.cfg
        """
        tpl = Template(json_dumps(process_chain_1))
        rv = self.server.post(
            URL_PREFIX + self.endpoint,
            headers=self.admin_auth_header,
            data=tpl.render(map="elevation2@PERMANENT"),
            content_type="application/json")
        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error")
        status_url = resp["urls"]["status"].split(URL_PREFIX)[-1]
        rv2 = self.server.put(
            URL_PREFIX + status_url,
            headers=self.admin_auth_header,
            data=tpl.render(map="elevation@PERMANENT"),
            content_type="application/json")
        self.assertEqual(rv2.status_code, 404)
        resp_data = json_loads(rv2.data)
        self.assertEqual(resp_data['status'], 'error')
        self.assertEqual(
            resp_data['message'],
            'Interim results are not set in the configureation')


if __name__ == '__main__':
    unittest.main()
