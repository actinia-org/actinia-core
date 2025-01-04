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
Tests: process queue test queue
"""
import unittest
import time
import datetime
from copy import deepcopy
from actinia_core.core.common.process_queue import (
    create_process_queue,
    enqueue_job,
    stop_process_queue,
)
from actinia_core.core.resource_data_container import ResourceDataContainer
from actinia_core.core.common.app import flask_app

try:
    from .test_resource_base import global_config
except ModuleNotFoundError:
    from test_resource_base import global_config

global_config = global_config

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


def job_with_exception(rdc):
    print("job_with_exception", rdc.api_info, rdc.orig_time)
    # time.sleep(3)
    # raise Exception("job_with_exception")


def job_short_run(rdc):
    for i in range(3):
        print("job_short_run", rdc.api_info, rdc.orig_time)
        # time.sleep(1)


def job_long_run(rdc):
    for i in range(8):
        print("job_long_run", rdc.api_info, rdc.orig_time)
        time.sleep(3)


class ProcessQueueTestCase(unittest.TestCase):
    """
    This class tests the api logging interface
    """

    def setUp(self):
        # We need to set the application context
        self.app_context = flask_app.app_context()
        self.app_context.push()
        # The test user
        self.user_id = "soeren"

        global global_config
        global_config.NUMBER_OF_WORKERS = 1

        self.rdc = ResourceDataContainer(
            grass_data_base="grass_data_base",
            grass_user_data_base="grass_user_data_base",
            grass_base_dir="grass_base_dir",
            request_data={"request_data": None},
            user_id="user_id",
            user_group="user_group",
            user_credentials={"user_credentials": None},
            resource_id="resource_id",
            status_url="status_url",
            api_info="api_info",
            resource_url_base="resource_url_base",
            orig_time=time.time(),
            orig_datetime=datetime.datetime.now(),
            config=global_config,
            project_name="project_name",
            mapset_name="mapset_name",
            map_name="map_name",
        )

    def tearDown(self):
        self.app_context.pop()

    def otest_1(self):
        create_process_queue(config=global_config, use_logger=False)

        args = deepcopy(self.rdc)
        args.api_info = 0

        args = deepcopy(self.rdc)
        args.api_info = 1
        enqueue_job(15, job_with_exception, args)
        args = deepcopy(self.rdc)
        args.api_info = 2
        enqueue_job(15, job_with_exception, args)
        args = deepcopy(self.rdc)
        args.api_info = 3
        enqueue_job(1, job_with_exception, args)
        args = deepcopy(self.rdc)
        args.api_info = 4
        enqueue_job(1, job_with_exception, args)
        args = deepcopy(self.rdc)
        args.api_info = 5
        enqueue_job(1, job_with_exception, args)
        args = deepcopy(self.rdc)
        args.api_info = 6
        enqueue_job(15, job_with_exception, args)
        args = deepcopy(self.rdc)
        args.api_info = 7
        enqueue_job(15, job_with_exception, args)
        args = deepcopy(self.rdc)
        args.api_info = 8
        enqueue_job(15, job_with_exception, args)

        time.sleep(10)
        stop_process_queue()

        return

    def otest_2(self):
        create_process_queue(config=global_config, use_logger=False)

        args = deepcopy(self.rdc)
        args.api_info = 0

        enqueue_job(30, job_with_exception, args)

        args = deepcopy(self.rdc)
        args.api_info = 1

        enqueue_job(30, job_short_run, args)

        args = deepcopy(self.rdc)
        args.api_info = 2

        enqueue_job(30, job_short_run, args)

        args = deepcopy(self.rdc)
        args.api_info = 3

        enqueue_job(30, job_short_run, args)

        args = deepcopy(self.rdc)
        args.api_info = 4

        enqueue_job(1, job_short_run, args)

        args = deepcopy(self.rdc)
        args.api_info = 5

        enqueue_job(30, job_long_run, args)

        args = deepcopy(self.rdc)
        args.api_info = 6

        enqueue_job(30, job_long_run, args)

        time.sleep(20)
        stop_process_queue()
        # return


if __name__ == "__main__":
    unittest.main()
