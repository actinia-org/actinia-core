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
User management base
"""

from actinia_core.core.common.config import global_config

__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

USER_ROLES = ["superadmin", "admin", "user", "guest"]


class ActiniaUserError(Exception):
    """Raise this exception in case a user creation error happens"""

    def __init__(self, message):
        message = "%s:  %s" % (str(self.__class__.__name__), message)
        Exception.__init__(self, message)


class ActiniaUserBase(object):
    """
    The Actinia Core user management base class

    This class manages the user base where the users stored in Redis database
    or keycloak are based on.
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
        """Constructor

        Initialize and create a user object.

        Args:
            user_id (str): The id (name, email, ..) of the user that must be
                           unique
            user_group (str): The group of the user
            user_role (str): The user role (superadmin, admin, user, guest)
            accessible_datasets (dict): Dict of project:mapset lists
            accessible_modules (list): A list of modules that are allowed to
                                       use
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
        """Create the permission dictionary"""

        self.permissions = {
            "accessible_datasets": self.accessible_datasets,
            "accessible_modules": self.accessible_modules,
            "cell_limit": self.cell_limit,
            "process_num_limit": self.process_num_limit,
            "process_time_limit": self.process_time_limit,
        }

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
                "Unsupported user role <%s> supported are %s"
                % (role, str(USER_ROLES))
            )
        self.user_role = role

    def get_role(self):
        return self.user_role

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

    def add_accessible_dataset(self, project_name, mapset_list):
        """Add a dataset to the accessible datasets

        If the dataset exists, the mapsets will be extended by the provided
        list

        Args:
            project_name (str): Project name
            mapset_list (list): List of mapset names

        Example::

            project_name="nc_spm_08"

            mapset_list = ["PERMANENT",
                          "user1",
                          "landsat"]

        """

        if project_name not in self.accessible_datasets:
            self.accessible_datasets[project_name] = mapset_list
        else:
            for mapset in mapset_list:
                if mapset not in self.accessible_datasets[project_name]:
                    self.accessible_datasets[project_name].append(mapset)

    def remove_mapsets_from_project(self, project_name, mapset_list):
        """Remove mapsets from an existing project

        Args:
            project_name (str): Project name
            mapset_list (list): List of mapset names that should be removed

        Example::

            project_name="nc_spm_08"

            mapset_list = ["landsat",]

        """

        if project_name in self.accessible_datasets:
            for mapset in mapset_list:
                if mapset in self.accessible_datasets[project_name]:
                    self.accessible_datasets[project_name].remove(mapset)

    def remove_project(self, project_name):
        """Remove a project from the accessible datasets

        Args:
            project_name (str): Project name

        Example::

            project_name="nc_spm_08"

        """

        if project_name in self.accessible_datasets:
            self.accessible_datasets.pop(project_name)

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

    def get_id(self):
        return self.user_id
