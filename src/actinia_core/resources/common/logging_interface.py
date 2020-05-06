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
import sys
import platform
from datetime import datetime

from colorlog import ColoredFormatter
from pythonjsonlogger import jsonlogger

from .config import global_config

if global_config.LOG_INTERFACE == "fluentd":
    from fluent import handler


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-present, Sören Gebbert and mundialis GmbH & Co. KG"


log = logging.getLogger('actinia-core')
stderrlog = logging.getLogger('actinia-core-stderr')
werkzeugLog = logging.getLogger('werkzeug')
gunicornLog = logging.getLogger('gunicorn')

# unfortunately, the config loads twice because of the read call here but it is
# needed to load the correct log level
global_config.read()

if global_config.LOG_LEVEL == 1:
    LOG_LEVEL = "ERROR"
elif global_config.LOG_LEVEL == 2:
    LOG_LEVEL = "WARNING"
elif global_config.LOG_LEVEL == 3:
    LOG_LEVEL = "INFO"
else:
    LOG_LEVEL = "DEBUG"


def setLogFormat(type):

    if type == 'stdout':
        format = global_config.LOG_STDOUT_FORMAT
    elif type == 'file':
        format = global_config.LOG_FILE_FORMAT

    logformat = ""
    if format == "json":
        logformat = CustomJsonFormatter('%(time) %(level) %(component) %(module)'
                                        '%(message) %(pathname) %(lineno)'
                                        '%(processName) %(threadName)'
                                        '%(node)')
    else:
        logformat = ColoredFormatter(
            '%(log_color)s[%(asctime)s] %(levelname)-10s: %(name)s.%(module)-'
            '10s -%(message)s [in %(pathname)s:%(lineno)d]%(reset)s'
        )
    return logformat


def setLogHandler(logger, type, format):
    if type == 'stdout' and global_config.LOG_INTERFACE == 'stdout':
        handler = logging.StreamHandler()
    elif type == 'file':
        handler = logging.handlers.RotatingFileHandler(
            global_config.WORKER_LOGFILE,
            maxBytes=2000000,
            backupCount=5
        )
    else:
        return
    handler.setFormatter(format)
    logger.addHandler(handler)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        # (Pdb) dir(record)
        # ... 'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName'
        # ,'getMessage', 'levelname', 'levelno', 'lineno', 'message', 'module',
        # 'msecs', 'msg', 'name', 'pathname', 'process', 'processName',
        # 'relativeCreated', 'stack_info', 'thread', 'threadName']

        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        log_record['time'] = now
        log_record['level'] = record.levelname
        log_record['component'] = record.name
        log_record['node'] = platform.node()


class StreamToLogger(object):
    """Simple logger to redirect sys.stdout and sys.stderr
    Inspired by: https://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/
    """

    def __init__(self, logger, log_level=logging.DEBUG):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''
        self.node = platform.node()

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            # the wrapper wraps log output from different loggers. To prevent:
            if 'gunicorn.' in line or 'actinia-gdi' in line:
                print(line.rstrip())
            else:
                # In case this is a stacktrace, it is logged line by line, each
                # wrapped in the log formatter. It is hardly readable and
                # context can get lost (but needed by e.g. kibana).
                self.logger.log(self.log_level, line.rstrip())
                if global_config.LOG_STDERR_FORMAT == 'plain':
                    # This is a tradeoff for readable stacktrace in the console
                    print(line.rstrip())

    def flush(self):
        pass


def createLogger():
    log.setLevel(getattr(logging, LOG_LEVEL))
    fileformat = setLogFormat('file')
    stdoutformat = setLogFormat('stdout')
    setLogHandler(log, 'file', fileformat)
    setLogHandler(log, 'stdout', stdoutformat)

    if global_config.LOG_INTERFACE == "fluentd":
        node = platform.node()
        custom_format = {
            'host': '%(hostname)s',
            'where': '%(module)s.%(funcName)s',
            'status': '%(levelname)s',
            'stack_trace': '%(exc_text)s'
        }
        fh = handler.FluentHandler('%s::actinia.worker' % node,
                                   host=global_config.LOG_FLUENT_HOST,
                                   port=global_config.LOG_FLUENT_PORT)
        fh_formatter = handler.FluentRecordFormatter(custom_format)
        fh.setFormatter(fh_formatter)
        log.addHandler(fh)

def createStderrLogger():
    stderrlog.setLevel(getattr(logging, LOG_LEVEL))
    fileformat = setLogFormat('file')
    setLogHandler(stderrlog, 'file', fileformat)

    if global_config.LOG_STDERR_FORMAT != 'plain':
        stdoutformat = setLogFormat('stdout')
        setLogHandler(stderrlog, 'stdout', stdoutformat)

    sl2 = StreamToLogger(stderrlog, logging.CRITICAL)
    sys.stderr = sl2
    # WARNING activate this only if you know what you are doing. It will format
    # everything that appears on stdout, even already formatted log messages
    # from different loggers (e.g. from plugins) and debug print statements.
    # sys.stdout = sl2

def createWerkzeugLogger():
    werkzeugLog.setLevel(getattr(logging, LOG_LEVEL))
    fileformat = setLogFormat('file')
    stdoutformat = setLogFormat('stdout')
    setLogHandler(werkzeugLog, 'file', fileformat)
    setLogHandler(werkzeugLog, 'stdout', stdoutformat)


def createGunicornLogger():
    gunicornLog.setLevel(getattr(logging, LOG_LEVEL))
    fileformat = setLogFormat('file')
    stdoutformat = setLogFormat('stdout')
    setLogHandler(gunicornLog, 'file', fileformat)
    setLogHandler(gunicornLog, 'stdout', stdoutformat)
    # gunicorn already has a lot of children logger, e.g gunicorn.http,
    # gunicorn.access. These lines deactivate their default handlers.
    for name in logging.root.manager.loggerDict:
        if "gunicorn." in name:
            logging.getLogger(name).propagate = True
            logging.getLogger(name).handlers = []


createLogger()
log.info("Log level is set to '%s'", LOG_LEVEL)
createStderrLogger()
createWerkzeugLogger()
createGunicornLogger()
