# -*- coding: utf-8 -*-
import unittest
from test_resource_base import ActiniaResourceTestCaseBase
from flask.json import dumps as json_dumps

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

process_chain_raster_import_export = {
    'list'
             : [{'flags'    : 'a',
                 'id'       : 'r_slope_aspect_1',
                 'inputs'   : [{'import_descr': {
                     'source': 'https://storage.googleapis.com/graas-geodata/elev_ned_30m.tif',
                     'type'  : 'raster'},
                     'param'                  : 'elevation',
                     'value'                  : 'elev_ned_30m'},
                     {'param': 'format', 'value': 'degree'},
                     {'param': 'precision', 'value': 'DCELL'}],
                 'module'   : 'r.slope.aspect',
                 'outputs'  : [{'export': {'format': 'GTiff', 'type': 'raster'},
                                'param' : 'slope',
                                'value' : 'elev_ned_30m_slope'},
                               {'export': {'format': 'GTiff', 'type': 'raster'},
                                'param' : 'aspect',
                                'value' : 'elev_ned_30m_aspect'}],
                 'overwrite': True,
                 'verbose'  : False},
                {'exe'   : '/bin/cat',
                 'id'    : 'cat_1',
                 'params': [],
                 'stdin' : 'r_slope_aspect_1::stderr'}],
    'version': '1'}
#
# [
#     {'module' : 'r.slope.aspect',
#      'id'     : 'r_slope_aspect_1',
#      'inputs' : [
#          {'import_descr': {'source': 'https://storage.googleapis.com/graas-geodata/elev_ned_30m.tif',
#                            'type'  : 'raster'},
#           'param'       : 'elevation',
#           'value'       : 'elev_ned_30m'},
#          {'param': 'format', 'value': 'degree'},
#          {'param': 'precision', 'value': 'DCELL'}
#      ],
#      'outputs': [
#          {'param' : 'slope', 'value': 'elev_ned_30m_slope',
#           'export': {'format': 'GTiff', 'type': 'raster'}},
#          {'param' : 'aspect', 'value': 'elev_ned_30m_aspect',
#           'export': {'format': 'GTiff', 'type': 'raster'}}
#      ]
#     },
#     {'exe'  : '/bin/cat',
#      'id'   : 'cat_1',
#      'stdin': 'r_slope_aspect_1::stderr'
#     }
# ]

process_chain_raster_import_info = {
    'list'   : [{'id'    : 'r_info',
                 'inputs': [{'import_descr': {'source': 'https://storage.googleapis.com/graas-geodata/elev_ned_30m.tif',
                                              'type'  : 'raster'},
                             'param'       : 'map',
                             'value'       : 'elev_ned_30m'}],
                 'module': 'r.info',
                 'flags' : 'g'}],
    'version': '1'}

process_chain_raster_import_error_no_file = {
    'list'   : [{'id'    : 'r_info',
                 'inputs': [
                     {'import_descr': {'source': 'https://storage.googleapis.com/graas-geodata/elev_ned_30m_nope.tif',
                                       'type'  : 'raster'},
                      'param'       : 'map',
                      'value'       : 'elev_ned_30m'}, ],
                 'module': 'r.info',
                 'flags' : 'g'}],
    'version': '1'}

process_chain_vector_import_info = {
    'list'   : [{'id'    : 'v_info',
                 'inputs': [{'import_descr': {'source': 'https://storage.googleapis.com/graas-geodata/polygon.gml',
                                              'type'  : 'vector'},
                             'param'       : 'map',
                             'value'       : 'polygon'}],
                 'module': 'v.info',
                 'flags' : 'g'}],
    'version': '1'}

process_chain_sentinel_import_info = {
    'list'   : [{'id'    : 'r_info',
                 'inputs': [{'import_descr': {'source'       : 'S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138',
                                              'type'         : 'sentinel2',
                                              'sentinel_band': 'B01'},
                             'param'       : 'map',
                             'value'       : 'sentinel_map'}],
                 'module': 'r.info',
                 'flags' : 'g'}],
    'version': '1'}

process_chain_sentinel_import_univar = {
    'list'   : [{'id'    : 'r_univar',
                 'inputs': [{'import_descr': {'source'       : 'S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138',
                                              'type'         : 'sentinel2',
                                              'sentinel_band': 'B01'},
                             'param'       : 'map',
                             'value'       : 'sentinel_map'}],
                 'module': 'r.univar',
                 'flags' : 'g'}],
    'version': '1'}

