# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2024 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Asynchronous merging of several mapsets into a single one
"""
import pickle
from flask import jsonify, make_response

from actinia_rest_lib.resource_base import ResourceBase
from actinia_core.core.common.kvdb_interface import enqueue_job
from actinia_core.processing.common.persistent_mapset_merger import start_job

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = "Copyright 2016-2024, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class AsyncPersistentMapsetMergerResource(ResourceBase):
    def __init__(self):
        ResourceBase.__init__(self)

    def post(self, project_name, mapset_name):
        """Merge several existing mapsets into a single one.
        All mapsets that should be merged and the target mapset will be locked
        for the processing.

        Args:
            project_name (str): The name of the project
            target_mapset_name (str): The name of the target mapset, into other
                                      mapsets should be merged

        Process arguments must be provided as JSON document in the POST
        request:
            ["mapset_A", "mapset_B", "mapset_C", "mapset_D", ...]

        Returns:
            flask.Response:
            The HTTP status and a JSON document that includes the
            status URL of the task that must be polled for updates.

        Example::

            {
              "HTTP code": 200,
              "Messages": "Resource accepted",
              "Resource id": "resource_id-985164c9-1db9-49cf-"
              "b2c4-3e8e48500e31",
              "Status": "accepted",
              "URLs": {
                "Resources": [],
                "Status": "http://104.155.60.87/resources/soeren/"
                          "resource_id-985164c9-1db9-49cf-b2c4-3e8e48500e31"
              },
              "User id": "soeren"
            }


        """
        # Preprocess the post call
        rdc = self.preprocess(
            has_json=True, project_name=project_name, mapset_name=mapset_name
        )

        if rdc:
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)
