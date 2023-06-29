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
This module is designed to deliver the API calls of a specific user
"""
from flask import g
from flask import jsonify, make_response
from flask_restful import Resource
from flask_restful_swagger_2 import swagger
from actinia_api.swagger2.actinia_core.apidocs import api_log_management
from actinia_api.swagger2.actinia_core.schemas.api_log_management import (
    ApiLogListModel,
)

from actinia_core.core.common.app import auth
from actinia_core.core.common.api_logger import ApiLogger
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.models.response_models import SimpleResponseModel
from actinia_core.rest.base.user_auth import check_user_permissions

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class APILogResource(Resource):
    """API logg management"""

    decorators = [log_api_call, check_user_permissions, auth.login_required]

    def __init__(self):
        # Configuration
        Resource.__init__(self)

        self.api_logger = ApiLogger()

        # Store the user id and user role of the current user
        self.user_id = g.user.get_id()
        self.user_role = g.user.get_role()

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", api_log_management.get_doc))
    def get(self, user_id):
        """
        Get a list of all API calls that have been called by the provided user.
        """

        if (
            self.user_role not in ["admin", "superadmin"]
            and user_id != self.user_id
        ):
            return make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message="You do not have the permission "
                        "to list the API calls of the user",
                    )
                ),
                401,
            )

        api_log_list = self.api_logger.list(user_id, 0, -1)
        return make_response(
            jsonify(ApiLogListModel(api_log_list=api_log_list)), 200
        )
