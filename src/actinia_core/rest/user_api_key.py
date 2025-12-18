# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2023 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
The user specific resources

This module specifies all endpoints to manage user accounts
in the kvdb database via REST API calls.

TODO: Implement POST full permission creation
      Implement PUT to modify existing users
"""
from flask_restful import reqparse
from flask_restful_swagger_2 import swagger
from flask import jsonify, make_response, g
from actinia_api.swagger2.actinia_core.apidocs import user_api_key
from actinia_api.swagger2.actinia_core.schemas.user_api_key import (
    TokenResponseModel,
)

from actinia_core.rest.base.base_login import LoginBase
from actinia_core.core.common.app import auth
from actinia_core.core.common.api_logger import log_api_call
from actinia_rest_lib.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2023, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


# Create a temporal module where, order, column parser
expiration_time_parser = reqparse.RequestParser()
expiration_time_parser.add_argument(
    "expiration_time",
    required=False,
    type=int,
    location="args",
    help="The expiration time in seconds for the generated token",
)


class APIKeyCreationResource(LoginBase):
    """Get an API key that has no expiration time"""

    def __init__(self):
        LoginBase.__init__(self)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", user_api_key.apikey_get_doc))
    def get(self):
        """Create an API key for permanent authentication."""

        try:
            return make_response(
                jsonify(
                    TokenResponseModel(
                        status="success",
                        token=g.user.generate_api_key(),
                        message="API key successfully generated",
                    )
                )
            )
        except Exception:
            return make_response(
                jsonify(
                    TokenResponseModel(
                        status="error",
                        token="",
                        message="Error while generating API key",
                    )
                ),
                400,
            )


class TokenCreationResource(LoginBase):
    """Get an authorization token"""

    decorators = [log_api_call, auth.login_required]

    def __init__(self):
        LoginBase.__init__(self)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("get", user_api_key.token_get_doc))
    def get(self):
        """Create an authentication token."""

        args = expiration_time_parser.parse_args()
        expiration = 86400

        try:
            if "expiration_time" in args:
                if args["expiration_time"]:
                    expiration = args["expiration_time"]

                    if expiration > 365 * 86400:
                        raise Exception(
                            "Expiration time is to large. Maximum is 365 days."
                        )

            return make_response(
                jsonify(
                    TokenResponseModel(
                        status="success",
                        token=g.user.generate_auth_token(
                            expiration=expiration
                        ),
                        message="Token successfully generated with "
                        "an expiration time of %i seconds" % expiration,
                    )
                )
            )
        except Exception as e:
            return make_response(
                jsonify(
                    TokenResponseModel(
                        status="error",
                        token="",
                        message="Error while generating token: %s" % str(e),
                    )
                ),
                400,
            )
