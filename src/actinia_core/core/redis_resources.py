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
Redis server resource logging interface
"""

from actinia_core.core.common.redis_base import RedisBaseInterface

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class RedisResourceInterface(RedisBaseInterface):
    """
    The Redis resource database interface
    """

    # The database to store the long pending resource status and results
    resource_id_prefix = "RESOURCE-ID::"
    resource_id_termination_prefix = "RESOURCE-ID-TERMINATION::"

    def __init__(self):
        """
        The resource database stores information about a resource that was
        created by a GRASS process or that is in state of creation. The GRASS
        process will continually update the state of the resource by altering
        the resource information.

        Other processes can access the state of the resource and deliver it to
        clients, independently which server process creates and updates the
        resource.

        Database entries are based on setex and have an expiration time of
        8640000 seconds (100 days) by default. This can also be set using the
        Actinia Core config file.

        The following scheme should be used::

            Client         GRASS Server              Resource DB
               |                |                         |
               |---------> Submit job     ---------> Create entry set accepted
               |<--------- Resource id                    |
               |                |                         |
               |           Start job      ---------> Update entry set running
               |                |                         |
               |---------> Status?                        |
               |           Request status ---------> Read entry
               |<--------- Deliver status <--------- Return entry
               |                |                         |
               |           Run job        ---------> Update entry set running
               |                |                         |
               |           Finish job     ---------> Update entry set finished
               |                |                         |
               |---------> Status?                        |
               |           Request status ---------> Read entry
               |<--------- Deliver status <--------- Return entry
               |                |                         |
               V                V                         V

            # Termination of a job

            Client         GRASS Server              Resource DB
               |                |                         |
               |---------> Submit job     ---------> Create entry
               |<--------- Resource id                    |
               |                |                         |
               |           Start job      ---------> Update entry set running
               |                |                         |
               |           Request status ---------> Read termination entry
               |           Run job        ---------> Update entry set running
               |                |                         |
               |-----------------------------------> Set termination entry
               |                |                         |
               |           Request status ---------> Read termination entry
               |           Terminate job  ---------> Update entry set
                                                     terminated
               |                |                         |
               |---------> Status?                        |
               |           Request status ---------> Read entry
               |<--------- Deliver status <--------- Return entry
               |                |                         |
               V                V                         V

        A GRASS server that delivers the job status may not be the same
        server that computes the results.

        The client does not set the termination entry directly,
        a GRASS REST process will do this.

        The GRASS process runner that updates the resource entries will
        check periodically for termination entries. If a termination
        entry exists, the job will be terminated and all allocated resources
        (RAM, HD) will be freed.

        """
        RedisBaseInterface.__init__(self)

    def set(self, resource_id, resource_entry, expiration=864000):
        """Set or update a resource entry

        Args:
            resource_id (str): The unique id of the resource
            resource_entry (str): The entry that should be put in the database
            expiration (int): The time in seconds when this resource should
                              expire

        """
        return self.redis_server.setex(
            self.resource_id_prefix + resource_id, expiration, resource_entry
        )

    def set_termination(self, resource_id, expiration=3600):
        """Set or update a resource termination entry

        The running job will check for termination periodically and will
        terminate the job if an entry exists.

        Args:
            resource_id (str): The unique id of the resource that should be
                               terminated
            expiration (int): The time in seconds when this resource should
                              expire

        """
        return self.redis_server.setex(
            self.resource_id_termination_prefix + resource_id, expiration, 1
        )

    def get(self, resource_id):
        """Get the resource entry if exists

        Args:
            resource_id (str): The unique id of the resource

        Returns:
            str:
            The resource entry or None
        """
        value = self.redis_server.get(self.resource_id_prefix + resource_id)
        return value

    def get_keys_from_pattern(self, resource_id_pattern):
        """Get all keys of a resource_id_pattern

        Args:
            resource_id_pattern (str): The pattern to the resources

        Returns:
            list:
            The list of the matching kesy
        """
        values = self.redis_server.scan_iter(
            self.resource_id_prefix + resource_id_pattern
        )
        resource_keys = list()
        for val in values:
            resource_keys.append(
                val.decode("utf-8").replace(self.resource_id_prefix, "")
            )
        return resource_keys

    def get_list(self, regexpr):
        """Get a list of resource entries if exists

        Args:
            regexpr (str): A regular expression

        Returns:
            list:
            A list of resource entries
        """
        key_list = self.redis_server.keys(self.resource_id_prefix + regexpr)
        resource_list = []
        if key_list:
            for key in key_list:
                value = self.redis_server.get(key.decode())
                resource_list.append(value)
        return resource_list

    def get_termination(self, resource_id):
        """Get the resource termination entry if exists

        The running job will check for termination periodically and will
        terminate the job if an entry exists.

        Args:
            resource_id (str): The unique id of the resource

        Returns:
            bool:
            True or False
        """
        return bool(
            self.redis_server.get(
                self.resource_id_termination_prefix + resource_id
            )
        )

    def get_termination_list(self, regexpr):
        """Get a list of termination resource entries if exists

        Args:
            regexpr (str): A regular expression

        Returns:
            list:
            A list of resource entries
        """
        term_key_list = self.redis_server.keys(
            self.resource_id_termination_prefix + regexpr
        )

        resource_list = []
        if term_key_list:
            for key in term_key_list:
                resource_list.append(key.decode())

        return resource_list

    def delete(self, resource_id):
        """Delete a resource entry

        Args:
            resource_id (str): The unique id of the resource

        """
        return self.redis_server.delete(self.resource_id_prefix + resource_id)

    def delete_termination(self, resource_id):
        """Delete a termination resource entry

        Args:
            resource_id (str): The unique id of the resource

        """
        return self.redis_server.delete(
            self.resource_id_termination_prefix + resource_id
        )


# Create the Redis interface instance
# redis_resource_interface = RedisResourceInterface()


def test_resource_entries(r):
    resource_id = "abcdefg"

    # Remove the resource entry if it exist
    r.delete(resource_id)

    ret = r.set(resource_id, "JSON file", expiration=20)
    if ret != 1:
        raise Exception("set does not work")

    ret = r.set(resource_id, "JSON file update", expiration=20)
    if ret != 1:
        raise Exception("set does not work")

    ret = r.get(resource_id)
    if ret != "JSON file update":
        raise Exception("get does not work")

    ret = r.set_termination(resource_id, expiration=20)
    if ret != 1:
        raise Exception("set_termination does not work")

    ret = r.get_termination(resource_id)
    if ret is not True:
        raise Exception("get_termination does not work")

    ret = r.delete(resource_id)
    if ret != 1:
        raise Exception("delete does not work")

    ret = r.get(resource_id)
    if ret is not None:
        raise Exception("get does not work")

    ret = r.delete_termination(resource_id)
    if ret != 1:
        raise Exception("delete_termination does not work")

    ret = r.get_termination(resource_id)
    if ret is not False:
        raise Exception("get_termination does not work")

    # Try the keys implementation

    r.delete(resource_id)

    ret = r.set(resource_id + "_1", "JSON file 1", expiration=20)
    if ret != 1:
        raise Exception("set does not work")

    ret = r.set(resource_id + "_2", "JSON file 2", expiration=20)
    if ret != 1:
        raise Exception("set does not work")

    ret = r.set(resource_id + "_3", "JSON file 3", expiration=20)
    if ret != 1:
        raise Exception("set does not work")

    rlist = r.get_list(resource_id + "*")
    print("line 275", rlist)
    for resource in rlist:
        if "JSON file" not in resource:
            raise Exception("keys does not work")

    ret = r.set_termination(resource_id + "_1", expiration=5)
    if ret != 1:
        raise Exception("set_termination does not work")

    ret = r.set_termination(resource_id + "_2", expiration=5)
    if ret != 1:
        raise Exception("set_termination does not work")

    ret = r.set_termination(resource_id + "_3", expiration=5)
    if ret != 1:
        raise Exception("set_termination does not work")

    rlist = r.get_termination_list(resource_id + "*")
    print(rlist)
    if len(rlist) != 3:
        raise Exception("set_termination does not work")


if __name__ == "__main__":
    import os
    import signal
    import time

    pid = os.spawnl(
        os.P_NOWAIT, "/usr/bin/redis-server", "./redis.conf", "--port 7000"
    )

    time.sleep(1)

    try:
        r = RedisResourceInterface()
        r.connect(host="localhost", port=7000)
        test_resource_entries(r)
        r.disconnect()
    except Exception:
        raise
    finally:
        os.kill(pid, signal.SIGTERM)
