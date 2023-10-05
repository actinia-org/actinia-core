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
Logging interface
"""

import logging
import logging.handlers
import os
import sys
import platform
from datetime import datetime

from pythonjsonlogger import jsonlogger

from actinia_core.core.common.config import global_config

# unfortunately, the config is read twice because of the read call here but it
# is needed to load the correct interface and log level at this time
global_config.read()

if "colored" in [
    global_config.LOG_STDOUT_FORMAT,
    global_config.LOG_FILE_FORMAT,
]:
    from colorlog import ColoredFormatter

if global_config.LOG_INTERFACE == "fluentd":
    from fluent import handler


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-present, Sören Gebbert and mundialis GmbH & Co. KG"
)


class BasicLogger(object):
    """Basic Logger Class to create a logger and add file and/or stdout handler
    depending on config with colored or json log format.

    Parameters
    ----------
    name : string
        Name of Logger to be created.
    """

    def __init__(self, name):
        self.createLogger(name)
        self.addFileHandler()
        self.addStdouthandler()

    def createLogger(self, name):
        self.log = logging.getLogger(name)
        self.initLevel()
        self.log.setLevel(getattr(logging, self.log_level))

    def addFileHandler(self):
        fileformat = self.getLogFormat("file")
        self.setLogHandler(self.log, "file", fileformat)

    def addStdouthandler(self):
        stdoutformat = self.getLogFormat("stdout")
        self.setLogHandler(self.log, "stdout", stdoutformat)

    def initLevel(self):
        level = global_config.LOG_LEVEL
        if level == 1:
            LOG_LEVEL = "ERROR"
        elif level == 2:
            LOG_LEVEL = "WARNING"
        elif level == 3:
            LOG_LEVEL = "INFO"
        else:
            LOG_LEVEL = "DEBUG"
        self.log_level = LOG_LEVEL

    def getLogFormat(self, type):
        if type == "stdout":
            format = global_config.LOG_STDOUT_FORMAT
        elif type == "file":
            format = global_config.LOG_FILE_FORMAT

        if format == "json":
            return CustomJsonFormatter(
                "%(time) %(level) %(component) %(module)%(message) %(pathname)"
                " %(lineno)%(processName) %(threadName)%(node)"
            )
        else:
            return ColoredFormatter(
                "%(log_color)s[%(asctime)s] %(levelname)-10s: "
                "%(name)s.%(module)-10s -%(message)s "
                "[in %(pathname)s:%(lineno)d]%(reset)s"
            )

    def setLogHandler(self, logger, type, format):
        if type == "stdout" and global_config.LOG_INTERFACE == "stdout":
            handler = logging.StreamHandler()
        elif type == "file":
            logfilepath = global_config.WORKER_LOGFILE.strip(
                global_config.WORKER_LOGFILE.split("/")[-1]
            )
            os.makedirs(logfilepath, exist_ok=True)
            handler = logging.handlers.RotatingFileHandler(
                global_config.WORKER_LOGFILE, maxBytes=2000000, backupCount=5
            )
        else:
            return
        handler.setFormatter(format)
        logger.addHandler(handler)


class ActiniaLogger(BasicLogger):
    """Actinia Logger which adds fluentd stream to BasicLogger if configured.

    Parameters
    ----------
    name : string
        Name of Logger to be created.
    """

    def __init__(self, name):
        BasicLogger.__init__(self, name)
        if global_config.LOG_INTERFACE == "fluentd":
            node = platform.node()
            custom_format = {
                "host": "%(hostname)s",
                "where": "%(module)s.%(funcName)s",
                "status": "%(levelname)s",
                "stack_trace": "%(exc_text)s",
            }
            fh = handler.FluentHandler(
                "%s::actinia.worker" % node,
                host=global_config.LOG_FLUENT_HOST,
                port=global_config.LOG_FLUENT_PORT,
            )
            fh_formatter = handler.FluentRecordFormatter(custom_format)
            fh.setFormatter(fh_formatter)
            self.log.addHandler(fh)


class StderrLogger(BasicLogger):
    """Standard Error Logger which collects all sys.stderr and redirects to
    logfile and console output, either in default log format (json/colored)
    or plain.

    Parameters
    ----------
    name : string
        Name of Logger to be created.
    """

    def __init__(self, name):
        self.createLogger(name)
        self.addFileHandler()

        if global_config.LOG_STDERR_FORMAT != "plain":
            self.addStdouthandler()

        sl = StreamToLogger(self.log)
        sys.stderr = sl
        # WARNING activate this only if you know what you are doing. It will
        # wrap everything that appears on stdout, even already formatted logs
        # from different loggers (e.g. from plugins) and debug print statements
        # sys.stdout = sl


class GunicornLogger(BasicLogger):
    """Collects gunicorn logs and transforms to configured format

    Parameters
    ----------
    name : string
        Name of Logger to be created.

    """

    def __init__(self, name):
        BasicLogger.__init__(self, name)
        # gunicorn already has a lot of children logger, e.g gunicorn.http,
        # gunicorn.access. These lines deactivate their default handlers.
        for name in logging.root.manager.loggerDict:
            if "gunicorn." in name:
                logging.getLogger(name).propagate = True
                logging.getLogger(name).handlers = []


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(
            log_record, record, message_dict
        )

        # (Pdb) dir(record)
        # ... 'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName'
        # ,'getMessage', 'levelname', 'levelno', 'lineno', 'message', 'module',
        # 'msecs', 'msg', 'name', 'pathname', 'process', 'processName',
        # 'relativeCreated', 'stack_info', 'thread', 'threadName']

        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        log_record["time"] = now
        log_record["level"] = record.levelname
        log_record["component"] = record.name
        log_record["node"] = platform.node()


class StreamToLogger(object):
    """Simple logger to redirect sys.stdout and sys.stderr
    Inspired by: https://www.electricmonk.nl/log/2011/08/14/
    redirect-stdout-and-stderr-to-a-logger-in-python/
    """

    def __init__(self, logger):
        self.logger = logger

    def write(self, buffer):
        for line in buffer.rstrip().splitlines():
            # the wrapper wraps log output from different loggers. To prevent:
            if "gunicorn." in line or "actinia-gdi" in line:
                print(line.rstrip())
            else:
                # In case this is a stacktrace, it is logged line by line, each
                # wrapped by the log formatter. It is hardly readable and
                # context can get lost (but needed by e.g. kibana).
                self.logger.log(logging.CRITICAL, line.rstrip())
                if global_config.LOG_STDERR_FORMAT == "plain":
                    # This is a tradeoff for readable stacktrace in the console
                    print(line.rstrip())

    def flush(self):
        pass


def createMainLogger():
    Log = ActiniaLogger("actinia-core")
    log = Log.log
    log.info("Log level is set to '%s'", Log.log_level)

    StderrLogger("actinia-core-stderr").log
    BasicLogger("werkzeug").log
    GunicornLogger("gunicorn").log

    return log


log = createMainLogger()
