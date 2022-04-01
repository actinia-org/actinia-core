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
Location management

TODO: Integrate into the ephemeral process chain approach
"""

import os
import shutil
from actinia_core.processing.actinia_processing.ephemeral.persistent_processing \
     import PersistentProcessing
from actinia_core.core.common.exceptions import AsyncProcessError

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class PersistentLocationCreator(PersistentProcessing):
    """Create a new location based on EPSG code
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):

        new_location = self.location_name

        self.location_name = self.config.GRASS_DEFAULT_LOCATION

        self._setup()

        epsg_code = self.request_data["epsg"]

        self._create_temp_database()

        pc = {"1": {"module": "g.proj",
                    "inputs": {"epsg": epsg_code,
                               "location": new_location},
                    "flags": "t"}}

        process_list = self._validate_process_chain(process_chain=pc,
                                                    skip_permission_check=True)

        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name="PERMANENT")

        self._execute_process_list(process_list)

        if os.path.isdir(os.path.join(self.temp_grass_data_base, new_location)):
            shutil.move(os.path.join(self.temp_grass_data_base,
                        new_location), self.grass_user_data_base)
        else:
            raise AsyncProcessError("Unable to create location <%s>" % new_location)

        self.finish_message = "Location <%s> successfully created" % new_location
