# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2022 Sören Gebbert and mundialis GmbH & Co. KG
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
STRDS raster map layer management

TODO: Integrate into the ephemeral process chain approach
"""
from flask_restful_swagger_2 import swagger
from flask import jsonify, make_response
import pickle
from actinia_api.swagger2.actinia_core.schemas.strds_raster_management import \
     STRDSRasterListResponseModel, RasterListRegisterModel

from actinia_core.core.request_parser import where_parser
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.models.response_models import \
    ProcessingResponseModel, ProcessingErrorResponseModel
from actinia_core.processing.common.strds_raster_management import \
    unregister_raster, register_raster, list_raster_strds

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class STRDSRasterManagement(ResourceBase):
    """Manage raster layer in a space time raster dataset
    """

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Get a list of all raster map layers that are registered '
                       'in a STRDS that is located in a specific location/mapset. '
                       'Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'strds_name',
                'description': 'The name of the STRDS',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'where',
                'description': 'A where statement to select user specific '
                               'raster map layers from the STRDS',
                'required': False,
                'in': 'query',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'This response returns a list of all raster map '
                               'layers that are registered a specific STRDS and '
                               'the log of the process chain that was used to '
                               'create the response.',
                'schema': STRDSRasterListResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why '
                               'creating a list of raster map layers from STRDS '
                               'did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def get(self, location_name, mapset_name, strds_name):
        """Get a list of all raster map layers that are registered in a STRDS
        """
        rdc = self.preprocess(has_json=False, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        if rdc:
            args = where_parser.parse_args()
            rdc.set_user_data(args)

            enqueue_job(self.job_timeout, list_raster_strds, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Register raster map layers in a STRDS located in a '
                       'specific location/mapset. '
                       'Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'strds_name',
                'description': 'The name of the STRDS',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'raster_list',
                'description': 'The list of raster map layers to be registered '
                               'in the STRDS',
                'required': True,
                'in': 'body',
                'schema': RasterListRegisterModel
            }
        ],
        'responses': {
            '200': {
                'description': 'Registration of raster map layers was '
                               'successfully finished.',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why raster '
                               'map layer registration did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def put(self, location_name, mapset_name, strds_name):
        """Register raster map layers in a STRDS located in a specific
        location/mapset.
        """
        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        if rdc:
            enqueue_job(self.job_timeout, register_raster, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['STRDS Management'],
        'description': 'Unregister raster map layers from a STRDS located in a '
                       'specific location/mapset. '
                       'Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The name of the location',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'strds_name',
                'description': 'The name of the STRDS',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'raster_list',
                'description': 'The list of raster map layers to be '
                               'unregistered from the STRDS',
                'required': True,
                'in': 'body',
                'schema': {"type": "array", "items": {"type": "string"}}
            }
        ],
        'responses': {
            '200': {
                'description': 'Unregistration of raster map layers was '
                               'successfully finished.',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why raster '
                               'map layer unregistration did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def delete(self, location_name, mapset_name, strds_name):
        """Unregister raster map layers from a STRDS located in a specific
        location/mapset.
        """
        rdc = self.preprocess(has_json=True, has_xml=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=strds_name)

        if rdc:
            enqueue_job(self.job_timeout, unregister_raster, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)
