# -*- coding: utf-8 -*-
"""
Compute areal categorical statistics on a raster map layer based on an input polygon.
"""

import pickle
from copy import deepcopy
from flask_restful_swagger_2 import swagger
from flask import jsonify, make_response
from actinia_core.resources.async_ephemeral_processing import AsyncEphemeralProcessing
from actinia_core.resources.async_resource_base import AsyncEphemeralResourceBase
from actinia_core.resources.common.redis_interface import enqueue_job
from actinia_core.resources.common.response_models import ProcessingResponseModel
from actinia_core.resources.common.app import auth
from actinia_core.resources.common.logging_interface import log_api_call
from actinia_core.resources.common.process_chain import ProcessChainModel


__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


DESCR="""Validate a process chain, check the provided sources (links)
and the mapsets. The list of processes that are executed by Actinia Core are returned in the
JSON response.
"""


SCHEMA_DOC={
    'tags': ['ephemeral processing'],
    'description': DESCR,
    'consumes':['application/json'],
    'parameters': [
        {
            'name': 'location_name',
            'description': 'The location name that contains the data that should be used in the process chain',
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
                           'A list of processes that will be executed by Actinia Core',
            'schema':ProcessingResponseModel
        },
        '400': {
            'description':'The error message and a detailed log why process chain validation '
                          'did not succeeded',
            'schema':ProcessingResponseModel
        }
    }
 }


class AsyncProcessValidationResource(AsyncEphemeralResourceBase):

    decorators = [log_api_call, auth.login_required]

    def _execute(self, location_name):

        rdc = self.preprocess(has_json=True, has_xml=True,
                              location_name=location_name)

        enqueue_job(self.job_timeout, start_job, rdc)

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name):

        self._execute(location_name)
        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


class SyncProcessValidationResource(AsyncProcessValidationResource):

    decorators = [log_api_call, auth.login_required]

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name):

        self._execute(location_name)
        http_code, response_model = self.wait_until_finish()
        return make_response(jsonify(response_model), http_code)


def start_job(*args):
    processing = AsyncProcessValidation(*args)
    processing.run()


class AsyncProcessValidation(AsyncEphemeralProcessing):

    def __init__(self, *args):
        AsyncEphemeralProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()

        process_chain = self._create_temporary_grass_environment_and_process_chain()

        result = []
        for process in process_chain:
            result.append(str(process))

        self.finish_message = "Validation successful"

        self.module_results = result
