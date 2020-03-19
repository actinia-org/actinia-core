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
Asynchronous computation in specific temporary generated mapsets
with export of required map layers.
"""
import pickle
import os
from flask import jsonify, make_response

from copy import deepcopy
from flask_restful_swagger_2 import swagger, Schema
from .ephemeral_processing import EphemeralProcessing
from .resource_base import ResourceBase
from .common.redis_interface import enqueue_job
from .common.process_object import Process
from .common.process_chain import ProcessChainModel
from .common.exceptions import AsyncProcessTermination
from .common.response_models import ProcessingResponseModel, ProcessingErrorResponseModel

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


DESCR="""Execute a user defined process chain in an ephemeral database
and provide the generated resources as downloadable files via URL's. Minimum required user role: user.

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

The persistent database will not be modified. The ephemeral database will be removed after processing.
Use the URL's provided in the finished response to download the resource that were specified
in the process chain for export.
"""


SCHEMA_DOC={
    'tags': ['Processing'],
    'description': DESCR,
    'consumes':['application/json'],
    'parameters': [
        {
            'name': 'location_name',
            'description': 'The location name that contains the data that should be processed',
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
            'schema':ProcessingResponseModel
        },
        '400': {
            'description':'The error message and a detailed log why process chain execution '
                          'did not succeeded',
            'schema':ProcessingErrorResponseModel
        }
    }
 }


class AsyncEphemeralExportResource(ResourceBase):
    """
    This class represents a resource that runs asynchronous processing tasks in
    a temporary mapset and exports the computed results as geotiff files.
    """
    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name):
        """Execute a user defined process chain in an ephemeral location/mapset and store the processing results
        for download.
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
    a temporary mapset and exports the computed results as geotiff files to the Amazon S3
    storage.
    """
    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc(deepcopy(SCHEMA_DOC))
    def post(self, location_name):
        """Execute a user defined process chain in an ephemeral location/mapset and store the processing result in an Amazon S3 bucket
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
        """Execute a user defined process chain in an ephemeral location/mapset and store the processing result in an Google cloud storage bucket
        """
        rdc = self.preprocess(has_json=True, location_name=location_name)
        rdc.set_storage_model_to_gcs()

        enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


def start_job(*args):
    processing = EphemeralProcessingWithExport(*args)
    processing.run()


