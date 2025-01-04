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
Mapset management resources

* List all mapsets
* Create mapset, Delete mapset, Get info about a mapset
* Lock mapset, unlock mapset, get mapset lock status
"""

import shutil
from actinia_core.processing.actinia_processing.ephemeral.persistent_processing import (
    PersistentProcessing,
)
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.models.response_models import (
    StringListProcessingResultResponseModel,
    MapsetInfoResponseModel,
    RegionModel,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class PersistentMapsetLister(PersistentProcessing):
    """List all mapsets in a project"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)
        self.response_model_class = StringListProcessingResultResponseModel

    def _execute(self):
        self._setup()
        # Create the temporary database and link all available mapsets into is
        self._create_temp_database()

        pc = {
            "1": {
                "module": "g.mapsets",
                "inputs": {"separator": "newline"},
                "flags": "l",
            }
        }

        process_list = self._validate_process_chain(
            process_chain=pc, skip_permission_check=True
        )
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base, mapset_name="PERMANENT"
        )

        self._execute_process_list(process_list)

        mapset_lists = []
        mapsets = self.module_output_log[0]["stdout"].split()

        for mapset in mapsets:
            mapset_lists.append(mapset.strip())

        self.module_results = mapset_lists


class PersistentGetProjectionRegionInfo(PersistentProcessing):
    """Read the current region and projection information"""

    integer_values = [
        "projection",
        "zone",
        "rows",
        "rows3",
        "cols",
        "cols3",
        "depths",
        "cells",
        "cells3",
    ]
    float_values = [
        "n",
        "s",
        "e",
        "w",
        "t",
        "b",
        "nsres",
        "nsres3",
        "ewres",
        "ewres3",
        "tbres",
    ]

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)
        self.response_model_class = MapsetInfoResponseModel

    def _execute(self):
        self._setup()

        pc = {
            "1": {"module": "g.region", "flags": "ug3"},
            "2": {"module": "g.proj", "flags": "fw"},
        }

        # Do not check the region size
        self.skip_region_check = True
        process_list = self._validate_process_chain(
            process_chain=pc, skip_permission_check=True
        )
        self._create_temp_database(self.required_mapsets)
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.target_mapset_name,
        )

        self._execute_process_list(process_list)

        mapset_region = {}
        region_settings = self.module_output_log[0]["stdout"].split()

        for region_token in region_settings:
            if "=" in region_token:
                key, value = region_token.strip().split("=")
                if key in self.integer_values:
                    mapset_region[key] = int(value)
                if key in self.float_values:
                    mapset_region[key] = float(value)

        self.module_results = dict(
            region=RegionModel(**mapset_region),
            projection=self.module_output_log[1]["stdout"],
        )

        # self.module_results = MapsetInfoModel(
        #     region=RegionModel(**mapset_region),
        #     projection=self.module_output_log[1]["stdout"]
        # )


class PersistentMapsetCreator(PersistentProcessing):
    """Create a mapset in an existing project"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()
        # Create temporary database
        self._create_temp_database()

        pc = {"1": {"module": "g.mapsets", "flags": "l"}}

        process_list = self._validate_process_chain(
            process_chain=pc, skip_permission_check=True
        )
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base, mapset_name="PERMANENT"
        )

        self._execute_process_list(process_list)

        mapset_list = []
        mapsets = self.module_output_log[0]["stdout"].split()

        for mapset in mapsets:
            mapset_list.append(mapset.strip())

        if self.target_mapset_name in mapset_list:
            raise AsyncProcessError(
                "Mapset <%s> exists." % self.target_mapset_name
            )

        # Create the new temporary mapset and merge it into the user database
        # project
        self._check_lock_target_mapset()
        self.required_mapsets = ["PERMANENT"]
        self._create_temporary_mapset(temp_mapset_name=self.temp_mapset_name)
        self._copy_merge_tmp_mapset_to_target_mapset()

        self.finish_message = (
            "Mapset <%s> successfully created." % self.target_mapset_name
        )


class PersistentMapsetDeleter(PersistentProcessing):
    """Delete a mapset from a project

    1. Create temporary database
    2. Check if PERMANENT mapset or global mapset which are not allowed to be
       deleted
    3. Check if the mapset exists
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()

        # For debug purpose
        # self.lock_interface.unlock(self.target_mapset_lock_id)

        if "PERMANENT" == self.target_mapset_name:
            raise AsyncProcessError(
                "The PERMANENT mapset can not be deleted. "
                "You must remove the project to get rid of it."
            )

        # Delete existing mapset
        self._check_lock_target_mapset()
        # The variable self.orig_mapset_path is set by
        # _check_lock_target_mapset()
        if self.target_mapset_exists is True:
            shutil.rmtree(self.orig_mapset_path)
            self.lock_interface.unlock(self.target_mapset_lock_id)
            self.finish_message = (
                "Mapset <%s> successfully removed." % self.target_mapset_name
            )
        else:
            raise AsyncProcessError(
                "Mapset <%s> does not exits" % self.target_mapset_name
            )


class PersistentGetMapsetLock(PersistentProcessing):
    """Get the mapset lock status"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()
        self._check_target_mapset_exists()
        if self.target_mapset_exists is False:
            raise AsyncProcessError(
                f"Unable to get lock status of mapset <{self.mapset_name}>"
                f" in project <{self.project_name}>: Mapset does not "
                "exist"
            )
        else:
            self.module_results = self.lock_interface.get(
                self.target_mapset_lock_id
            )
            self.finish_message = "Mapset lock state: %s" % str(
                self.module_results
            )


class PersistentMapsetLocker(PersistentProcessing):
    """Lock a mapset"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()
        self._check_lock_target_mapset()
        if self.target_mapset_exists is False:
            raise AsyncProcessError(
                "Unable to lock mapset <%s>. Mapset doesn not exists."
                % self.target_mapset_name
            )

        self.finish_message = (
            "Mapset <%s> successfully locked" % self.target_mapset_name
        )

    def _final_cleanup(self):
        """
        Final cleanup called in the run function at the very end of processing
        """
        # Clean up and remove the temporary files
        self._cleanup()


class PersistentMapsetUnlocker(PersistentProcessing):
    """Unlock a locked mapset"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()
        self._check_target_mapset_exists()
        if self.target_mapset_exists is False:
            raise AsyncProcessError(
                (
                    "Unable to unlock mapset <%s> in project <%s>:"
                    " Mapset does not exist"
                )
                % (self.mapset_name, self.project_name)
            )
        else:
            self.lock_interface.unlock(self.target_mapset_lock_id)
            self.finish_message = (
                "Mapset <%s> successfully unlocked" % self.target_mapset_name
            )
