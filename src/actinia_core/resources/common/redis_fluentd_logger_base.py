# -*- coding: utf-8 -*-
"""
Base class for logger that use fluentd for logging and resource storage
"""
import time
from actinia_core.resources.common.config import global_config

try:
    from fluent import sender
    from fluent import event
    has_fluent = True
except:
    has_fluent = False

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


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
