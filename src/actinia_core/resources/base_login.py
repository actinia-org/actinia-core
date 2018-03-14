# -*- coding: utf-8 -*-
"""
Base class for user management resources
"""

from flask_restful import Resource
from actinia_core.resources.common.app import auth
from actinia_core.resources.common.logging_interface import log_api_call
from actinia_core.resources.common.messages_logger import MessageLogger
from actinia_core.resources.user_auth import very_admin_role

__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class LoginBase(Resource):
    """
    Base class for all login resources related classes
    """
    # Authorization is required for all resources
    # API logging is required for all resources
    decorators = [log_api_call, very_admin_role, auth.login_required]

    def __init__(self):
        Resource.__init__(self)
        self.message_logger = MessageLogger()
