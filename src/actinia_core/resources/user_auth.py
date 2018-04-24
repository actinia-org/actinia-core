#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
User authentication and credential check.
"""
import os
from functools import wraps

from flask import g, abort, jsonify, make_response
from .common.config import global_config
from .common.app import auth
from .common.user import ActiniaUser
from .common.messages_logger import MessageLogger

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


@auth.verify_password
def verify_password(username_or_token, password):
    """Verify the user name and password.

    Instead of a user name an authentication token
    or an API token can be provided.
    This function is called by the
    @auth.login_required decorator.

    Args:
        username_or_token (str): The username or an authentication token
        password (str): The optional user password, not required in case of token

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
    """Create a dummy user for configuration in which authorization is not required

    Args:
        f (function): The function to wrap

    Returns:
        function: The decorator functions

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Set a default user
        g.user = ActiniaUser(user_id=global_config.DEFAULT_USER,
                           user_group=global_config.DEFAULT_USER_GROUP)

        return f(*args, **kwargs)
    return decorated_function


def very_admin_role(f):
    """Verify if the user has admin rights

    This decorator function verifies if the role of
    of the login user is "admin"  or superadmin.

    It will abort with a 401 response if the user is not admin

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
    to access locations, mapsets and modules.

    The function arguments are checked if they conatin:

        - location_name
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

        location_name = None
        mapset_name = None
        module_name = None

        if "location_name" in kwargs:
            location_name = kwargs["location_name"]

        if "mapset_name" in kwargs:
            mapset_name = kwargs["mapset_name"]

        if "module_name" in kwargs:
            module_name = kwargs["module_name"]

        ret = check_location_mapset_module_access(user_credentials=g.user.get_credentials(),
                                                  config=global_config,
                                                  location_name=location_name,
                                                  mapset_name=mapset_name,
                                                  module_name=module_name)
        if ret is not None:
            message_logger = MessageLogger()
            message_logger.error(str(ret[1]))
            abort(ret[0], str(ret[1]))

        return f(*args, **kwargs)
    return decorated_function


def check_location_mapset_module_access(user_credentials,
                                        config,
                                        location_name=None,
                                        mapset_name=None,
                                        module_name=None):
    """Check the user permissions to access locations, mapsets and modules.

    If the user has an admin or superadmin role, the tests are skipped.

    Args:
        user_credentials (dict): The user credentials dictionary
        config (Actinia Core_api.resources.common.config.Configuration): The Actinia Core configuration
        location_name (str): Name of the location to access
        mapset_name (str): Name of the mapset to access
        module_name (str): Name of the module to access

    Returns:
        tuple:
        In case of missing permissions a tuple with HTTP status
        code and a dict with status and message entries
        or "None" if the user has all required permissions or is admin

    """

    # Admin is allowed to do anything
    if user_credentials["user_role"] == "admin" or user_credentials["user_role"] == "superadmin":
        return None

    # Mapset without location results in error
    if location_name is None and mapset_name is not None:
            resp = {"Status":"error",
                    "Messages":"Internal error, mapset definition without location"}
            return (500, resp)

    if location_name:
        # Check if the location exists in the global database, if not return
        grass_data_base = config.GRASS_DATABASE
        location_path = os.path.join(grass_data_base, location_name)
        if os.path.exists(location_path) is False or \
                        os.path.isdir(location_path) is False or\
                        os.access(location_path, os.R_OK & os.X_OK) is False:
            return None

        # Check if the mapset exists in the global location, if not return
        if mapset_name:
            mapset_path = os.path.join(location_path, mapset_name)

            if os.path.exists(mapset_path) is False or \
                            os.path.isdir(mapset_path) is False or\
                            os.access(mapset_path, os.R_OK & os.X_OK) is False:
                return None

        # Check permissions to the global database locations and mapsets
        accessible_datasets = user_credentials["permissions"]["accessible_datasets"]

        if location_name not in accessible_datasets:
            resp = {"Status":"error",
                    "Messages":"Unauthorized access to location <%s>"%location_name}
            return (401, resp)

        # Check if the mapset is allowed to be accessed
        if mapset_name:
            # Check if the mapset exists in the global database
            if not accessible_datasets[location_name] or \
                            mapset_name not in accessible_datasets[location_name]:
                resp = {"Status":"error",
                        "Messages":"Unauthorized access to mapset <%s> in location <%s>"%(mapset_name,
                                                                                         location_name)}
                return (401, resp)

    # Check if the module name is in the access list
    if module_name:
        accessible_modules = user_credentials["permissions"]["accessible_modules"]
        if module_name not in accessible_modules:
            resp = {"Status":"error",
                    "Messages":"Module <%s> is not supported"%module_name}
            return (401, resp)

    return None
