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
Keycloak user management

TODO:
"""

from keycloak import KeycloakOpenID
from jose.exceptions import ExpiredSignatureError

from actinia_core.core.common.user_base import (
    ActiniaUserBase,
    # ActiniaUserError,
)
from actinia_core.core.logging_interface import log
# from actinia_core.core.common.config import global_config

__author__ = "Anika Weinmann"
__copyright__ = (
    "Copyright 2022, mundialis GmbH & Co. KG"
)


USER_ROLES = ["superadmin", "admin", "user", "guest"]


class ActiniaKeycloakUser(ActiniaUserBase):
    """
    The Actinia Core keycloak user management class

    This class manages the user which are stored in keycloak
    """

    @staticmethod
    def verify_keycloak_token(token):
        # TODO read from config
        keycloak_url = "http://keycloak:8080/auth/"
        realm = "actinia-realm"
        client_id = "actinia-client"
        client_secret_key = "KCXeHuJCLfd8qIhwIYkWZLrkauzBkLAb"

        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm,
            client_secret_key=client_secret_key
        )
        KEYCLOAK_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\n" + \
            keycloak_openid.public_key() + "\n-----END PUBLIC KEY-----"
        options = {
            "verify_signature": True,
            "verify_aud": True,
            "verify_exp": True
        }
        try:
            token_info = keycloak_openid.decode_token(
                token, key=KEYCLOAK_PUBLIC_KEY, options=options
            )
        except ExpiredSignatureError:
            return None
        except Exception:
            return None
        user_id = token_info["preferred_username"]
        kwargs = {
            "user_role": token_info["resource_access"][client_id]["roles"][0],
            "cell_limit": token_info["cell_limit"],
            "process_num_limit": token_info["process_num_limit"],
            "process_time_limit": token_info["process_time_limit"],
        }
        if (token_info["accessible_datasets"] and
                token_info["accessible_datasets"] != "None"):
            kwargs["accessible_datasets"] = token_info["accessible_datasets"]
        if (token_info["accessible_modules"] and
                token_info["accessible_modules"] != "None"):
            kwargs["accessible_modules"] = token_info["accessible_modules"]
        GROUP_PREFIX = "/actinia-user/"  # TODO set it in config
        groups = list()
        for group in token_info["groups"]:
            if group.startswith(GROUP_PREFIX):
                groups.append(group.replace(GROUP_PREFIX, ""))
        if len(groups) == 0:
            log.error(
                f"Authentication ERROR: User {user_id} has no user group."
            )
            return None
        elif len(groups) > 1:
            log.warning(
                f"User {user_id} has more than one group taking {groups[0]}."
            )
        kwargs["user_group"] = groups[0]
        user = ActiniaKeycloakUser(
            user_id,
            **kwargs,
        )
        user._generate_permission_dict()
        return user

    # def read_from_db(self):
    #
    #     creds = self.db.get_credentials(self.user_id)
    #     self.user_role = self.get_role()
    #     self.user_group = self.get_group()
    #     self.password_hash = self.get_password_hash()
    #
    #     self.permissions = creds["permissions"]
    #     self.cell_limit = creds["permissions"]["cell_limit"]
    #     self.accessible_datasets = creds["permissions"]["accessible_datasets"]
    #     self.accessible_modules = creds["permissions"]["accessible_modules"]
    #     self.process_num_limit = creds["permissions"]["process_num_limit"]
    #     self.process_time_limit = creds["permissions"]["process_time_limit"]

    # def exists(self):
    #     """Check if the user exists
    #
    #     Returns:
    #         bool:
    #         True if the user exists, False otherwise
    #     """
    #     if self.user_id is None:
    #         return False
    #
    #     return self.db.exists(self.user_id)

    # def get_role(self): # ???
    #     """Return the role from the database
    #
    #     Returns:
    #         str:
    #         Return the role from the database
    #     """
    #     return self.db.get_role(self.user_id)

    def get_group(self):
        """Return the user group

        Returns:
            str:
            Return the user group
        """
        return self.user_group

    def get_credentials(self):
        """Return the user credentials as a dictionary

        Returns:
            dict:
            Return the user credentials as a dictionary
        """
        self._generate_permission_dict()
        credentials = {
            "user_id": self.user_id,
            "user_role": self.user_role,
            "user_group": self.user_group,
            "permissions": self.permissions,
        }
        return credentials

    # def get_accessible_datasets(self):
    #     """Return a dictionary of location:mapset list entries
    #
    #     Returns:
    #         dict:
    #         Return a dictionary of location:mapset list entries
    #     """
    #
    #     self.permissions = self.db.get_credentials(self.user_id)["permissions"]
    #
    #     if self.permissions and "accessible_datasets" in self.permissions:
    #         return self.permissions["accessible_datasets"]

    # def get_accessible_modules(self):
    #     """Return a list of all accessible modules
    #
    #     Returns:
    #         list:
    #         Return a list of all accessible modules
    #     """
    #
    #     self.permissions = self.db.get_credentials(self.user_id)["permissions"]
    #
    #     if self.permissions and "accessible_modules" in self.permissions:
    #         return self.permissions["accessible_modules"]

    # def get_cell_limit(self):
    #     """Return the cell limit
    #
    #     Returns:
    #         int:
    #         The value or None if nothing was found
    #     """
    #
    #     self.permissions = self.db.get_credentials(self.user_id)["permissions"]
    #
    #     if self.permissions and "cell_limit" in self.permissions:
    #         return self.permissions["cell_limit"]

    # def get_process_num_limit(self):
    #     """Return the process number limit
    #
    #     Returns:
    #         int:
    #         The value or None if nothing was found
    #     """
    #
    #     self.permissions = self.db.get_credentials(self.user_id)["permissions"]
    #
    #     if self.permissions and "process_num_limit" in self.permissions:
    #         return self.permissions["process_num_limit"]

    # def get_process_time_limit(self):
    #     """Return the process time limit
    #
    #     Returns:
    #         int:
    #         The value or None if nothing was found
    #     """
    #
    #     self.permissions = self.db.get_credentials(self.user_id)["permissions"]
    #
    #     if self.permissions and "process_time_limit" in self.permissions:
    #         return self.permissions["process_time_limit"]

    # def commit(self):
    #     """Commit the user to the database
    #
    #     All internal variables must be initialized:
    #
    #         self.user_id
    #         self.user_group
    #         self.password_hash
    #         self.user_role
    #
    #     Returns:
    #         bool:
    #         True in case of success, False otherwise
    #     """
    #     if self.user_id is None:
    #         return False
    #     if self.user_group is None:
    #         return False
    #     if self.password_hash is None:
    #         return False
    #     if self.user_role is None:
    #         return False
    #
    #     self._generate_permission_dict()
    #
    #     ret = self.db.add(
    #         user_id=self.user_id,
    #         user_group=self.user_group,
    #         password_hash=self.password_hash,
    #         user_role=self.user_role,
    #         permissions=self.permissions,
    #     )
    #     return ret

    # def update(self):
    #     """Update the user to the database
    #
    #     This variable mus be initialized beforehand:
    #
    #         self.user_id
    #
    #     Only the internal variables that should be updates must be initialized:
    #
    #         self.user_group
    #         self.password_hash
    #         self.user_role
    #         self.permissions
    #
    #     Returns:
    #         bool:
    #         True in case of success, False otherwise
    #     """
    #     if self.user_id is None:
    #         return False
    #
    #     self._generate_permission_dict()
    #
    #     ret = self.db.update(
    #         user_id=self.user_id,
    #         user_group=self.user_group,
    #         password_hash=self.password_hash,
    #         user_role=self.user_role,
    #         permissions=self.permissions,
    #     )
    #     return ret

    # def list_all_users(self):
    #     """List all users in the database
    #
    #     Returns:
    #         list:
    #         List of all users
    #     """
    #     return self.db.list_all_ids()

    # def delete(self):
    #     """
    #     Delete a user from the user database
    #
    #     Returns:
    #         bool:
    #         True if success, False otherwise
    #     """
    #
    #     if self.exists():
    #         return self.db.delete(self.user_id)
    #
    #     return False

    # @staticmethod
    # def create_user(
    #     user_id,
    #     user_group,
    #     password,
    #     user_role="user",
    #     accessible_datasets={
    #         "nc_spm_08": ["PERMANENT", "user1", "landsat"],
    #         "ECAD": ["PERMANENT"],
    #         "latlong_wgs84": ["PERMANENT"],
    #     },
    #     accessible_modules=global_config.MODULE_ALLOW_LIST,
    #     cell_limit=global_config.MAX_CELL_LIMIT,
    #     process_num_limit=global_config.PROCESS_NUM_LIMIT,
    #     process_time_limit=global_config.PROCESS_TIME_LIMT,
    # ):
    #     """Create a new user object and initialize it
    #
    #     Args:
    #         user_id (str): The id (name, email, ..) of the user that must be
    #                        unique
    #         user_group (str): The group of the user
    #         user_role (str): The password
    #         accessible_datasets (dict): The user role (admin, user, guest)
    #         accessible_modules (list): Dict of location:mapset lists
    #         cell_limit (int): Maximum number of cells to process
    #         process_num_limit (int): The maximum number of processes the user
    #                                  is allowed to run in a single chain
    #         process_time_limit (int): The maximum number of seconds a user
    #                                   process is allowed to run
    #
    #     Returns:
    #         actinia_core_api.common.user.ActiniaKeycloakUser:
    #         A new user object in case of success, or None in case of failure
    #
    #     """
    #     user = ActiniaKeycloakUser(
    #         user_id=user_id,
    #         user_group=user_group,
    #         user_role=user_role,
    #         accessible_datasets=accessible_datasets,
    #         accessible_modules=accessible_modules,
    #         cell_limit=cell_limit,
    #         process_num_limit=process_num_limit,
    #         process_time_limit=process_time_limit,
    #     )
    #     user.hash_password(password)
    #
    #     if user.commit() is True:
    #         return user
    #     return None