# [{'module': 'r.univar',
#   'id'    : 'r_univar_sentinel2',
#   'inputs': [{'import_descr': {'source': 'S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138',
#                                'type': 'sentinel2',
#                                'sentinel_band': 'B01'},
#               'param': 'map', 'value': 'sentinel_map'}],
#   'flags' : 'g'}]

process_chain_sentinel_import_stats = {
    'list'   : [{'id'    : 'r_stats',
                 'inputs': [{'import_descr': {'source'       : 'S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138',
                                              'type'         : 'sentinel2',
                                              'sentinel_band': 'B01'},
                             'param'       : 'input',
                             'value'       : 'sentinel_map'}],
                 'module': 'r.stats',
                 'flags' : 'a'}],
    'version': '1'}

process_chain_sentinel_import_error = {
    'list'   : [{'id'    : 'r_stats',
                 'inputs': [
                     {'import_descr': {'source'       : 'S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138_NOPE',
                                       'type'         : 'sentinel2',
                                       'sentinel_band': 'B01'},
                      'param'       : 'input',
                      'value'       : 'sentinel_map'}],
                 'module': 'r.info',
                 'flags' : 'g'}],
    'version': '1'}

process_chain_sentinel_import_export = {
    'list': [{'id': 'importer_1',
              'inputs': [{'import_descr': {'source': 'S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138',
                                           'type': 'sentinel2',
                                           'sentinel_band': 'B01'},
                          'param': 'map',
                          'value': 'sentinel_map'},
                         {'import_descr': {'source': 'https://storage.googleapis.com/graas-geodata/elev_ned_30m.tif',
                                           'type': 'raster'},
                          'param': 'map',
                          'value': 'elev_ned_30m'}],
              "outputs": [{"export": {'type': 'raster', 'format': 'GTiff'},
                           'param': 'map',
                           "value": "sentinel_map"},
                          {"export": {'type': 'raster', 'format': 'GTiff'},
                           'param': 'map',
                           "value": "elev_ned_30m"}],
              'module': 'importer'}],

    'version': '1'}


process_chain_sentinel_import_export_sentinel_ndvi = {
    'list': [{'id': 'importer_1',
              'module': 'importer',
              'inputs': [{'import_descr': {'source': 'S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138',
                                           'type': 'sentinel2',
                                           'sentinel_band': 'B04'},
                          'param': 'map',
                          'value': 'B04'},
                         {'import_descr': {'source': 'S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138',
                                           'type': 'sentinel2',
                                           'sentinel_band': 'B08'},
                          'param': 'map',
                          'value': 'B08'}]},
             {'id': 'rmapcalc_1',
              'module': 'r.mapcalc',
              'inputs': [{'param': 'expression',
                          'value': 'NDVI = (B08 - B04)/(B08 + B04)'}]},
             {'id': 'exporter_1',
              'module': 'exporter',
              "outputs": [{"export": {'type': 'raster', 'format': 'GTiff'},
                           'param': 'map',
                           "value": "NDVI"}]}
             ],

    'version': '1'}


class AsyncProcessTestCase(ActiniaResourceTestCaseBase):

    def test_raster_import_export_sentinel_ndvi(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_sentinel_import_export_sentinel_ndvi),
                              content_type="application/json")

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="finished")

    def test_raster_import_export(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_sentinel_import_export),
                              content_type="application/json")

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="finished")

    def test_raster_import(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_raster_import_info),
                              content_type="application/json")

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="finished")

    def test_raster_import_nofile(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_raster_import_error_no_file),
                              content_type="application/json")

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=400, status="error")

    def test_import_export(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_raster_import_export),
                              content_type="application/json")

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="finished")

    def test_vector_import(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_vector_import_info),
                              content_type="application/json")

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="finished")

    def test_sentinel_import_info(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_sentinel_import_info),
                              content_type="application/json")

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="finished")

    def test_sentinel_import_univar(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_sentinel_import_univar),
                              content_type="application/json")

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="finished")

    def test_sentinel_import_stats(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_sentinel_import_stats),
                              content_type="application/json")

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=200, status="finished")

    def test_sentinel_import_error(self):
        rv = self.server.post('/locations/nc_spm_08/processing_async_export',
                              headers=self.admin_auth_header,
                              data=json_dumps(process_chain_sentinel_import_error),
                              content_type="application/json")

        self.waitAsyncStatusAssertHTTP(rv, headers=self.admin_auth_header,
                                       http_status=400, status="error")


if __name__ == '__main__':
    unittest.main()
