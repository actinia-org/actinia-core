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
from actinia_core.processing.actinia_processing.ephemeral.persistent_processing \
     import PersistentProcessing
from actinia_core.core.common.process_object import Process
from actinia_core.core.common.exceptions import AsyncProcessError


__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class ResourceStorageDelete(PersistentProcessing):
    """Delete the user specific resource directory
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)
        self.user_resource_storage_path = os.path.join(
            self.config.GRASS_RESOURCE_DIR, self.user_id)

    def _execute(self):

        self._setup()

        if (os.path.exists(self.user_resource_storage_path)
                and os.path.isdir(self.user_resource_storage_path)):
            executable = "/bin/rm"
            args = ["-rf", self.user_resource_storage_path]

            self._run_process(Process(exec_type="exec",
                                      executable=executable,
                                      id="delete_user_specific_resource_directory",
                                      executable_params=args))

            os.mkdir(self.user_resource_storage_path)
            self.finish_message = "Resource storage successfully removed."
        else:
            raise AsyncProcessError(
                "Resource storage directory <%s> does not exist."
                % self.user_resource_storage_path)
