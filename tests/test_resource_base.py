# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2022 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
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

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = "Copyright 2016-2022, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"

# Create endpoints
create_endpoints()

kvdb_pid = None
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
    global kvdb_pid

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
        # Start the kvdb server for user and logging management
        kvdb_pid = os.spawnl(
            os.P_NOWAIT,
            "/usr/bin/valkey-server",
            "common/valkey.conf",
            "--port %i" % global_config.KVDB_SERVER_PORT,
        )
        time.sleep(1)


def stop_kvdb():
    if server_test is False:
        global kvdb_pid
        # Kill th kvdb server
        if kvdb_pid is not None:
            os.kill(kvdb_pid, signal.SIGTERM)


# Register the kvdb stop function
atexit.register(stop_kvdb)
# Setup the environment
setup_environment()

URL_PREFIX = URL_PREFIX


class ActiniaResourceTestCaseBase(ActiniaTestCaseBase):
    pass
