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
Resource storage management

TODO: Tests required
"""

from flask import jsonify, make_response
from flask_restful import reqparse
from flask_restful_swagger_2 import swagger
import pickle
from actinia_api.swagger2.actinia_core.apidocs import (
    resource_storage_management,
)

from actinia_rest_lib.resource_base import ResourceBase
from actinia_core.core.common.kvdb_interface import enqueue_job
from actinia_core.processing.common.resource_storage_management import (
    start_resource_storage_size,
    start_resource_storage_remove,
)

from actinia_core.core.common.app import auth
from actinia_core.core.common.api_logger import log_api_call
from actinia_rest_lib.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.rest.base.user_auth import check_admin_role
from actinia_core.rest.base.user_auth import check_user_permissions

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = "Copyright 2016-2022, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class SyncResourceStorageResource(ResourceBase):
    decorators = [
        log_api_call,
        check_user_permissions,
        check_admin_role,
        auth.login_required,
    ]

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", resource_storage_management.get_doc))
    def get(self):
        """Get the current size of the resource storage"""
        rdc = self.preprocess(has_json=False, has_xml=False)

        if rdc:
            enqueue_job(
                self.job_timeout,
                start_resource_storage_size,
                rdc,
                queue_type_overwrite=True,
            )
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    def _create_parser(self):
        """Create the delete option arguments

        The parameter contain:

            olderthan : for older than X days

        Returns:
            The argument parser

        """
        parser = reqparse.RequestParser()
        parser.add_argument(
            "olderthan",
            type=int,
            location="args",
            help="Older than x days. X must be specified as integer value",
        )
        return parser

    @endpoint_decorator()
    @swagger.doc(
        check_endpoint("delete", resource_storage_management.delete_doc)
    )
    def delete(self):
        """Clean the resource storage and remove all cached data"""
        rdc = self.preprocess(has_json=False, has_xml=False)

        olderthan = None
        parser = self._create_parser()
        args = parser.parse_args()
        if "olderthan" in args and args["olderthan"] is not None:
            olderthan = args["olderthan"]

        if rdc:
            enqueue_job(
                self.job_timeout,
                start_resource_storage_remove,
                rdc,
                olderthan,
                queue_type_overwrite=True,
            )
            http_code, response_model = pickle.loads(self.response_data)
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)
