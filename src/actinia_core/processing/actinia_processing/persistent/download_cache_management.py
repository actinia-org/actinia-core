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
Download cache management

TODO: Tests required
"""

import os
from actinia_core.processing.actinia_processing.ephemeral.persistent_processing import (
    PersistentProcessing,
)
from actinia_core.core.common.process_object import Process
from actinia_core.core.common.exceptions import AsyncProcessError

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class DownloadCacheDelete(PersistentProcessing):
    """Delete the whole download cache directory"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)
        self.user_download_cache_path = os.path.join(
            self.config.DOWNLOAD_CACHE, self.user_id
        )

    def _execute(self):
        self._setup()

        if os.path.exists(self.user_download_cache_path) and os.path.isdir(
            self.user_download_cache_path
        ):
            executable = "/bin/rm"
            args = ["-rf", self.user_download_cache_path]

            self._run_process(
                Process(
                    exec_type="exec",
                    executable=executable,
                    id="delete_download_cache_directory",
                    executable_params=args,
                )
            )

            os.mkdir(self.user_download_cache_path)
            self.finish_message = "Download cache successfully removed."
        else:
            raise AsyncProcessError(
                "Download cache directory <%s> does not exist."
                % self.user_download_cache_path
            )
