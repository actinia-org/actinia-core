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
Main file of the Actinia Core API
"""

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

from flask import make_response
from actinia_api import URL_PREFIX

from actinia_core.core.common.app import flask_app

# This is a simple endpoint to check the health of the Actinia Core server
# This is needed by Google load balancer


@flask_app.route(URL_PREFIX + "/health_check")
def health_check():
    # TODO: Add checks of the Actinia Core compute node state
    #       - is the config correct
    #       - Are the queues running
    #       - Is redis available
    # TODO: This check must be triggered to respond with 404 for node
    #       replacement in case of an update or bugfix.
    #       Hence, the load balance will not deliver any content to this node
    #       if the health check responses with a 404.
    return make_response("OK", 200)
