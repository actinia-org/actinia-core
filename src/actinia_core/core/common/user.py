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
User management

TODO: User update must be implemented
"""

from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer,
                          BadSignature, SignatureExpired)
from itsdangerous import JSONWebSignatureSerializer
from actinia_core.core.common.config import global_config
from actinia_core.core.redis_user import redis_user_interface

__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


USER_ROLES = ["superadmin",
              "admin",
              "user",
              "guest"]


class ActiniaUserError(Exception):
    """Raise this exception in case a user creation error happens
    """
    def __init__(self, message):
        message = "%s:  %s" % (str(self.__class__.__name__), message)
        Exception.__init__(self, message)


class ActiniaUser(object):
    """
    The Actinia Core user management class

    This class manages the user which are stored in the
    Redis database
    """

    db = redis_user_interface

    def __init__(self, user_id, user_group=None, user_role=None,
                 accessible_datasets={"nc_spm_08": ["PERMANENT",
                                                    "user1",
                                                    "landsat"],
                                      "ECAD": ["PERMANENT"],
                                      "latlong_wgs84": ["PERMANENT"]},
                 accessible_modules=global_config.MODULE_ALLOW_LIST,
                 cell_limit=global_config.MAX_CELL_LIMIT,
                 process_num_limit=global_config.PROCESS_NUM_LIMIT,
                 process_time_limit=global_config.PROCESS_TIME_LIMT):
        """Constructor

        Initialize and create a user object. To commit a new user to the database,
        set all required permissions and call the commit() function.

        To read the data of an existing user, simple initialize the constructor
        with the user_id and call read_from_db().

        Args:
            user_id (str): The id (name, email, ..) of the user that must be unique
            user_group (str): The group of the user
            user_role (str): The user role (superadmin, admin, user, guest)
            accessible_datasets (dict): Dict of location:mapset lists
            accessible_modules (list): A list of modules that are allowed to use
            cell_limit (int): Maximum number of cells to process
            process_num_limit (int): The maximum number of processes the user
                                     is allowed to run in a single chain
            process_time_limit (int): The maximum number of seconds a user
                                      process is allowed to run

        """

        self.user_id = user_id
        self.user_group = user_group
        self.password_hash = None
        self.user_role = None
        self.permissions = None
        self.cell_limit = None
        self.accessible_datasets = {}
        self.accessible_modules = []
        self.process_num_limit = None
        self.process_time_limit = None

        if user_role:
            self.set_role(user_role)
        if accessible_datasets is not None:
            self.set_accessible_datasets(accessible_datasets)
        if accessible_modules is not None:
            self.set_accessible_modules(accessible_modules)
        if cell_limit is not None:
            self.set_cell_limit(cell_limit)
        if process_num_limit is not None:
            self.set_process_num_limit(process_num_limit)
        if process_time_limit is not None:
            self.set_process_time_limit(process_time_limit)

    def _generate_permission_dict(self):
        """Create the permission dictionary
        """

        self.permissions = {"accessible_datasets": self.accessible_datasets,
                            "accessible_modules": self.accessible_modules,
                            "cell_limit": self.cell_limit,
                            "process_num_limit": self.process_num_limit,
                            "process_time_limit": self.process_time_limit}

    def read_from_db(self):

        creds = self.db.get_credentials(self.user_id)
        self.user_role = self.get_role()
        self.user_group = self.get_group()
        self.password_hash = self.get_password_hash()

        self.permissions = creds["permissions"]
        self.cell_limit = creds["permissions"]["cell_limit"]
        self.accessible_datasets = creds["permissions"]["accessible_datasets"]
        self.accessible_modules = creds["permissions"]["accessible_modules"]
        self.process_num_limit = creds["permissions"]["process_num_limit"]
        self.process_time_limit = creds["permissions"]["process_time_limit"]

    def set_role(self, role):
        """Set the user role

        Args:
            role: The user role, can be admin, user or guest

        Raises:
            ActiniaUserError in case the role is not supported

        The following roles are supported:
        USER_ROLES = ["superadmin",
                      "admin",
                      "user",
                      "guest"]
        """
        if role not in USER_ROLES:
            raise ActiniaUserError(
                "Unsupported user role <%s> supported are %s" % (role, str(USER_ROLES)))
        self.user_role = role

    def has_guest_role(self):
        return self.get_role() == "guest"

    def has_user_role(self):
        return self.get_role() == "user"

    def has_admin_role(self):
        return self.get_role() == "admin"

    def has_superadmin_role(self):
        return self.get_role() == "superadmin"

    def set_group(self, group):
        """Set the user group

        Args:
            group: The user group

        """
        self.user_group = group

    def set_accessible_datasets(self, accessible_datasets):
        """Set the accessible datasets

        Args:
            accessible_datasets (dict):

        Example::

            {"nc_spm_08":["PERMANENT",
                          "user1",
                          "landsat"],
             "utm32N":["PERMANENT",
                       "sentinel2_bonn"]
            }

        """
        self.accessible_datasets = accessible_datasets

    def add_accessible_dataset(self, location_name, mapset_list):
        """Add a dataset to the accessible datasets

        If the dataset exists, the mapsets will be extended by the provided list

        Args:
            location_name (str): Location name
            mapset_list (list): List of mapset names

        Example::

            location_name="nc_spm_08"

            mapset_list = ["PERMANENT",
                          "user1",
                          "landsat"]

        """

        if location_name not in self.accessible_datasets:
            self.accessible_datasets[location_name] = mapset_list
        else:
            for mapset in mapset_list:
                if mapset not in self.accessible_datasets[location_name]:
                    self.accessible_datasets[location_name].append(mapset)

    def remove_mapsets_from_location(self, location_name, mapset_list):
        """Remove mapsets from an existing location

        Args:
            location_name (str): Location name
            mapset_list (list): List of mapset names that should be removed

        Example::

            location_name="nc_spm_08"

            mapset_list = ["landsat",]

        """

        if location_name in self.accessible_datasets:
            for mapset in mapset_list:
                if mapset in self.accessible_datasets[location_name]:
                    self.accessible_datasets[location_name].remove(mapset)

    def remove_location(self, location_name):
        """Remove a location from the accessible datasets

        Args:
            location_name (str): Location name

        Example::

            location_name="nc_spm_08"

        """

        if location_name in self.accessible_datasets:
            self.accessible_datasets.pop(location_name)

    def set_accessible_modules(self, accessible_modules):
        """Set the accessible modules

        Args:
            accessible_modules (list): A list of module names

        Example::

            ["g.region", "i.vi"]

        """
        self.accessible_modules = accessible_modules

    def add_accessible_modules(self, module_names):
        """Set the accessible modules

        Args:
            module_names (list): A list of module names

        Example::

            ["g.region", "i.vi"]

        """
        for name in module_names:
            if name not in self.accessible_modules:
                self.accessible_modules.append(name)

    def remove_accessible_modules(self, module_names):
        """Remove accessible modules from the list

        Args:
            module_names (list): A list of module names that should be removed

        Example::

            ["g.region", "i.vi"]

        """
        for name in module_names:
            if name in self.accessible_modules:
                self.accessible_modules.remove(name)

    def set_cell_limit(self, cell_limit):
        """Set the maximum number of cells that the user is allowed to process

        Args:
            cell_limit (int):

        Raises:
            ActiniaUserError in case the cell_limit is not supported
        """

        try:
            self.cell_limit = int(cell_limit)
        except Exception:
            raise ActiniaUserError("Wrong format for cell limit")

    def set_process_num_limit(self, process_num_limit):
        """Set the maximum number of processes that the user is allowed to run
        in a single process chain

        Args:
            process_num_limit (int):

        Raises:
            ActiniaUserError in case the cell_limit is not supported
        """

        try:
            self.process_num_limit = int(process_num_limit)
        except Exception:
            raise ActiniaUserError("Wrong format for process_num_limit")

    def set_process_time_limit(self, process_time_limit):
        """Set the maximum number of seconds that the user is allowed to run
        a single process

        Args:
            process_time_limit (int):

        Raises:
            ActiniaUserError in case the process_time_limit is not supported
        """

        try:
            self.process_time_limit = int(process_time_limit)
        except Exception:
            raise ActiniaUserError("Wrong format for process_time_limit")

    def __str__(self):
        creds = self.get_credentials()

        string = ""

        for entry in creds:
            if entry == "password_hash":
                continue
            string += entry + ": " + str(creds[entry]) + "\n"

        return(string)

    def exists(self):
        """Check if the user exists

        Returns:
            bool:
            True if the user exists, False otherwise
        """
        if self.user_id is None:
            return False

        return self.db.exists(self.user_id)

    def get_id(self):
        return self.user_id

    def verify_password(self, password):
        """
        Verify the provided password with the stored passord hash

        Args:
            password (str):

        Returns:
            bool:
            True if success, False otherwise
        """
        return pwd_context.verify(password, self.get_password_hash())

    def get_role(self):
        """Return the role from the database

        Returns:
            str:
            Return the role from the database
        """
        return self.db.get_role(self.user_id)

    def get_group(self):
        """Return the user group from the database

        Returns:
            str:
            Return the user group from the database
        """
        return self.db.get_group(self.user_id)

    def get_credentials(self):
        """Return the user credentials as a dictionary

        Returns:
            dict:
            Return the user credentials as a dictionary
        """
        return self.db.get_credentials(self.user_id)

    def get_accessible_datasets(self):
        """Return a dictionary of location:mapset list entries

        Returns:
            dict:
            Return a dictionary of location:mapset list entries
        """

        self.permissions = self.db.get_credentials(self.user_id)["permissions"]

        if self.permissions and "accessible_datasets" in self.permissions:
            return self.permissions["accessible_datasets"]

    def get_accessible_modules(self):
        """Return a list of all accessible modules

        Returns:
            list:
            Return a list of all accessible modules
        """

        self.permissions = self.db.get_credentials(self.user_id)["permissions"]

        if self.permissions and "accessible_modules" in self.permissions:
            return self.permissions["accessible_modules"]

    def get_cell_limit(self):
        """Return the cell limit

        Returns:
            int:
            The value or None if nothing was found
        """

        self.permissions = self.db.get_credentials(self.user_id)["permissions"]

        if self.permissions and "cell_limit" in self.permissions:
            return self.permissions["cell_limit"]

    def get_process_num_limit(self):
        """Return the process number limit

        Returns:
            int:
            The value or None if nothing was found
        """

        self.permissions = self.db.get_credentials(self.user_id)["permissions"]

        if self.permissions and "process_num_limit" in self.permissions:
            return self.permissions["process_num_limit"]

    def get_process_time_limit(self):
        """Return the process time limit

        Returns:
            int:
            The value or None if nothing was found
        """

        self.permissions = self.db.get_credentials(self.user_id)["permissions"]

        if self.permissions and "process_time_limit" in self.permissions:
            return self.permissions["process_time_limit"]

    def get_password_hash(self):
        """Return the password hash from the database

        Returns:
            int:
            Return the password hash from the database
        """
        return self.db.get_password_hash(self.user_id)

    def generate_api_key(self):
        """Generate an API key based on the user id

        Returns:
            str:
            API key
        """
        s = JSONWebSignatureSerializer(global_config.SECRET_KEY)
        return s.dumps({"user_id": self.user_id})

    def generate_auth_token(self, expiration=86400):
        """Generate an authentication token with a specific expiration time

        Args:
            expiration ()int: Time in seconds, default 86400s -> one day

        Returns:
            str:
            The auth token
        """
        s = TimedJSONWebSignatureSerializer(global_config.SECRET_KEY,
                                            expires_in=expiration)
        return s.dumps({'user_id': self.user_id})

    def commit(self):
        """Commit the user to the database

        All internal variables must be initialized:

            self.user_id
            self.user_group
            self.password_hash
            self.user_role

        Returns:
            bool:
            True in case of success, False otherwise
        """
        if self.user_id is None:
            return False
        if self.user_group is None:
            return False
        if self.password_hash is None:
            return False
        if self.user_role is None:
            return False

        self._generate_permission_dict()

        ret = self.db.add(user_id=self.user_id,
                          user_group=self.user_group,
                          password_hash=self.password_hash,
                          user_role=self.user_role,
                          permissions=self.permissions)
        return ret

    def update(self):
        """Update the user to the database

        This variable mus be initialized beforehand:

            self.user_id

        Only the internal variables that should be updates must be initialized:

            self.user_group
            self.password_hash
            self.user_role
            self.permissions

        Returns:
            bool:
            True in case of success, False otherwise
        """
        if self.user_id is None:
            return False

        self._generate_permission_dict()

        ret = self.db.update(user_id=self.user_id,
                             user_group=self.user_group,
                             password_hash=self.password_hash,
                             user_role=self.user_role,
                             permissions=self.permissions)
        return ret

    def hash_password(self, password):
        """Create a password hash and store it in the object

        Args:
            password (str):

        """
        self.password_hash = pwd_context.hash(password)

    def list_all_users(self):
        """List all users in the database

        Returns:
            list:
            List of all users
        """
        return self.db.list_all_ids()

    def delete(self):
        """
        Delete a user from the user database

        Returns:
            bool:
            True if success, False otherwise
        """

        if self.exists():
            return self.db.delete(self.user_id)

        return False

    @staticmethod
    def verify_api_key(api_key):
        """Verify an API key based on the user name

        Returns:
            Actinia Core_api.common.user.ActiniaUser:
            A user object is success or None
        """
        s = JSONWebSignatureSerializer(global_config.SECRET_KEY)

        try:
            data = s.loads(api_key)
        except BadSignature:
            return None

        user = ActiniaUser(data["user_id"])
        if user.exists():
            return user

        return None

    @staticmethod
    def verify_auth_token(token):
        s = TimedJSONWebSignatureSerializer(global_config.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = ActiniaUser(data['user_id'])
        if user.exists():
            return user
        return None

    @staticmethod
    def create_user(user_id,
                    user_group,
                    password,
                    user_role="user",
                    accessible_datasets={"nc_spm_08": ["PERMANENT",
                                                       "user1",
                                                       "landsat"],
                                         "ECAD": ["PERMANENT"],
                                         "latlong_wgs84": ["PERMANENT"]},
                    accessible_modules=global_config.MODULE_ALLOW_LIST,
                    cell_limit=global_config.MAX_CELL_LIMIT,
                    process_num_limit=global_config.PROCESS_NUM_LIMIT,
                    process_time_limit=global_config.PROCESS_TIME_LIMT):
        """Create a new user object and initialize it

        Args:
            user_id (str): The id (name, email, ..) of the user that must be unique
            user_group (str): The group of the user
            user_role (str): The password
            accessible_datasets (dict): The user role (admin, user, guest)
            accessible_modules (list): Dict of location:mapset lists
            cell_limit (int): Maximum number of cells to process
            process_num_limit (int): The maximum number of processes the user
                                     is allowed to run in a single chain
            process_time_limit (int): The maximum number of seconds a user
                                      process is allowed to run

        Returns:
            actinia_core_api.common.user.ActiniaUser:
            A new user object in case of success, or None in case of failure

        """
        user = ActiniaUser(user_id=user_id,
                           user_group=user_group,
                           user_role=user_role,
                           accessible_datasets=accessible_datasets,
                           accessible_modules=accessible_modules,
                           cell_limit=cell_limit,
                           process_num_limit=process_num_limit,
                           process_time_limit=process_time_limit)
        user.hash_password(password)

        if user.commit() is True:
            return user
        return None
