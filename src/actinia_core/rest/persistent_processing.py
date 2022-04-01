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
Asynchronous computation in specific temporary generated and then copied
or original mapsets
"""
import pickle
from copy import deepcopy
from flask import jsonify, make_response
from flask_restful_swagger_2 import swagger

from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.core.common.process_chain import ProcessChainModel
from actinia_core.models.response_models import ProcessingResponseModel
from actinia_core.processing.common.persistent_processing import start_job

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Guido Riembauer, Anika Weinmann"
__copyright__ = "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"

DESCR = """Execute a user defined process chain in an existing mapset
of the persistent user database or in a new mapset that will be
created by this request in the persistent user database.

The process chain is executed asynchronously. The provided status URL
in the response must be polled to gain information about the processing
progress and finishing status.

**Note**

    Space-time dataset processing can only be performed in a new mapset
    that is created by this resource call, since merging of temporal databases
    of different mapsets is not supported yet.

The mapset that is used for processing will be locked until the process
chain execution finished (successfully or not), even if the mapset is be
created by the request.
Other requests on the locked mapset will abort with a mapset lock error.

The persistent user database will not be modified if
the process chain does not run successfully. The processing is performed
in an ephemeral database and then merged or copied into the persistent user database.

**Note**

    Make sure that the process chain definition identifies all raster, vector or
    space time datasets correctly with name and mapset: name@mapset.

    All required mapsets will be identified by analysing the input parameter
    of all module descriptions in the provided process chain
    and mounted into the ephemeral database that is used for processing.

"""


SCHEMA_DOC = {
    'tags': ['Processing'],
    'description': DESCR,
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'location_name',
            'description': 'The location name',
            'required': True,
            'in': 'path',
            'type': 'string',
            'default': 'nc_spm_08'
        },
        {
            'name': 'mapset_name',
            'description': 'The name of an existing mapset or a new mapset that '
                           'should be created',
            'required': True,
            'in': 'path',
            'type': 'string'
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
                           'chain execution did not succeed',
            'schema': ProcessingResponseModel
        }
    }
}


class AsyncPersistentResource(ResourceBase):

    def __init__(self, resource_id=None, iteration=None, post_url=None):
        ResourceBase.__init__(self, resource_id, iteration, post_url)

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name, mapset_name):
        """Execute a user defined process chain that creates a new mapset or
        runs in an existing one.

        The process chain that describes the GRASS modules that should be
        executed must be provided as JSON payload of the POST request.

        Args:
            location_name (str): The name of the location
            mapset_name (str): The name of the mapset

        Returns:
            flask.Response:
            The HTTP status and a JSON document that includes the
            status URL of the task that must be polled for updates.

        Process chain input format:

            {                                           # A process chain is a
                                                          dict with entries for
                                                          each module that should
                                                          be run
               Id:{                                     # Id must be numerical
                                                          and indicates the process
                                                          order
                    "module": <module_name>,            # Name of the module to run
                    "stdin":  <Id::stdout | Id::stderr> # Use the output of a
                                                          specific module as
                                                          input for this module
                                                        # Id:stdout, Id:stderr
                                                          are available
                    "inputs ":{                         # Definition of all input
                                                          parameters as key:value
                                                          pairs
                              <parameter name>:<value>, # e.g.: value ==
                                                          "raster_name@mapset_name"
                                                          or "degree" or 0.0
                              <parameter name>:<value>  # e.g.: value ==
                                                          $file::slope_output_file
                                                          to specify an output file
                                                        # that name will be
                                                          automatically generated
                                                          by the API.
                    },
                    "outputs": {                         # Definition of all
                                                           outputs using key:value
                                                           pairs
                        <parameter name>: {
                            "name":<value>,              # Output name e.g.
                                                           "my_aspect_map" or a
                                                           temporary file id
                                                         # definition: $file::id
                                                           eg: $file::aspect_output_file
                                                         # This file can be used
                                                           in other module as input
                            "export": {                  # Export options, if present
                                                           this map will be exported
                                "format": <value>        # Set the export format
                                                           raster=GeoTiff (default),
                                                           vector = shape (default)
                                "type": <output type>,   # Output type e.g.: raster,
                                                           vector, file, stds
                            }
                        },
                        <parameter name>: {
                            "name": <value>,             # Output name e.g.
                                                           "my_slope_map"
                            "export": {                  # Export options, if
                                                           present this map will
                                                           be exported
                                "format": <value>        # Set the export format
                                                           raster=GeoTiff (default),
                                                           vector = shape (default)
                                "type": <output type>,   # Output type e.g.: raster,
                                                           vector, file, stds
                            }
                        }
                    },
                    "flags": <flags>,                    # All flags in a string
                                                           e.g.: "ge"
                    "overwrite": <True|False>,           # Set True to overwrite
                                                           existing data
                    "verbose": <True|False>              # Verbosity of the module
                },
               Id: {                                     # The id of an executable
                                                           command, that is not a
                                                           grass module
                    "executable": <path>,                # The name and path of
                                                           the executable e.g. /bin/cp
                    "stdin": <Id::stdout | Id::stderr>   # Use the output of a
                                                           specific module as
                                                           input for this module
                                                         # Id::stdout, Id::stderr
                                                           are available
                    "parameters": [<parameter>,]         # A list of strings that
                                                           represent the parameters
                                                           that may contain
                                                         # temporary file definitions:
                                                           $file::id  eg:
                                                           $file::aspect_output_file
               },
                ...
            }

        """
        # Preprocess the post call
        rdc = self.preprocess(
            has_json=True, location_name=location_name, mapset_name=mapset_name)

        if rdc:
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)
