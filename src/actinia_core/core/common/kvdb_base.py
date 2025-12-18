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
Kvdb base class
"""

import valkey
from actinia_core.core.logging_interface import log

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2023, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class KvdbBaseInterface(object):
    """
    The base class for most kvdb database interfaces
    """

    def __init__(self):
        self.connection_pool = None
        self.kvdb_server = None

    def connect(self, host="localhost", port=6379, password=None):
        """Connect to a specific kvdb server

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
        self.kvdb_server = valkey.StrictValkey(
            connection_pool=self.connection_pool
        )
        try:
            self.kvdb_server.ping()
        except valkey.exceptions.ResponseError as e:
            log.error("Could not connect to " + host, port, str(e))
        except valkey.exceptions.AuthenticationError:
            log.error("Invalid password")
        except valkey.exceptions.ConnectionError as e:
            log.error(str(e))

    def disconnect(self):
        self.connection_pool.disconnect()
