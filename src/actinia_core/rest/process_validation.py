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
Compute areal categorical statistics on a raster map layer based on an input polygon.
"""

import pickle
from copy import deepcopy
from flask_restful_swagger_2 import swagger
from flask import jsonify, make_response
from actinia_core.rest.ephemeral_processing import EphemeralProcessing
from actinia_core.rest.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.models.response_models import \
    ProcessingResponseModel, ProcessingErrorResponseModel
from actinia_core.core.common.app import auth
from actinia_core.core.common.api_logger import log_api_call
from actinia_core.core.common.process_chain import ProcessChainModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


DESCR = """Validate a process chain, check the provided sources (links)
and the mapsets. The list of processes that were checked by Actinia are returned in the
JSON response.
"""


SCHEMA_DOC = {
    'tags': ['Processing'],
    'description': DESCR,
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'location_name',
            'description': 'The location name that contains the data that '
                           'should be used in the process chain',
            'required': True,
            'in': 'path',
            'type': 'string',
            'default': 'nc_spm_08'
        },
        {
            'name': 'process_chain',
            'description': 'The process chain that should be validated',
            'required': True,
            'in': 'body',
            'schema': ProcessChainModel
        }
    ],
    'responses': {
        '200': {
            'description': 'The result of the process chain validation. '
                           'A list of processes that will be executed by '
                           'Actinia Core',
            'schema': ProcessingResponseModel
        },
        '400': {
            'description': 'The error message and a detailed log why process '
                           'chain validation did not succeeded',
            'schema': ProcessingErrorResponseModel
        }
    }
}


class AsyncProcessValidationResource(ResourceBase):

    decorators = [log_api_call, auth.login_required]

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name):
        """Validate a process chain asynchronously, check the provided sources
        and the mapsets."""

        rdc = self.preprocess(has_json=True, has_xml=True,
                              location_name=location_name)

        if rdc:
            rdc.set_storage_model_to_file()
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


class SyncProcessValidationResource(ResourceBase):

    decorators = [log_api_call, auth.login_required]

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name):
        """Validate a process chain synchronously, check the provided sources
        and the mapsets."""

        rdc = self.preprocess(has_json=True, has_xml=True,
                              location_name=location_name)

        if rdc:
            rdc.set_storage_model_to_file()
            enqueue_job(self.job_timeout, start_job, rdc)
            http_code, response_model = self.wait_until_finish()
        else:
            http_code, response_model = pickle.loads(self.response_data)

        return make_response(jsonify(response_model), http_code)


def start_job(*args):
    processing = ProcessValidation(*args)
    processing.run()


class ProcessValidation(EphemeralProcessing):

    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()

        process_chain = self._create_temporary_grass_environment_and_process_list()

        result = []
        for process in process_chain:
            result.append(str(process))

        self.finish_message = "Validation successful"

        self.module_results = result
