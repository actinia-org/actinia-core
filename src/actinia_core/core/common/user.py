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
User management

TODO: User update must be implemented
"""

from passlib.apps import custom_app_context as pwd_context
import jwt
from datetime import datetime, timezone, timedelta
from actinia_core.core.common.config import global_config
from actinia_core.core.redis_user import redis_user_interface
from actinia_core.core.common.user_base import (
    ActiniaUserBase,
)

__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = "Copyright 2016-2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class ActiniaUser(ActiniaUserBase):
    """
    The Actinia Core user management class

    This class manages the user which are stored in the
    Redis database
    """

    db = redis_user_interface

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

    def __str__(self):
        creds = self.get_credentials()

        string = ""

        for entry in creds:
            if entry == "password_hash":
                continue
            string += entry + ": " + str(creds[entry]) + "\n"

        return string

    def exists(self):
        """Check if the user exists

        Returns:
            bool:
            True if the user exists, False otherwise
        """
        if self.user_id is None:
            return False

        return self.db.exists(self.user_id)

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
        """Return a dictionary of project:mapset list entries

        Returns:
            dict:
            Return a dictionary of project:mapset list entries
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
        api_key = jwt.encode(
            {"user_id": self.user_id},
            global_config.SECRET_KEY,
            algorithm="HS512",
        )

        return api_key

    def generate_auth_token(self, expiration=86400):
        """Generate an authentication token with a specific expiration time

        Args:
            expiration ()int: Time in seconds, default 86400s -> one day

        Returns:
            str:
            The auth token
        """
        exp_date = datetime.now(tz=timezone.utc) + timedelta(
            seconds=expiration
        )
        token = jwt.encode(
            {"user_id": self.user_id, "exp": exp_date},
            global_config.SECRET_KEY,
            algorithm="HS512",
        )
        return token

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

        ret = self.db.add(
            user_id=self.user_id,
            user_group=self.user_group,
            password_hash=self.password_hash,
            user_role=self.user_role,
            permissions=self.permissions,
        )
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

        ret = self.db.update(
            user_id=self.user_id,
            user_group=self.user_group,
            password_hash=self.password_hash,
            user_role=self.user_role,
            permissions=self.permissions,
        )
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
        try:
            data = jwt.decode(
                api_key,
                global_config.SECRET_KEY,
                leeway=timedelta(seconds=10),
                algorithms=["HS512"],
            )
        except jwt.exceptions.DecodeError:
            return None

        if data is None:
            return None
        if "user_id" not in data.keys():
            return None

        user = ActiniaUser(data["user_id"])
        if user.exists():
            return user

        return None

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(
                token,
                global_config.SECRET_KEY,
                leeway=timedelta(seconds=10),
                algorithms=["HS512"],
                options={"require": ["exp"], "verify_exp": True},
            )
        except jwt.exceptions.DecodeError:
            return None
        except jwt.exceptions.ExpiredSignatureError:
            return None

        if data is None:
            return None
        if "user_id" not in data.keys():
            return None

        user = ActiniaUser(data["user_id"])
        if user.exists():
            return user
        return None

    @staticmethod
    def create_user(
        user_id,
        user_group,
        password,
        user_role="user",
        accessible_datasets={
            "nc_spm_08": ["PERMANENT", "user1", "landsat"],
            "ECAD": ["PERMANENT"],
            "latlong_wgs84": ["PERMANENT"],
        },
        accessible_modules=global_config.MODULE_ALLOW_LIST,
        cell_limit=global_config.MAX_CELL_LIMIT,
        process_num_limit=global_config.PROCESS_NUM_LIMIT,
        process_time_limit=global_config.PROCESS_TIME_LIMT,
    ):
        """Create a new user object and initialize it

        Args:
            user_id (str): The id (name, email, ..) of the user that must be
                           unique
            user_group (str): The group of the user
            user_role (str): The password
            accessible_datasets (dict): The user role (admin, user, guest)
            accessible_modules (list): Dict of project:mapset lists
            cell_limit (int): Maximum number of cells to process
            process_num_limit (int): The maximum number of processes the user
                                     is allowed to run in a single chain
            process_time_limit (int): The maximum number of seconds a user
                                      process is allowed to run

        Returns:
            actinia_core_api.common.user.ActiniaUser:
            A new user object in case of success, or None in case of failure

        """
        user = ActiniaUser(
            user_id=user_id,
            user_group=user_group,
            user_role=user_role,
            accessible_datasets=accessible_datasets,
            accessible_modules=accessible_modules,
            cell_limit=cell_limit,
            process_num_limit=process_num_limit,
            process_time_limit=process_time_limit,
        )
        user.hash_password(password)

        if user.commit() is True:
            return user
        return None
