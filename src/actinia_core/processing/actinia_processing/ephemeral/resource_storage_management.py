# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2022 Sören Gebbert and mundialis GmbH & Co. KG
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
Resource storage management

TODO: Tests required
"""

import os
from actinia_core.processing.actinia_processing.ephemeral_processing import (
    EphemeralProcessing,
)
from actinia_core.core.common.process_object import Process
from actinia_core.models.response_models import (
    StorageResponseModel,
    StorageModel,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class ResourceStorageSize(EphemeralProcessing):
    """Compute the download cache size"""

    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)
        self.response_model_class = StorageResponseModel
        self.user_resource_storage_path = os.path.join(
            self.config.GRASS_RESOURCE_DIR, self.user_id
        )

    def _execute(self):
        self._setup()

        if not os.path.exists(self.user_resource_storage_path):
            os.mkdir(self.user_resource_storage_path)

        executable = "/usr/bin/du"
        args = ["-sb", self.user_resource_storage_path]

        self._run_process(
            Process(
                exec_type="exec",
                executable=executable,
                id="compute_download_cache_size",
                executable_params=args,
            )
        )

        dc_size = int(self.module_output_log[0]["stdout"].split("\t")[0])
        quota_size = int(self.config.GRASS_RESOURCE_QUOTA * 1024 * 1024 * 1024)

        model = StorageModel(
            used=dc_size,
            free=quota_size - dc_size,
            quota=quota_size,
            free_percent=int(100 * (quota_size - dc_size) / quota_size),
        )
        self.module_results = model

        self.finish_message = "Resource storage size successfully computed"
