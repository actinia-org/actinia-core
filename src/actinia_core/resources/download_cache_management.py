# -*- coding: utf-8 -*-
"""
Download cache management

TODO: Tests required
"""

import os
from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger

from actinia_core.resources.async_ephemeral_processing import AsyncEphemeralProcessing
from actinia_core.resources.async_persistent_processing import AsyncPersistentProcessing
from actinia_core.resources.async_resource_base import AsyncEphemeralResourceBase
from actinia_core.resources.common.redis_interface import enqueue_job
from actinia_core.resources.common.process_object import Process
from actinia_core.resources.common.exceptions import AsyncProcessError
from actinia_core.resources.common.response_models import StorageResponseModel, StorageModel, ProcessingResponseModel
from actinia_core.resources.common.logging_interface import log_api_call
from actinia_core.resources.user_auth import very_admin_role
from actinia_core.resources.user_auth import check_user_permissions
from actinia_core.resources.common.app import auth

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class SyncDownloadCacheResource(AsyncEphemeralResourceBase):
    decorators = [log_api_call, check_user_permissions,
                  very_admin_role, auth.login_required]

    @swagger.doc({
        'tags': ['download cache management'],
        'description': 'Returns the current size of the download cache. Minimum required user role: admin.',
        'responses': {
            '200': {
                'description': 'The current state of the download cache',
                'schema': StorageResponseModel
            },
            '400': {
                'description': 'The error message why cache information gathering did not succeeded',
                'schema': ProcessingResponseModel
            }
        }
    })
    def get(self):
        """Returns the current size of the download cache"""
        rdc = self.preprocess(has_json=False, has_xml=False)

        enqueue_job(self.job_timeout, start_download_cache_size, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)

    @swagger.doc({
        'tags': ['download cache management'],
        'description': 'Clean the download cache and remove all cached data. Minimum required user role: admin.',
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

        enqueue_job(self.job_timeout, start_download_cache_remove, rdc)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


def start_download_cache_size(*args):
    processing = DownloadCacheSize(*args)
    processing.run()


class DownloadCacheSize(AsyncEphemeralProcessing):
    """Compute the download cache size
    """

    def __init__(self, *args):
        AsyncEphemeralProcessing.__init__(self, *args)
        self.user_download_cache_path = os.path.join(self.config.DOWNLOAD_CACHE, self.user_id)
        self.response_model_class = StorageResponseModel

    def _execute(self):

        self._setup()

        if os.path.exists(self.user_download_cache_path) and os.path.isdir(self.user_download_cache_path):

            executable = "/usr/bin/du"
            args = ["-sb", self.user_download_cache_path]

            self._run_process(Process(exec_type="exec",
                                      executable=executable,
                                      executable_params=args))
            print("Disk usage ",self.module_output_log[0]["stdout"])
            dc_size = int(self.module_output_log[0]["stdout"].split("\t")[0])
            quota_size = int(self.config.DOWNLOAD_CACHE_QUOTA * 1024 * 1024 * 1024)

            model = StorageModel(used=dc_size,
                                 free=quota_size - dc_size,
                                 quota=quota_size,
                                 free_percent=int(100 * (quota_size - dc_size) / quota_size))
            self.module_results = model

            self.finish_message = "Download cache size successfully computed"
        else:
            raise AsyncProcessError("Download cache directory <%s> does not exist." % self.user_download_cache_path)


def start_download_cache_remove(*args):
    processing = DownloadCacheDelete(*args)
    processing.run()


class DownloadCacheDelete(AsyncPersistentProcessing):
    """Delete the whole download cache directory
    """

    def __init__(self, *args):

        AsyncPersistentProcessing.__init__(self, *args)
        self.user_download_cache_path = os.path.join(self.config.DOWNLOAD_CACHE, self.user_id)

    def _execute(self):

        self._setup()

        if os.path.exists(self.user_download_cache_path) and os.path.isdir(self.user_download_cache_path):
            executable = "/bin/rm"
            args = ["-rf", self.user_download_cache_path]

            self._run_process(Process(exec_type="exec",
                                      executable=executable,
                                      executable_params=args))

            os.mkdir(self.user_download_cache_path)
            self.finish_message = "Download cache successfully removed."
        else:
            raise AsyncProcessError("Download cache directory <%s> does not exist." % self.user_download_cache_path)
