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
Asynchronous computation in specific temporary generated mapsets
with export of required map layers.
"""
import pickle
from flask import jsonify, make_response

from copy import deepcopy
from flask_restful_swagger_2 import swagger
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.common.process_chain import ProcessChainModel
from actinia_core.models.response_models import \
    ProcessingResponseModel, ProcessingErrorResponseModel
from actinia_core.processing.common.ephemeral_processing_with_export \
     import start_job

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"
__email__ = "info@mundialis.de"


DESCR = """Execute a user defined process chain in an ephemeral database
and provide the generated resources as downloadable files via URL's.
Minimum required user role: user.

The process chain is executed asynchronously. The provided status URL
in the response must be polled to gain information about the processing
progress and finishing status.

**Note**

    Make sure that the process chain definition identifies all raster, vector or
    space-time datasets correctly with name and mapset: name@mapset if you use
    data from other mapsets in the specified location.

    All required mapsets will be identified by analysing the input parameter
    of all module descriptions in the provided process chain
    and mounted read-only into the ephemeral database that is used for processing.

The persistent database will not be modified. The ephemeral database will be
removed after processing.
Use the URL's provided in the finished response to download the resource that
were specified in the process chain for export.

**Note**

    The endpoint allows the creation of STAC ITEMS through the
    ACTINIA STAC PLUGIN the STAC item is stored in a dedicated
    CATALOG following the standard from STAC specification (https://stacspec.org/)
"""


SCHEMA_DOC = {
    'tags': ['Processing'],
    'description': DESCR,
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'location_name',
            'description': 'The location name that contains the data that should '
                           'be processed',
            'required': True,
            'in': 'path',
            'type': 'string',
            'default': 'nc_spm_08'
        },
        {
            'name': 'process_chain',
            'description': 'The process chain that should be executed',
            'required': True,
            'in': 'body',
            'schema': ProcessChainModel
        }
    ],
    'responses': {
        '200': {
            'description': 'The result of the process chain execution',
            'schema': ProcessingResponseModel
        },
        '400': {
            'description': 'The error message and a detailed log why process '
                           'chain execution did not succeeded',
            'schema': ProcessingErrorResponseModel
        }
    }
}


class AsyncEphemeralExportResource(ResourceBase):
    """
    This class represents a resource that runs asynchronous processing tasks in
    a temporary mapset and exports the computed results as geotiff files.
    """
    def __init__(self, resource_id=None, iteration=None, post_url=None):
        ResourceBase.__init__(self, resource_id, iteration, post_url)

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name):
        """Execute a user defined process chain in an ephemeral location/mapset
        and store the processing results for download.
        """
        rdc = self.preprocess(has_json=True, location_name=location_name)

        if rdc:
            rdc.set_storage_model_to_file()
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


class AsyncEphemeralExportS3Resource(ResourceBase):
    """
    This class represents a resource that runs asynchronous processing tasks in
    a temporary mapset and exports the computed results as geotiff files to the
    Amazon S3 storage.
    """
    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name):
        """Execute a user defined process chain in an ephemeral location/mapset and
        store the processing result in an Amazon S3 bucket
        """
        rdc = self.preprocess(has_json=True, location_name=location_name)
        rdc.set_storage_model_to_s3()

        enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


class AsyncEphemeralExportGCSResource(ResourceBase):
    """
    This class represents a resource that runs asynchronous processing tasks in
    a temporary mapset and exports the computed results as geotiff files to the
    Google Cloud Storage.
    """
    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name):
        """Execute a user defined process chain in an ephemeral location/mapset
        and store the processing result in an Google cloud storage bucket
        """
        rdc = self.preprocess(has_json=True, location_name=location_name)
        rdc.set_storage_model_to_gcs()

        enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)
