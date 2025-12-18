# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2025 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Log messages as debug, info, warning and error
"""

import time
import platform
from .kvdb_fluentd_logger_base import KvdbFluentLoggerBase

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2025, Sören Gebbert & mundialis GmbH & Co. KG"


class MessageLogger(KvdbFluentLoggerBase):
    """Message logger that puts are logs to stderr"""

    def __init__(self, config=None, user_id=None, fluent_sender=None):
        KvdbFluentLoggerBase.__init__(
            self, config=config, user_id=user_id, fluent_sender=fluent_sender
        )

    def _log_message(self, log_level, message):
        node = platform.node()
        ctime = time.ctime()

        log_dict = {
            "node": node,
            "ctime": ctime,
            "user_id": self.user_id,
            "log_level": log_level,
            "status": "message",
            "message": message,
            "logger": "messages_logger",
        }

        self.send_to_logger(log_level, log_dict)

        # TODO: is this return value used anywhere?
        return message

    def debug(self, debug_message):
        if self.log_level >= 4:
            return self._log_message("DEBUG", debug_message)

    def info(self, info_message):
        if self.log_level >= 3:
            return self._log_message("INFO", info_message)

    def warning(self, warn_message):
        if self.log_level >= 2:
            return self._log_message("WARNING", warn_message)

    def error(self, error_message):
        if self.log_level >= 1:
            return self._log_message("ERROR", error_message)
