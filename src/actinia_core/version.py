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
from .resources.common.app import flask_app, API_VERSION, URL_PREFIX
from .resources.common.config import global_config
from . import __version__

# Return the version of Actinia Core as REST API call
@flask_app.route(URL_PREFIX + '/version')
def version():
    """Return the version information and the roles that are activated

    Returns: Response

    """
    info = {"version":__version__, "plugins":",".join(global_config.PLUGINS)}

    if 'actinia_gdi' in global_config.PLUGINS:
        from actinia_gdi import __version__ as actinia_gdi_version
        info['plugin_versions'] = {'actinia_gdi': actinia_gdi_version}

    return make_response(jsonify(info), 200)
