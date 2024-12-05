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
Tests: Async Process test case
"""
import os
import unittest
from flask.json import dumps as json_dumps

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

try:
    import actinia_stac_plugin

    if actinia_stac_plugin:
        no_stac_plugin = False
except Exception:
    no_stac_plugin = True

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Julia Haas, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

process_chain_raster_import_export = {
    "list": [
        {
            "flags": "a",
            "id": "r_slope_aspect_1",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data["elev_ned_30m_tif"],
                        "type": "raster",
                    },
                    "param": "elevation",
                    "value": "elev_ned_30m",
                },
                {"param": "format", "value": "degree"},
                {"param": "precision", "value": "DCELL"},
            ],
            "module": "r.slope.aspect",
            "outputs": [
                {
                    "export": {"format": "GTiff", "type": "raster"},
                    "param": "slope",
                    "value": "elev_ned_30m_slope",
                },
                {
                    "export": {"format": "GTiff", "type": "raster"},
                    "param": "aspect",
                    "value": "elev_ned_30m_aspect",
                },
            ],
            "overwrite": False,
            "verbose": False,
        },
        {
            "exe": "/bin/cat",
            "id": "cat_1",
            "params": [],
            "stdin": "r_slope_aspect_1::stderr",
        },
    ],
    "version": "1",
}

process_chain_raster_import_info = {
    "list": [
        {
            "id": "r_info",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data["elev_ned_30m_tif"],
                        "type": "raster",
                    },
                    "param": "map",
                    "value": "elev_ned_30m",
                }
            ],
            "module": "r.info",
            "flags": "g",
        }
    ],
    "version": "1",
}

process_chain_raster_import_error_no_file = {
    "list": [
        {
            "id": "r_info",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data[
                            "elev_ned_30m_nope_tif"
                        ],
                        "type": "raster",
                    },
                    "param": "map",
                    "value": "elev_ned_30m",
                },
            ],
            "module": "r.info",
            "flags": "g",
        }
    ],
    "version": "1",
}

process_chain_vector_import_info = {
    "list": [
        {
            "id": "v_info",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data["polygon_gml"],
                        "type": "vector",
                    },
                    "param": "map",
                    "value": "polygon",
                }
            ],
            "module": "v.info",
            "flags": "g",
        }
    ],
    "version": "1",
}

process_chain_sentinel_import_info = {
    "list": [
        {
            "id": "r_info",
            "inputs": [
                {
                    "import_descr": {
                        "source": "S2A_MSIL1C_20170212T104141_N0204_R008_"
                        "T31TGJ_20170212T104138",
                        "type": "sentinel2",
                        "sentinel_band": "B01",
                    },
                    "param": "map",
                    "value": "sentinel_map",
                }
            ],
            "module": "r.info",
            "flags": "g",
        }
    ],
    "version": "1",
}

process_chain_sentinel_import_univar = {
    "list": [
        {
            "id": "r_univar",
            "inputs": [
                {
                    "import_descr": {
                        "source": "S2A_MSIL1C_20170212T104141_N0204_R008_"
                        "T31TGJ_20170212T104138",
                        "type": "sentinel2",
                        "sentinel_band": "B01",
                    },
                    "param": "map",
                    "value": "sentinel_map",
                }
            ],
            "module": "r.univar",
            "flags": "g",
        }
    ],
    "version": "1",
}

process_chain_sentinel_import_stats = {
    "list": [
        {
            "id": "r_stats",
            "inputs": [
                {
                    "import_descr": {
                        "source": "S2A_MSIL1C_20170212T104141_N0204_R008_"
                        "T31TGJ_20170212T104138",
                        "type": "sentinel2",
                        "sentinel_band": "B01",
                    },
                    "param": "input",
                    "value": "sentinel_map",
                }
            ],
            "module": "r.stats",
            "flags": "a",
        }
    ],
    "version": "1",
}

process_chain_sentinel_import_error = {
    "list": [
        {
            "id": "r_stats",
            "inputs": [
                {
                    "import_descr": {
                        "source": "S2A_MSIL1C_20170212T104141_N0204_R008_"
                        "T31TGJ_20170212T104138_NOPE",
                        "type": "sentinel2",
                        "sentinel_band": "B01",
                    },
                    "param": "input",
                    "value": "sentinel_map",
                }
            ],
            "module": "r.info",
            "flags": "g",
        }
    ],
    "version": "1",
}

process_chain_sentinel_import_export = {
    "list": [
        {
            "id": "importer_1",
            "inputs": [
                {
                    "import_descr": {
                        "source": "S2A_MSIL1C_20170212T104141_N0204_R008_"
                        "T31TGJ_20170212T104138",
                        "type": "sentinel2",
                        "sentinel_band": "B01",
                    },
                    "param": "map",
                    "value": "sentinel_map",
                },
                {
                    "import_descr": {
                        "source": additional_external_data["elev_ned_30m_tif"],
                        "type": "raster",
                    },
                    "param": "map",
                    "value": "elev_ned_30m",
                },
            ],
            "outputs": [
                {
                    "export": {"type": "raster", "format": "GTiff"},
                    "param": "map",
                    "value": "sentinel_map",
                },
                {
                    "export": {"type": "raster", "format": "GTiff"},
                    "param": "map",
                    "value": "elev_ned_30m",
                },
            ],
            "module": "importer",
        }
    ],
    "version": "1",
}


process_chain_sentinel_import_export_sentinel_ndvi = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "S2A_MSIL1C_20170212T104141_N0204_R008_"
                        "T31TGJ_20170212T104138",
                        "type": "sentinel2",
                        "sentinel_band": "B04",
                    },
                    "param": "map",
                    "value": "B04",
                },
                {
                    "import_descr": {
                        "source": "S2A_MSIL1C_20170212T104141_N0204_R008_"
                        "T31TGJ_20170212T104138",
                        "type": "sentinel2",
                        "sentinel_band": "B08",
                    },
                    "param": "map",
                    "value": "B08",
                },
            ],
        },
        {
            "id": "rmapcalc_1",
            "module": "r.mapcalc",
            "inputs": [
                {
                    "param": "expression",
                    "value": "NDVI = (B08 - B04)/(B08 + B04)",
                }
            ],
        },
        {
            "id": "exporter_1",
            "module": "exporter",
            "outputs": [
                {
                    "export": {"type": "raster", "format": "GTiff"},
                    "param": "map",
                    "value": "NDVI",
                }
            ],
        },
    ],
    "version": "1",
}

process_chain_stac_import = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "stac.defaultStac.rastercube."
                        "landsat-8-l1-c1",
                        "type": "stac",
                        "semantic_label": "B1",
                        "extent": {
                            "spatial": {
                                "bbox": [[30.192, -16.369, 42.834, -0.264]]
                            },
                            "temporal": {
                                "interval": [["2021-09-09", "2021-09-12"]]
                            },
                        },
                        "filter": {},
                    },
                    "param": "map",
                    "value": "landsat-8-l1-c1",
                }
            ],
        }
    ],
    "version": 1,
}

process_chain_stac_filter_error_import = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "stac.STAC_Others.rastercube."
                        "sentinel-s2-l2a",
                        "type": "stac",
                        "semantic_label": "red",
                        "extent": {
                            "spatial": {"bbox": [[-180, -16.369, 90, -0.264]]},
                            "temporal": {
                                "interval": [["2023-09-09", "2022-09-12"]]
                            },
                        },
                        "filter": {},
                    },
                    "param": "map",
                    "value": "landsat-8-l1-c1",
                }
            ],
        }
    ],
    "version": 1,
}

process_chain_stac_source_error_import = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": "sentinel-s2-l2a",
                        "type": "stac",
                        "semantic_label": "red",
                        "extent": {
                            "spatial": {
                                "bbox": [[30.192, -16.369, 42.834, -0.264]]
                            },
                            "temporal": {
                                "interval": [["2021-09-09", "2021-09-12"]]
                            },
                        },
                        "filter": {},
                    },
                    "param": "map",
                    "value": "landsat-8-l1-c1",
                }
            ],
        }
    ],
    "version": 1,
}

process_chain_raster_import_resample_resolution = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data[
                            "elev_ned_30m_epsg4326_tif"
                        ],
                        "type": "raster",
                        "resample": "bilinear_f",
                        "resolution": "value",
                        "resolution_value": "100",
                    },
                    "param": "map",
                    "value": "elev_ned_100m",
                }
            ],
        }
    ],
    "version": 1,
}

process_chain_raster_import_resample_resolution_info = {
    "list": [
        {
            "id": "r_info",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data[
                            "elev_ned_30m_epsg4326_tif"
                        ],
                        "type": "raster",
                        "resample": "bilinear_f",
                        "resolution": "value",
                        "resolution_value": "100",
                    },
                    "param": "map",
                    "value": "elev_ned_100m",
                }
            ],
            "module": "r.info",
            "flags": "g",
            "stdout": {"id": "r_info", "format": "kv", "delimiter": "="},
        }
    ],
    "version": "1",
}

process_chain_raster_import_resample_resolution_error_resamp = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data[
                            "elev_ned_30m_epsg4326_tif"
                        ],
                        "type": "raster",
                        "resample": "bilinea",
                        "resolution": "value",
                        "resolution_value": "100",
                    },
                    "param": "map",
                    "value": "elev_ned_100m",
                }
            ],
        }
    ],
    "version": 1,
}

process_chain_raster_import_resample_resolution_error_resol = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data[
                            "elev_ned_30m_epsg4326_tif"
                        ],
                        "type": "raster",
                        "resample": "bilinear_f",
                        "resolution": "values",
                        "resolution_value": "100",
                    },
                    "param": "map",
                    "value": "elev_ned_100m",
                }
            ],
        }
    ],
    "version": 1,
}

pc_raster_import_resample_resolution_error_val_missing = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data[
                            "elev_ned_30m_epsg4326_tif"
                        ],
                        "type": "raster",
                        "resample": "bilinear_f",
                        "resolution": "value",
                    },
                    "param": "map",
                    "value": "elev_ned_100m",
                }
            ],
        }
    ],
    "version": 1,
}

pc_raster_import_resample_resolution_error_val_not_float = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data[
                            "elev_ned_30m_epsg4326_tif"
                        ],
                        "type": "raster",
                        "resample": "bilinear_f",
                        "resolution": "value",
                        "resolution_value": "not float",
                    },
                    "param": "map",
                    "value": "elev_ned_100m",
                }
            ],
        }
    ],
    "version": 1,
}

pc_raster_import_resample_resolution_error_resol_not_set = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data[
                            "elev_ned_30m_epsg4326_tif"
                        ],
                        "type": "raster",
                        "resample": "bilinear_f",
                        "resolution_value": "100",
                    },
                    "param": "map",
                    "value": "elev_ned_100m",
                }
            ],
        }
    ],
    "version": 1,
}

pc_raster_import_resample_resolution_error_resol_not_val = {
    "list": [
        {
            "id": "importer_1",
            "module": "importer",
            "inputs": [
                {
                    "import_descr": {
                        "source": additional_external_data[
                            "elev_ned_30m_epsg4326_tif"
                        ],
                        "type": "raster",
                        "resample": "bilinear_f",
                        "resolution": "estimated",
                        "resolution_value": "100",
                    },
                    "param": "map",
                    "value": "elev_ned_100m",
                }
            ],
        }
    ],
    "version": 1,
}


class AsyncProcessTestCase(ActiniaResourceTestCaseBase):
    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_raster_import_export_sentinel_ndvi(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(
                process_chain_sentinel_import_export_sentinel_ndvi
            ),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_raster_import_export(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_sentinel_import_export),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    def test_raster_import(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_raster_import_info),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    def test_raster_import_nofile(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_raster_import_error_no_file),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

    def test_import_export(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_raster_import_export),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    def test_vector_import(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_vector_import_info),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_sentinel_import_info(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_sentinel_import_info),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_sentinel_import_univar(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_sentinel_import_univar),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_sentinel_import_stats(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_sentinel_import_stats),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    @unittest.skipIf(
        "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
        and "GOOGLE_CLOUD_PROJECT" not in os.environ,
        "Test is skipped because 'GOOGLE_APPLICATION_CREDENTIALS' and "
        "'GOOGLE_CLOUD_PROJECT' not set",
    )
    def test_sentinel_import_error(self):
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_sentinel_import_error),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

    # Test for STAC
    @unittest.skipIf(no_stac_plugin, "STAC Plugin not installed")
    def test_stac_import(self):
        """
        Test of STAC collection import with http response 200
        """

        endpoint = (
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export"
        )
        rv = self.server.post(
            endpoint,
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_stac_import),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    @unittest.skipIf(no_stac_plugin, "STAC Plugin not installed")
    def test_stac_source_error_import(self):
        """
        Test of STAC collection import with http response 400,
        raising error on wrongly structured, undefined, or missing source ID.
        """
        endpoint = (
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export"
        )
        rv = self.server.post(
            endpoint,
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_stac_source_error_import),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

    @unittest.skipIf(no_stac_plugin, "STAC Plugin not installed")
    def test_stac_source_filter_error_import(self):
        """
        Test of STAC collection import with http response 400,
        raising error on filtering parameter such as wrong temporal interval
        or wrong Spatial coordinates in bbox.

        """
        endpoint = (
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export"
        )
        rv = self.server.post(
            endpoint,
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_stac_filter_error_import),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

    def test_raster_import_resample_resolution(self):
        """
        Test raster import with defined resampling method and defined
        resolution method, with http response 200
        """
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(process_chain_raster_import_resample_resolution),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv,
            headers=self.admin_auth_header,
            http_status=200,
            status="finished",
        )

    def test_raster_import_resample_resolution_info(self):
        """
        Test resampling and resolution values for raster import by retrieving
        resampling and resolution info
        """
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(
                process_chain_raster_import_resample_resolution_info
            ),
            content_type="application/json",
        )

        resp = self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header
        )

        resample_val = "resample=bilinear_f"
        resolution_val = "100"

        r_info_results = resp["process_results"]["r_info"]
        r_import_process_log = resp["process_log"][1]

        self.assertEqual(
            r_info_results["ewres"],
            resolution_val,
            "'ewres' does not match set resolution",
        )
        self.assertEqual(
            r_info_results["nsres"],
            resolution_val,
            "'nsres' does not match set resolution %s" % resolution_val,
        )
        self.assertEqual(
            r_import_process_log["parameter"][3],
            resample_val,
            "'resampling method' does not match set resampling method %s"
            % resample_val,
        )

    def test_raster_import_resample_resolution_error_resamp(self):
        """
        Test raster import with defined resampling method and defined
        resolution method, with http response 400, resample value not
        in options
        """
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(
                process_chain_raster_import_resample_resolution_error_resamp
            ),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

    def test_raster_import_resample_resolution_error_resol(self):
        """
        Test raster import with defined resampling method and defined
        resolution method, with http response 400, resolution value not
        in options
        """
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(
                process_chain_raster_import_resample_resolution_error_resol
            ),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

    def test_raster_import_resample_resolution_error_val_missing(self):
        """
        Test raster import with defined resampling method and defined
        resolution method, with http response 400, key "value" missing when
        resolution set to value
        """
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(
                pc_raster_import_resample_resolution_error_val_missing
            ),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

    def test_raster_import_resample_resolution_error_val_not_float(self):
        """
        Test raster import with defined resampling method and defined
        resolution method, with http response 400, value for "value" not
        convertible to float
        """
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(
                pc_raster_import_resample_resolution_error_val_not_float
            ),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

    def test_raster_import_resample_resolution_error_resol_not_set(self):
        """
        Test raster import with defined resampling method and defined
        resolution method, with http response 400, resolution not set when
        value set
        """
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(
                pc_raster_import_resample_resolution_error_resol_not_set
            ),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )

    def test_raster_import_resample_resolution_error_resol_not_val(self):
        """
        Test raster import with defined resampling method and defined
        resolution method, with http response 400, resolution not set to
        "value" when value set
        """
        rv = self.server.post(
            f"{URL_PREFIX}/{self.project_url_part}/nc_spm_08/"
            "processing_async_export",
            headers=self.admin_auth_header,
            data=json_dumps(
                pc_raster_import_resample_resolution_error_resol_not_val
            ),
            content_type="application/json",
        )

        self.waitAsyncStatusAssertHTTP(
            rv, headers=self.admin_auth_header, http_status=400, status="error"
        )


if __name__ == "__main__":
    unittest.main()
