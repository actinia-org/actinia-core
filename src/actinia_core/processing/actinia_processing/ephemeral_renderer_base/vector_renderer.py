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
Raster map renderer

"""

from tempfile import NamedTemporaryFile
from actinia_core.processing.actinia_processing.ephemeral_processing import (
    EphemeralProcessing,
)
from actinia_core.processing.actinia_processing.ephemeral.base.renderer_base import (
    EphemeralRendererBase,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class EphemeralVectorRenderer(EphemeralRendererBase):
    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)

    def _execute(self, skip_permission_check=True):
        """Render the vector image

        Workflow:

            1. The default region is set to the vector region
            2. User specific region settings are applied
            3. d.vect is invoked to create the PNG file

        """

        self._setup()

        vector_name = self.map_name
        options = self.rdc.user_data
        self.required_mapsets.append(self.mapset_name)

        with NamedTemporaryFile(suffix=".png") as file:
            result_file = file.name

        region_pc = self._setup_render_environment_and_region(
            options=options, result_file=result_file
        )

        pc = {}
        pc["1"] = {
            "module": "g.region",
            "inputs": {"vector": vector_name + "@" + self.mapset_name},
        }
        pc["2"] = region_pc
        pc["3"] = {
            "module": "d.vect",
            "inputs": {"map": vector_name + "@" + self.mapset_name},
            "flags": "c",
        }

        # Run the selected modules
        self.skip_region_check = True
        process_list = (
            self._create_temporary_grass_environment_and_process_list(
                process_chain=pc, skip_permission_check=True
            )
        )
        self._execute_process_list(process_list)

        self.module_results = result_file
