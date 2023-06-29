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
Base class for logger that uses fluentd/stdout for logging and resource storage
"""
import time
import logging

from actinia_core.core.common.config import global_config
from .logging_interface import log

if global_config.LOG_INTERFACE == "fluentd":
    from fluent import sender


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-present, Sören Gebbert and mundialis GmbH & Co. KG"
)


class RedisFluentLoggerBase(object):
    """Base class for all logger that use Redis and fluentd for logging"""

    def __init__(self, config=None, user_id=None, fluent_sender=None):
        if config is None:
            config = global_config
        if user_id is None:
            user_id = "Unknown"

        self.host = config.LOG_FLUENT_HOST
        self.port = config.LOG_FLUENT_PORT
        self.interface = config.LOG_INTERFACE
        self.log_level = config.LOG_LEVEL
        self.user_id = user_id
        self.fluent_sender = fluent_sender

        # The fluentd sender
        if fluent_sender is None and global_config.LOG_INTERFACE == "fluentd":
            self.fluent_sender = sender.FluentSender(
                "actinia_logger", host=self.host, port=self.port
            )

    def _send_to_fluent(self, tag, data):
        try:
            cur_time = int(time.time())
            self.fluent_sender.emit_with_time(
                tag, timestamp=cur_time, data=data
            )
        except Exception as e:
            log.error(
                (
                    "%s is unable to connect to fluentd server host %s "
                    "port %i Error: %s, Content %s"
                )
                % (tag, self.host, self.port, str(e), str(data))
            )

        # keep this until sure that all logs are fetched if stdout log is set
        # tags = ['RESOURCE_LOG', 'API_LOG', 'INFO', 'DEBUG']
        if (
            "RESOURCE_LOG" not in tag
            and "API_LOG" not in tag
            and "INFO" not in tag
            and "DEBUG" not in tag
        ):
            print(
                "WARNING: Some output might not be redirected to STDOUT:"
                + " %s %s %s" % (tag, str(cur_time), str(data))
            )

    def _send_to_logging_interface(self, tag, data):
        if tag == "RESOURCE_LOG" and "status" in data:
            if data["status"] == "error":
                log.error(data)
            elif data["status"] == "terminated":
                log.warning(data)
            else:
                log.info(data)

        elif tag == "API_LOG":
            log.info(data)

        # MESSAGES_LOGGER
        else:
            try:
                log.log(getattr(logging, tag), data)
            except AttributeError:
                log.debug("Unknown log tag for logging: %s", tag)
                log.info(data)

    def send_to_logger(self, tag, data):
        if global_config.LOG_INTERFACE == "fluentd":
            self._send_to_fluent(tag, data)

        # always send to logger as file logger (and stdout) is included here
        self._send_to_logging_interface(tag, data)
