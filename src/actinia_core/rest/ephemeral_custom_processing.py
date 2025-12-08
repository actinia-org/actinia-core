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
Running a custom UNIX process outside the GRASS GIS environment
"""
import pickle
from flask import jsonify, make_response

from actinia_rest_lib.resource_base import ResourceBase
from actinia_core.core.common.kvdb_interface import enqueue_job
from actinia_core.processing.common.ephemeral_custom_processing import (
    start_job,
)

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2022, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class AsyncEphemeralCustomResource(ResourceBase):
    """This class represents a custom process resource
    that will be asynchronously executed without the initialization
    of the GRASS environment.
    """

    def __init__(self):
        ResourceBase.__init__(self)

    def post(self, executable):
        """Run a custom process

        The process is identified by executable

        Args:
            executable (str): Name of the executable

        Process arguments must be provided as JSON document in the POST
        request:
            ["arg_1", "arg_2", "arg_3", "arg_4", ...]

        Returns:
            flask.Response:
            The HTTP status and a JSON document that includes the
            status URL of the export task that must be polled for updates.

        """
        # Preprocess the post call
        rdc = self.preprocess(has_json=True)

        if rdc:
            rdc.set_user_data(executable)
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)
