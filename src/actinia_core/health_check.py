#!flask/bin/python
# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2023 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Main file of the Actinia Core API
"""

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2023, Sören Gebbert & mundialis GmbH & Co. KG"
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
    #       - Is kvdb available
    # TODO: This check must be triggered to respond with 404 for node
    #       replacement in case of an update or bugfix.
    #       Hence, the load balance will not deliver any content to this node
    #       if the health check responses with a 404.
    return make_response("OK", 200)
