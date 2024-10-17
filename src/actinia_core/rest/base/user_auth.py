#!/usr/bin/env python
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
User authentication and credential check
"""
import os
from functools import wraps

from flask import g, abort
from actinia_core.core.common.config import global_config
from actinia_core.core.common.app import auth
from actinia_core.core.common.keycloak_user import ActiniaKeycloakUser
from actinia_core.core.common.user import ActiniaUser
from actinia_core.core.common.user_noauth import ActiniaUserNoAuth
from actinia_core.core.messages_logger import MessageLogger

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Julia Haas, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


if not global_config.AUTHENTICATION:
    # No authentication
    @auth.login_required
    def login_required(a, b):
        return False

    @auth.verify_password
    def verify_password(username_or_token, password):
        g.user = ActiniaUserNoAuth.create_user()
        return True


if global_config.KEYCLOAK_CONFIG_PATH:

    @auth.verify_token
    def verify_token(token):
        """Verify the keycloak token.
        A keycloak authentication token has to be provided.
        This function is called by the
        @auth.login_required decorator.
        Args:
            token (str): An authentication token
        Returns:
            bool: True if authorized or False if not
        """
        user = ActiniaKeycloakUser.verify_keycloak_token(token)
        if not user:
            return False
        g.user = user
        return True


if global_config.KEYCLOAK_CONFIG_PATH is None and global_config.AUTHENTICATION:

    @auth.verify_password
    def verify_password(username_or_token, password):
        """Verify the user name and password.

        Instead of a user name an authentication token
        or an API token can be provided.
        This function is called by the
        @auth.login_required decorator.

        Args:
            username_or_token (str): The username or an authentication token
            password (str): The optional user password, not required in case of
                            token

        Returns:
            bool: True if authorized or False if not

        """
        # first try to authenticate by token
        user = ActiniaUser.verify_auth_token(username_or_token)

        if not user:
            user = ActiniaUser.verify_api_key(username_or_token)

        if not user:
            # try to authenticate with username/password
            user = ActiniaUser(user_id=username_or_token)
            if not user.exists() or not user.verify_password(password):
                return False
        # Store the user globally
        g.user = user
        return True


def create_dummy_user(f):
    """
    Create a dummy user for configuration in which authorization is not
    required

    Args:
        f (function): The function to wrap

    Returns:
        function: The decorator functions

    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Set a default user
        g.user = ActiniaUser(
            user_id=global_config.DEFAULT_USER,
            user_group=global_config.DEFAULT_USER_GROUP,
        )

        return f(*args, **kwargs)

    return decorated_function


def check_admin_role(f):
    """Verify if the user has admin rights

    This decorator function verifies if the role
    of the login user is "admin" or "superadmin".

    It will abort with a 401 response if the user is not admin or superadmin

    Args:
        f (function): The function to wrap

    Returns:
        function: The decorator functions

    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            abort(401)

        if g.user.get_role() != "admin" and g.user.get_role() != "superadmin":
            abort(401)

        return f(*args, **kwargs)

    return decorated_function


def check_user_role(f):
    """Verify if the user has user or admin rights

    This decorator function verifies if the role
    of the login user is "user", "admin" or "superadmin".

    It will abort with a 401 response if the user is not user,
    admin or superadmin

    Args:
        f (function): The function to wrap

    Returns:
        function: The decorator functions

    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            abort(401)

        allowed_roles = ["user", "admin", "superadmin"]
        if g.user.get_role() not in allowed_roles:
            abort(401)

        return f(*args, **kwargs)

    return decorated_function


def check_admin_role_or_own_userid(f):
    """Verify if the user has admin rights or requests own user ID

    This decorator function verifies if the role
    of the login user is "admin" or "superadmin"
    or the user request the own user ID.

    It will abort with a 401 response if the user is not admin and the user
    is not the own user ID

    Args:
        f (function): The function to wrap

    Returns:
        function: The decorator functions

    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            abort(401)

        if g.user.get_role() != "admin" and g.user.get_role() != "superadmin":
            if g.user.user_id != kwargs["user_id"]:
                abort(401)

        return f(*args, **kwargs)

    return decorated_function


def very_superadmin_role(f):
    """Verify if the user has superadmin rights

    This decorator function verifies if the role of
    of the login user is "superadmin".

    It will abort with a 401 response if the user is not superadmin

    Args:
        f (function): The function to wrap

    Returns:
        function: The decorator functions

    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            abort(401)

        if g.user.get_role() != "superadmin":
            abort(401)

        return f(*args, **kwargs)

    return decorated_function


