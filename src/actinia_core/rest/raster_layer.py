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
Raster layer resources
"""
from flask import jsonify, make_response, request
from flask_restful_swagger_2 import swagger
import os
import pickle
from uuid import uuid4
from werkzeug.utils import secure_filename
from actinia_api.swagger2.actinia_core.apidocs import raster_layer

from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.core.utils import allowed_file
from actinia_core.models.response_models import SimpleResponseModel
from actinia_core.processing.common.raster_layer import (
    start_info_job,
    start_delete_job,
    start_create_job,
)
from actinia_core.rest.base.map_layer_base import MapLayerRegionResourceBase

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Guido Riembauer, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class RasterLayerResource(MapLayerRegionResourceBase):
    """Return information about a specific raster layer as JSON"""

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", raster_layer.get_doc))
    def get(self, project_name, mapset_name, raster_name):
        """Get information about an existing raster map layer."""
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=raster_name,
        )
        if rdc:
            enqueue_job(
                self.job_timeout,
                start_info_job,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish(0.02)
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("delete", raster_layer.delete_doc))
    def delete(self, project_name, mapset_name, raster_name):
        """Delete an existing raster map layer."""
        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=raster_name,
        )
        if rdc:
            enqueue_job(
                self.job_timeout,
                start_delete_job,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish(0.1)
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", raster_layer.post_doc))
    def post(self, project_name, mapset_name, raster_name):
        """Create a new raster layer by uploading a GeoTIFF"""

        allowed_extensions = ["tif", "tiff"]

        # TODO check if another content type can be used
        content_type = request.content_type.split(";")[0]
        if content_type != "multipart/form-data":
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message="Content type is not 'multipart/form-data'",
                    )
                ),
                400,
            )

        if "file" not in request.files:
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message="No file part indicated in postbody.",
                    )
                ),
                400,
            )

        # create download cache path if does not exists
        if os.path.exists(self.download_cache):
            pass
        else:
            os.mkdir(self.download_cache)

        # save file from request
        id = str(uuid4())
        file = request.files["file"]
        if file.filename == "":
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error", message="No selected file"
                    )
                ),
                400,
            )
        if allowed_file(file.filename, allowed_extensions):
            name, extension = secure_filename(file.filename).rsplit(".", 1)
            filename = f"{name}_{id}.{extension}"
            file_path = os.path.join(self.download_cache, filename)
            file.save(file_path)
        else:
            os.remove(file_path)
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message="File has a not allowed extension. "
                        f"Please use {','.join(allowed_extensions)}.",
                    )
                ),
                400,
            )

        rdc = self.preprocess(
            has_json=False,
            has_xml=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=raster_name,
        )
        if rdc:
            rdc.set_request_data(file_path)
            enqueue_job(self.job_timeout, start_create_job, rdc)

        http_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), http_code)
