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
Base class for logger that use fluentd for logging and resource storage
"""
import time
from .config import global_config

try:
    from fluent import sender
    from fluent import event
    has_fluent = True
except:
    has_fluent = False

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class RedisFluentLoggerBase(object):
    """Base class for all logger that use Redis and fluentd for logging
    """

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
        if fluent_sender is None and has_fluent:
            self.fluent_sender = sender.FluentSender('actinia_logger', host=self.host, port=self.port)

    def send_to_fluent(self, tag, data):

        if has_fluent:
            cur_time = int(time.time())
            self.fluent_sender.emit_with_time(tag, timestamp=cur_time, data=data)
