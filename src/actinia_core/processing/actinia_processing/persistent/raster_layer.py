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
import os
from actinia_core.processing.actinia_processing.ephemeral.persistent_processing import (
    PersistentProcessing,
)
from actinia_core.core.common.exceptions import AsyncProcessError

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Guido Riembauer, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class PersistentRasterDeleter(PersistentProcessing):
    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        """Delete a specific raster layer

        Use the original mapset for processing
        """
        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        pc = {}
        pc["1"] = {
            "module": "g.remove",
            "inputs": {"type": "raster", "name": raster_name},
            "flags": "f",
        }

        self.skip_region_check = True
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

        if "WARNING: No data base element files found" in "\n".join(
            self.module_output_log[0]["stderr"]
        ):
            raise AsyncProcessError(
                "Raster layer <%s> not found" % raster_name
            )

        self.finish_message = (
            "Raster layer <%s> successfully removed." % raster_name
        )


class PersistentRasterCreator(PersistentProcessing):
    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        """Create a specific raster layer

        This approach is complex, since the raster generation is performed in a
        localc temporary mapset that is later merged into the target mapset.
        Workflow:

        1. Check the process chain
        2. Lock the temp and target mapsets
        3. Setup GRASS and create the temporary mapset
        4. Execute g.list of the first process chain to check if the target
           raster exists
        5. If the target raster does not exists then run r.import
        6. Copy the local temporary mapset to the storage and merge it into the
           target mapset
        """
        self._setup()

        raster_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        pc_1 = {}
        pc_1["1"] = {
            "module": "g.list",
            "inputs": {
                "type": "raster",
                "pattern": raster_name,
                "mapset": self.target_mapset_name,
            },
        }
        # Check the first process chain
        pc_1 = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc_1
        )

        pc_2 = {}
        pc_2["1"] = {
            "module": "r.import",
            "inputs": {"input": self.rdc.request_data, "output": raster_name},
        }
        # Check the second process chain
        pc_2 = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc_2
        )

        self._check_lock_target_mapset()
        self._lock_temp_mapset()
        self._create_temporary_grass_environment()
        self._execute_process_list(pc_1)

        # check if raster exists
        raster_list = self.module_output_log[0]["stdout"].split("\n")

        if len(raster_list[0]) > 0:
            try:
                os.remove(self.rdc.request_data)
            except Exception:
                pass
            raise AsyncProcessError(
                "Raster layer <%s> exists. Please rename it or delete the old "
                "raster layer" % raster_name
            )

        self._execute_process_list(pc_2)
        self._copy_merge_tmp_mapset_to_target_mapset()

        # Delete imported file
        msg = ""
        try:
            os.remove(self.rdc.request_data)
        except Exception:
            msg = " WARNING: Uploaded file can not be removed."

        self.finish_message = (
            f"Raster layer <{raster_name}> successfully " f"imported.{msg}"
        )
