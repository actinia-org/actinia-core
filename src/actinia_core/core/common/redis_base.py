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
Redis base class
"""

import valkey
from actinia_core.core.logging_interface import log

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class RedisBaseInterface(object):
    """
    The base class for most redis database interfaces
    """

    def __init__(self):
        self.connection_pool = None
        self.redis_server = None

    def connect(self, host="localhost", port=6379, password=None):
        """Connect to a specific redis server

        Args:
            host (str): The host name or IP address
            port (int): The port
            password (str): The password

        """
        kwargs = dict()
        kwargs["host"] = host
        kwargs["port"] = port
        if password and password is not None:
            kwargs["password"] = password
        self.connection_pool = valkey.ConnectionPool(**kwargs)
        del kwargs
        self.redis_server = valkey.StrictRedis(
            connection_pool=self.connection_pool
        )
        try:
            self.redis_server.ping()
        except valkey.exceptions.ResponseError as e:
            log.error("Could not connect to " + host, port, str(e))
        except valkey.exceptions.AuthenticationError:
            log.error("Invalid password")
        except valkey.exceptions.ConnectionError as e:
            log.error(str(e))

    def disconnect(self):
        self.connection_pool.disconnect()
