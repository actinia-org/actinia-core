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
Storage base class
"""
import os
import shutil
from .storage_interface_base import ResourceStorageBase

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ResourceStorageFilesystem(ResourceStorageBase):
    """Storage class of generated resources at the disk storage that is
    configured in the config file
    """

    def __init__(self, user_id, resource_id, config, resource_url_base=None):
        """Storage class of generated resources at the disk storage that is
        configured in the config file

        Args:
            user_id: The user id
            resource_id: The resource id
            config: The configuration of Actinia Core
            resource_url_base: The base URL name that must be used to create
                               the resource urls
        """
        ResourceStorageBase.__init__(self, user_id, resource_id, config)

        self.resource_url_base = resource_url_base
        self.resource_dir = self.config.GRASS_RESOURCE_DIR
        self.user_export_path = os.path.join(self.resource_dir, self.user_id)
        self.resource_export_path = os.path.join(
            self.user_export_path, self.resource_id
        )
        self.dir_created = False

    def _create_resource_directory(self):
        """Create a new resource directory based on the resource base, the user
        id and the resource id. This directory will contain all exported files
        of the process chain.

        This method will create the directory only once and will ignore
        repeating calls.

        Raises:
            IOError: If the resource path is not accessible.
        """

        if self.dir_created is True:
            return

        # check if the resource base is accessible
        if os.path.isdir(self.resource_dir) and os.access(
            self.resource_dir, os.R_OK | os.X_OK | os.W_OK
        ):
            if os.path.exists(self.user_export_path) is False:
                os.mkdir(self.user_export_path)
                os.chmod(self.user_export_path, 0o0700)

            # Check if the user path can be created if it does not exist
            if os.path.isdir(self.user_export_path) and os.access(
                self.user_export_path, os.R_OK | os.X_OK | os.W_OK
            ):
                # Create the resource directory
                if os.path.exists(self.resource_export_path) is False:
                    os.mkdir(self.resource_export_path)
                    os.chmod(self.resource_export_path, 0o0700)

                # Check access just in case the resource exists
                if os.path.isdir(self.resource_export_path) and os.access(
                    self.resource_export_path, os.R_OK | os.X_OK | os.W_OK
                ):
                    # TODO Add the directory to the scheduler list
                    pass
                else:
                    raise IOError(
                        "Unable to create resource directory <%s>"
                        % self.resource_export_path
                    )
            else:
                raise IOError(
                    "Unable to create resource user directory <%s>"
                    % self.user_export_path
                )
        else:
            raise IOError(
                "Unable to access the base resource directory <%s>"
                % self.resource_dir
            )

        self.dir_created = True

    def setup(self):
        """
        Setup the resource directory to store files in it via store_resource()

        Raises:
            IOError: If the resource path is not accessible.
        """
        self._create_resource_directory()

    def get_resource_urls(self):
        """
        Return all resource urls that were generated when storing a resource
        on disk

        Returns:
            (list): A list of urls

        """
        return self.resource_url_list

    def store_resource(self, file_path):
        """Store a resource (file) at the user resource storage and return an
        URL to the resource accessible via HTTP

        Args:
            file_path:

        Raises:
            IOError: If the resource path is not accessible.

        Returns:
            (str): the resource url that points to the stored resource

        """
        file_name = os.path.basename(file_path)
        export_path = os.path.join(self.resource_export_path, file_name)
        shutil.move(file_path, export_path)
        url = self.resource_url_base.replace("__None__", file_name)

        self.resource_url_list.append(url)
        self.resource_file_list.append(file_path)

        return url

    def remove_resources(self):
        """Remove the resource export path and everything inside"""
        if os.path.exists(self.resource_export_path) and os.path.isdir(
            self.resource_export_path
        ):
            shutil.rmtree(self.resource_export_path, ignore_errors=True)
