# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2023 mundialis GmbH & Co. KG
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
User management for no authentication
"""

# from passlib.apps import custom_app_context as pwd_context
# import jwt
# from datetime import datetime, timezone, timedelta
from actinia_core.core.common.config import global_config
from actinia_core.core.redis_user import redis_user_interface
from actinia_core.core.common.user import ActiniaUser


__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2023, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"


class ActiniaUserNoAuth(ActiniaUser):
    """
    The Actinia Core user management class for no authentication
    """

    db = redis_user_interface

    def __init__(self):
        """Constructor
        Initialize and create a user object for no authentication.
        """
        self.user_id = global_config.DEFAULT_USER
        self.user_group = global_config.DEFAULT_USER_GROUP
        self.password_hash = None
        self.user_role = "superadmin"
        self.permissions = None
        self.cell_limit = global_config.MAX_CELL_LIMIT
        self.accessible_datasets = {
            "nc_spm_08": ["PERMANENT", "user1", "landsat"],
            "ECAD": ["PERMANENT"],
            "latlong_wgs84": ["PERMANENT"],
        }
        self.accessible_modules = global_config.MODULE_ALLOW_LIST
        self.process_num_limit = global_config.PROCESS_NUM_LIMIT
        self.process_time_limit = global_config.PROCESS_TIME_LIMT

    @staticmethod
    def create_user():
        """Create a new user object for no authentication and initialize it

        Returns:
            actinia_core_api.common.user_noauth.ActiniaUserNoAuth:
            A new user object in case of success, or None in case of failure
        """
        user = ActiniaUserNoAuth()
        user.hash_password("")

        if user.commit() is True:
            return user
        return None
