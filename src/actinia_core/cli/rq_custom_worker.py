#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2023 Sören Gebbert and mundialis GmbH & Co. KG
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
Redis Queue server custom worker
"""
from rq import Connection, Worker
from redis import Redis

# We need to append the path to the actinia_core package, since
# flask API does not send the correct module and package paths
# to the worker, so the workers are unable to de-serialize
# that object that are required by the asynchronous process classes.

# import sys
# import actinia_core
# from os.path import dirname
# sys.path.append(dirname(actinia_core.__file__))
# Integrate the fluentd logger into the logging infrastructure
# https://github.com/fluent/fluent-logger-python
import logging
import logging.handlers
from actinia_core.core.common.config import Configuration
from actinia_core.core.logging_interface import log
import os
import argparse
import platform

has_fluent = False

try:
    from fluent import handler

    has_fluent = True
except Exception:
    print("Fluent is not available")
    has_fluent = False

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-2023, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def main():
    parser = argparse.ArgumentParser(
        description="Start a single Actinia Core "
        "custom worker listening to a specific queue."
        "It uses the logfile settings that are specified "
        "in the default Actinia Core configuration file"
        "or a file specified by an optional path."
    )

    if parser.prog == "rq_custom_worker":
        log.warning(
            'The command "rq_custom_worker" is deprecated and will be '
            'removed soon. Use "actinia-worker" instead!'
        )

    parser.add_argument(
        "queue",
        type=str,
        help="The name of the queue that should be listen to by the worker",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=False,
        help="The path to the Actinia Core configuration file",
    )
    parser.add_argument(
        "-q",
        "--quit",
        action="store_true",
        required=False,
        help="Wether or not the worker should exit when the queue is emptied.",
    )

    args = parser.parse_args()

    conf = Configuration()
    try:
        if args.config and os.path.isfile(args.config):
            conf.read(path=args.config)
        else:
            conf.read()
    except IOError as e:
        print(
            "WARNING: unable to read config file, "
            "will use defaults instead, IOError: %s" % str(e)
        )

    # Provide queue names to listen to as arguments to this script,
    # similar to rq worker
    with Connection(
        Redis(
            conf.REDIS_QUEUE_SERVER_URL,
            conf.REDIS_QUEUE_SERVER_PORT,
            password=conf.REDIS_QUEUE_SERVER_PASSWORD,
        )
    ):
        logger = logging.getLogger("rq.worker")
        logger.setLevel(logging.ERROR)

        node = platform.node()

        if conf.LOG_INTERFACE == "fluentd" and has_fluent is True:
            custom_format = {
                "host": "%(hostname)s",
                "where": "%(module)s.%(funcName)s",
                "status": "%(levelname)s",
                "stack_trace": "%(exc_text)s",
            }
            fh = handler.FluentHandler(
                "%s::rq.worker" % node,
                host=conf.LOG_FLUENT_HOST,
                port=conf.LOG_FLUENT_PORT,
            )
            formatter = handler.FluentRecordFormatter(custom_format)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        # Add the log message handler to the logger
        log_file_name = "%s_%s.log" % (conf.WORKER_LOGFILE, args.queue)
        lh = logging.handlers.RotatingFileHandler(
            log_file_name,
            maxBytes=2000000,
            backupCount=5,
        )
        logger.addHandler(lh)
        logger.fatal(
            msg="Started rq.worker: %s\n"
            "host %s port: %s \n"
            "logging into %s"
            % (
                args.queue,
                conf.REDIS_QUEUE_SERVER_URL,
                conf.REDIS_QUEUE_SERVER_PORT,
                log_file_name,
            )
        )

        actinia_worker = Worker(
            [
                args.queue,
            ]
        )
        if bool(args.quit) is True:
            actinia_worker.work(burst=True)
        else:
            actinia_worker.work()


if __name__ == "__main__":
    main()
