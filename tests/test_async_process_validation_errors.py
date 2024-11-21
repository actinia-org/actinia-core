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
Tests: Async process validation test case
"""
import unittest
from flask.json import dumps as json_dumps, loads as json_loads
from pprint import pprint

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

# param wrong
process_chain_error_1 = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"paramp": "raster", "value": "elevation@PERMANENT"},
                {"param": "res", "value": "10000"},
            ],
            "flags": "p",
            "verbose": True,
        }
    ],
}

# value wrong
process_chain_error_2 = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster", "values": "elevation@PERMANENT"},
                {"param": "res", "value": "10000"},
            ],
            "flags": "p",
            "verbose": True,
        }
    ],
}

# module wrong
process_chain_error_3 = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "modules": "g.region",
            "inputs": [
                {"param": "raster", "value": "elevation@PERMANENT"},
                {"param": "res", "value": "10000"},
            ],
            "flags": "p",
            "verbose": True,
        }
    ],
}

# Id wrong
process_chain_error_4 = {
    "version": 1,
    "list": [
        {
            "ids": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster", "value": "elevation@PERMANENT"},
                {"param": "res", "value": "10000"},
            ],
            "flags": "p",
            "verbose": True,
        }
    ],
}

# Wrong mapset
process_chain_error_5 = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster", "value": "elevation@PERMAFROST"},
                {"param": "res", "value": "10000"},
            ],
            "flags": "p",
            "verbose": True,
        }
    ],
}

# param missing on output
process_chain_output_error_1 = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster", "value": "elevation@PERMANENT"},
                {"param": "res", "value": "10000"},
            ],
            "flags": "p",
            "verbose": True,
        },
        {
            "id": "2",
            "module": "r.out.ascii",
            "inputs": [{"param": "input", "value": "elevation@PERMANENT"}],
            "outputs": [{"params": "output", "value": "$file::out1"}],
        },
    ],
}

# value missing on output
process_chain_output_error_2 = {
    "version": 1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster", "value": "elevation@PERMANENT"},
                {"param": "res", "value": "10000"},
            ],
            "flags": "p",
            "verbose": True,
        },
        {
            "id": "2",
            "module": "r.out.ascii",
            "inputs": [{"param": "input", "value": "elevation@PERMANENT"}],
            "outputs": [{"param": "output", "values": "$file::out1"}],
        },
    ],
}

# Wrong Landsat scene id
process_chain_landsat_error_1 = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "LT52170762005240COA00-NOT",
                        "type": "landsat",
                        "landsat_atcor": "dos1",
                    },
                    "param": "map",
                    "value": "ignored",
                }
            ],
        }
    ],
    "version": "1",
}

# Wrong type
process_chain_landsat_error_2 = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "LT52170762005240COA00",
                        "type": "landsatpo",
                        "landsat_atcor": "dos1",
                    },
                    "param": "map",
                    "value": "ignored",
                }
            ],
        }
    ],
    "version": "1",
}

# Wrong Landsat atcor type
process_chain_landsat_error_3 = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "LT52170762005240COA00",
                        "type": "landsat",
                        "landsat_atcor": "ddos1",
                    },
                    "param": "map",
                    "value": "ignored",
                }
            ],
        }
    ],
    "version": "1",
}

# Missing sentinel_band
process_chain_sent_1 = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "S2B_MSIL1C_20171010T131249_N0205_R081_"
                        "T26VPR_20171010T131243",
                        "type": "sentinel2",
                    },
                    "param": "map",
                    "value": "B04",
                }
            ],
        }
    ],
    "version": "1",
}

# Missing type
process_chain_sent_2 = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "S2B_MSIL1C_20171010T131249_N0205_R081_"
                        "T26VPR_20171010T131243",
                        "sentinel_band": "B04",
                    },
                    "param": "map",
                    "value": "B04",
                }
            ],
        }
    ],
    "version": "1",
}


# Wrong webhook URL
process_chain_error_webhook_finished = {
    "version": 1,
    "webhooks": {
        "finished": "http://0.0.0.0:5005/webhook/finished_not",
        "update": "http://0.0.0.0:5005/webhook/update",
    },
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster", "value": "elevation@PERMANENT"},
                {"param": "res", "value": "10000"},
            ],
            "flags": "p",
            "verbose": True,
        }
    ],
}


process_chain_error_webhook_update = {
    "version": 1,
    "webhooks": {
        "finished": "http://0.0.0.0:5005/webhook/finished",
        "update": "http://0.0.0.0:5005/webhook/update_not",
    },
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster", "value": "elevation@PERMANENT"},
                {"param": "res", "value": "10000"},
            ],
            "flags": "p",
            "verbose": True,
        }
    ],
}


class AsyncProcessValidationTestCase(ActiniaResourceTestCaseBase):
    def test_async_processing_error_webhook_finished(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_error_webhook_finished),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_error_webhook_update(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_error_webhook_update),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_error_1(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_error_1),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_error_2(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_error_2),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_error_3(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_error_3),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_error_4(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_error_4),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_error_5(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_error_5),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_output_error_1(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_output_error_1),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_output_error_2(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_output_error_2),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_landsat_error_1(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_landsat_error_1),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_landsat_error_2(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_landsat_error_2),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_landsat_error_3(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_landsat_error_3),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_sent_error_1(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_sent_1),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )

    def test_async_processing_sent_error_2(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "process_chain_validation_sync",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_sent_2),
            content_type="application/json",
        )

        pprint(json_loads(rv.data))
        self.assertEqual(
            rv.status_code,
            400,
            "HTML status code is wrong %i" % rv.status_code,
        )
        self.assertEqual(
            rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype
        )


if __name__ == "__main__":
    unittest.main()
