#!flask/bin/python
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
Returns the version information and the roles that are activated
"""

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

from flask import make_response, jsonify
import importlib
import subprocess

from .resources.common.app import flask_app, URL_PREFIX
from .resources.common.config import global_config
from .resources.common.logging_interface import log
from . import __version__


G_VERSION = {}
PLUGIN_VERSIONS = {}


def init_versions():
    g_version = subprocess.run(
        ['grass', '--tmp-location', 'epsg:4326', '--exec',
         'g.version', '-rge'], capture_output=True).stdout
    log.debug('Detecting GRASS GIS version')
    for i in g_version.decode('utf-8').strip('\n').split('\n'):
        G_VERSION[i.split('=')[0]] = i.split('=')[1]

    log.debug('Detecting Plugin versions')
    for i in global_config.PLUGINS:
        module = importlib.import_module(i)
        PLUGIN_VERSIONS[i] = module.__version__


# Return the version of Actinia Core as REST API call
@flask_app.route(URL_PREFIX + '/version')
def version():
    """Return the version information and the roles that are activated

    Returns: Response

    """
    info = {}
    info['version'] = __version__
    info['plugins'] = ",".join(global_config.PLUGINS)
    info['grass_version'] = G_VERSION
    info['plugin_versions'] = PLUGIN_VERSIONS

    return make_response(jsonify(info), 200)
