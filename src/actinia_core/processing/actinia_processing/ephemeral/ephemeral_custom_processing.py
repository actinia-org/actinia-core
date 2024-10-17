# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2024 Sören Gebbert and mundialis GmbH & Co. KG
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
Running a custom UNIX process outside the GRASS GIS environment
"""
from actinia_core.processing.actinia_processing.ephemeral_processing import (
    EphemeralProcessing,
)
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.rest.base.user_auth import (
    check_project_mapset_module_access,
)
from actinia_core.core.common.process_object import Process

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class EphemeralCustomProcessing(EphemeralProcessing):
    """Run a custom process asynchronously"""

    def __init__(self, *args):
        """Setup the variables of this class

        Args:
            rdc (ResourceDataContainer): The data container that contains all
                                         required variables for processing
        """

        EphemeralProcessing.__init__(self, *args)
        self.executable = self.rdc.user_data
        self.executable_params = self.rdc.request_data

        self._update_num_of_steps(1)

    def _execute(self, skip_permission_check=False):
        """Overwrite this function in subclasses

        Setup the user credentials, check the executable access and run the
        process
        """
        # Setup the user credentials and logger
        self._setup(init_grass=False)

        # Check if the user has access to the required process executable
        resp = check_project_mapset_module_access(
            self.user_credentials, self.config, module_name=self.executable
        )

        if resp is not None:
            raise AsyncProcessError(
                "Executable <%s> is not supported" % self.executable
            )

        p = Process(
            exec_type="exec",
            executable=self.executable,
            executable_params=self.executable_params,
            id=f"exec_{self.executable}",
            stdin_source=None,
        )

        self._run_process(p)

    def _final_cleanup(self):
        """
        Final cleanup called in the run function at the very end of processing
        """
        # Nothing to cleanup
        pass
