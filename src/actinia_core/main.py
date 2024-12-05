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
Actinia Core
"""

import os
from .endpoints import create_endpoints
from .version import init_versions
from actinia_core.core.common.app import flask_app
from actinia_core.core.common.config import global_config, DEFAULT_CONFIG_PATH
from actinia_core.core.common.redis_interface import connect
from actinia_core.core.common.process_queue import create_process_queue

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

# if os.environ.get('DEFAULT_CONFIG_PATH'):
#     DEFAULT_CONFIG_PATH = os.environ['DEFAULT_CONFIG_PATH']
if os.path.exists(DEFAULT_CONFIG_PATH) is True and os.path.isfile(
    DEFAULT_CONFIG_PATH
):
    global_config.read(DEFAULT_CONFIG_PATH)

# Create the endpoints based on the global config
create_endpoints()
init_versions()

# TODO: Implement a better error handler
# @flask_app.errorhandler(InvalidUsage)
# def handle_invalid_usage(error):
#    response = error.to_json()
#    response.status_code = error.status_code
#    return response

# Connect the redis interfaces
redis_args = (global_config.REDIS_SERVER_URL, global_config.REDIS_SERVER_PORT)
if global_config.REDIS_SERVER_PW and global_config.REDIS_SERVER_PW is not None:
    redis_args = (*redis_args, global_config.REDIS_SERVER_PW)

connect(*redis_args)
del redis_args

# Create the process queue
create_process_queue(global_config)

###############################################################################
if __name__ == "__main__":
    # Connect to the database
    flask_app.run(host="0.0.0.0", port=8080, debug=True)
