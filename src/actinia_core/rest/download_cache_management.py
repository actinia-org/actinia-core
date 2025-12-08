# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2022 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
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

from actinia_rest_lib.resource_base import ResourceBase
from actinia_core.core.common.kvdb_interface import enqueue_job
from actinia_core.core.common.api_logger import log_api_call
from actinia_rest_lib.endpoint_config import (
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

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2022, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


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
