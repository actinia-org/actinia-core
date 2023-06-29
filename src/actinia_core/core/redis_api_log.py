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
Redis server interface for API logging
"""

from actinia_core.core.common.redis_base import RedisBaseInterface

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class RedisAPILogInterface(RedisBaseInterface):
    """
    The Redis API log database interface
    """

    # API logging entries are lists in the Redis database using LPUSH, LTRIM,
    # LRANGE for management
    api_log_prefix = "API-LOG-LIST::"

    def __init__(self):
        RedisBaseInterface.__init__(self)

    """
    ########################## API  LOG #######################################
    """

    """
    The API logs are organized by lists that have as key the user id.
    Each API call from a user_id is logged in its dedicated list with
    lpush calls. For each user_id exists a dedicated list of API calls.

    Log entries for a user id can be listed trimmed and the log can be
    completely deleted.

    ..code:

    user_id_1 : log entry 1
                log entry 2
                log entry 3

    user_id_2 : log entry 1
                log entry 2
                log entry 3

    """

    def add(self, user_id, log_entry):
        """Add a API log entry to a user specific  API log list in the Redis
        server

        Args:
            user_id (str): The user id of the API log
            log_entry (str): A string

        Returns:
            int:
            The index of the new entry in the api log list

        """
        return self.redis_server.lpush(
            self.api_log_prefix + user_id, log_entry
        )

    def list(self, user_id, start, end):
        """Return all API log entries between start and end indices

        Args:
            user_id (str): The user id of the API log
            start (int): Integer start index
            end (int): Integer end index

        Returns:
            list:
            A list of user specific API log entries

        """
        return self.redis_server.lrange(
            self.api_log_prefix + user_id, start, end
        )

    def trim(self, user_id, start, end):
        """Remove all API log entries outside start and end indices

        Args:
            user_id (str): The user id of the API log
            start (int): Integer start index
            end (int): Integer end index

        Returns:
            bool:
            True in any case

        """
        return self.redis_server.ltrim(
            self.api_log_prefix + user_id, start, end
        )

    def size(self, user_id):
        """Return the number of entries in the api log list

        Args:
            user_id (str): The user id of the API log

        Returns:
            int:
            The number of entries in the api log list

        """
        return self.redis_server.llen(self.api_log_prefix + user_id)

    def delete(self, user_id):
        """Remove the log list

        Args:
            user_id (str): The user id of the API log

        Returns:
            bool:
            True in case of success, False otherwise

        """
        return bool(self.redis_server.delete(self.api_log_prefix + user_id))


# Create the Redis interface instance
redis_api_log_interface = RedisAPILogInterface()


def test_api_logging(r):
    user_id = "abcdefg"

    # Remove the loglist
    r.delete(user_id)

    ret = r.add(user_id, "API-log entry 1")
    if ret != 1:
        raise Exception("add does not work")

    ret = r.add(user_id, "API-log entry 2")
    if ret != 2:
        raise Exception("add does not work")

    ret = r.add(user_id, "API-log entry 3")
    if ret != 3:
        raise Exception("add does not work")

    print(r.list(user_id, 0, -1))

    ret = r.size(user_id)
    if ret != 3:
        raise Exception("size does not work")

    if r.trim(user_id, 0, 1) is not True:
        raise Exception("trim_log_entries does not work")

    ret = r.size(user_id)
    if ret != 2:
        raise Exception("size does not work")

    # Remove the loglist
    if r.delete(user_id) is not True:
        raise Exception("delete does not work")


if __name__ == "__main__":
    import os
    import signal
    import time

    pid = os.spawnl(
        os.P_NOWAIT, "/usr/bin/redis-server", "./redis.conf", "--port 7000"
    )

    time.sleep(1)

    try:
        r = RedisAPILogInterface()
        r.connect(host="localhost", port=7000)
        test_api_logging(r)
        r.disconnect()
    except Exception:
        raise
    finally:
        os.kill(pid, signal.SIGTERM)
