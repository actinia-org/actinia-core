# -*- coding: utf-8 -*-
"""
Storage base class
"""
from abc import ABCMeta, abstractmethod

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class ResourceStorageBase(object):
    """Abstract storage base class of generated resources

    """
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
        """Setup the resource storage
        """
        pass

    @abstractmethod
    def get_resource_urls(self):
        """Return all resource urls that were generated when storing a resource on disk

        Returns:
            (list): A list of urls

        """
        return self.resource_url_list

    @abstractmethod
    def store_resource(self, file_path):
        """Store a resource (file) at the user resource storage and return an URL to the resource accessible via HTTP

        Args:
            file_path:

        Returns:
            (str): the resource url that points to the stored resource

        """
        pass

    @abstractmethod
    def remove_resources(self):
        """Remove all stored resources
        """
        pass
