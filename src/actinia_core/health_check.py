#!flask/bin/python
# -*- coding: utf-8 -*-
"""
Main file of the Actinia Core API
"""

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"

from .resources.common.app import flask_app, URL_PREFIX
from flask import make_response

# This is a simple endpoint to check the health of the Actinia Core server
# This is needed by Google load balancer
@flask_app.route(URL_PREFIX + '/health_check')
def health_check():
    # TODO: Add checks of the Actinia Core compute node state
    #       - is the config correct
    #       - Are the queues running
    #       - Is redis available
    # TODO: This check must be triggered to respond with 404 for node replacement
    #       in case of an update or bugfix.
    #       Hence, the load balance will not deliver any content to this node if
    #       the health check responses with a 404.
    return make_response("OK", 200)
