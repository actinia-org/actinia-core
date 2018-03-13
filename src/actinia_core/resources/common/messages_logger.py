# -*- coding: utf-8 -*-
"""
Log messages as debug, info, warning and error
"""

import time
import sys
import platform
from actinia_core.resources.common.redis_fluentd_logger_base import RedisFluentLoggerBase

try:
    from fluent import sender
    from fluent import event

    has_fluent = True
except:
    has_fluent = False

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class MessageLogger(RedisFluentLoggerBase):
    """Message logger that puts are logs to stderr
    """

    def __init__(self, config=None, user_id=None, fluent_sender=None):
        RedisFluentLoggerBase.__init__(self, config=config, user_id=user_id, fluent_sender=fluent_sender)

        if has_fluent is False:
            self.interface = "stderr"

    def _prepare_message(self, log_level, message):

        node = platform.node()
        ctime = time.ctime()

        return "## %s ## %s\thost=%s\tuser_id=%s\tmessage:\t%s\n" % (log_level, ctime, node, self.user_id, message)

    def _log_message(self, log_level, message):

        if self.interface == "fluentd":

            try:
                node = platform.node()
                ctime = time.ctime()

                self.send_to_fluent(log_level, {"node": node,
                                                "ctime": ctime,
                                                "user_id": self.user_id,
                                                "log_level": log_level,
                                                "status": "message",
                                                "message": message})
            except Exception as e:
                sys.stderr.write("MessageLogger ERROR: Unable to connect to fluentd server "
                                 "host %s port %i error: %s" % (self.host,
                                                                self.port,
                                                                str(e)))
                message = self._prepare_message(log_level, message)
                sys.stderr.write(message)
        else:
            message = self._prepare_message(log_level, message)
            sys.stderr.write(message)
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
