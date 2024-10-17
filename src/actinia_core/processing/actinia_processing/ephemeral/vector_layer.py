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
Vector layer resources
"""
from actinia_api.swagger2.actinia_core.schemas.vector_layer import (
    VectorInfoResponseModel,
    VectorAttributeModel,
    VectorInfoModel,
)

from actinia_core.processing.actinia_processing.ephemeral_processing import (
    EphemeralProcessing,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Guido Riembauer, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class EphemeralVectorInfo(EphemeralProcessing):
    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)
        self.response_model_class = VectorInfoResponseModel

    def _execute(self):
        """Read info from a vector layer

        Use a temporary mapset for processing
        """
        self._setup()

        vector_name = self.rdc.map_name
        self.required_mapsets.append(self.mapset_name)

        pc = {}
        pc["1"] = {
            "module": "v.info",
            "inputs": {"map": vector_name + "@" + self.mapset_name},
            "flags": "gte",
        }

        pc["2"] = {
            "module": "v.info",
            "inputs": {"map": vector_name + "@" + self.mapset_name},
            "flags": "h",
        }

        pc["3"] = {
            "module": "v.info",
            "inputs": {"map": vector_name + "@" + self.mapset_name},
            "flags": "c",
        }

        self.skip_region_check = True
        process_list = (
            self._create_temporary_grass_environment_and_process_list(
                process_chain=pc, skip_permission_check=True
            )
        )
        self._execute_process_list(process_list)

        kv_list = self.module_output_log[0]["stdout"].split("\n")

        vector_info = {}
        # Regular metadata
        for string in kv_list:
            if "=" in string:
                k, v = string.split("=", 1)
                vector_info[k] = v

        kv_list = self.module_output_log[1]["stdout"].split("\n")
        # Command that created the vector
        for string in kv_list:
            if "COMMAND:" in string:
                k, v = string.split(":", 1)
                vector_info[k] = v

        datatypes = self.module_output_log[2]["stdout"].split("\n")

        # Datatype of the vector table
        attr_list = []
        for string in datatypes:
            if "|" in string:
                dt_dict = {}
                col_type, col_name = string.split("|", 1)
                dt_dict["type"] = col_type
                dt_dict["column"] = col_name
                attr_list.append(VectorAttributeModel(**dt_dict))

        vector_info["Attributes"] = attr_list

        self.module_results = VectorInfoModel(**vector_info)