class EphemeralProcessingWithExport(EphemeralProcessing):
    """
    This class processes GRASS data on the local machine in an temporary mapset
    and copies the exported results to a dedicated storage location.

    The temporary mapset will be removed by this class when the processing finished
    and the results are stored in the dedicated storage location.

    TODO: Implement the export of arbitrary files that were generated in the processing of the process chain
    """
    def __init__(self, rdc):
        """
        Setup the variables of this class

        Args:
            rdc (ResourceDataContainer): The data container that contains all required variables for processing

        """
        EphemeralProcessing.__init__(self, rdc)
        # Create the storage interface to store the exported resources
        self.storage_interface = rdc.create_storage_interface()

    def _export_raster(self, raster_name,
                       format="GTiff",
                       additional_options=[],
                       use_raster_region=False):
        """Export a specific raster layer with r.out.gdal as GeoTiff.

        The result is stored in a temporary directory
        that is located in the temporary grass database.

        The region of the raster layer can be used for export. In this case a temporary region
        will be used for export, so that the original region of the mapset is not modified.

        Args:
            raster_name (str): The name of the raster layer
            format (str): GTiff
            additional_options (list): Unused
            use_raster_region (bool): Use the region of the raster layer for export

        Returns:
            tuple: A tuple (file_name, output_path)

        Raises:
            AsyncProcessError: If a GRASS module return status is not 0

        """
        # Export the layer
        prefix = ".tiff"
        if format == "GTiff":
            prefix = ".tiff"

        # Remove a potential mapset
        file_name = raster_name.split("@")[0] + prefix

        if use_raster_region is True:

            p = Process(exec_type="grass",
                             executable="g.region",
                             executable_params=["raster=%s"%raster_name, "-g"],
                             stdin_source=None)

            self._update_num_of_steps(1)
            self._run_module(p)

        # Save the file in the temporary directory of the temporary gisdb
        output_path = os.path.join(self.temp_file_path, file_name)

        # generate overviews with compression:
        os.environ['COMPRESS_OVERVIEW'] = "LZW"
        module_name = "r.out.gdal"
        args = ["-fmt", "input=%s"%raster_name, "format=%s"%format,
                "createopt=COMPRESS=LZW,TILED=YES", "overviews=5", "output=%s"%output_path]

        if additional_options:
            args.extend(additional_options)

        p = Process(exec_type="grass",
                         executable=module_name,
                         executable_params=args,
                         stdin_source=None)

        self._update_num_of_steps(1)
        self._run_module(p)

        return file_name, output_path

    def _export_vector(self, vector_name,
                       format="GML",
                       additional_options=[]):
        """Export a specific vector layer with v.out.ogr using a specific output format

        The result is stored in a temporary directory
        that is located in the temporary grass database.

        The resulting vector file will always be compressed using zip

        Args:
            vector_name (str): The name of the raster layer
            format (str): GML, GeoJSON, ESRI_Shapefile, SQLite, CSV
            additional_options (list): Unused

        Returns:
            tuple: A tuple (file_name, output_path)

        Raises:
            AsyncProcessError: If a GRASS module return status is not 0

        """
        # Export the layer
        prefix = ""
        if format == "GML":
            prefix = ".gml"
        if format == "GeoJSON":
            prefix = ".json"
        if format == "ESRI_Shapefile":
            prefix = ""
        if format == "SQLite":
            prefix = ".sqlite"
        if format == "GPKG":
            prefix = ".gpkg"
        if format == "CSV":
            prefix = ".csv"

        # Remove a potential mapset
        file_name = vector_name.split("@")[0] + prefix
        archive_name = file_name + ".zip"
        # switch into the temporary working directory to use relative path for zip
        os.chdir(self.temp_file_path)

        module_name = "v.out.ogr"
        args = ["-e", "input=%s"%vector_name, "format=%s"%format,
                "output=%s"%file_name]

        if additional_options:
            args.extend(additional_options)

        # Export
        p = Process(exec_type="grass",
                         executable=module_name,
                         executable_params=args,
                         stdin_source=None)

        self._update_num_of_steps(1)
        self._run_module(p)

        # Compression
        compressed_output_path = os.path.join(self.temp_file_path, archive_name)

        executable = "/usr/bin/zip"
        args = ["-r", archive_name, file_name]

        p = Process(exec_type="exec",
                         executable=executable,
                         executable_params=args,
                         stdin_source=None)

        self._update_num_of_steps(1)
        self._run_process(p)

        return archive_name, compressed_output_path

    def _export_postgis(self, vector_name, dbstring,
                       output_layer=None,
                       additional_options=[]):
        """Export a specific vector layer with v.out.postgis to a PostGIS database

        Args:
            vector_name (str): The name of the raster layer
            dbstring (str): The PostgreSQL database string to connect to the output database
            output_layer (str): The name of the PostgreSQL database table
            additional_options (list): Unused

        Raises:
            AsyncProcessError: If a GRASS module return status is not 0

        """

        module_name = "v.out.postgis"
        args = ["-l", "input=%s"%vector_name, "output=%s"%dbstring]

        if output_layer:
            args.append("output_layer=%s"%output_layer)

        if additional_options:
            args.extend(additional_options)

        # Export
        p = Process(exec_type="grass",
                         executable=module_name,
                         executable_params=args,
                         stdin_source=None)

        self._update_num_of_steps(1)
        self._run_module(p)

    def _export_file(self, tmp_file, file_name):
        """Export a specific file

        The result is stored in a temporary directory
        that is located in the temporary grass database.

        The output file will always be compressed using zip

        Args:
            tmp_file (str): The name of the temporary file generated by a module
            file_name (str): The file name to be used for export

        Returns:
            tuple: A tuple (file_name, output_path)

        Raises:
            AsyncProcessError: If a GRASS module return status is not 0

        """
        # Export the file
        archive_name = file_name + ".zip"
        # switch into the temporary working directory to use relative path for zip
        os.chdir(self.temp_file_path)

        # Compression
        compressed_output_path = os.path.join(self.temp_file_path, archive_name)

        executable = "/usr/bin/zip"
        args = ["-r", archive_name, tmp_file]

        p = Process(exec_type="exec",
                         executable=executable,
                         executable_params=args,
                         stdin_source=None)

        self._update_num_of_steps(1)
        self._run_process(p)

        return archive_name, compressed_output_path

    def _export_resources(self, use_raster_region=False):
        """Export all resources that were listed in the process chain description.

        Save all exported files in a temporary directory first, then copy the data to its destination
        after the export is finished. The temporary data will be finally removed.

        At the moment only raster layer export is supported.

        """
        for resource in self.resource_export_list:

            # print("Check for termination %i"%self.resource_logger.get_termination(self.user_id, self.resource_id))

            # Check for termination requests between the exports
            if bool(self.resource_logger.get_termination(self.user_id, self.resource_id)) is True:
                raise AsyncProcessTermination("Resource export was terminated by user request")

            # Raster export
            if resource["export"]["type"] in ["raster", "vector", "file"]:

                output_type = resource["export"]["type"]
                output_path = None

                # Legacy code
                if "name" in resource:
                    file_name = resource["name"]
                if "value" in resource:
                    file_name = resource["value"]

                if output_type == "raster":
                    message = "Export raster layer <%s> with format %s"%(file_name, resource["export"]["format"])
                    self._send_resource_update(message)
                    output_name, output_path = self._export_raster(raster_name=file_name,
                                                                   format=resource["export"]["format"],
                                                                   use_raster_region=use_raster_region)
                elif output_type == "vector":
                    if "PostgreSQL" in resource["export"]["format"]:
                        dbstring = resource["export"]["dbstring"]
                        output_layer = None
                        if "output_layer" in resource["export"]:
                            output_layer = resource["export"]["output_layer"]

                        message = "Export vector layer <%s> to PostgreSQL database"%(file_name)
                        self._send_resource_update(message)
                        self._export_postgis(vector_name=file_name, dbstring=dbstring, output_layer=output_layer)
                        # continue
                    else:
                        message = "Export vector layer <%s> with format %s"%(file_name, resource["export"]["format"])
                        self._send_resource_update(message)
                        output_name, output_path = self._export_vector(vector_name=file_name,
                                                                       format=resource["export"]["format"])
                elif output_type == "file":
                    file_name = resource["file_name"]
                    tmp_file = resource["tmp_file"]
                    output_name, output_path = self._export_file(tmp_file=tmp_file, file_name=file_name)
                else:
                    raise AsyncProcessTermination("Unknown export format %s"%output_type)

                message = "Moving generated resources to final destination"
                self._send_resource_update(message)

                # Store the temporary file in the resource storage
                # and receive the resource URL
                if output_path is not None:
                    resource_url = self.storage_interface.store_resource(output_path)
                    self.resource_url_list.append(resource_url)

    def _execute(self, skip_permission_check=False):
        """Overwrite this function in subclasses

        Overwrite this function in subclasses

            - Setup user credentials
            - Setup the storage interface
            - Analyse the process chain
            - Initialize and create the temporal database and mapset
            - Run the modules
            - Export the results
            - Cleanup

        """
        # Setup the user credentials and logger
        self._setup()

        # Create and check the resource directory
        self.storage_interface.setup()

        EphemeralProcessing._execute(self)

        # Export all resources and generate the finish response
        self._export_resources()

    def _final_cleanup(self):
        """Overwrite this function in subclasses to perform the final cleanup
        """
        # Clean up and remove the temporary gisdbase
        self._cleanup()
        # Remove resource directories
        if "error" in self.run_state or "terminated" in self.run_state:
            self.storage_interface.remove_resources()
