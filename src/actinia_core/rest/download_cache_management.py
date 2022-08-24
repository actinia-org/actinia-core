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
Download cache management

TODO: Tests required
"""

from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
import pickle
from actinia_api.swagger2.actinia_core.apidocs import download_cache_management

from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.rest.base.user_auth import check_admin_role
from actinia_core.rest.base.user_auth import check_user_permissions
from actinia_core.core.common.app import auth
from actinia_core.processing.common.download_cache_management import (
    start_download_cache_size,
    start_download_cache_remove,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis"


class SyncDownloadCacheResource(ResourceBase):
    decorators = [
        log_api_call,
        check_user_permissions,
        check_admin_role,
        auth.login_required,
    ]

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", download_cache_management.get_doc))
    def get(self):
        """Get the current size of the download cache"""
        rdc = self.preprocess(has_json=False, has_xml=False)

        if rdc:
            enqueue_job(
                self.job_timeout,
                start_download_cache_size,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint("delete", download_cache_management.delete_doc)
    )
    def delete(self):
        """Clean the download cache and remove all cached data"""
        rdc = self.preprocess(has_json=False, has_xml=False)

        if rdc:
            enqueue_job(
                self.job_timeout,
                start_download_cache_remove,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)
