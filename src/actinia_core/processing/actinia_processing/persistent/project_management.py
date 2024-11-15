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
Project management

TODO: Integrate into the ephemeral process chain approach
"""

import os
import shutil
from actinia_core.processing.actinia_processing.ephemeral.persistent_processing import (
    PersistentProcessing,
)
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.version import G_VERSION

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class PersistentProjectCreator(PersistentProcessing):
    """Create a new project based on EPSG code"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        new_project = self.project_name

        self.project_name = self.config.GRASS_DEFAULT_PROJECT

        self._setup()

        epsg_code = self.request_data["epsg"]

        self._create_temp_database()

        grass_version_s = G_VERSION["version"]
        grass_version = [int(item) for item in grass_version_s.split(".")[:2]]
        project_param = "location" if grass_version < [8, 4] else "project"
        pc = {
            "version": 1,
            "list": [
                {
                    "id": "1",
                    "module": "g.proj",
                    "inputs": [
                        {"param": "epsg", "value": epsg_code},
                        {"param": project_param, "value": new_project},
                    ],
                    "flags": "t",
                }
            ],
        }

        process_list = self._validate_process_chain(
            process_chain=pc, skip_permission_check=True
        )

        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base, mapset_name="PERMANENT"
        )

        self._execute_process_list(process_list)

        if os.path.isdir(os.path.join(self.temp_grass_data_base, new_project)):
            shutil.move(
                os.path.join(self.temp_grass_data_base, new_project),
                self.grass_user_data_base,
            )
        else:
            raise AsyncProcessError(
                "Unable to create project <%s>" % new_project
            )

        self.finish_message = "Project <%s> successfully created" % new_project
