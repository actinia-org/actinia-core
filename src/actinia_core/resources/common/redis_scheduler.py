# -*- coding: utf-8 -*-
"""
Redis server scheduler interface
"""

from actinia_core.resources.common.redis_base import RedisBaseInterface

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class RedisSchedulerInterface(RedisBaseInterface):
    """
    The Redis scheduler database interface
    """
    list = "SCHEDULER-LIST"

    def __init__(self):
        RedisBaseInterface.__init__(self)

    ########################## SCHEDULER LOG ##################################
    """
    The scheduler log is a simple list in the Redis database that stores all
    resources that should be deleted after a specific time. A scheduler process
    reads the list and removes all resources (files, images, ...) that expired
    their life cycle. The scheduler process is responsible to delete
    log entries that have been expired.
    """

    def add(self, log):
        """Add a scheduler log entry to the scheduler log list at the Redis server

        Args:
            log: A string

        Returns:
            int:
            The index of the new entry in the scheduler log list
        """
        return self.redis_server.lpush(self.list, log)

    def list(self, start, end):
        """Return all scheduler log entries between start and end indices

        Args:
            start (int): Integer start index
            end (int): Integer end index

        Returns:
            list:
            A list of scheduler log entries
        """
        return self.redis_server.lrange(self.list, start, end)

    def trim(self, start, end):
        """Remove all scheduler log entries outside start and end indices

        Args:
            start (int): Integer start index
            end (int): Integer end index

        """
        return self.redis_server.ltrim(self.list, start, end)

    def size(self):
        """Return the number of entries in the scheduler log list

        Returns:
            int:
            The number of entries in the scheduler log list
        """
        return self.redis_server.llen(self.list)

    def delete(self):
        """Remove the scheduler log list
        """
        return self.redis_server.delete(self.list)

# Create the Redis interface instance
# redis_scheduler_interface = RedisSchedulerInterface()


def test_scheduler_logging(r):

    # Remove the loglist
    r.delete()

    ret = r.add("Scheduler log entry 1")
    if ret != 1:
        raise Exception("add does not work")

    ret = r.add("Scheduler log entry 2")
    if ret != 2:
        raise Exception("add does not work")

    ret = r.add("Scheduler log entry 3")
    if ret != 3:
        raise Exception("add does not work")

    print(r.list(0, -1))

    ret = r.size()
    if ret != 3:
        raise Exception("size does not work")

    if r.trim(0, 1) is not True:
        raise Exception("trim_log does not work")

    ret = r.size()
    if ret != 2:
        raise Exception("size does not work")

    # Remove the loglist
    if r.delete() is not True:
        raise Exception("delete does not work")

if __name__ == '__main__':
    import os, signal
    import time

    pid = os.spawnl(os.P_NOWAIT, "/usr/bin/redis-server", "./redis.conf", "--port 7000")

    time.sleep(1)

    try:
        r = RedisSchedulerInterface()
        r.connect(host="localhost", port=7000)
        test_scheduler_logging(r)
        r.disconnect()
    except Exception as e:
        raise
    finally:
        os.kill(pid, signal.SIGTERM)
