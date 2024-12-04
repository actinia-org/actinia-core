# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2022 Sören Gebbert and mundialis GmbH & Co. KG
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
from actinia_core.core.logging_interface import log
from .config import global_config
from .process_queue import enqueue_job as enqueue_job_local

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

job_queues = []
redis_conn = None


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
    """Disconnect all required redis interfaces"""
    redis_user_interface.disconnect()
    redis_api_log_interface.disconnect()


def __create_job_queue(queue_name):
    """Create a single job queue for asynchronous processing

    Args:
        queue_name: The name of the queue

    """
    # Redis work queue and connection
    global job_queues, redis_conn

    if not any(q.name == queue_name for q in job_queues):
        host = global_config.REDIS_QUEUE_SERVER_URL
        port = global_config.REDIS_QUEUE_SERVER_PORT
        password = global_config.REDIS_QUEUE_SERVER_PASSWORD

        kwargs = dict()
        kwargs["host"] = host
        kwargs["port"] = port
        if password and password is not None:
            kwargs["password"] = password
        redis_conn = Redis(**kwargs)

        string = "Create queue %s with server %s:%s" % (queue_name, host, port)
        log.info(string)
        queue = rq.Queue(queue_name, connection=redis_conn)
        job_queues.append(queue)


def __enqueue_job_redis(queue, timeout, func, *args):
    """Enqueue a job in the job queues

    Args:
        func: The function to call from the subprocess
        *args: The function arguments
    """

    log.info("Enqueue job in queue %s" % queue.name)
    # Below timeout is defined in resource_base.pyL295.
    # If it is higher than 2147483647, it will be set to never expire.
    # Else it would raise an error:
    # int(process_time_limit * process_num_limit * 20)
    # which is 630720000000 and raises in worker:
    # OverflowError: Python int too large to convert to C int
    if timeout > 2147483647:
        timeout = -1  # never exprire
    ret = queue.enqueue(
        func,
        *args,
        job_timeout=timeout,
        ttl=global_config.REDIS_QUEUE_JOB_TTL,
        result_ttl=global_config.REDIS_QUEUE_JOB_TTL,
    )
    log.info(ret)


def enqueue_job(timeout, func, *args, queue_type_overwrite=None):
    """Write the provided function in a queue

    Args:
        timeout: The timeout of the process
        func: The function to call from the subprocess/worker
        *args: The function arguments
    """
    global job_queues, redis_conn
    num_queues = global_config.NUMBER_OF_WORKERS
    queue_type = global_config.QUEUE_TYPE
    queue_name = "local"
    if queue_type_overwrite:
        queue_type = global_config.QUEUE_TYPE_OVERWRITE

    if queue_type == "per_job":
        resource_id = args[0].resource_id
        queue_name = "%s_%s" % (global_config.WORKER_QUEUE_PREFIX, resource_id)
        __create_job_queue(queue_name)
        for i in job_queues:
            if i.name == queue_name:
                args[0].set_queue_name(queue_name)
                __enqueue_job_redis(i, timeout, func, *args)

    elif queue_type == "per_user":
        user_id = args[0].user_id
        queue_name = "%s_%s" % (global_config.WORKER_QUEUE_PREFIX, user_id)
        # Run __create_job_queue everytime.
        # If queue already exists, it does nothing.
        __create_job_queue(queue_name)
        for i in job_queues:
            if i.name == queue_name:
                args[0].set_queue_name(queue_name)
                __enqueue_job_redis(i, timeout, func, *args)

    elif queue_type == "redis":
        if job_queues == []:
            for i in range(num_queues):
                queue_name = "%s_%s" % (global_config.WORKER_QUEUE_PREFIX, i)
                __create_job_queue(queue_name)
        # The redis incr approach is used here
        # to chose for each job a different queue
        num = redis_conn.incr("actinia_worker_count", 1)
        current_queue = num % num_queues
        args[0].set_queue_name(job_queues[current_queue].name)
        __enqueue_job_redis(job_queues[current_queue], timeout, func, *args)

    elif queue_type == "local":
        # __enqueue_job_local(timeout, func, *args)
        args[0].set_queue_name(queue_name)
        enqueue_job_local(timeout, func, *args)
        return
        # Just in case the current process queue does not work
        # Then use the most simple solution by just starting the process
        from multiprocessing import Process

        p = Process(target=func, args=args)
        p.start()
