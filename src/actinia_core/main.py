#!flask/bin/python
# -*- coding: utf-8 -*-
"""
Actinia Core
"""

import os
from  actinia_core import endpoints
from  actinia_core import health_check
from  actinia_core import version
from actinia_core.resources.common.exceptions import InvalidUsage
from actinia_core.resources.common.app import flask_app
from actinia_core.resources.common.config import global_config, DEFAULT_CONFIG_PATH
from actinia_core.resources.common.redis_interface import connect, create_job_queues
from actinia_core.resources.common.process_queue import create_process_queue

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"

if os.path.exists(DEFAULT_CONFIG_PATH) is True and os.path.isfile(DEFAULT_CONFIG_PATH):
    global_config.read(DEFAULT_CONFIG_PATH)

# Create the endpoints based on the global config
endpoints.create_endpoints()

@flask_app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = error.to_json()
    response.status_code = error.status_code
    return response

# Connect the redis interfaces
connect(global_config.REDIS_SERVER_URL,
        global_config.REDIS_SERVER_PORT)

create_process_queue(global_config)

# Create the job queue for redis
#create_job_queues(global_config.REDIS_QUEUE_SERVER_URL,
#                  global_config.REDIS_QUEUE_SERVER_PORT,
#                  global_config.NUMBER_OF_WORKERS)

########################################################################################################################
if __name__ == '__main__':
    # Connect to the database
    flask_app.run(host='0.0.0.0', port=8080, debug=True)
