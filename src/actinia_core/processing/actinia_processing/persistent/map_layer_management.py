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
from actinia_core.processing.actinia_processing.ephemeral.persistent_processing import (
    PersistentProcessing,
)
from actinia_core.core.request_parser import extract_glist_parameters
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.models.response_models import (
    StringListProcessingResultResponseModel,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class PersistentListLayers(PersistentProcessing):
    """List all map layers (raster, vector) of a specific mapset,
    dependent on the provided type.
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)
        self.response_model_class = StringListProcessingResultResponseModel

    def _execute(self):
        self._setup()

        args, layer_type = self.data
        self.required_mapsets.append(self.target_mapset_name)

        options = extract_glist_parameters(args)

        pc = {"1": {"module": "g.list", "inputs": {}}}

        for key in options:
            pc["1"]["inputs"][key] = options[key]

        pc["1"]["inputs"]["mapset"] = self.target_mapset_name
        pc["1"]["inputs"]["type"] = layer_type

        self.skip_region_check = True
        process_list = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc
        )
        self._create_temp_database(self.required_mapsets)
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.target_mapset_name,
        )

        self._execute_process_list(process_list)

        raster_layers_with_mapset = []
        raster_layers = self.module_output_log[0]["stdout"].split()

        for raster_layer in raster_layers:
            raster_layers_with_mapset.append(raster_layer.strip())

        self.module_results = raster_layers_with_mapset


class PersistentRemoveLayers(PersistentProcessing):
    """Remove layers in a mapset"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()

        args, layer_type = self.data
        self.required_mapsets.append(self.target_mapset_name)

        options = extract_glist_parameters(args)

        pc = {"1": {"module": "g.remove", "inputs": {}, "flags": "f"}}
        for key in options:
            pc["1"]["inputs"][key] = options[key]
        pc["1"]["inputs"]["type"] = layer_type

        self.skip_region_check = True
        process_list = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc
        )
        self._create_temp_database(self.required_mapsets)
        self._check_lock_target_mapset()
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.target_mapset_name,
        )

        self._execute_process_list(process_list)

        if "WARNING: No data base element files found" in "\n".join(
            self.module_output_log[0]["stderr"]
        ):
            raise AsyncProcessError("<%s> layer not found" % layer_type)

        self.finish_message = "Successfully removed %s layers." % layer_type


class PersistentRenameLayers(PersistentProcessing):
    """Rename raster layers in a mapset"""

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()

        _, layer_type = self.data
        self.required_mapsets.append(self.target_mapset_name)

        # List format must be
        # [(a, a_new),(b, b_new),(c, c_new), ...]
        name_list = list()
        for old_name, new_name in self.request_data:
            name_list.append("%s,%s" % (old_name, new_name))
        name_string = ",".join(name_list)

        pc = {"1": {"module": "g.rename", "inputs": {layer_type: name_string}}}

        self.skip_region_check = True
        process_list = self._validate_process_chain(
            skip_permission_check=True, process_chain=pc
        )
        self._create_temp_database(self.required_mapsets)
        self._check_lock_target_mapset()
        self._create_grass_environment(
            grass_data_base=self.temp_grass_data_base,
            mapset_name=self.target_mapset_name,
        )

        self._execute_process_list(process_list)

        if "WARNING: " in "\n".join(self.module_output_log[0]["stderr"]):
            if "not found" in "\n".join(self.module_output_log[0]["stderr"]):
                raise AsyncProcessError("Error while renaming map layers")

        self.finish_message = "Successfully renamed %s layers." % layer_type
