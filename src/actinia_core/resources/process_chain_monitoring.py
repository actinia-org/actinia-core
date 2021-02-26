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
Process Chain Monitoring
"""
import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
import tempfile
from flask import jsonify, make_response, Response
from flask_restful_swagger_2 import swagger, Schema

from .resource_management import ResourceManager
from .common.response_models import ProcessingResponseModel, SimpleResponseModel

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2021, mundialis GmbH & Co. KG"
__maintainer__ = "mudnialis"
__email__ = "info@mudnialis.de"


def create_scatter_plot(x, y, xlabel, ylabel, title):

    result_file = tempfile.mktemp(suffix=".png")
    plt.scatter(x, y, s=np.pi*5, c=(1,0,0))
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    y_up = (max(y) + 9) // 10 * 10
    plt.ylim(0, y_up)
    y_len = len(y)
    step = y_up / 10
    plt.xticks(np.arange(1, len(y) + 1, step=1))
    plt.savefig(result_file)
    return result_file


def compute_mapset_size_diffs(mapset_sizes):
    diffs = [None] * len(mapset_sizes)
    diffs[0] = mapset_sizes[0] # TODO not correct cause an empty mapset has also a size!
    for i in range(1, len(mapset_sizes)):
        diffs[i] = mapset_sizes[i] - mapset_sizes[i-1]
    return diffs


class MapsetSizeResponseModel(Schema):
    """Response schema for mapset sizes of a resource
    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The status of the resource, values: success, error'
        },
        'mapset_sizes': {
            'type': 'array',
            'items': {"type": "integer"},
            'description': 'The list of mapset sizes of a resource in bytes'
        }
    }
    example = {"mapset_sizes": [29946, 29946], "status": "success"}
    required = ["status", "mapset_sizes"]


class MapsetSizeResource(ResourceManager):
    """
    This class return the mapset sizes of a resource
    """
    def __init__(self):

        # Configuration
        ResourceManager.__init__(self)

    @swagger.doc({
        'tags': ['Process Chain Monitoring'],
        'description': 'Get the mapset sizes of a resource. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'user_id',
                'description': 'The unique user name/id',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'resource_id',
                'description': 'The id of the resource',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'The current state of the resource',
                'schema': MapsetSizeResponseModel
            },
            '400': {
                'description': 'The error message if the resource does not exists',
                'schema': SimpleResponseModel
            }
        }
    })
    def get(self, user_id, resource_id):
        """Get the sizes of mapset of a resource."""

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        response_data = self.resource_logger.get(user_id, resource_id)

        if response_data is not None:
            http_code, pc_response_model = pickle.loads(response_data)

            pc_status = pc_response_model['status']
            if pc_status in ['accepted', 'running']:
                return make_response(jsonify(SimpleResponseModel(
                    status="error",
                    message="Resource is not ready it is %s" % pc_status)),
                    400)

            mapset_sizes = [proc['mapset_size']
                for proc in pc_response_model['process_log']]

            return make_response(
                jsonify(MapsetSizeResponseModel(
                status="success", mapset_sizes=mapset_sizes)), http_code)
        else:
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="Resource does not exist")), 400)


class MapsetSizeDiffResource(ResourceManager):
    """
    This class return the mapset size differences of a resource
    """
    def __init__(self):

        # Configuration
        ResourceManager.__init__(self)

    @swagger.doc({
        'tags': ['Process Chain Monitoring'],
        'description': 'Get the mapset size differences of a resource. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'user_id',
                'description': 'The unique user name/id',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'resource_id',
                'description': 'The id of the resource',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'The current state of the resource',
                'schema': MapsetSizeResponseModel
            },
            '400': {
                'description': 'The error message if the resource does not exists',
                'schema': SimpleResponseModel
            }
        }
    })
    def get(self, user_id, resource_id):
        """Get the size differences of mapset of a resource."""

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        response_data = self.resource_logger.get(user_id, resource_id)

        if response_data is not None:
            http_code, pc_response_model = pickle.loads(response_data)

            pc_status = pc_response_model['status']
            if pc_status in ['accepted', 'running']:
                return make_response(jsonify(SimpleResponseModel(
                    status="error",
                    message="Resource is not ready it is %s" % pc_status)),
                    400)

            mapset_sizes = [proc['mapset_size']
                for proc in pc_response_model['process_log']]
            diffs = compute_mapset_size_diffs(mapset_sizes)

            return make_response(
                jsonify(MapsetSizeResponseModel(
                status="success", mapset_sizes=diffs)), http_code)
        else:
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="Resource does not exist")), 400)


class MaxMapsetSizeResponseModel(Schema):
    """Response schema for maximum mapset size of a resouce
    """
    type = 'object'
    properties = {
        'status': {
            'type': 'string',
            'description': 'The status of the resource, values: success, error'
        },
        'max_mapset_size': {
            'type': 'integer',
            'description': 'The maximum mapset size of a resource in bytes'
        }
    }
    example = {"max_mapset_size": 29949, "status": "success"}
    required = ["status", "max_mapset_size"]


