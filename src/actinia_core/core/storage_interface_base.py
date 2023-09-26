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
from abc import ABCMeta, abstractmethod

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ResourceStorageBase(object):
    """Abstract storage base class of generated resources"""

    __metaclass__ = ABCMeta

    def __init__(self, user_id, resource_id, config):
        """Abstract storage base class of generated resources

        Args:
            user_id: The user id
            resource_id: The resource id
            config: The configuration of actinia core
        """

        self.user_id = user_id
        self.resource_id = resource_id
        self.config = config
        self.resource_url_list = []
        self.resource_file_list = []

    @abstractmethod
    def setup(self):
        """Setup the resource storage"""
        pass

    @abstractmethod
    def get_resource_urls(self):
        """Return all resource urls that were generated when storing a resource
        on disk

        Returns:
            (list): A list of urls

        """
        return self.resource_url_list

    @abstractmethod
    def store_resource(self, file_path):
        """Store a resource (file) at the user resource storage and return an
        URL to the resource accessible via HTTP

        Args:
            file_path:

        Returns:
            (str): the resource url that points to the stored resource

        """
        pass

    @abstractmethod
    def remove_resources(self):
        """Remove all stored resources"""
        pass
