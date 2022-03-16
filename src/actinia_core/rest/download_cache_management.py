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
Download cache management

TODO: Tests required
"""

import os
from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger
import pickle
from actinia_core.rest.ephemeral_processing import EphemeralProcessing
from actinia_core.rest.persistent_processing import PersistentProcessing
from actinia_core.rest.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.common.process_object import Process
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.models.response_models import \
    StorageResponseModel, StorageModel, ProcessingResponseModel
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.core.user_auth import very_admin_role
from actinia_core.core.user_auth import check_user_permissions
from actinia_core.core.common.app import auth

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class SyncDownloadCacheResource(ResourceBase):
    decorators = [log_api_call, check_user_permissions,
                  very_admin_role, auth.login_required]

    @swagger.doc({
        'tags': ['Cache Management'],
        'description': 'Get the current size of the download cache. '
                       'Minimum required user role: admin.',
        'responses': {
            '200': {
                'description': 'The current state of the download cache',
                'schema': StorageResponseModel
            },
            '400': {
                'description': 'The error message why cache information '
                               'gathering did not succeeded',
                'schema': ProcessingResponseModel
            }
        }
    })
    def get(self):
        """Get the current size of the download cache"""
        rdc = self.preprocess(has_json=False, has_xml=False)

        if rdc:
            enqueue_job(self.job_timeout, start_download_cache_size, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['Cache Management'],
        'description': 'Clean the download cache and remove all cached data. '
                       'Minimum required user role: admin.',
        'responses': {
            '200': {
                'description': 'Processing status of cache deletion',
                'schema': StorageResponseModel
            },
            '400': {
                'description': 'The error message why cache cleaning did not succeeded',
                'schema': ProcessingResponseModel
            }
        }
    })
    def delete(self):
        """Clean the download cache and remove all cached data"""
        rdc = self.preprocess(has_json=False, has_xml=False)

        if rdc:
            enqueue_job(self.job_timeout, start_download_cache_remove, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)


def start_download_cache_size(*args):
    processing = DownloadCacheSize(*args)
    processing.run()


class DownloadCacheSize(EphemeralProcessing):
    """Compute the download cache size
    """

    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)
        self.user_download_cache_path = os.path.join(
            self.config.DOWNLOAD_CACHE, self.user_id)
        self.response_model_class = StorageResponseModel

    def _execute(self):

        self._setup()

        if (os.path.exists(self.user_download_cache_path)
                and os.path.isdir(self.user_download_cache_path)):

            executable = "/usr/bin/du"
            args = ["-sb", self.user_download_cache_path]

            self._run_process(Process(exec_type="exec",
                                      executable=executable,
                                      id="compute_download_cache_size",
                                      executable_params=args))
            print("Disk usage ", self.module_output_log[0]["stdout"])
            dc_size = int(self.module_output_log[0]["stdout"].split("\t")[0])
            quota_size = int(self.config.DOWNLOAD_CACHE_QUOTA * 1024 * 1024 * 1024)

            model = StorageModel(
                used=dc_size,
                free=quota_size - dc_size,
                quota=quota_size,
                free_percent=int(100 * (quota_size - dc_size) / quota_size))
            self.module_results = model

            self.finish_message = "Download cache size successfully computed"
        else:
            raise AsyncProcessError(
                "Download cache directory <%s> does not exist."
                % self.user_download_cache_path)


def start_download_cache_remove(*args):
    processing = DownloadCacheDelete(*args)
    processing.run()


class DownloadCacheDelete(PersistentProcessing):
    """Delete the whole download cache directory
    """

    def __init__(self, *args):

        PersistentProcessing.__init__(self, *args)
        self.user_download_cache_path = os.path.join(
            self.config.DOWNLOAD_CACHE, self.user_id)

    def _execute(self):

        self._setup()

        if (os.path.exists(self.user_download_cache_path)
                and os.path.isdir(self.user_download_cache_path)):
            executable = "/bin/rm"
            args = ["-rf", self.user_download_cache_path]

            self._run_process(Process(exec_type="exec",
                                      executable=executable,
                                      id="delete_download_cache_directory",
                                      executable_params=args))

            os.mkdir(self.user_download_cache_path)
            self.finish_message = "Download cache successfully removed."
        else:
            raise AsyncProcessError(
                "Download cache directory <%s> does not exist."
                % self.user_download_cache_path)
