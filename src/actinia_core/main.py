#!flask/bin/python
# -*- coding: utf-8 -*-
#
# Actinia Core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks.
#
# Copyright (c) 2016 Sören Gebbert
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
"""
Actinia Core
"""

import os
from .endpoints import create_endpoints
from .health_check import health_check
from .version import version
from .resources.common.app import flask_app
from .resources.common.config import global_config, DEFAULT_CONFIG_PATH
from .resources.common.redis_interface import connect, create_job_queues
from .resources.common.process_queue import create_process_queue

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"

if os.path.exists(DEFAULT_CONFIG_PATH) is True and os.path.isfile(DEFAULT_CONFIG_PATH):
    global_config.read(DEFAULT_CONFIG_PATH)

# Create the endpoints based on the global config
create_endpoints()

# TODO: Implement a better error handler
#@flask_app.errorhandler(InvalidUsage)
#def handle_invalid_usage(error):
#    response = error.to_json()
#    response.status_code = error.status_code
#    return response

# Connect the redis interfaces
connect(global_config.REDIS_SERVER_URL,
        global_config.REDIS_SERVER_PORT)

# Create the process queue
create_process_queue(global_config)

# Disabled since the redis queue does not work in Python3
# Create the job queue for redis
#create_job_queues(global_config.REDIS_QUEUE_SERVER_URL,
#                  global_config.REDIS_QUEUE_SERVER_PORT,
#                  global_config.NUMBER_OF_WORKERS)

########################################################################################################################
if __name__ == '__main__':
    # Connect to the database
    flask_app.run(host='0.0.0.0', port=8080, debug=True)
