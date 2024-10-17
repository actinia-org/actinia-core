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
Keycloak user management

Possible TODOs: add list_all_users, delete, create_user (, exists).
        In this case, keycloak admin console would be needed and actinia would
        need to store keycloak admin credentials!
"""
from keycloak import KeycloakOpenID

from actinia_core.core.common.user_base import (
    ActiniaUserBase,
)
from actinia_core.core.logging_interface import log
from actinia_core.core.common.config import global_config

__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def create_user_from_tokeninfo(token_info):
    """
    Function to create a keycloak user from the keycloak token.
    """
    attr_prefix = (
        global_config.KEYCLOAK_ATTR_PREFIX
        if global_config.KEYCLOAK_ATTR_PREFIX is not None
        else ""
    )
    user_id = token_info["preferred_username"]
    kwargs = {
        "user_role": token_info["resource_access"][
            global_config.KEYCLOAK_CLIENT_ID
        ]["roles"][0],
        "cell_limit": token_info[f"{attr_prefix}cell_limit"],
        "process_num_limit": token_info[f"{attr_prefix}process_num_limit"],
        "process_time_limit": token_info[f"{attr_prefix}process_time_limit"],
    }
    acc_ds_name = f"{attr_prefix}accessible_datasets"
    if token_info[acc_ds_name] and token_info[acc_ds_name] != "None":
        kwargs["accessible_datasets"] = token_info[acc_ds_name]
    acc_mod_name = f"{attr_prefix}accessible_modules"
    if token_info[acc_mod_name] and token_info[acc_mod_name] != "None":
        kwargs["accessible_modules"] = token_info[acc_mod_name]
    groups = list()
    for group in token_info["groups"]:
        if group.startswith(global_config.KEYCLOAK_GROUP_PREFIX):
            groups.append(
                group.replace(global_config.KEYCLOAK_GROUP_PREFIX, "")
            )
    if len(groups) == 0:
        log.error(f"Authentication ERROR: User {user_id} has no user group.")
        return None
    elif len(groups) > 1:
        log.warning(
            f"User {user_id} has more than one group, taking {groups[0]}."
        )
    kwargs["user_group"] = groups[0]
    user = ActiniaKeycloakUser(
        user_id,
        **kwargs,
    )
    user._generate_permission_dict()
    # adding group members
    if "group_members" in token_info and token_info["group_members"]:
        user.set_group_members(
            ",".join(token_info["group_members"]).split(",")
        )
    return user


class ActiniaKeycloakUser(ActiniaUserBase):
    """
    The Actinia Core keycloak user management class

    This class manages a user which is stored in keycloak
    """

    def __init__(
        self,
        user_id,
        user_group=None,
        user_role=None,
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
        if isinstance(accessible_datasets, str):
            datasets = dict()
            lm_list = accessible_datasets.split(",")
            for lm in lm_list:
                if "/" in lm:
                    project, mapset = lm.split("/")
                else:
                    project = lm
                    mapset = None
                if project not in datasets:
                    datasets[project] = []
                datasets[project].append(mapset)
        else:
            datasets = accessible_datasets
        if isinstance(accessible_modules, str):
            modules = accessible_modules.split(",")
        else:
            modules = accessible_modules
        super().__init__(
            user_id,
            user_group=user_group,
            user_role=user_role,
            accessible_datasets=datasets,
            accessible_modules=modules,
            cell_limit=cell_limit,
            process_num_limit=process_num_limit,
            process_time_limit=process_time_limit,
        )
        self.group_members = list()

    @staticmethod
    def verify_keycloak_token(token):
        keycloak_openid = KeycloakOpenID(
            server_url=global_config.KEYCLOAK_URL,
            client_id=global_config.KEYCLOAK_CLIENT_ID,
            realm_name=global_config.KEYCLOAK_REALM,
            client_secret_key=global_config.KEYCLOAK_CLIENT_SECRET_KEY,
        )
        KEYCLOAK_PUBLIC_KEY = (
            "-----BEGIN PUBLIC KEY-----\n"
            + keycloak_openid.public_key()
            + "\n-----END PUBLIC KEY-----"
        )
        options = {
            "verify_signature": True,
            "verify_aud": True,
            "verify_exp": True,
        }
        try:
            token_info = keycloak_openid.decode_token(
                token, key=KEYCLOAK_PUBLIC_KEY, options=options
            )
        except Exception:
            return None
        return create_user_from_tokeninfo(token_info)

    def set_group_members(self, group_members):
        """Set the user group_members

        Args:
            group: The user group_members

        """
        self.group_members = group_members

    def check_group_members(self, user_id):
        """Check if the user_id is in the group_members attribute.

        Args:
            user_id (str): The id (name, email, ..) of the user that must be
                           unique

        Returns:
            bool:
            Return the if the user_id is in the group_members
        """
        return user_id in self.group_members

    # def exists(self):  # rest/user_management ???
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

    def get_role(self):
        """Return the role

        Returns:
            str:
            Return the role
        """
        return self.user_role

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

    def get_accessible_datasets(self):
        """Return a dictionary of project:mapset list entries

        Returns:
            dict:
            Return a dictionary of project:mapset list entries
        """
        self._generate_permission_dict()

        if self.permissions and "accessible_datasets" in self.permissions:
            return self.permissions["accessible_datasets"]

    def get_accessible_modules(self):
        """Return a list of all accessible modules

        Returns:
            list:
            Return a list of all accessible modules
        """
        self._generate_permission_dict()

        if self.permissions and "accessible_modules" in self.permissions:
            return self.permissions["accessible_modules"]

    def get_cell_limit(self):
        """Return the cell limit

        Returns:
            int:
            The value or None if nothing was found
        """
        self._generate_permission_dict()

        if self.permissions and "cell_limit" in self.permissions:
            return self.permissions["cell_limit"]

    def get_process_num_limit(self):
        """Return the process number limit

        Returns:
            int:
            The value or None if nothing was found
        """
        self._generate_permission_dict()

        if self.permissions and "process_num_limit" in self.permissions:
            return self.permissions["process_num_limit"]

    def get_process_time_limit(self):
        """Return the process time limit

        Returns:
            int:
            The value or None if nothing was found
        """
        self._generate_permission_dict()

        if self.permissions and "process_time_limit" in self.permissions:
            return self.permissions["process_time_limit"]
