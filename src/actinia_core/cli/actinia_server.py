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
Actinia server script

This script is for testing purpose only, since the actinia server should
run behind the uwsgi application server.
"""
import argparse
import os
from actinia_core.endpoints import create_endpoints
from actinia_core.core.common.app import flask_app
from actinia_core.core.common.config import global_config, DEFAULT_CONFIG_PATH
from actinia_core.core.common.redis_interface import connect
from actinia_core.core.common.process_queue import create_process_queue

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2023, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def main():
    parser = argparse.ArgumentParser(
        description="Start actinia server. A running redis server"
        + " is required."
    )

    parser.add_argument(
        "--host",
        type=str,
        required=False,
        default="0.0.0.0",
        help="The IP address that should be used for the server",
    )

    parser.add_argument(
        "--port",
        type=int,
        required=False,
        default=5000,
        help="The port that should be used for the server",
    )

    parser.add_argument(
        "--debug",
        type=bool,
        required=False,
        default=True,
        help="Set True to activate debugging",
    )

    args = parser.parse_args()

    if os.path.exists(DEFAULT_CONFIG_PATH) is True and os.path.isfile(
        DEFAULT_CONFIG_PATH
    ):
        global_config.read(DEFAULT_CONFIG_PATH)

    # Create the endpoints based on the global config
    create_endpoints()

    # Connect the redis interfaces
    redis_args = (
        global_config.REDIS_SERVER_URL,
        global_config.REDIS_SERVER_PORT,
    )
    if (
        global_config.REDIS_SERVER_PW
        and global_config.REDIS_SERVER_PW is not None
    ):
        redis_args = (*redis_args, global_config.REDIS_SERVER_PW)

    connect(*redis_args)
    del redis_args

    # Create the process queue
    create_process_queue(global_config)

    flask_app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
