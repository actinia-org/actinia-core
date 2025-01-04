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
Compute areal categorical statistics on a raster map layer based on an input
polygon.
"""

import pickle
from flask_restful_swagger_2 import swagger
from flask import jsonify, make_response
from actinia_api.swagger2.actinia_core.apidocs import process_validation

from actinia_core.core.common.app import auth
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.processing.common.process_validation import start_job

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class AsyncProcessValidationResource(ResourceBase):
    decorators = [log_api_call, auth.login_required]

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", process_validation.post_doc))
    def post(self, project_name):
        """Validate a process chain asynchronously, check the provided sources
        and the mapsets."""

        rdc = self.preprocess(
            has_json=True, has_xml=True, project_name=project_name
        )

        if rdc:
            rdc.set_storage_model_to_file()
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


class SyncProcessValidationResource(ResourceBase):
    decorators = [log_api_call, auth.login_required]

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", process_validation.post_doc))
    def post(self, project_name):
        """Validate a process chain synchronously, check the provided sources
        and the mapsets."""

        rdc = self.preprocess(
            has_json=True, has_xml=True, project_name=project_name
        )

        if rdc:
            rdc.set_storage_model_to_file()
            enqueue_job(self.job_timeout, start_job, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)
