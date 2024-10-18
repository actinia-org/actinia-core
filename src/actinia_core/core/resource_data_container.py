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
Resource Data Container
"""
from .storage_interface_filesystem import ResourceStorageFilesystem
from .storage_interface_aws_s3 import ResourceStorageS3
from .storage_interface_gcs import ResourceStorageGCS

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ResourceDataContainer(object):
    """Class that manages the data send from the resource
    to the enqueued asynchronous processing object
    """

    def __init__(
        self,
        grass_data_base,
        grass_user_data_base,
        grass_base_dir,
        request_data,
        user_id,
        user_group,
        resource_id,
        iteration,
        status_url,
        api_info,
        resource_url_base,
        orig_time,
        orig_datetime,
        user_credentials,
        config,
        project_name,
        mapset_name,
        map_name,
    ):
        """

        Args:
            grass_data_base (str): GRASS GIS database root directory that
                                   contains global projects
            grass_user_data_base (str): GRASS GIS database user directory that
                                        contains group specific projects
            grass_base_dir (str): The installation directory of GRASS GIS
            request_data (dict): The module chain dictionary
            user_id (str): The user id
            user_group (str): The user group
            resource_id (str): The id of the resource
            iteration (int): The iteartion of the job
            status_url (str): The url to be used to create the status response
            api_info (ApiInfoModel): Information about the API call
            resource_url_base (str): The base URL for resources
            orig_time (time): The time of origin (seconds)
            orig_datetime (datetime): The datetime of origin (datetime format)
            user_credentials (dict): The user credentials dict
            config (actinia_core.core.config.Configuration): The actinia
                                                             configuration
            project_name (str): The name of the project to work in
            mapset_name (str): The name of the target mapset in which the
                               computation should be performed
            map_name: The name of the map or other resource (raster, vector,
                      STRDS, color, ...)

        """

        self.grass_data_base = grass_data_base
        self.grass_user_data_base = grass_user_data_base
        self.grass_base_dir = grass_base_dir
        self.request_data = request_data
        self.user_id = user_id
        self.user_group = user_group
        self.resource_id = resource_id
        self.iteration = iteration
        self.status_url = status_url
        self.api_info = api_info
        self.resource_url_base = resource_url_base
        self.user_credentials = user_credentials
        self.config = config
        self.project_name = project_name
        self.mapset_name = mapset_name
        self.map_name = map_name
        self.orig_time = orig_time
        self.orig_datetime = orig_datetime
        self.user_data = None
        self.storage_model = "file"
        self.queue = None

    # def __str__(self):
    #    return str(self.__dict__)

    def set_user_data(self, user_data):
        """Put all required data for processing into the data object

        Args:
            user_data: Any payload that must be passed in addition tot the
                       request data, like command arguments and so on

        """
        self.user_data = user_data

    def set_request_data(self, request_data):
        self.request_data = request_data

    def set_queue_name(self, queue_name):
        self.queue = queue_name

    def set_storage_model_to_file(self):
        self.storage_model = "file"

    def set_storage_model_to_s3(self):
        self.storage_model = "s3"

    def set_storage_model_to_gcs(self):
        self.storage_model = "gcs"

    def get_storage_model(self):
        return self.storage_model

    def is_storage_model_file(self):
        return self.storage_model == "file"

    def is_storage_model_s3(self):
        return self.storage_model == "s3"

    def is_storage_model_gcs(self):
        return self.storage_model == "gcs"

    def create_storage_interface(self):
        """Create the storage interface

        Returns: Either ResourceStorageFilesystem, ResourceStorageGCS or
                 ResourceStorageS3
        """
        if self.is_storage_model_file():
            return ResourceStorageFilesystem(
                user_id=self.user_id,
                resource_id=self.resource_id,
                config=self.config,
                resource_url_base=self.resource_url_base,
            )

        if self.is_storage_model_s3():
            return ResourceStorageS3(
                user_id=self.user_id,
                resource_id=self.resource_id,
                config=self.config,
            )

        if self.is_storage_model_gcs():
            return ResourceStorageGCS(
                user_id=self.user_id,
                resource_id=self.resource_id,
                config=self.config,
            )
