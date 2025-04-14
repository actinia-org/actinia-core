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
Base class for asynchronous processing
"""

import pickle
from flask import jsonify, make_response
from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.processing.common.ephemeral_processing import start_job

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class AsyncEphemeralResource(ResourceBase):
    """This class represents a processing resource that works on a temporary
    mapset.
    """

    def __init__(self, resource_id=None, iteration=None, post_url=None):
        ResourceBase.__init__(self, resource_id, iteration, post_url)

    def post(self, project_name):
        """Start an async GRASS processing task, that is completely temporary.
        The generated mapset is only created temporally, all created resources
        will be deleted after the processing finished.

        None:
            This resource should not be used in production, only for benchmarks
            and tests!

        Args:
            project_name (str): The name of the project

        Returns:
            flask.Response:
            The HTTP status and a JSON document that includes the
            status URL of the task that must be polled for updates.

        Process chain input format::

            {                                           # A process chain is a
                                                          dict with entries for
                                                          each module that
                                                          should be run
               Id:{                                     # Id must be numerical
                                                          and indicates the
                                                          process order
                    "module":<module_name>,             # Name of the module to
                                                          run
                    "stdin":<Id::stdout | Id::stderr>   # Use the output of a
                                                          specific module as
                                                          input for this module
                                                        # Id:stdout, Id:stderr
                                                          are available
                    "inputs":{                          # Definition of all
                                                          input parameters as
                                                          key:value pairs
                             <parameter name>:<value>,  # e.g.: value == "raste
                                                          r_name@mapset_name"
                                                          or "degree" or 0.0
                             <parameter name>:<value>   # e.g.: value == $file
                                                          ::slope_output_file
                                                          to specify an output
                                                          file
                                                        # that name will be
                                                          automatically
                                                          generated by the API.
                    },
                    "outputs":{                         # Definition of all
                                                          outputs using
                                                          key:value pairs
                        <parameter name>:{
                            "name":<value>,             # Output name e.g.
                                                          "my_aspect_map" or a
                                                          temporary file id
                                                        # definition: $file::id
                                                          eg: $file::aspect_
                                                          output_file
                                                        # This file can be used
                                                          in other module as
                                                          input
                            "export":{                  # Export options, if
                                                          present this map will
                                                          be exported
                                "format":<value>        # Set the export format
                                                          raster=GeoTiff
                                                          (default), vector =
                                                          shape (default)
                                "type":<output type>,   # Output type e.g.:
                                                          raster, vector, file,
                                                          stds
                            }
                        },
                        <parameter name>:{
                            "name":<value>,             # Output name e.g.
                                                          "my_slope_map"
                            "export":{                  # Export options, if
                                                          present this map will
                                                          be exported
                                "format":<value>        # Set the export format
                                                          raster=GeoTiff
                                                          (default), vector =
                                                          shape (default)
                                "type":<output type>,   # Output type e.g.:
                                                          raster, vector, file,
                                                          stds
                            }
                        }
                    },
                    "flags":<flags>,                    # All flags in a string
                                                          e.g.: "ge"
                    "overwrite":<True|False>,           # Set True to overwrite
                                                          existing data
                    "verbose":<True|False>              # Verbosity of the
                                                          module
                },
               Id:{                                     # The id of an
                                                          executable command,
                                                          that is not a grass
                                                          module
                    "executable":<path>,                # The name and path of
                                                          the executable e.g.
                                                          /bin/cp
                    "stdin":<Id::stdout | Id::stderr>   # Use the output of a
                                                          specific module as
                                                          input for this module
                                                        # Id::stdout, Id::
                                                          stderr are available
                    "parameters":[<parameter>,]         # A list of strings
                                                          that represent the
                                                          parameters that may
                                                          contain
                                                        # temporary file
                                                          definitions:
                                                          $file::id  eg:
                                                          $file::aspect_output
                                                          _file
               },
                ...
            }

        """
        # Preprocess the post call
        rdc = self.preprocess(project_name=project_name)

        if rdc:
            # IDEA: here VM start (asyncron - subprocess?)
            # QUESTION:
            # * set status to accepted or to startingVM?
            # * consider from "queue_type": only if "per_job", "per_user" the VM should be started?
            # prepare_actinia(vm_size, queue_name (created in enqueue_job))
            #    * check if VM already run (if only one VM should be started per user)
            #    * start VM
            #    * install actinia
            #    * start worker for queue_name (execute_actinia)
            # vm_size, ... in preprocess (attributes of rdc?)
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)
