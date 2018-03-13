# -*- coding: utf-8 -*-
"""
Redis base class
"""

import redis

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class RedisBaseInterface(object):
    """
    The base class for most redis database interfaces
    """

    def __init__(self):
        self.connection_pool = None
        self.redis_server = None

    def connect(self, host="localhost", port=6379):
        """Connect to a specific redis server

        Args:
            host (str): The host name or IP address
            port (int): The port

        """
        self.connection_pool = redis.ConnectionPool(host=host, port=port)
        self.redis_server = redis.StrictRedis(connection_pool=self.connection_pool)

    def disconnect(self):
        self.connection_pool.disconnect()