class MaxMapsetSizeResource(ResourceManager):
    """
    This class return the maximum mapset size of a resource
    """
    def __init__(self):

        # Configuration
        ResourceManager.__init__(self)

    @swagger.doc({
        'tags': ['Process Chain Monitoring'],
        'description': 'Get the maximum mapset size of a resource. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'user_id',
                'description': 'The unique user name/id',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'resource_id',
                'description': 'The id of the resource',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'The current state of the resource',
                'schema': MaxMapsetSizeResponseModel
            },
            '400': {
                'description': 'The error message if the resource does not exists',
                'schema': SimpleResponseModel
            }
        }
    })
    def get(self, user_id, resource_id):
        """Get the maximum size of mapset of a resource."""

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        response_data = self.resource_logger.get(user_id, resource_id)

        if response_data is not None:
            http_code, pc_response_model = pickle.loads(response_data)

            pc_status = pc_response_model['status']
            if pc_status in ['accepted', 'running']:
                return make_response(jsonify(SimpleResponseModel(
                    status="error",
                    message="Resource is not ready it is %s" % pc_status)),
                    400)

            mapset_sizes = [proc['mapset_size']
                for proc in pc_response_model['process_log']]
            max_mapset_size = max(mapset_sizes)

            return make_response(
                jsonify(MaxMapsetSizeResponseModel(
                status="success", max_mapset_size=max_mapset_size)), http_code)
        else:
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="Resource does not exist")), 400)


class MapsetSizeRenderResource(ResourceManager):
    """
    This class renders the mapset sizes of a resource
    """
    def __init__(self):

        # Configuration
        ResourceManager.__init__(self)

    @swagger.doc({
        'tags': ['Process Chain Monitoring'],
        'description': 'Render the mapset sizes of a resource. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'user_id',
                'description': 'The unique user name/id',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'resource_id',
                'description': 'The id of the resource',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'produces':["image/png"],
        'responses': {
            '200': {
                'description': 'The PNG image'},
            '400': {
                'description': 'The error message and a detailed log why rendering did not succeeded',
                'schema': SimpleResponseModel
            }
        }
    })
    def get(self, user_id, resource_id):
        """Render the mapset sizes of a resource."""

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        response_data = self.resource_logger.get(user_id, resource_id)

        if response_data is not None:
            http_code, pc_response_model = pickle.loads(response_data)

            pc_status = pc_response_model['status']
            if pc_status in ['accepted', 'running']:
                return make_response(jsonify(SimpleResponseModel(
                    status="error",
                    message="Resource is not ready it is %s" % pc_status)),
                    400)

            mapset_sizes = [proc['mapset_size']
                for proc in pc_response_model['process_log']]


            y = np.array(mapset_sizes)
            x = np.array(list(range(1, len(mapset_sizes) + 1)))
            unit = "bytes"
            for new_unit in ['KB', 'MB', 'GB', 'TB']:
                if max(y) > 1024.:
                    y = y/1024.
                    unit = new_unit
                    print(new_unit)
                else:
                    break

            # create png
            result_file = create_scatter_plot(
                x, y, 'process chain steps', 'mapset size [%s]' % unit,
                'Mapset sizes of the resource\n%s' % resource_id)

            if result_file:
                if os.path.isfile(result_file):
                    image = open(result_file, "rb").read()
                    os.remove(result_file)
                    return Response(image, mimetype='image/png')
        else:
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="Resource does not exist")), 400)


class MapsetSizeDiffRenderResource(ResourceManager):
    """
    This class renders the mapset size differences of a resource
    """
    def __init__(self):

        # Configuration
        ResourceManager.__init__(self)

    @swagger.doc({
        'tags': ['Process Chain Monitoring'],
        'description': 'Render the mapset size differences of a resource. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'user_id',
                'description': 'The unique user name/id',
                'required': True,
                'in': 'path',
                'type': 'string'
            },
            {
                'name': 'resource_id',
                'description': 'The id of the resource',
                'required': True,
                'in': 'path',
                'type': 'string'
            }
        ],
        'produces':["image/png"],
        'responses': {
            '200': {
                'description': 'The PNG image'},
            '400': {
                'description': 'The error message and a detailed log why rendering did not succeeded',
                'schema': SimpleResponseModel
            }
        }
    })
    def get(self, user_id, resource_id):
        """Render the mapset sizes of a resource."""

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        response_data = self.resource_logger.get(user_id, resource_id)

        if response_data is not None:
            http_code, pc_response_model = pickle.loads(response_data)

            pc_status = pc_response_model['status']
            if pc_status in ['accepted', 'running']:
                return make_response(jsonify(SimpleResponseModel(
                    status="error",
                    message="Resource is not ready it is %s" % pc_status)),
                    400)

            mapset_sizes = [proc['mapset_size']
                for proc in pc_response_model['process_log']]
            diffs = compute_mapset_size_diffs(mapset_sizes)

            y = np.array(diffs)
            x = np.array(list(range(1, len(mapset_sizes) + 1)))
            unit = "bytes"
            for new_unit in ['KB', 'MB', 'GB', 'TB']:
                if max(y) > 1024.:
                    y = y/1024.
                    unit = new_unit
                    print(new_unit)
                else:
                    break

            # create png
            result_file = create_scatter_plot(
                x, y, 'process chain steps', 'mapset size [%s]' % unit,
                'Mapset sizes of the resource\n%s' % resource_id)

            if result_file:
                if os.path.isfile(result_file):
                    image = open(result_file, "rb").read()
                    os.remove(result_file)
                    return Response(image, mimetype='image/png')
        else:
            return make_response(jsonify(SimpleResponseModel(
                status="error",
                message="Resource does not exist")), 400)
