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

from colorlog import ColoredFormatter

from .api_logger import ApiLogger, log_api_call
from .resources_logger import ResourceLogger
from .config import global_config


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-present, Sören Gebbert and mundialis GmbH & Co. KG"


log = logging.getLogger('actinia-core')
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


def setLogFormat(veto=None):
    logformat = ColoredFormatter(
        '%(log_color)s[%(asctime)s] %(levelname)-10s: %(name)s.%(module)-'
        '10s -%(message)s [in %(pathname)s:%(lineno)d]%(reset)s'
    )
    return logformat


def setLogHandler(logger, type, format):
    handler = logging.StreamHandler()
    handler.setFormatter(format)
    logger.addHandler(handler)


def createLogger():
    log.setLevel(getattr(logging, LOG_LEVEL))
    stdoutformat = setLogFormat()
    setLogHandler(log, 'stdout', stdoutformat)


def createWerkzeugLogger():
    werkzeugLog.setLevel(getattr(logging, LOG_LEVEL))
    stdoutformat = setLogFormat()
    setLogHandler(werkzeugLog, 'stdout', stdoutformat)


def createGunicornLogger():
    gunicornLog.setLevel(getattr(logging, LOG_LEVEL))
    stdoutformat = setLogFormat()
    setLogHandler(gunicornLog, 'stdout', stdoutformat)
    # gunicorn already has a lot of children logger, e.g gunicorn.http,
    # gunicorn.access. These lines deactivate their default handlers.
    for name in logging.root.manager.loggerDict:
        if "gunicorn." in name:
            logging.getLogger(name).propagate = True
            logging.getLogger(name).handlers = []


createLogger()
log.info("Log level is set to '%s'", LOG_LEVEL)
createWerkzeugLogger()
createGunicornLogger()
