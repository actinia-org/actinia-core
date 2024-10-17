# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2024 Sören Gebbert and mundialis GmbH & Co. KG
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
Redis server lock interface
"""

import redis

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class RedisLockingInterface(object):
    """
    The Redis locking database interface
    """

    # Redis LUA script to lock e resource
    # Two keys must be provided, the name of the resource and the expiration
    # time in seconds
    # lock_resource("project/mapset", 30)
    # Return 1 for success and 0 for unable to acquire lock because
    # resource-lock already exists
    lua_lock_resource = """
    local value_exists = redis.call('EXISTS', KEYS[1])
    if value_exists == 0 then
      redis.call("SETEX", KEYS[1], KEYS[2], 1)
      return 1
    end
    return 0
    """

    # LUA script to extend the lock valid time
    # Two keys must be provided, the name of the resource and the expiration
    # time in seconds
    # extend_resource_lock("user/project/mapset", 30)
    # Return 1 for success, 0 for resource does not exists
    lua_extend_resource_lock = """
    local value_exists = redis.call('EXISTS', KEYS[1])
    if value_exists == 0 then
        return 0
    else
      redis.call("EXPIRE", KEYS[1], KEYS[2])
      return 1
    end
    """

    # LUA script to unlock a resource
    # Return 1 for success, 0 for resource does not exists
    lua_unlock_resource = """
    local value_exists = redis.call('EXISTS', KEYS[1])
    if value_exists == 0 then
        return 0
    else
      redis.call("DEL", KEYS[1])
      return 1
    end
    """

    # Locks are Key-Value pairs in the Redis database using SET and DEl for
    # management
    lock_prefix = "RESOURCE-LOCK::"

    def __init__(self):
        self.connection_pool = None
        self.redis_server = None
        self.call_lock_resource = None
        self.call_extend_resource_lock = None
        self.call_unlock_resource = None

    def connect(self, host, port, password=None):
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
        self.connection_pool = redis.ConnectionPool(**kwargs)
        del kwargs
        self.redis_server = redis.StrictRedis(
            connection_pool=self.connection_pool
        )

        # Register the resource lock scripts in Redis
        self.call_lock_resource = self.redis_server.register_script(
            self.lua_lock_resource
        )
        self.call_extend_resource_lock = self.redis_server.register_script(
            self.lua_extend_resource_lock
        )
        self.call_unlock_resource = self.redis_server.register_script(
            self.lua_unlock_resource
        )

    def disconnect(self):
        self.connection_pool.disconnect()

    """
    LOCK
    The lock mechanism can be used to avoid concurrent access to GRASS GIS
    mapsets by several processes. A mapset has a unique id:

        project/mapset

    That can be used to create a resource lock. Locking and lock checking
    are atomic operations. Hence, it is guaranteed that only a single
    process in a distributed system can access the resource if the locking
    mechanism is used.
    """

    def get(self, resource_id, expiration=30):
        """Get the status of a resource lock

        Args:
            resource_id (str): Name of the resource to lock, for example
                               "project/mapset"

        Returns:
             bool:
             True if resource is locked, False otherwise

        """
        return bool(self.redis_server.get(self.lock_prefix + str(resource_id)))

    def lock(self, resource_id, expiration=30):
        """Lock a resource for a specific time frame

        The lock is acquired for the provided time

        This function will put a prefix before the resource name
        to avoid key conflicts with other resources that are logged
        in the Redis database.

        Args:
            resource_id (str): Name of the resource to lock, for example
                               "project/mapset"
            expiration (int): The time in seconds for which the lock is
                              acquired

        Returns:
             int:
             1 for success and 0 if unable to acquire lock because
             resource-lock already exists

        """

        keys = [self.lock_prefix + str(resource_id), expiration]
        return self.call_lock_resource(keys=keys)

    def extend(self, resource_id, expiration=30):
        """Extent the expiration of a resource lock for a specific time frame

        This function will put a prefix before the resource name
        to avoid key conflicts with other resources that are logged
        in the Redis database.

        Args:
            resource_id (str): Name of the resource to extent the lock, for
                               example "project/mapset"
            expiration (int): The time in seconds for which the lock is
                              acquired

        Returns:
            int:
            1 for success and 0 if unable to extent the lock because resource
            does not exists

        """
        keys = [self.lock_prefix + str(resource_id), expiration]
        # print("Extend Lock", expiration, self.lock_prefix + str(resource_id),
        # str(self))
        return self.call_extend_resource_lock(keys=keys)

    def unlock(self, resource_id):
        """Unlock a resource

        This function will put a prefix before the resource name
        to avoid key conflicts with other resources that are logged
        in the Redis database.

        Args:
            resource_id (str): Name of the resource to remove the lock, for
                               example "project/mapset"

        Returns:
            int:
            1 for success and 0 if unable to unlock

        """
        keys = [
            self.lock_prefix + str(resource_id),
        ]
        # print("UnLock", self.lock_prefix + str(resource_id), str(self))
        return self.call_unlock_resource(keys=keys)


# Create the Redis interface instance
# redis_lock_interface = RedisLockingInterface()


def test_locking(r):
    resource = "project/mapset"

    # Remove the lock if its present
    r.unlock(resource)

    ret = r.lock(resource, 5)
    if ret != 1:
        raise Exception("lock_resource does not work")

    ret = r.get(resource, 5)
    print("Lock status True", ret)
    if ret is not True:
        raise Exception("get lock does not work")

    ret = r.get("nothing", 5)
    print("Lock status False", ret)
    if ret is not False:
        raise Exception("get lock does not work")

    ret = r.extend(resource, 5)
    if ret != 1:
        raise Exception("extend_resource_lock does not work")
    ret = r.lock(resource, 5)
    if ret != 0:
        raise Exception("lock_resource does not work")
    ret = r.unlock(resource)
    if ret != 1:
        raise Exception("unlock_resource does not work")
    ret = r.unlock(resource)
    if ret != 0:
        raise Exception("unlock_resource does not work")
    ret = r.extend(resource, 5)
    if ret != 0:
        raise Exception("extend_resource_lock does not work")


if __name__ == "__main__":
    import os
    import signal
    import time

    pid = os.spawnl(
        os.P_NOWAIT, "/usr/bin/redis-server", "./redis.conf", "--port 7000"
    )

    time.sleep(1)

    try:
        r = RedisLockingInterface()
        r.connect(host="localhost", port=7000)
        test_locking(r)
        r.disconnect()
    except Exception:
        raise
    finally:
        os.kill(pid, signal.SIGTERM)