def check_user_permissions(f):
    """Check the user permissions

    This decorator function verifies the user permissions
    to access projects, mapsets and modules.

    The function arguments are checked if they contain:

        - project_name
        - mapset_name
        - module_name

    The user role admin can access everything.

    Args:
        f (function): The function to wrap

    Returns:
        function: The decorator functions

    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        project_name = None
        mapset_name = None
        module_name = None

        if "project_name" in kwargs:
            project_name = kwargs["project_name"]

        if "mapset_name" in kwargs:
            mapset_name = kwargs["mapset_name"]

        if "module_name" in kwargs:
            module_name = kwargs["module_name"]

        ret = check_project_mapset_module_access(
            user_credentials=g.user.get_credentials(),
            config=global_config,
            project_name=project_name,
            mapset_name=mapset_name,
            module_name=module_name,
        )
        if ret is not None:
            message_logger = MessageLogger()
            message_logger.error(str(ret[1]))
            abort(ret[0], str(ret[1]))

        return f(*args, **kwargs)

    return decorated_function


def check_project_mapset_module_access(
    user_credentials,
    config,
    project_name=None,
    mapset_name=None,
    module_name=None,
):
    """Check the user permissions to access projects, mapsets and modules.

    If the user has an admin or superadmin role, the tests are skipped.

    Args:
        user_credentials (dict): The user credentials dictionary
        config (actinia_core.core.common.config.Configuration): The actinia
                                                                configuration
        project_name (str): Name of the project to access
        mapset_name (str): Name of the mapset to access
        module_name (str): Name of the module to access

    Returns:
        tuple:
        In case of missing permissions a tuple with HTTP status
        code and a dict with status and message entries
        or "None" if the user has all required permissions or is admin

    """

    # Admin is allowed to do anything
    if (
        user_credentials["user_role"] == "admin"
        or user_credentials["user_role"] == "superadmin"
    ):
        return None

    # Mapset without project results in error
    if project_name is None and mapset_name is not None:
        resp = {
            "Status": "error",
            "Messages": "Internal error, mapset definition without project",
        }
        return (500, resp)

    if project_name:
        # Check if the project exists in the global database, if not return
        grass_data_base = config.GRASS_DATABASE
        project_path = os.path.join(grass_data_base, project_name)
        if (
            os.path.exists(project_path) is False
            or os.path.isdir(project_path) is False
            or os.access(project_path, os.R_OK & os.X_OK) is False
        ):
            return None

        # Check if the mapset exists in the global project, if not return
        if mapset_name:
            mapset_path = os.path.join(project_path, mapset_name)

            if (
                os.path.exists(mapset_path) is False
                or os.path.isdir(mapset_path) is False
                or os.access(mapset_path, os.R_OK & os.X_OK) is False
            ):
                return None

        # Check permissions to the global database projects and mapsets
        accessible_datasets = user_credentials["permissions"][
            "accessible_datasets"
        ]

        if project_name not in accessible_datasets:
            resp = {
                "Status": "error",
                "Messages": "Unauthorized access to project <%s>"
                % project_name,
            }
            return (401, resp)

        # Check if the mapset is allowed to be accessed
        if mapset_name:
            # Check if the mapset exists in the global database
            if (
                not accessible_datasets[project_name]
                or mapset_name not in accessible_datasets[project_name]
            ):
                resp = {
                    "Status": "error",
                    "Messages": "Unauthorized access to mapset "
                    "<%s> in project <%s>" % (mapset_name, project_name),
                }
                return (401, resp)

    # Check if the module name is in the access list
    if module_name:
        accessible_modules = user_credentials["permissions"][
            "accessible_modules"
        ]
        if module_name not in accessible_modules:
            resp = {
                "Status": "error",
                "Messages": "Module <%s> is not supported" % module_name,
            }
            return (401, resp)

    return None
