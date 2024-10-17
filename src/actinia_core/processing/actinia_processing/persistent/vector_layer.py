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
Vector layer resources
"""
import os
from shutil import rmtree

from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.processing.actinia_processing.ephemeral.persistent_processing import (
    PersistentProcessing,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Guido Riembauer, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class PersistentVectorDeleter(PersistentProcessing):
    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        """Delete a specific vector layer from a project in the user database

        Use the original mapset for processing
        """
        self._setup()

        vector_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        pc = {}
        pc["1"] = {
            "module": "g.remove",
            "inputs": {"type": "vector", "name": vector_name},
            "flags": "f",
        }

        self.skip_region_check = True
        process_list = self._validate_process_chain(
            process_chain=pc, skip_permission_check=True
        )
        self._check_lock_target_mapset()
        self._create_grass_environment(
            grass_data_base=self.grass_user_data_base,
            mapset_name=self.target_mapset_name,
        )

        self._execute_process_list(process_list)

        if "WARNING: No data base element files found" in "\n".join(
            self.module_output_log[0]["stderr"]
        ):
            raise AsyncProcessError(
                "Vector layer <%s> not found" % (vector_name)
            )

        self.finish_message = (
            "Vector layer <%s> successfully removed." % vector_name
        )


class PersistentVectorCreator(PersistentProcessing):
    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        """Create a specific vector layer

        This approach is complex, since the vector generation is performed in a
        local temporary mapset that is later merged into the target mapset.
        Workflow:

        1. Check the process chain
        2. Lock the temp and target mapsets
        3. Setup GRASS and create the temporary mapset
        4. Execute g.list of the first process chain to check if the target
           vector exists
        5. If the target vector does not exist then run v.import
        6. Copy the local temporary mapset to the storage and merge it into the
           target mapset
        """
        self._setup()

        vector_name = self.map_name
        self.required_mapsets.append(self.target_mapset_name)

        pc_1 = {}
        pc_1["1"] = {
            "module": "g.list",
            "inputs": {
                "type": "vector",
                "pattern": vector_name,
                "mapset": self.target_mapset_name,
            },
        }
        # Check the first process chain
        self.skip_region_check = True
        pc_1 = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc_1
        )

        pc_2 = {}
        pc_2["1"] = {
            "module": "v.import",
            "inputs": {"input": self.rdc.request_data},
            "outputs": {"output": {"name": vector_name}},
        }
        # Check the second process chain
        self.skip_region_check = True
        pc_2 = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc_2
        )

        self._check_lock_target_mapset()
        self._lock_temp_mapset()
        self._create_temporary_grass_environment(
            source_mapset_name=self.target_mapset_name
        )
        self._execute_process_list(pc_1)

        # check if vector exists
        raster_list = self.module_output_log[0]["stdout"].split("\n")

        if len(raster_list[0]) > 0:
            raise AsyncProcessError("Vector layer <%s> exists." % vector_name)

        self._execute_process_list(pc_2)
        self._copy_merge_tmp_mapset_to_target_mapset()

        # Delete imported file
        msg = ""
        try:
            if self.rdc.request_data.endswith(".shp"):
                rmtree(
                    os.path.dirname(self.rdc.request_data), ignore_errors=True
                )
            else:
                os.remove(self.rdc.request_data)
        except Exception:
            msg = " WARNING: Uploaded file cannot be removed."

        self.finish_message = (
            f"Vector layer <{vector_name}> successfully " f"imported.{msg}"
        )
