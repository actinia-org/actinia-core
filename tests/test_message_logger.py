# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2023 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Tests: Message logger test case

"""
import unittest
from actinia_core.core.common.config import Configuration
from actinia_core.core.messages_logger import MessageLogger

__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2023, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class MessageLoggerTestCase(unittest.TestCase):
    """
    This class tests the user interface, the creation and deletion
    of a user entry in a Kvdb database
    """

    def test_change_loglevel(self):
        c = Configuration()
        c.LOG_LEVEL = 4

        logger = MessageLogger(config=c, user_id="soeren")
        logger.debug("debug")
        logger.info("info")
        logger.warning("warning")
        logger.error("error")

        c = Configuration()
        c.LOG_LEVEL = 3

        logger = MessageLogger(config=c, user_id="soeren")
        logger.debug("debug")
        logger.info("info")
        logger.warning("warning")
        logger.error("error")

        c = Configuration()
        c.LOG_LEVEL = 2

        logger = MessageLogger(config=c, user_id="soeren")
        logger.debug("debug")
        logger.info("info")
        logger.warning("warning")
        logger.error("error")

        c = Configuration()
        c.LOG_LEVEL = 1

        logger = MessageLogger(config=c, user_id="soeren")
        logger.debug("debug")
        logger.info("info")
        logger.warning("warning")
        logger.error("error")

    def test_fluentd(self):
        c = Configuration()
        c.LOG_LEVEL = 4
        c.LOG_INTERFACE = "fluentd"

        logger = MessageLogger(config=c, user_id="soeren")
        logger.debug("debug")
        logger.info("info")
        logger.warning("warning")
        logger.error("error")


if __name__ == "__main__":
    unittest.main()
