# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2022 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Download cache management

TODO: Tests required
"""

import os
from actinia_processing_lib.persistent_processing import (
    PersistentProcessing,
)
from actinia_core.core.common.process_object import Process
from actinia_processing_lib.exceptions import AsyncProcessError

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2022, Sören Gebbert & mundialis GmbH & Co. KG"
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
