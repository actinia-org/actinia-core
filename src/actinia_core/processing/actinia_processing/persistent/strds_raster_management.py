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
STRDS raster map layer management

TODO: Integrate into the ephemeral process chain approach
"""
import tempfile
from actinia_api.swagger2.actinia_core.schemas.strds_raster_management import (
    STRDSRasterListResponseModel,
    STRDSRasterListEntryModel,
)

from actinia_core.processing.actinia_processing.ephemeral.persistent_processing import (
    PersistentProcessing,
)
from actinia_core.core.common.exceptions import AsyncProcessError

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class PersistentRasterSTRDSLister(PersistentProcessing):
    """List all mapsets in a project"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)
        self.response_model_class = STRDSRasterListResponseModel

    def _execute(self):
        self._setup()

        result_file = tempfile.NamedTemporaryFile(
            dir=self.temp_file_path, delete=True
        )

        pc = {
            "1": {
                "module": "t.rast.list",
                "inputs": {
                    "input": "%s@%s" % (self.map_name, self.mapset_name),
                    "columns": "id,start_time,end_time,north,south,"
                    "east,west,min,max,rows,cols",
                    "separator": "|",
                },
                "outputs": {"output": {"name": result_file.name}},
                "flags": "u",
            }
        }

        if self.rdc.user_data:
            for option in self.rdc.user_data:
                if self.rdc.user_data[option] is not None:
                    pc["1"]["inputs"][option] = self.rdc.user_data[option]

        process_list = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc
        )

        self._create_temp_database(mapsets=self.required_mapsets)
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.mapset_name,
        )
        self._execute_process_list(process_list)

        result_file.flush()
        result = open(result_file.name, "r").readlines()
        result_file.close()

        output_list = []
        for line in result:
            values = line.strip().split("|")
            output_list.append(
                STRDSRasterListEntryModel(
                    id=values[0],
                    start_time=values[1],
                    end_time=values[2],
                    north=values[3],
                    south=values[4],
                    east=values[5],
                    west=values[6],
                    min=values[7],
                    max=values[8],
                    rows=values[9],
                    cols=values[10],
                )
            )

        self.module_results = output_list


class PersistentRasterSTRDSRegisterer(PersistentProcessing):
    """Register a list of timestamped raster map layers in a STRDS"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()

        input_file = tempfile.NamedTemporaryFile(
            dir=self.temp_file_path, delete=True, mode="w"
        )

        for map_entry in self.request_data:
            if (
                "name" not in map_entry
                or "start_time" not in map_entry
                or "end_time" not in map_entry
            ):
                raise AsyncProcessError(
                    "Wrong input format for raster map layer registration"
                )

            line = "%s|%s|%s\n" % (
                map_entry["name"],
                map_entry["start_time"],
                map_entry["end_time"],
            )
            input_file.write(line)
        input_file.flush()
        input_file.seek(0)

        pc = {
            "1": {
                "module": "t.register",
                "inputs": {
                    "input": "%s@%s" % (self.map_name, self.mapset_name),
                    "type": "raster",
                    "separator": "|",
                    "file": input_file.name,
                },
            }
        }

        self._check_lock_target_mapset()
        self._create_temp_database(mapsets=self.required_mapsets)
        process_list = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc
        )
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.mapset_name,
        )

        self._execute_process_list(process_list)

        input_file.close()


class PersistentRasterSTRDSUnregisterer(PersistentProcessing):
    """Unregister a list of timestamped raster map layers from a STRDS"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()

        input_file = tempfile.NamedTemporaryFile(
            dir=self.temp_file_path, delete=True, mode="w"
        )

        for map_name in self.request_data:
            line = "%s\n" % map_name
            input_file.write(line)
        input_file.flush()

        pc = {
            "1": {
                "module": "t.unregister",
                "inputs": {
                    "input": "%s@%s" % (self.map_name, self.mapset_name),
                    "type": "raster",
                    "file": input_file.name,
                },
            }
        }

        process_list = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc
        )
        self._check_lock_target_mapset()
        self._create_temp_database(mapsets=self.required_mapsets)
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.mapset_name,
        )

        self._execute_process_list(process_list)

        input_file.close()
