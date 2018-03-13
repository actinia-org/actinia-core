#!flask/bin/python
# -*- coding: utf-8 -*-

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"

from flask import make_response, jsonify
from actinia_core.resources.common.app import flask_app
from actinia_core.resources.common.config import global_config

# Return the version of Actinia Core as REST API call
@flask_app.route('/version')
def version():
    """Return the version information and the roles that are activated

    Returns: Response

    """
    info = {"version":"0.01", "roles":global_config.ROLES}
    return make_response(jsonify(info), 200)
