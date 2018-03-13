# -*- coding: utf-8 -*-
import unittest
from test_resource_base import ActiniaResourceTestCaseBase
from flask.json import dumps as json_dumps

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

# param wrong
process_chain_error_1 = {
    "version":1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"paramp": "raster",
                 "value": "elevation@PERMANENT"},
                {"param":"res",
                 "value": "10000"}
            ],
            "flags": "p",
            "verbose": True
        }
    ]
}

# value wrong
process_chain_error_2 = {
    "version":1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster",
                 "values": "elevation@PERMANENT"},
                {"param":"res",
                 "value": "10000"}
            ],
            "flags": "p",
            "verbose": True
        }
    ]
}

# module wrong
process_chain_error_3 = {
    "version":1,
    "list": [
        {
            "id": "1",
            "modules": "g.region",
            "inputs": [
                {"param": "raster",
                 "value": "elevation@PERMANENT"},
                {"param":"res",
                 "value": "10000"}
            ],
            "flags": "p",
            "verbose": True
        }
    ]
}

# Id wrong
process_chain_error_4 = {
    "version":1,
    "list": [
        {
            "ids": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster",
                 "value": "elevation@PERMANENT"},
                {"param":"res",
                 "value": "10000"}
            ],
            "flags": "p",
            "verbose": True
        }
    ]
}

# Wrong mapset
process_chain_error_5 = {
    "version":1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster",
                 "value": "elevation@PERMAFROST"},
                {"param":"res",
                 "value": "10000"}
            ],
            "flags": "p",
            "verbose": True
        }
    ]
}

# param missing on output
process_chain_output_error_1 = {
    "version":1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster",
                 "value": "elevation@PERMANENT"},
                {"param":"res",
                 "value": "10000"}
            ],
            "flags": "p",
            "verbose": True
        },
        {
            "id": "2",
            "module": "r.out.ascii",
            "inputs": [{"param":"input",
                        "value": "elevation@PERMANENT"}],
            "outputs": [
                {"params":"output",
                 "value": "$file::out1"}
            ]
        }
    ]
}

# value missing on output
process_chain_output_error_2 = {
    "version":1,
    "list": [
        {
            "id": "1",
            "module": "g.region",
            "inputs": [
                {"param": "raster",
                 "value": "elevation@PERMANENT"},
                {"param":"res",
                 "value": "10000"}
            ],
            "flags": "p",
            "verbose": True
        },
        {
            "id": "2",
            "module": "r.out.ascii",
            "inputs": [{"param":"input",
                        "value": "elevation@PERMANENT"}],
            "outputs": [
                {"param":"output",
                 "values": "$file::out1"}
            ]
        }
    ]
}

# Wrong Landsat scene id
process_chain_landsat_error_1 = {
    "list": [
        {"id": "importer_1",
         "module": "importer",
         "inputs": [{"import_descr": {"source": "LT52170762005240COA00-NOT",
                                       "type": "landsat",
                                       "landsat_atcor": "dos1"},
                     "param": "map",
                     "value": "ignored"}
                    ]
         }],
    "version": "1"
}

# Wrong type
process_chain_landsat_error_2 = {
    "list": [
        {"id": "importer_1",
         "module": "importer",
         "inputs": [{"import_descr": {"source": "LT52170762005240COA00",
                                       "type": "landsatpo",
                                       "landsat_atcor": "dos1"},
                     "param": "map",
                     "value": "ignored"}
                    ]
         }],
    "version": "1"
}

# Wrong Landsat atcor type
process_chain_landsat_error_3 = {
    "list": [
        {"id": "importer_1",
         "module": "importer",
         "inputs": [{"import_descr": {"source": "LT52170762005240COA00",
                                       "type": "landsat",
                                       "landsat_atcor": "ddos1"},
                     "param": "map",
                     "value": "ignored"}
                    ]
         }],
    "version": "1"
}

# Missing sentinel_band
process_chain_sent_1 = {
    "list": [
        {"id": "importer_1",
         "module": "importer",
         "inputs": [{"import_descr": {"source": "S2B_MSIL1C_20171010T131249_N0205_R081_T26VPR_20171010T131243",
                                      "type": "sentinel2"},
                     "param": "map",
                     "value": "B04"}]}
         ],
    "version": "1"
}

# Missing type
process_chain_sent_2 = {
    "list": [
        {"id": "importer_1",
         "module": "importer",
         "inputs": [{"import_descr": {"source": "S2B_MSIL1C_20171010T131249_N0205_R081_T26VPR_20171010T131243",
                                      "sentinel_band": "B04"},
                     "param": "map",
                     "value": "B04"}]}
         ],
    "version": "1"
}


class AsyncProcessValidationTestCase(ActiniaResourceTestCaseBase):

    def test_async_processing_error_1(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_error_1),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_error_2(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_error_2),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_error_3(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_error_3),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_error_4(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_error_4),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_error_5(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_error_5),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_output_error_1(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_output_error_1),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_output_error_2(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_output_error_2),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_landsat_error_1(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_landsat_error_1),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_landsat_error_2(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_landsat_error_2),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_landsat_error_3(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_landsat_error_3),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_sent_error_1(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_sent_1),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)

    def test_async_processing_sent_error_2(self):
        rv = self.server.post('/locations/nc_spm_08/process_chain_validation_sync',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_sent_2),
                              content_type="application/json")

        print(rv.data)
        self.assertEqual(rv.status_code, 400, "HTML status code is wrong %i"%rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s"%rv.mimetype)


if __name__ == '__main__':
    unittest.main()
