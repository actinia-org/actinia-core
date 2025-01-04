#!flask/bin/python
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
Returns the version information and the roles that are activated
"""

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

from flask import make_response, jsonify, request
from importlib import metadata
import os
import re
import subprocess
import sys
from actinia_api import URL_PREFIX

from actinia_core.core.common.app import flask_app
from actinia_core.core.common.config import global_config
from actinia_core.core.logging_interface import log
from actinia_core.models.response_models import LinkResponseModel
from . import __version__


G_VERSION = {}
PLUGIN_VERSIONS = {}
PYTHON_VERSION = ""
API_VERSION = ""


def init_versions():
    global PYTHON_VERSION
    global API_VERSION

    g_version = subprocess.run(
        [
            "grass",
            "--tmp-project",
            "epsg:4326",
            "--exec",
            "g.version",
            "-rge",
        ],
        capture_output=True,
    ).stdout
    if not g_version:
        # for GRASS GIS version < 8.4
        g_version = subprocess.run(
            [
                "grass",
                "--tmp-location",
                "epsg:4326",
                "--exec",
                "g.version",
                "-rge",
            ],
            capture_output=True,
        ).stdout
    log.debug("Detecting GRASS GIS version")
    for i in g_version.decode("utf-8").strip("\n").split("\n"):
        try:
            G_VERSION[i.split("=")[0]] = i.split("=")[1]
        except IndexError:
            pass

    log.debug("Detecting Plugin versions")
    for i in global_config.PLUGINS:
        try:
            PLUGIN_VERSIONS[i] = metadata.version(i)
        except metadata.PackageNotFoundError:
            PLUGIN_VERSIONS[i] = metadata.version(f"{i}.wsgi")

    log.debug("Detecting API versions")
    API_VERSION = metadata.version("actinia_api")

    PYTHON_VERSION = sys.version.replace("\n", "- ")


def valid_additional_version_info_key(cand):
    """Checks whether the input is a valid key for inclusion in the version/
    output. Keys may only contain lowercase letters and the underscore, have
    a length between 1 and 25 and must not be any of the reserved keys which
    we will set and populate."""
    minlength = 1
    maxlength = 25
    valid_reg_ex = "^[a-z_]{" + str(minlength) + "," + str(maxlength) + "}$"
    reserved_keys = [
        "grass_version",
        "plugin_versions",
        "plugins",
        "python_version",
        "version",
        "api_version",
    ]
    return cand and cand not in reserved_keys and re.match(valid_reg_ex, cand)


def parse_additional_version_info(env_value):
    """Parses key:value pairs which are separated with pipes and returns them
    as dictionary."""
    additional_info = {}
    # split at pipe |
    kvp_pairs = env_value.split("|")
    for kvp_pair in kvp_pairs:
        # split at colon : but only max once
        kvp = kvp_pair.split(":", 1)
        if len(kvp) == 2 and valid_additional_version_info_key(kvp[0]):
            additional_info[kvp[0]] = kvp[1]
    return additional_info


def find_additional_version_info():
    """If there is a ACTINIA_ADDITIONAL_VERSION_INFO environment variable,
    we'll try to parse its value and return more information that will
    eventually be added to the version output"""
    env_name = "ACTINIA_ADDITIONAL_VERSION_INFO"
    if env_name in os.environ:
        return parse_additional_version_info(os.environ[env_name])
    return {}


def find_running_since_info():
    """If there is a ACTINIA_RUNNING_SINCE environment variable, return its
    content"""
    env_name = "ACTINIA_RUNNING_SINCE"
    if env_name in os.environ:
        return os.environ[env_name]
    return "n/a"


# Return the version of Actinia Core as REST API call
@flask_app.route(URL_PREFIX + "/version")
def version():
    """Return the version information and the roles that are activated

    Returns: Response

    """
    # start with any potential additional version info or an empty dictionary
    info = find_additional_version_info()
    info["version"] = __version__
    info["plugins"] = ",".join(global_config.PLUGINS)
    info["grass_version"] = G_VERSION
    info["plugin_versions"] = PLUGIN_VERSIONS
    info["api_version"] = API_VERSION
    info["python_version"] = PYTHON_VERSION
    info["running_since"] = find_running_since_info()

    return make_response(jsonify(info), 200)


# Return a hint that this version is outdated
@flask_app.route("/api/v1/<path:actinia_path>")
def hint(actinia_path):
    """Return a hint that this version is no longer installed. If an older
    version is installed, this endpoint will be overwritten by a proxy.

    Returns: Response

    """
    url = request.url_root.strip("/") + URL_PREFIX + "/" + actinia_path

    return make_response(
        jsonify(
            LinkResponseModel(
                status="Not found",
                message=(
                    "Are you looking for the current API version? "
                    "Change 'v1' to 'v3' in the URL."
                ),
                links=[url],
            ),
            404,
        )
    )


@flask_app.route("/api/v2/<path:actinia_path>")
def hint_v2(actinia_path):
    """Return a hint that this version is no longer installed. If an older
    version is installed, this endpoint will be overwritten by a proxy.

    Returns: Response

    """
    url = request.url_root.strip("/") + URL_PREFIX + "/" + actinia_path

    return make_response(
        jsonify(
            LinkResponseModel(
                status="Not found",
                message=(
                    "Are you looking for the current API version? "
                    "Change 'v2' to 'v3' in the URL."
                ),
                links=[url],
            ),
            404,
        )
    )
