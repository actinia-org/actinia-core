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
import boto3
from .storage_interface_base import ResourceStorageBase

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ResourceStorageS3(ResourceStorageBase):
    """Storage class of generated resources to be put in a AWS S3 bucket"""

    def __init__(self, user_id, resource_id, config):
        """Storage class of generated resources to be put in a AWS S3 bucket

        Args:
            user_id: The user id
            resource_id: The resource id
            config: The configuration of Actinia Core
        """
        ResourceStorageBase.__init__(self, user_id, resource_id, config)

        self.s3_client = None
        self.session = None
        self.bucket_name = self.config.S3_AWS_RESOURCE_BUCKET

    def setup(self):
        """Setup the AWS S3 botot3 client and the AWS login credentials"""

        self.session = boto3.Session(
            region_name=self.config.S3_AWS_DEFAULT_REGION,
            aws_access_key_id=self.config.S3_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.config.S3_AWS_SECRET_ACCESS_KEY,
        )
        self.s3_client = self.session.client("s3")

    def get_resource_urls(self):
        """Return all resource urls that were generated when storing a resource
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

        Returns:
            (str): the resource url that points to the stored resource

        """

        file_name = os.path.basename(file_path)
        object_path = os.path.join(self.user_id, self.resource_id, file_name)

        # Upload the file and show the progress
        self.s3_client.upload_file(file_path, self.bucket_name, object_path)

        # Generate a persistent URL from the Bucket
        url = self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket_name, "Key": object_path},
        )

        self.resource_file_list.append(object_path)
        self.resource_url_list.append(url)
        return url

    def remove_resources(self):
        """Remove the resource export path and everything inside"""
        for s3_object in self.resource_file_list:
            self.s3_client.delete_object(
                Bucket=self.bucket_name, Key=s3_object
            )
