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
Raster layer resources
"""

from actinia_api.swagger2.actinia_core.schemas.raster_layer import (
    RasterInfoModel,
)
from actinia_core.processing.actinia_processing.ephemeral_processing import (
    EphemeralProcessing,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Guido Riembauer, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class EphemeralRasterInfo(EphemeralProcessing):
    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)

    def _execute(self):
        """Read info from a raster layer

        Use a temporary mapset for processing
        """
        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.mapset_name)

        pc = {}
        pc["1"] = {
            "module": "r.info",
            "inputs": {"map": raster_name + "@" + self.mapset_name},
            "flags": "gre",
        }

        self.skip_region_check = True
        process_list = (
            self._create_temporary_grass_environment_and_process_list(
                process_chain=pc, skip_permission_check=True
            )
        )
        self._execute_process_list(process_list)

        kv_list = self.module_output_log[0]["stdout"].split("\n")

        raster_info = {}

        for string in kv_list:
            if "=" in string:
                k, v = string.split("=", 1)
                raster_info[k] = v

        self.module_results = RasterInfoModel(**raster_info)
