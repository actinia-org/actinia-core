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
Asynchronous computation in specific temporary generated mapsets
with export of required map layers.
"""
import pickle
from flask import jsonify, make_response

from flask_restful_swagger_2 import swagger
from actinia_api.swagger2.actinia_core.apidocs import (
    ephemeral_processing_with_export,
)

from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.processing.common.ephemeral_processing_with_export import (
    start_job,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class AsyncEphemeralExportResource(ResourceBase):
    """
    This class represents a resource that runs asynchronous processing tasks in
    a temporary mapset and exports the computed results as geotiff files.
    """

    def __init__(self, resource_id=None, iteration=None, post_url=None):
        ResourceBase.__init__(self, resource_id, iteration, post_url)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint("post", ephemeral_processing_with_export.post_doc)
    )
    def post(self, project_name):
        """Execute a user defined process chain in an ephemeral project/mapset
        and store the processing results for download.
        """
        rdc = self.preprocess(has_json=True, project_name=project_name)

        if rdc:
            rdc.set_storage_model_to_file()
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


class AsyncEphemeralExportS3Resource(ResourceBase):
    """
    This class represents a resource that runs asynchronous processing tasks in
    a temporary mapset and exports the computed results as geotiff files to the
    Amazon S3 storage.
    """

    def __init__(self):
        ResourceBase.__init__(self)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint("post", ephemeral_processing_with_export.post_doc)
    )
    def post(self, project_name):
        """Execute a user defined process chain in an ephemeral project/mapset
        and store the processing result in an Amazon S3 bucket
        """
        rdc = self.preprocess(has_json=True, project_name=project_name)
        rdc.set_storage_model_to_s3()

        enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


class AsyncEphemeralExportGCSResource(ResourceBase):
    """
    This class represents a resource that runs asynchronous processing tasks in
    a temporary mapset and exports the computed results as geotiff files to the
    Google Cloud Storage.
    """

    def __init__(self):
        ResourceBase.__init__(self)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint("post", ephemeral_processing_with_export.post_doc)
    )
    def post(self, project_name):
        """Execute a user defined process chain in an ephemeral project/mapset
        and store the processing result in an Google cloud storage bucket
        """
        rdc = self.preprocess(has_json=True, project_name=project_name)
        rdc.set_storage_model_to_gcs()

        enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)
