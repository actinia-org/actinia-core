# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2021 mundialis GmbH & Co. KG
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
from tempfile import NamedTemporaryFile
from flask import jsonify, make_response, Response
from flask_restful_swagger_2 import swagger
from actinia_api.swagger2.actinia_core.apidocs import process_chain_monitoring
from actinia_api.swagger2.actinia_core.schemas.process_chain_monitoring import (
    MapsetSizeResponseModel,
    MaxMapsetSizeResponseModel,
)

from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.rest.resource_management import ResourceManager
from actinia_core.models.response_models import SimpleResponseModel

__license__ = "GPLv3"
__author__ = "Anika Weinmann, Carmen Tawalika"
__copyright__ = "Copyright 2021, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def create_scatter_plot(x, y, xlabel, ylabel, title):
    plt.clf()
    plt.scatter(x, y, s=(np.pi * 5), c=(1, 0, 0))
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    y_up = (max(y) + 9) // 10 * 10
    plt.ylim(0, y_up)
    step = y_up / 10
    plt.xticks(np.arange(1, len(y) + 1, step=step))
    with NamedTemporaryFile(suffix=".png", mode="wb", delete=False) as f:
        plt.savefig(f)
    return f.name


def compute_mapset_size_diffs(mapset_sizes):
    diffs = [None] * len(mapset_sizes)
    # TODO not correct cause an empty mapset has also a size!
    diffs[0] = mapset_sizes[0]
    for i in range(1, len(mapset_sizes)):
        diffs[i] = mapset_sizes[i] - mapset_sizes[i - 1]
    return diffs


class MapsetSizeResource(ResourceManager):
    """
    This class returns the mapset sizes of a resource
    """

    def __init__(self):
        # Configuration
        ResourceManager.__init__(self)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint("get", process_chain_monitoring.mapset_size_get_doc)
    )
    def get(self, user_id, resource_id):
        """Get the sizes of mapset of a resource."""

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        response_data = self.resource_logger.get(user_id, resource_id)

        if response_data is not None:
            http_code, pc_response_model = pickle.loads(response_data)

            pc_status = pc_response_model["status"]
            if pc_status in ["accepted", "running"]:
                return make_response(
                    jsonify(
                        SimpleResponseModel(
                            status="error",
                            message="Resource is not ready it is %s"
                            % pc_status,
                        )
                    ),
                    400,
                )

            mapset_sizes = [
                proc["mapset_size"]
                for proc in pc_response_model["process_log"]
            ]

            return make_response(
                jsonify(
                    MapsetSizeResponseModel(
                        status="success", mapset_sizes=mapset_sizes
                    )
                ),
                http_code,
            )
        else:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error", message="Resource does not exist"
                    )
                ),
                400,
            )


class MapsetSizeDiffResource(ResourceManager):
    """
    This class returns the step-by-step mapset size differences of a resource
    """

    def __init__(self):
        # Configuration
        ResourceManager.__init__(self)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint("get", process_chain_monitoring.mapset_sizediff_get_doc)
    )
    def get(self, user_id, resource_id):
        """Get the step-by-step mapset size differences of a resource."""

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        response_data = self.resource_logger.get(user_id, resource_id)

        if response_data is not None:
            http_code, pc_response_model = pickle.loads(response_data)

            pc_status = pc_response_model["status"]
            if pc_status in ["accepted", "running"]:
                return make_response(
                    jsonify(
                        SimpleResponseModel(
                            status="error",
                            message="Resource is not ready it is %s"
                            % pc_status,
                        )
                    ),
                    400,
                )

            mapset_sizes = [
                proc["mapset_size"]
                for proc in pc_response_model["process_log"]
            ]
            diffs = compute_mapset_size_diffs(mapset_sizes)

            return make_response(
                jsonify(
                    MapsetSizeResponseModel(
                        status="success", mapset_sizes=diffs
                    )
                ),
                http_code,
            )
        else:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error", message="Resource does not exist"
                    )
                ),
                400,
            )


