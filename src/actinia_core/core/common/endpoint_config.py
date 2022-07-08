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
            row[0]: [method.upper() for method in row[1].split(",")] for row in reader if len(row) == 2}
else:
    endpoints_dict = None


def check_endpoint(api_doc, method):
    endpoint_class = sys._getframe().f_back.f_code.co_name
    method_upper = method.upper()
    print(f"Check endpoint {endpoint_class} {method_upper}")
    if (endpoints_dict is None or
        (endpoint_class in endpoints_dict and
         method_upper in endpoints_dict[endpoint_class])):
        return api_doc
    else:
        return False

# def check_endpoint(func):
# # def check_endpoint(endpoint_class, method):
#     def check(self, *args, **kwargs):
#         endpoint_class = type(self).__name__
#         method = func.__name__
#         print(f"Check endpoint {endpoint_class} {method}")
#         return (endpoints_dict is None or
#                 (endpoint_class in endpoints_dict and
#                  method in endpoints_dict[endpoint_class]))
#     return check


# class endpoint_decorator(object):
#     def __init__(self, dec, endpoint_class, method, *args):
#         self.decorator = dec
#         self.endpoint_class = endpoint_class
#         self.method = method
#         self.args = args
#
#     def __call__(self, func):
#         print(self.endpoint_class)
#         if (endpoints_dict is None or
#                 (self.endpoint_class in endpoints_dict and
#                  self.method in endpoints_dict[self.endpoint_class])):
#             return self.decorator(func)
#         else:
#             # Return the function unchanged, not decorated.
#             # Return the function without api docs
#             # TODO return 404
#             print(f"NOT FOUND! {self.endpoint_class} - {self.method}")
#             def not_found(*arg):
#                 message = {
#                     'status': 404,
#                     'message': 'Not Found',
#                 }
#                 resp = jsonify(message)
#                 resp.status_code = 404
#                 return resp
#             return not_found(self.args)


# class endpoint_decorator(object):
#     def __init__(self, dec, endpoint_class, method, *args):
#         self.decorator = dec
#         self.endpoint_class = endpoint_class
#         self.method = method
#         self.args = args
#
#     def __call__(self, func, *args, **kwargs):
#         print(self.endpoint_class)
#         if (endpoints_dict is None or
#                 (self.endpoint_class in endpoints_dict and
#                  self.method in endpoints_dict[self.endpoint_class])):
#             return func(*args, **kwargs)
#         else:
#             # Return the function unchanged, not decorated.
#             # Return the function without api docs
#             # TODO return 404
#             print(f"NOT FOUND! {self.endpoint_class} - {self.method}")
#             def not_found():
#                 res = (jsonify(SimpleResponseModel(
#                     status=404,
#                     message='Error'
#                 )))
#                 return make_response("test", 404)
#             return not_found()

# class endpoint_decorator(object):
#     def __init__(self, dec, endpoint_class, method, *args):
#         self.decorator = dec
#         self.endpoint_class = endpoint_class
#         self.method = method
#         self.args = args
#
#     def __call__(self, func, *args, **kwargs):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             def not_found():
#                 # res = (jsonify(SimpleResponseModel(
#                 #     status=404,
#                 #     message='Error'
#                 # )))
#                 return make_response("test", 404)
#
#             if (endpoints_dict is None or
#                     (self.endpoint_class in endpoints_dict and
#                      self.method in endpoints_dict[self.endpoint_class])):
#                 print("endpoint_decorator: IF")
#                 result = self.decorator(func(*args, **kwargs))
#                 return result
#             else:
#                 print(f"NOT FOUND! {self.endpoint_class} - {self.method}")
#                 result = not_found()
#                 return result
#         return wrapper


class endpoint_decorator(object):
    def __init__(self, dec, api_desc, endpoint_class, method, *args):
        self.decorator = dec
        self.api_desc = api_desc
        self.endpoint_class = endpoint_class
        self.method = method
        self.args = args
        print("INIT", self.endpoint_class)
        self.decorator(api_desc)
        # return result

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(self.endpoint_class)
            # def not_found():
            #     # res = (jsonify(SimpleResponseModel(
            #     #     status=404,
            #     #     message='Error'
            #     # )))
            #     return make_response("test", 404)

            if True:
            # if (endpoints_dict is None or
            #         (self.endpoint_class in endpoints_dict and
            #          self.method in endpoints_dict[self.endpoint_class])):
                print("endpoint_decorator: IF")
                result = self.decorator(func(*args, **kwargs))
                return result
            else:
                print(f"NOT FOUND! {self.endpoint_class} - {self.method}")
            #     result = not_found()
            #     return result
        return wrapper
