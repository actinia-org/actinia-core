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
Render base classes
"""

import os
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


class EphemeralRendererBase(EphemeralProcessing):
    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)

    def _setup_render_environment_and_region(
        self, options, result_file, legacy=True
    ):
        """Setup the render environment and create a g.region
         process chain entry to setup the extent from the options.

        Args:
            options: The parser options that contain n, s, e and w entries for
                     region settings
            result_file: The resulting PNG file name
            legacy: If True use the legacy process chain format for the
                    g.region process definition

        Returns:
            A process chain entry of g.region

        """
        os.putenv("GRASS_RENDER_IMMEDIATE", "png")
        os.putenv("GRASS_RENDER_WIDTH", str(options["width"]))
        os.putenv("GRASS_RENDER_HEIGHT", str(options["height"]))
        os.putenv("GRASS_RENDER_TRANSPARENT", "TRUE")
        os.putenv("GRASS_RENDER_TRUECOLOR", "TRUE")
        os.putenv("GRASS_RENDER_FILE", result_file)
        os.putenv("GRASS_RENDER_FILE_READ", "TRUE")

        if legacy is True:
            pc = {"module": "g.region", "inputs": {}, "flags": "g"}
            if options:
                for key in options:
                    if key in ["n", "s", "e", "w"]:
                        value = options[key]
                        pc["inputs"][key] = value
        else:
            pc = {"id": "2", "module": "g.region", "inputs": [], "flags": "g"}
            if options:
                for key in options:
                    if key in ["n", "s", "e", "w"]:
                        value = options[key]
                        pc["inputs"].append(
                            {"param": key, "value": str(value)}
                        )

        return pc
