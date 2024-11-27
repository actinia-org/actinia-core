# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2019 Sören Gebbert and mundialis GmbH & Co. KG
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
Tests: Actinia resource test case base
"""
import atexit
import os
import signal
import time
from actinia_core.testsuite import ActiniaTestCaseBase, URL_PREFIX
from actinia_core.core.common.config import global_config
from actinia_core.endpoints import create_endpoints

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"

# Create endpoints
create_endpoints()

redis_pid = None
server_test = False

# If this environmental variable is set, then a real http request will be send
# instead of using the flask test_client.
if "ACTINIA_SERVER_TEST" in os.environ:
    server_test = bool(os.environ["ACTINIA_SERVER_TEST"])

base_url_data = "https://apps.mundialis.de/actinia_test_datasets"
additional_external_data = {
    "rio_json": f"{base_url_data}/rio.json",
    "brazil_json": f"{base_url_data}/brazil_polygon.json",
    "elev_ned_30m_tif": f"{base_url_data}/elev_ned_30m.tif",
    "elev_ned_30m_epsg4326_tif": f"{base_url_data}/elev_ned_30m_epsg4326.tif",
    "elev_ned_30m_nope_tif": f"{base_url_data}/elev_ned_30m_nope.tif",
    "polygon_gml": f"{base_url_data}/polygon.gml",
    "census_wake2000_gml": f"{base_url_data}/census_wake2000.gml",
    "census_wake2000_zip": f"{base_url_data}/census_wake2000.zip",
    "geology_30m_tif": f"{base_url_data}/geology_30m.tif",
    "geology_30m_zip": f"{base_url_data}/geology_30m.zip",
    "pointInBonn": f"{base_url_data}/pointInBonn.geojson",
    "elevation": f"{base_url_data}/elevation.tif",
}


def setup_environment():
    global redis_pid

    # GRASS GIS
    # Setup the test environment
    global_config.GRASS_GIS_BASE = "/usr/local/grass/"
    global_config.GRASS_GIS_START_SCRIPT = "/usr/local/bin/grass"
    # global_config.GRASS_DATABASE= "/usr/local/grass_test_db"
    # global_config.GRASS_DATABASE = "%s/actinia/grass_test_db" % home
    global_config.GRASS_TMP_DATABASE = "/tmp"
    # TODO: never secretly overwrite config parameters
    custom_actinia_cfg = True
    if server_test is False and custom_actinia_cfg is False:
        # Start the redis server for user and logging management
        redis_pid = os.spawnl(
            os.P_NOWAIT,
            "/usr/bin/redis-server",
            "common/redis.conf",
            "--port %i" % global_config.REDIS_SERVER_PORT,
        )
        time.sleep(1)


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

URL_PREFIX = URL_PREFIX


class ActiniaResourceTestCaseBase(ActiniaTestCaseBase):
    pass
