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
import datetime
from google.cloud import storage
from .storage_interface_base import ResourceStorageBase

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ResourceStorageGCS(ResourceStorageBase):
    """
    Storage class of generated resources to be put in a Google Cloud Storage
    bucket
    """

    def __init__(self, user_id, resource_id, config):
        """
        Storage class of generated resources to be put in a Google Cloud
        Storage bucket

        Args:
            user_id: The user id
            resource_id: The resource id
            config: The configuration of Actinia Core
        """
        ResourceStorageBase.__init__(self, user_id, resource_id, config)

        self.storage_client = None
        self.bucket_name = self.config.GCS_RESOURCE_BUCKET

    def setup(self):
        """
        Setup the Google Cloud Storage (GCS) client and the GCS credentials
        """
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
            self.config.GOOGLE_APPLICATION_CREDENTIALS
        )
        self.storage_client = storage.Client()

    def get_resource_urls(self):
        """Return all resource urls that were generated

        Returns:
            (list): A list of urls

        """
        return self.resource_url_list

    def store_resource(self, file_path):
        """Store a resource (file) at the user resource storage and return an
        URL to the resource accessible via HTTP(S)

        Args:
            file_path:

        Returns:
            (str): the resource url that points to the stored resource
        """

        file_name = os.path.basename(file_path)
        object_path = os.path.join(self.user_id, self.resource_id, file_name)

        if not self.bucket_name:
            Exception("No storage bucket was defined")

        bucket = self.storage_client.get_bucket(self.bucket_name)
        blob = bucket.blob(object_path)
        blob.upload_from_filename(file_path)

        # Generate a persistent URL from the Bucket
        url = blob.generate_signed_url(
            # This URL is valid for 10 days
            expiration=datetime.timedelta(days=10),
            # Allow GET requests using this URL.
            method="GET",
        )

        self.resource_file_list.append(object_path)
        self.resource_url_list.append(url)
        return url

    def remove_resources(self):
        """Remove the resource export path and everything inside"""
        for blob_name in self.resource_file_list:
            bucket = self.storage_client.get_bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
