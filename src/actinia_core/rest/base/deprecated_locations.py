# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2024 mundialis GmbH & Co. KG
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
Deprecated location decorator
"""


from flask import jsonify, make_response, request
from functools import wraps

from actinia_core.models.response_models import SimpleResponseModel
from actinia_core.version import G_VERSION


__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2024, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"


def location_deprecated_decorator(func):
    """Add deprecation for location to headers.
    Requesting GRASS GIS version to add:
    * deprecation warning inside headers for GRASS >= 8.4
    * permanently moved page error for GRASS >= 9.0
    * error if projects is used for GRASS < 8.4
    * else no addition to result

    Args:
        func (function): The function to wrap

    Returns:
        function: The decorator functions
    """

    @wraps(func)
    def decorator(*args, **kwargs):
        current_url = request.base_url
        project_url = current_url.replace("locations", "projects")
        # get current GRASS GIS version
        grass_version_s = G_VERSION["version"]
        grass_version = [int(item) for item in grass_version_s.split(".")[:2]]
        if (
            "locations" in current_url
            and grass_version >= [8, 4]
            and grass_version < [9, 0]
        ):
            # deprecation warning inside headers for GRASS >= 8.4
            result = func(*args, **kwargs)
            result.headers.set("Deprecation", "With GRASS GIS 8.4")
            result.headers.set("Sunset", "With GRASS GIS 9.0")
            result.headers.set("Location", project_url)
        elif "locations" in current_url and grass_version >= [9, 0]:
            # permanently moved page error for GRASS >= 9.0
            result = make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message=f"Moved Permanently to {project_url}.",
                    )
                ),
                301,
            )
        elif "projects" in current_url and grass_version < [8, 4]:
            # error if projects is used for GRASS < 8.4
            result = make_response(
                jsonify(
                    SimpleResponseModel(
                        status="error",
                        message="Not Found. The requested URL is only "
                        "available from GRASS GIS version 8.4.",
                    )
                ),
                404,
            )
        else:
            # else no addition to result
            result = func(*args, **kwargs)
        return result

    return decorator
