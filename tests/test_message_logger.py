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
Tests: Message logger test case

"""
import unittest
from actinia_core.core.common.config import Configuration
from actinia_core.core.messages_logger import MessageLogger

__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class MessageLoggerTestCase(unittest.TestCase):
    """
    This class tests the user interface, the creation and deletion
    of a user entry in a Redis database
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
