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
Raster colors management

TODO: Maybe more tests required, test_raster_colors.py is in place and works
"""

from tempfile import NamedTemporaryFile
from actinia_core.processing.actinia_processing.ephemeral_processing import (
    EphemeralProcessing,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class EphemeralRasterColorsOutput(EphemeralProcessing):
    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)

    def _execute(self, skip_permission_check=True):
        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.mapset_name)

        with NamedTemporaryFile(
            mode="w+", suffix=".color", dir=self.temp_file_path
        ) as file:
            result_file = file.name

        self.request_data = {
            "1": {"module": "r.colors.out", "inputs": {"map": "", "rules": ""}}
        }
        self.request_data["1"]["inputs"]["map"] = (
            raster_name + "@" + self.mapset_name
        )
        self.request_data["1"]["inputs"]["rules"] = result_file

        # Run the selected modules
        process_list = (
            self._create_temporary_grass_environment_and_process_list(
                skip_permission_check=True
            )
        )
        self._execute_process_list(process_list)

        with open(result_file, "r") as file:
            result = file.read().strip().split("\n")

        self.module_results = result
