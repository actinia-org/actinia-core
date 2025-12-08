# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2018 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Base class for user management resources
"""

from flask_restful import Resource
from actinia_core.core.common.app import auth
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.core.messages_logger import MessageLogger
from actinia_core.rest.base.user_auth import check_admin_role

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class LoginBase(Resource):
    """
    Base class for all login resources related classes
    """

    # Authorization is required for all resources
    # API logging is required for all resources
    decorators = [log_api_call, check_admin_role, auth.login_required]

    def __init__(self):
        Resource.__init__(self)
        self.message_logger = MessageLogger()
