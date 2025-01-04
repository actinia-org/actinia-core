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
Process queue implementation using multiprocessing, Queue() and Thread.

The process queue is responsible to run all requests in actinia that
require to execute GRASS GIS processes or UNIX processes to create a response.

The process queue supports logging of the stderr output of the executed
processes into a rotating logfile and fluent server.
"""

import pickle
import time
from datetime import datetime
import queue as standard_queue
from multiprocessing import Process, Queue
from threading import Thread, Lock
import atexit
from actinia_core.core.resources_logger import ResourceLogger
from actinia_core.core.logging_interface import log


has_fluent = False

try:
    from fluent import handler

    if handler:
        has_fluent = True
except Exception:
    print("Fluent is not available")
    has_fluent = False


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-present, Sören Gebbert and mundialis GmbH & Co. KG"
)

process_queue = Queue()
process_queue_manager = None


def create_process_queue(config, use_logger=True):
    """Create the process queue that will start all processes in a separate
    process. It uses a multiprocessing.Queue() to receive Processes
    (function and arguments)

    The process queue can only be started once

    Args:
        config: The global configuration
        use_logger: Use the rotating file logger and fluent for stderr logging
                    of the processes
    """
    global process_queue_manager

    if process_queue_manager is None:
        p = Process(
            target=start_process_queue_manager,
            args=(config, process_queue, use_logger),
        )
        p.start()
        process_queue_manager = p


def enqueue_job(timeout, func, *args):
    """Put the provided function and arguments in the process queue

    Args:
        timeout: The timeout of the process, if the timeout is exceeded by the
                 process it will be killed
        func: The function to call from the subprocess
        *args: The function arguments, the first argument must be the
               RessourceDataContainer
    """
    process_queue.put((func, timeout, args))

    # # for debugging in ephemeral_processing.py (see also grass_init.py)
    # # only uncomment ONE of the following endpoints:

    # # for '/projects/<string:project_name>/processing_async'
    # from ...rest.ephemeral_processing import \
    #     AsyncEphemeralResource
    # from ...processing.common.ephemeral_processing import start_job
    # from ...processing.actinia_processing.ephemeral_processing \
    #      import EphemeralProcessing
    # processing = EphemeralProcessing(*args)
    # processing.run()

    # # for '/projects/<string:project_name>/processing_async_export'
    # from ...processing.actinia_processing.ephemeral.\
    #     ephemeral_processing_with_export import EphemeralProcessingWithExport
    # processing = EphemeralProcessingWithExport(*args)
    # processing.run()

    # # for /projects/{project_name}/mapsets/{mapset_name}/processing_async
    # from ...processing.actinia_processing.ephemeral.persistent_processing \
    #     import PersistentProcessing
    # processing = PersistentProcessing(*args)
    # processing.run()


def stop_process_queue():
    """Destroy the process queue and terminate all running and enqueued jobs"""
    global process_queue_manager
    # Send stop to the queue
    process_queue.put("STOP")
    # Wait for all joining processes
    if process_queue_manager:
        # print("Waited for process_queue_manager")
        process_queue_manager.join(3)
        # print("Terminate process_queue_manager")
        process_queue_manager.terminate()
    process_queue_manager = None


# Register the stop_process_queue in the exit handler
atexit.register(stop_process_queue)


class EnqueuedProcess(object):
    """The class that takes care of the handling of a single process. It
    provides support for timeout check, exit status check and resource
    termination commits.
    It implements methods to start and gently terminate processes, so that the
    resource database will be updated with the current state.

    - timeout check -- Check if a waiting process exceedes its timeout for
                       waiting to be run and terminate it.
                       A resource update will be send to the resource database.
    - exits status check -- Check if the exit status of the process was 0, if
                            not check if the resource database acknowledged
                            this with a termination or error message, if not
                            send a resource update
    - termination commits - Terminate the process and send an update to the
                            resource database about the termination
    """

    def __init__(self, func, timeout, resource_logger, args):
        self.process = Process(target=func, args=args)
        self.timeout = timeout
        self.config = args[0].config
        self.resource_id = args[0].resource_id
        self.iteration = args[0].iteration
        self.user_id = args[0].user_id
        self.api_info = args[0].api_info
        self.resource_logger = resource_logger
        self.init_time = time.time()

        self.started = False

    def __del__(self):
        pass
        # print("Process deleted", self.resource_id)

    def start(self):
        """Start the process

        :return:
        """
        # print("Start job: ", self.api_info)
        self.started = True
        self.process.start()

    def terminate(self, status, message):
        """Terminate the process

        Send a termination response to the resource database.

        Args:
            status: The status why termination was requested
            message: The message why the process was terminated by the server
                     (timeout, server shutdown, ...)
        """
        # print("Terminate process with message: ", message)

        if self.process.is_alive():
            self.process.terminate()

        self._send_resource_update(status=status, message=message)

    def is_alive(self):
        return self.process.is_alive()

    def exitcode(self):
        return self.process.exitcode

    def check_timeout(self):
        """
        Check if the process waited longer for running then the timeout that
        was set

        Terminate the process if the timeout limit was exceeded.

        Returns:
             False if within timeout, True if the process terminated itself
        """
        # print("Check timeout for process: ", self.api_info)
        if self.started is False:
            current_time = time.time()
            diff = current_time - self.init_time
            if self.timeout < diff:
                self.terminate(
                    status="timeout",
                    message="Processes exceeded timeout (%i) in "
                    "waiting queue and was terminated." % self.timeout,
                )
                return True

        return False

    def check_exit(self):
        """Check the exitcode, if a non-zero exit code was received then
        send an update to the resource logger that something strange happened.
        Send only if the status of the resource is not "error", "terminated"
        or "timeout".

        """
        if self.process.exitcode is not None and self.process.exitcode != 0:
            # Check if the process noticed the error already
            response_data = self.resource_logger.get(
                self.user_id, self.resource_id, self.iteration
            )

            if response_data is not None:
                _, response_model = pickle.loads(response_data)
                if (
                    response_model["status"] != "error"
                    and response_model["status"] != "terminated"
                    and response_model["status"] != "timeout"
                ):
                    message = (
                        "The process unexpectedly terminated with exit code %i"
                        % self.process.exitcode
                    )
                    self._send_resource_update(
                        status="error",
                        message=message,
                        response_data=response_data,
                    )

    def _send_resource_update(self, status, message, response_data=None):
        """
        Send a response to the resource logger about the current resource state

        Args:
            status: The status that should be set (terminated)
            message: The message
        """
        # print("Send resource update status: ", status, " message: ", message)
        # Get the latest response and use it as template for the resource
        # update
        if response_data is None:
            response_data = self.resource_logger.get(
                self.user_id, self.resource_id, self.iteration
            )

        # Send the termination response
        if response_data is not None:
            http_code, response_model = pickle.loads(response_data)
            # print("Resource", http_code, response_model)
            response_model["status"] = status
            response_model["message"] = (
                "The process was terminated by the server: %s" % message
            )
            orig_time = response_model["accept_timestamp"]
            response_model["timestamp"] = time.time()
            response_model["datetime"] = str(datetime.now())
            response_model["time_delta"] = (
                response_model["timestamp"] - orig_time
            )

            document = pickle.dumps([http_code, response_model])

            self.resource_logger.commit(
                user_id=self.user_id,
                resource_id=self.resource_id,
                iteration=self.iteration,
                document=document,
                expiration=self.config.REDIS_RESOURCE_EXPIRE_TIME,
            )


def queue_watcher(queue, data_set, lock):
    """This function runs in a separate thread to check the queue

    Args:
        queue: The queue to check
        data_set: The set to add the received data
        lock: The lock to be used for locking the set access
    """

    while True:
        try:
            # print("Check for new data in queue")
            data = queue.get(block=True)
            lock.acquire_lock()
            data_set.add(data)
            # print("Add data to set", len(data_set))
            lock.release_lock()
        except standard_queue.Empty:
            pass


def start_process_queue_manager(config, queue, use_logger):
    """
    The process queue manager that runs the infinite loop for worker creation

    - This function creates the stderr logger if requested
    - It listen to a queue in an infinite loop:
        - The queue is watched in a separate thread so that no data get lost
        - Check if new processes are in the data set() that is filled by the
          queue watcher
        - Check the timeout of waiting processes
        - Enqueue and start new processes
        - Remove finished processes or processes that exceeded their waiting
          timeout
        - Stop the queue and exit all running processes if the "STOP" isgnal
          was send via Queue()

    Args:
        config: The global config
        queue: The multiprocessing.Queue() object that should be listened to
        use_logger: Create logifle and fluent logger to log the stderr of the
                    processes
    """
    global finished_procs

    data_set = set()
    lock = Lock()
    # Start the thread that permanently listens to the queue
    queue_thread = Thread(target=queue_watcher, args=(queue, data_set, lock))
    queue_thread.start()

    running_procs = set()
    waiting_processes = set()

    fluent_sender = None
    # Fluentd hack to work in a multiprocessing environment
    try:
        from fluent import sender

        fluent_sender = sender.FluentSender(
            "actinia_process_logger",
            host=config.LOG_FLUENT_HOST,
            port=config.LOG_FLUENT_PORT,
        )
    except Exception:
        pass
    # We need the resource logger to send updates to the resource database
    kwargs = dict()
    kwargs["host"] = config.REDIS_SERVER_URL
    kwargs["port"] = config.REDIS_SERVER_PORT
    if config.REDIS_SERVER_PW and config.REDIS_SERVER_PW is not None:
        kwargs["password"] = config.REDIS_SERVER_PW
    # Seems to log only on rare occasions: when a job waits too long in the
    # queue and terminates itself.
    resource_logger = ResourceLogger(**kwargs, fluent_sender=fluent_sender)
    del kwargs

    count = 0
    try:
        while True:
            # Get the process data from the set that is filled in the queue
            # thread
            data = None
            lock.acquire_lock()
            if len(data_set) > 0:
                # print("Jobs from queue: ", len(data_set))
                data = data_set.pop()
            lock.release_lock()

            if data is not None:
                # Stop all (running and waiting) processes if the STOP command
                # was detected and leave the loop
                if "STOP" in data:
                    for enqproc in running_procs:
                        enqproc.terminate(
                            status="error",
                            message="Running process was terminated by server "
                            "shutdown.",
                        )
                    for enqproc in waiting_processes:
                        enqproc.terminate(
                            status="error",
                            message="Waiting process was terminated by server "
                            "shutdown.",
                        )
                    del queue_thread
                    queue.close()
                    # print("Exit loop")
                    exit(0)
                # Enqueue a new process
                elif len(data) == 3:
                    func, timeout, args = data
                    log.info("Enqueue process: %s", args[0].api_info)
                    enqproc = EnqueuedProcess(
                        func=func,
                        timeout=timeout,
                        resource_logger=resource_logger,
                        args=args,
                    )
                    waiting_processes.add(enqproc)

            if len(running_procs) < config.NUMBER_OF_WORKERS:
                if len(waiting_processes) > 0:
                    enqproc = waiting_processes.pop()
                    running_procs.add(enqproc)
                    log.info("Run process: %s", enqproc.api_info)
                    enqproc.start()

            # Purge processes that are finished or exceeded their timeout each
            # 40th loop
            if count % 10 == 0:
                count = 0
                procs_to_remove = []
                # purge processes that has been finished
                for enqproc in running_procs:
                    if enqproc.started is True and enqproc.is_alive() is False:
                        # Check if the process finished with an error and send
                        # a resource update if required
                        enqproc.check_exit()
                        procs_to_remove.append(enqproc)
                for enqproc in procs_to_remove:
                    running_procs.remove(enqproc)

                procs_to_remove = []
                # purge processes that have exceeded their timeout for waiting
                for enqproc in waiting_processes:
                    check = enqproc.check_timeout()
                    if check is True:
                        procs_to_remove.append(enqproc)
                for enqproc in procs_to_remove:
                    waiting_processes.remove(enqproc)

            time.sleep(0.05)
            count += 1
    except Exception:
        raise
    finally:
        queue.close()
