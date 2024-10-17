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
STRDS map layer management

TODO: Integrate into the ephemeral process chain approach
"""
from actinia_api.swagger2.actinia_core.schemas.strds_management import (
    STRDSInfoModel,
    STRDSInfoResponseModel,
)

from actinia_core.processing.actinia_processing.ephemeral.persistent_processing import (
    PersistentProcessing,
)
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.models.response_models import (
    StringListProcessingResultResponseModel,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class PersistentSTRDSLister(PersistentProcessing):
    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)
        self.response_model_class = StringListProcessingResultResponseModel

    def _execute(self):
        self._setup()

        pc = {
            "1": {
                "module": "t.list",
                "inputs": {"type": "strds", "column": "name"},
            }
        }

        # Make sure that only the current mapset is used for strds listing
        has_where = False

        if self.rdc.user_data:
            for option in self.rdc.user_data:
                if self.rdc.user_data[option] is not None:
                    if "where" in option:
                        select = (
                            self.rdc.user_data[option]
                            + " AND mapset = '%s'" % self.mapset_name
                        )
                        pc["1"]["inputs"]["where"] = select
                        has_where = True
                    else:
                        pc["1"]["inputs"][option] = self.rdc.user_data[option]

        if has_where is False:
            select = "mapset='%s'" % self.mapset_name
            pc["1"]["inputs"]["where"] = select

        process_list = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc
        )
        self._create_temp_database()
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.mapset_name,
        )

        self._execute_process_list(process_list)

        mapset_lists = []
        mapsets = self.module_output_log[0]["stdout"].split()

        for mapset in mapsets:
            mapset_lists.append(mapset.strip())

        self.module_results = mapset_lists


class PersistentSTRDSInfo(PersistentProcessing):
    """Gather the STRDS information"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)
        self.response_model_class = STRDSInfoResponseModel

    def _execute(self):
        self._setup()

        pc = {
            "1": {
                "module": "t.info",
                "inputs": {"type": "strds", "input": self.map_name},
                "flags": "g",
            }
        }

        process_list = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc
        )
        self._create_temp_database()
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.mapset_name,
        )

        self._execute_process_list(process_list)

        kv_list = self.module_output_log[0]["stdout"].split("\n")

        strds = {}

        for string in kv_list:
            if "=" in string:
                k, v = string.split("=", 1)
                strds[k] = v

        self.module_results = STRDSInfoModel(**strds)
        self.finish_message = (
            "Information gathering for STRDS <%s> successful" % self.map_name
        )


class PersistentSTRDSDeleter(PersistentProcessing):
    """Delete a STRDS"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()
        self.required_mapsets.append(self.target_mapset_name)

        args = self.rdc.user_data

        pc = {
            "1": {
                "module": "t.remove",
                "inputs": {"type": "strds", "inputs": self.map_name},
                "flags": "f",
            }
        }

        if args and "recursive" in args and args["recursive"] is True:
            pc["1"]["flags"] = "rf"

        process_list = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc
        )

        self._create_temp_database()
        self._check_lock_target_mapset()

        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.target_mapset_name,
        )

        self._execute_process_list(process_list)
        self.finish_message = "STRDS <%s> successfully deleted" % self.map_name


class PersistentSTRDSCreator(PersistentProcessing):
    """Create a STRDS"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()
        self.required_mapsets.append(self.target_mapset_name)

        pc_1 = {}
        pc_1["1"] = {
            "module": "t.list",
            "inputs": {
                "type": "strds",
                "where": "id = '%s@%s'"
                % (self.map_name, self.target_mapset_name),
            },
        }
        # Check the first process chain
        pc_1 = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc_1
        )

        pc_2 = {
            "1": {
                "module": "t.create",
                "inputs": {"type": "strds", "output": self.map_name},
            }
        }

        if self.request_data:
            for key in self.request_data:
                pc_2["1"]["inputs"][key] = self.request_data[key]

        pc_2 = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc_2
        )
        self._create_temp_database()
        self._check_lock_target_mapset()

        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.target_mapset_name,
        )

        self._execute_process_list(pc_1)

        # check if STRDS exists
        raster_list = self.module_output_log[0]["stdout"].split("\n")

        if len(raster_list[0]) > 0:
            raise AsyncProcessError("STRDS <%s> exists." % self.map_name)

        self._execute_process_list(pc_2)

        self.finish_message = "STRDS <%s> successfully created" % self.map_name
