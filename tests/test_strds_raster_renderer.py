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
Tests: STRDS render test case
"""
import unittest
from pprint import pprint
from flask.json import loads as json_load
from flask.json import dumps as json_dumps
try:
    from .test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX
except:
    from test_resource_base import ActiniaResourceTestCaseBase, URL_PREFIX


__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"

location = 'nc_spm_08'
strds_mapset = 'modis_lst'
strds_url = (URL_PREFIX +
             '/locations/%(location)s/mapsets/%(mapset)s/strds'
             % {'location': location, 'mapset': strds_mapset})
strds_data = 'LST_Day_monthly'


class STRDSRenderTestCase(ActiniaResourceTestCaseBase):

    def test_strds_render_1(self):

        new_mapset = "strds_render_test"
        self.create_new_mapset(new_mapset, location)

        # Create success
        rv = self.server.post(URL_PREFIX +
                                '/locations/%(location)s/mapsets/%(mapset)s/strds/test_strds_register'
                                % {'location': location, 'mapset': new_mapset},
                              headers=self.admin_auth_header,
                              data=json_dumps({"temporaltype": "absolute",
                                               "title": "A nice title",
                                               "description": "A nice description"}),
                              content_type="application/json")
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" % rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype)

        # Create the raster layer
        rv = self.server.post(URL_PREFIX + '/locations/%(location)s/mapsets/%(mapset)s/raster_layers/test_layer_1' % {'location': location, 'mapset': new_mapset},
                              headers=self.admin_auth_header,
                              data=json_dumps({"expression": "1"}),
                              content_type="application/json")
        pprint(json_load(rv.data))
        rv = self.server.post(URL_PREFIX + '/locations/%(location)s/mapsets/%(mapset)s/raster_layers/test_layer_2' % {'location': location, 'mapset': new_mapset},
                              headers=self.admin_auth_header,
                              data=json_dumps({"expression": "2"}),
                              content_type="application/json")
        pprint(json_load(rv.data))
        rv = self.server.post(URL_PREFIX + '/locations/%(location)s/mapsets/%(mapset)s/raster_layers/test_layer_3' % {'location': location, 'mapset': new_mapset},
                              headers=self.admin_auth_header,
                              data=json_dumps({"expression": "3"}),
                              content_type="application/json")
        pprint(json_load(rv.data))

        raster_layers = [{"name": "test_layer_1", "start_time": "2000-01-01", "end_time": "2000-01-02"},
                         {"name": "test_layer_2", "start_time": "2000-01-02", "end_time": "2000-01-03"},
                         {"name": "test_layer_3", "start_time": "2000-01-03", "end_time": "2000-01-04"}]

        rv = self.server.put(URL_PREFIX + "/locations/%(location)s/mapsets/%(mapset)s/strds/test_strds_register/raster_layers" % {'location': location, 'mapset': new_mapset},
                             data=json_dumps(raster_layers),
                             content_type="application/json",
                             headers=self.admin_auth_header)
        pprint(json_load(rv.data))
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" % rv.status_code)
        self.assertEqual(rv.mimetype, "application/json", "Wrong mimetype %s" % rv.mimetype)

        # Check strds
        rv = self.server.get(URL_PREFIX + "/locations/%(location)s/mapsets/%(mapset)s/strds/test_strds_register/render?"
                             "width=100&height=100" % {'location': location, 'mapset': new_mapset},
                             headers=self.admin_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" % rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype)

        # # Check strds
        rv = self.server.get(URL_PREFIX + "/locations/%(location)s/mapsets/%(mapset)s/strds/test_strds_register/render?"
                             "width=100&height=100&start_time=2000-01-01 00:00:00&end_time=2000-01-02 00:00:00" % {'location': location, 'mapset': new_mapset},
                             headers=self.admin_auth_header)
        self.assertEqual(rv.status_code, 200, "HTML status code is wrong %i" % rv.status_code)
        self.assertEqual(rv.mimetype, "image/png", "Wrong mimetype %s" % rv.mimetype)


if __name__ == '__main__':
    unittest.main()
