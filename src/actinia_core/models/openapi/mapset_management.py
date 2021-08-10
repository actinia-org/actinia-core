# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2018 Sören Gebbert and mundialis GmbH & Co. KG
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
Model for Mapset management resources
"""
from copy import deepcopy
from actinia_core.models.response_models import ProcessingResponseModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class MapsetLockManagementResponseModel(ProcessingResponseModel):
    """The response content that is returned by the GET request
    """
    type = 'object'
    properties = deepcopy(ProcessingResponseModel.properties)
    properties["process_results"] = {}
    properties["process_results"]["type"] = "boolean"
    required = deepcopy(ProcessingResponseModel.required)
    example = {
        "accept_datetime": "2018-05-02 11:03:26.529673",
        "accept_timestamp": 1525259006.5296717,
        "api_info": {
            "endpoint": "mapsetlockmanagementresource",
            "method": "GET",
            "path": "/locations/nc_spm_08/mapsets/PERMANENT/lock",
            "request_url": "http://localhost:8080/locations/nc_spm_08/mapsets/"
                           "PERMANENT/lock"
        },
        "datetime": "2018-05-02 11:03:26.586348",
        "http_code": 200,
        "message": "Mapset lock state: False",
        "process_chain_list": [],
        "process_log": [],
        "process_results": False,
        "progress": {
            "num_of_steps": 0,
            "step": 0
        },
        "resource_id": "resource_id-162101d9-2abc-417e-83ef-dc6f52ed7aaf",
        "status": "finished",
        "time_delta": 0.056743621826171875,
        "timestamp": 1525259006.5863316,
        "urls": {
            "resources": [],
            "status": "http://localhost:8080/resources/admin/"
                      "resource_id-162101d9-2abc-417e-83ef-dc6f52ed7aaf"
        },
        "user_id": "admin"
    }
