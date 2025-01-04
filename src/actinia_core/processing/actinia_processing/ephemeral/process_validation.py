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
Compute areal categorical statistics on a raster map layer based on an input
polygon.
"""

from actinia_core.processing.actinia_processing.ephemeral_processing import (
    EphemeralProcessing,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class ProcessValidation(EphemeralProcessing):
    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()

        process_chain = (
            self._create_temporary_grass_environment_and_process_list()
        )

        result = []
        for process in process_chain:
            result.append(str(process))

        self.finish_message = "Validation successful"

        self.module_results = result
