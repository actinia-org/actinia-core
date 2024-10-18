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
import os
import atexit

from actinia_core.processing.actinia_processing.ephemeral.persistent_processing import (
    PersistentProcessing,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class PersistentRasterColorsRules(PersistentProcessing):
    """Set the color table of a raster map from color rules

    Perform the processing in the original mapset
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self, skip_permission_check=True):
        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        options = self.request_data

        pc = {"1": {"module": "r.colors", "inputs": {}}}
        pc["1"]["inputs"]["map"] = raster_name + "@" + self.target_mapset_name

        if "rules" in options:
            with NamedTemporaryFile(
                mode="w+",
                delete=False,
                suffix=".color",
                dir=self.temp_file_path,
            ) as rules:
                for line in options["rules"]:
                    rules.write(line + "\n")

            pc["1"]["inputs"]["rules"] = rules.name
            atexit.register(remove_rules_file, rules.name)
        else:
            for option in options:
                pc["1"]["inputs"][option] = options[option]

        process_list = self._validate_process_chain(
            process_chain=pc, skip_permission_check=True
        )
        self._check_lock_target_mapset()
        self._create_temp_database(self.required_mapsets)
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.target_mapset_name,
        )

        self._execute_process_list(process_list)


def remove_rules_file(rules_file):
    os.remove(rules_file)
