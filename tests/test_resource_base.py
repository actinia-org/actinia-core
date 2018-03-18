# -*- coding: utf-8 -*-
import atexit
import os
import signal
import time
from actinia_core.testsuite import ActiniaTestCaseBase
from actinia_core.resources.common.config import global_config

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"

redis_pid = None
server_test = False
custom_graas_cfg = False

# If this environmental variable is set, then a real http request will be send
# instead of using the flask test_client.
if "GRAAS_SERVER_TEST" in os.environ:
    server_test = bool(os.environ["GRAAS_SERVER_TEST"])
# Set this variable to use a graas config file in a docker container
if "GRAAS_CUSTOM_TEST_CFG" in os.environ:
    custom_graas_cfg = str(os.environ["GRAAS_CUSTOM_TEST_CFG"])


def setup_environment():
    global redis_pid
    # Set the port to the test redis server
    global_config.REDIS_SERVER_SERVER = "localhost"
    global_config.REDIS_SERVER_PORT = 7000

    # home = os.getenv("HOME")

    # GRASS

    # Setup the test environment
    global_config.GRASS_GIS_BASE="/usr/local/grass-7.5.svn"
    global_config.GRASS_GIS_START_SCRIPT="/usr/local/bin/grass75"
    # global_config.GRASS_DATABASE= "/usr/local/grass_test_db"
    # global_config.GRASS_DATABASE = "%s/graas/grass_test_db" % home
    global_config.GRASS_TMP_DATABASE = "/tmp"

    if server_test is False and custom_graas_cfg is False:
        # Start the redis server for user and logging management
        redis_pid = os.spawnl(os.P_NOWAIT, "/usr/bin/redis-server",
                              "common/redis.conf",
                              "--port %i" % global_config.REDIS_SERVER_PORT)
        time.sleep(1)

    if server_test is False and custom_graas_cfg is not False:
        global_config.read(custom_graas_cfg)


def stop_redis():
    if server_test is False:
        global redis_pid
        # Kill th redis server
        if redis_pid is not None:
            os.kill(redis_pid, signal.SIGTERM)

# Register the redis stop function
atexit.register(stop_redis)
# Setup the environment
setup_environment()


class ActiniaResourceTestCaseBase(ActiniaTestCaseBase):
    pass