class MaxMapsetSizeResource(ResourceManager):
    """
    This class returns the maximum mapset size of a resource
    """

    def __init__(self):
        # Configuration
        ResourceManager.__init__(self)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint("get", process_chain_monitoring.mapset_maxsize_get_doc)
    )
    def get(self, user_id, resource_id):
        """Get the maximum size of mapset of a resource."""

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        response_data = self.resource_logger.get(user_id, resource_id)

        if response_data is not None:
            http_code, pc_response_model = pickle.loads(response_data)

            pc_status = pc_response_model["status"]
            if pc_status in ["accepted", "running"]:
                return make_response(
                    jsonify(
                        SimpleResponseModel(
                            status="error",
                            message="Resource is not ready it is %s"
                            % pc_status,
                        )
                    ),
                    400,
                )

            mapset_sizes = [
                proc["mapset_size"]
                for proc in pc_response_model["process_log"]
            ]
            max_mapset_size = max(mapset_sizes)

            return make_response(
                jsonify(
                    MaxMapsetSizeResponseModel(
                        status="success", max_mapset_size=max_mapset_size
                    )
                ),
                http_code,
            )
        else:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error", message="Resource does not exist"
                    )
                ),
                400,
            )


class MapsetSizeRenderResource(ResourceManager):
    """
    This class renders the mapset sizes of a resource
    """

    def __init__(self):
        # Configuration
        ResourceManager.__init__(self)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint(
            "get", process_chain_monitoring.mapset_render_sizes_get_doc
        )
    )
    def get(self, user_id, resource_id):
        """Render the mapset sizes of a resource."""

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        response_data = self.resource_logger.get(user_id, resource_id)

        if response_data is not None:
            _, pc_response_model = pickle.loads(response_data)

            pc_status = pc_response_model["status"]
            if pc_status in ["accepted", "running"]:
                return make_response(
                    jsonify(
                        SimpleResponseModel(
                            status="error",
                            message="Resource is not ready it is %s"
                            % pc_status,
                        )
                    ),
                    400,
                )

            mapset_sizes = [
                proc["mapset_size"]
                for proc in pc_response_model["process_log"]
            ]

            y = np.array(mapset_sizes)
            x = np.array(list(range(1, len(mapset_sizes) + 1)))
            unit = "bytes"
            for new_unit in ["KB", "MB", "GB", "TB"]:
                if max(y) > 1024.0:
                    y = y / 1024.0
                    unit = new_unit
                    print(new_unit)
                else:
                    break

            # create png
            result_file = create_scatter_plot(
                x,
                y,
                "process chain steps",
                "mapset size [%s]" % unit,
                "Mapset sizes of the resource\n%s" % resource_id,
            )

            if result_file:
                if os.path.isfile(result_file):
                    image = open(result_file, "rb").read()
                    os.remove(result_file)
                    return Response(image, mimetype="image/png")
        else:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error", message="Resource does not exist"
                    )
                ),
                400,
            )


class MapsetSizeDiffRenderResource(ResourceManager):
    """
    This class renders the step-by-step mapset size differences of a resource
    """

    def __init__(self):
        # Configuration
        ResourceManager.__init__(self)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint(
            "get", process_chain_monitoring.mapset_render_sizediff_get_doc
        )
    )
    def get(self, user_id, resource_id):
        """Render the step-by-step mapset size differences of a resource."""

        ret = self.check_permissions(user_id=user_id)
        if ret:
            return ret

        response_data = self.resource_logger.get(user_id, resource_id)

        if response_data is not None:
            _, pc_response_model = pickle.loads(response_data)

            pc_status = pc_response_model["status"]
            if pc_status in ["accepted", "running"]:
                return make_response(
                    jsonify(
                        SimpleResponseModel(
                            status="error",
                            message="Resource is not ready, it is %s"
                            % pc_status,
                        )
                    ),
                    400,
                )

            mapset_sizes = [
                proc["mapset_size"]
                for proc in pc_response_model["process_log"]
            ]
            diffs = compute_mapset_size_diffs(mapset_sizes)

            y = np.array(diffs)
            x = np.array(list(range(1, len(mapset_sizes) + 1)))
            unit = "bytes"
            for new_unit in ["KB", "MB", "GB", "TB"]:
                if max(y) > 1024.0:
                    y = y / 1024.0
                    unit = new_unit
                    print(new_unit)
                else:
                    break

            # create png
            result_file = create_scatter_plot(
                x,
                y,
                "process chain steps",
                "mapset size [%s]" % unit,
                "Step-by-step mapset size differences of the resource\n%s"
                % resource_id,
            )

            if result_file:
                if os.path.isfile(result_file):
                    image = open(result_file, "rb").read()
                    os.remove(result_file)
                    return Response(image, mimetype="image/png")
        else:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error", message="Resource does not exist"
                    )
                ),
                400,
            )
