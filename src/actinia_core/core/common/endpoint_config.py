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
Entpoint configuration
"""

import csv
from flask import jsonify
from flask import make_response
from functools import wraps
import sys

from actinia_core.core.common.config import global_config
from actinia_core.models.response_models import SimpleResponseModel


__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2022, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"


if global_config.ENDPOINTS_CONFIG is not None:
    with open(global_config.ENDPOINTS_CONFIG, mode="r") as inp:
        reader = csv.reader(inp, delimiter=';')
        endpoints_dict = {
            row[0]: [
                method.upper() for method in row[1].split(",")
            ] for row in reader if len(row) == 2}
else:
    endpoints_dict = None


def check_endpoint(method, api_doc):
    endpoint_class = sys._getframe().f_back.f_code.co_name
    method_upper = method.upper()
    if (endpoints_dict is None or
        (endpoint_class in endpoints_dict and
         method_upper in endpoints_dict[endpoint_class])):
        return api_doc
    else:
        return False


def endpoint_decorator():

    def decorator(func):
        endpoint_class, method = func.__qualname__.split(".")
        method_upper = method.upper()

        @wraps(func)
        def wrapper(*args, **kwargs):

            if (endpoints_dict is None or
                (endpoint_class in endpoints_dict and
                 method_upper in endpoints_dict[endpoint_class])):
                result = func(*args, **kwargs)
                return result
            else:
                return make_response(jsonify(SimpleResponseModel(
                    status="error",
                    message="Not Found. The requested URL is not configured on"
                            " the server.")), 404)
        return wrapper

    return decorator
