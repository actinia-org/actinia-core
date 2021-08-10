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
Redis connection interface
"""
import rq
from redis import Redis
from actinia_core.core.redis_user import redis_user_interface
from actinia_core.core.redis_api_log import redis_api_log_interface
from .config import global_config
from .process_queue import enqueue_job as enqueue_job_local

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

# Job handling
job_queues = []
redis_conn = None
num_queues = None


def create_job_queues(host, port, num_of_queues):
    """Create the job queues for asynchronous processing

    TODO: The redis queue approach does not work and is deactivated

    Note:
        Make sure that the global configuration was updated
        before calling this function.

    Args:
        host: The hostname of the redis server
        port: The port of the redis server
        num_of_queues: The number of queues that should be created

    """
    # Redis work queue and connection
    global job_queues, redis_conn, num_queues

    redis_conn = Redis(host=host, port=port)
    num_queues = num_of_queues

    for i in range(num_of_queues):
        name = "%s_%i" % (global_config.WORKER_QUEUE_NAME, i)

        string = "Create queue %s with server %s:%s" % (name, host, port)
        print(string)
        queue = rq.Queue(name, connection=redis_conn)
        job_queues.append(queue)


def enqueue_job(timeout, func, *args):
    """Execute the provided function in a subprocess

    Args:
        func: The function to call from the subprocess
        *args: The function arguments

    Returns:
        int:
        The current queue index

    """
    enqueue_job_local(timeout, func, *args)
    return

    # Just i case the current process queue does not work
    # Then use the most simple solution by just starting the process
    from multiprocessing import Process
    p = Process(target=func, args=args)
    p.start()

    return


def enqueue_job_old(timeout, func, *args):
    """Enqueue a job in the job queues

    TODO: The redis queue approach does not work and is deactivated

    The enqueue function uses a redis incr approach
    to chose for each job a different queue

    Note:
        The function create_job_queues() must be run
        before a job can be enqueued.

    Args:
        func: The function to call from the subprocess
        *args: The function arguments

    Returns:
        int:
        The current queue index

    """

    global job_queues, redis_conn, num_queues

    # Increase the counter
    num = redis_conn.incr("actinia_worker_count", 1)
    # Compute the current
    current_queue = num % num_queues
    print("###  Enqueue job in queue %i" % current_queue)
    ret = job_queues[current_queue].enqueue(
        func,
        *args,
        timeout=timeout,
        ttl=global_config.REDIS_QUEUE_JOB_TTL,
        result_ttl=global_config.REDIS_QUEUE_JOB_TTL)
    print(ret)

    return current_queue


def connect(host, port, pw=None):
    """Connect all required redis interfaces that should be used
       in the main server process.

       These interfaces are connected here for performance reasons.
       The redis job queue is initialized here as well.

    Args:
        host (str): The hostname of the redis server
        port (str): The port of the redis server
        pw (str): The password of the redis server

    """
    redis_user_interface.connect(host, port, pw)
    redis_api_log_interface.connect(host, port, pw)


def disconnect():
    """Disconnect all required redis interfaces
    """
    redis_user_interface.disconnect()
    redis_api_log_interface.disconnect()
