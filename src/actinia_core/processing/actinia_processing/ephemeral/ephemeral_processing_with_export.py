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
Asynchronous computation in specific temporary generated mapsets
with export of required map layers.
"""
import os
from actinia_core.processing.actinia_processing.ephemeral_processing import (
    EphemeralProcessing,
)
from actinia_core.core.common.process_object import Process
from actinia_core.core.common.exceptions import AsyncProcessTermination
from actinia_core.core.stac_exporter_interface import STACExporter

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class EphemeralProcessingWithExport(EphemeralProcessing):
    """
    This class processes GRASS data on the local machine in an temporary mapset
    and copies the exported results to a dedicated storage project.

    The temporary mapset will be removed by this class when the processing
    finished and the results are stored in the dedicated storage project.

    TODO: Implement the export of arbitrary files that were generated in the
          processing of the process chain
    """

    def __init__(self, rdc):
        """
        Setup the variables of this class

        Args:
            rdc (ResourceDataContainer): The data container that contains all
                                         required variables for processing

        """
        EphemeralProcessing.__init__(self, rdc)
        # Create the storage interface to store the exported resources
        self.storage_interface = rdc.create_storage_interface()

    def _export_raster(
        self,
        raster_name,
        format="COG",
        additional_options=[],
        use_raster_region=False,
    ):
        """Export a specific raster layer with r.out.gdal as GeoTiff.

        The result is stored in a temporary directory
        that is located in the temporary grass database.

        The region of the raster layer can be used for export. In this case a
        temporary region will be used for export, so that the original region
        of the mapset is not modified.
        COG-Driver: https://gdal.org/drivers/raster/cog.html

        Args:
            raster_name (str): The name of the raster layer
            format (str): COG (default; requires GDAL >= 3.1 on server), GTiff
            additional_options (list): Unused
            use_raster_region (bool): Use the region of the raster layer for
                                      export

        Returns:
            tuple: A tuple (file_name, output_path)

        Raises:
            AsyncProcessError: If a GRASS module return status is not 0

        """
        # Export the layer
        suffix = ".tif"
        # Remove a potential mapset
        file_name = raster_name.split("@")[0] + suffix

        if use_raster_region is True:
            p = Process(
                exec_type="grass",
                executable="g.region",
                executable_params=["raster=%s" % raster_name, "-g"],
                id=f"exporter_region_{raster_name}",
                stdin_source=None,
            )

            self._update_num_of_steps(1)
            self._run_module(p)

        if format == "COG":
            # check if GDAL has COG driver
            from osgeo import gdal

            driver_list = [
                gdal.GetDriver(i).ShortName
                for i in range(gdal.GetDriverCount())
            ]
            if "COG" not in driver_list:
                format = "GTiff"
                self.message_logger.info(
                    "COG driver not available, using GTiff driver"
                )

        # Save the file in the temporary directory of the temporary gisdb
        output_path = os.path.join(self.temp_file_path, file_name)

        module_name = "r.out.gdal"
        args = [
            "-fmt",
            "input=%s" % raster_name,
            "format=%s" % format,
            "output=%s" % output_path,
        ]
        create_opts = "createopt=BIGTIFF=YES,COMPRESS=LZW"

        if format == "GTiff":
            # generate overviews with compression:
            os.environ["COMPRESS_OVERVIEW"] = "LZW"
            args.append("overviews=5")
            create_opts += ",TILED=YES"

        args.append(create_opts)

        if additional_options:
            args.extend(additional_options)

        p = Process(
            exec_type="grass",
            executable=module_name,
            executable_params=args,
            id=f"exporter_raster_{raster_name}",
            stdin_source=None,
        )

        self._update_num_of_steps(1)
        self._run_module(p)

        return file_name, output_path

    def _export_strds(self, strds_name, format="GTiff"):
        """Export a specific strds layer with t.rast.export.

        The result is stored in a temporary directory
        that is located in the temporary grass database.

        Args:
            strds_name (str): The name of the strds layer
            format (str): GTiff (only option)

        Returns:
            tuple: A tuple (file_name, output_path)

        """
        suffix = ".tar.gz"
        file_name = strds_name.split("@")[0] + suffix
        output_path = os.path.join(self.temp_file_path, file_name)

        if format != "GTiff":
            format = "GTiff"
            self.message_logger.info(
                "Only GTiff driver is supported for STRDS export."
            )

        module_name = "t.rast.export"
        args = [
            "input=%s" % strds_name,
            "format=%s" % format,
            "output=%s" % output_path,
            "directory=%s" % self.temp_file_path,
            "compression=%s" % "gzip",
        ]
        # optimized for GTiff
        create_opts = "createopt=BIGTIFF=YES,COMPRESS=LZW,TILED=YES"
        args.append(create_opts)
        os.environ["COMPRESS_OVERVIEW"] = "LZW"

        p = Process(
            exec_type="grass",
            executable=module_name,
            executable_params=args,
            id=f"exporter_strds_{strds_name}",
            stdin_source=None,
        )

        self._update_num_of_steps(1)
        self._run_module(p)

        return file_name, output_path

    def _export_vector(
        self, vector_name, format="GPKG", additional_options=[]
    ):
        """
        Export a specific vector layer with v.out.ogr using a specific output
        format

        The result is stored in a temporary directory
        that is located in the temporary grass database.

        The resulting vector file will always be compressed using zip

        Args:
            vector_name (str): The name of the raster layer
            format (str): GPKG (default), GML, GeoJSON, ESRI_Shapefile, SQLite,
                          CSV
            additional_options (list): Unused

        Returns:
            tuple: A tuple (file_name, output_path)

        Raises:
            AsyncProcessError: If a GRASS module return status is not 0

        """
        # Export the layer
        prefix = ""
        if format == "GPKG":
            prefix = ".gpkg"
        if format == "GML":
            prefix = ".gml"
        if format == "GeoJSON":
            prefix = ".json"
        if format == "ESRI_Shapefile":
            prefix = ""
        if format == "SQLite":
            prefix = ".sqlite"
        if format == "CSV":
            prefix = ".csv"

        # Remove a potential mapset
        file_name = vector_name.split("@")[0] + prefix
        archive_name = file_name + ".zip"
        # switch into the temporary working directory to use relative path for
        # zip
        os.chdir(self.temp_file_path)

        module_name = "v.out.ogr"
        args = [
            "-e",
            "input=%s" % vector_name,
            "format=%s" % format,
            "output=%s" % file_name,
        ]

        if additional_options:
            args.extend(additional_options)

        # Export
        p = Process(
            exec_type="grass",
            executable=module_name,
            executable_params=args,
            id=f"exporter_vector_{vector_name}",
            stdin_source=None,
        )

        self._update_num_of_steps(1)
        self._run_module(p)

        # Compression
        compressed_output_path = os.path.join(
            self.temp_file_path, archive_name
        )

        executable = "/usr/bin/zip"
        args = ["-r", archive_name, file_name]

        p = Process(
            exec_type="exec",
            executable=executable,
            executable_params=args,
            id=f"exporter_zip_{vector_name}",
            stdin_source=None,
        )

        self._update_num_of_steps(1)
        self._run_process(p)

        return archive_name, compressed_output_path

    def _export_postgis(
        self, vector_name, dbstring, output_layer=None, additional_options=[]
    ):
        """
        Export a specific vector layer with v.out.postgis to a PostGIS database

        Args:
            vector_name (str): The name of the raster layer
            dbstring (str): The PostgreSQL database string to connect to the
                            output database
            output_layer (str): The name of the PostgreSQL database table
            additional_options (list): Unused

        Raises:
            AsyncProcessError: If a GRASS module return status is not 0

        """

        module_name = "v.out.postgis"
        args = ["-l", "input=%s" % vector_name, "output=%s" % dbstring]

        if output_layer:
            args.append("output_layer=%s" % output_layer)

        if additional_options:
            args.extend(additional_options)

        # Export
        p = Process(
            exec_type="grass",
            executable=module_name,
            executable_params=args,
            id=f"exporter_postgis_{vector_name}",
            stdin_source=None,
        )

        self._update_num_of_steps(1)
        self._run_module(p)

    def _export_file(self, tmp_file, file_name):
        """Export a specific file

        The result is stored in a temporary directory
        that is located in the temporary grass database.

        The output file will always be compressed using zip

        Args:
            tmp_file (str): The name of the temporary file generated by a
                            module
            file_name (str): The file name to be used for export

        Returns:
            tuple: A tuple (file_name, output_path)

        Raises:
            AsyncProcessError: If a GRASS module return status is not 0

        """
        # Export the file
        archive_name = file_name + ".zip"
        # switch into the temporary working directory to use relative path for
        # zip
        os.chdir(self.temp_file_path)

        # Compression
        compressed_output_path = os.path.join(
            self.temp_file_path, archive_name
        )

        executable = "/usr/bin/zip"
        args = ["-r", archive_name, tmp_file]

        p = Process(
            exec_type="exec",
            executable=executable,
            executable_params=args,
            id=f"exporter_file_{file_name}",
            stdin_source=None,
        )

        self._update_num_of_steps(1)
        self._run_process(p)

        return archive_name, compressed_output_path

    def _export_resources(self, use_raster_region=False):
        """
        Export all resources that were listed in the process chain description.

        Save all exported files in a temporary directory first, then copy the
        data to its destination after the export is finished.
        The temporary data will be finally removed.

        At the moment only raster layer export is supported.

        """

        for resource in self.resource_export_list:
            # Check for termination requests between the exports
            if (
                bool(
                    self.resource_logger.get_termination(
                        self.user_id, self.resource_id, self.iteration
                    )
                )
                is True
            ):
                raise AsyncProcessTermination(
                    "Resource export was terminated by user request"
                )

            # Raster export
            if resource["export"]["type"] in [
                "raster",
                "vector",
                "file",
                "strds",
            ]:
                output_type = resource["export"]["type"]
                output_path = None

                # Legacy code
                if "name" in resource:
                    file_name = resource["name"]
                if "value" in resource:
                    file_name = resource["value"]

                if output_type == "raster":
                    message = "Export raster layer <%s> with format %s" % (
                        file_name,
                        resource["export"]["format"],
                    )
                    self._send_resource_update(message)
                    _, output_path = self._export_raster(
                        raster_name=file_name,
                        format=resource["export"]["format"],
                        use_raster_region=use_raster_region,
                    )

                elif output_type == "vector":
                    if "PostgreSQL" in resource["export"]["format"]:
                        dbstring = resource["export"]["dbstring"]
                        output_layer = None
                        if "output_layer" in resource["export"]:
                            output_layer = resource["export"]["output_layer"]

                        message = (
                            "Export vector layer <%s> to PostgreSQL database"
                            % (file_name)
                        )
                        self._send_resource_update(message)
                        self._export_postgis(
                            vector_name=file_name,
                            dbstring=dbstring,
                            output_layer=output_layer,
                        )
                        # continue
                    else:
                        message = "Export vector layer <%s> with format %s" % (
                            file_name,
                            resource["export"]["format"],
                        )
                        self._send_resource_update(message)
                        _, output_path = self._export_vector(
                            vector_name=file_name,
                            format=resource["export"]["format"],
                        )
                elif output_type == "file":
                    file_name = resource["file_name"]
                    tmp_file = resource["tmp_file"]
                    _, output_path = self._export_file(
                        tmp_file=tmp_file, file_name=file_name
                    )
                elif output_type == "strds":
                    message = "Export strds layer <%s> with format %s" % (
                        file_name,
                        resource["export"]["format"],
                    )
                    self._send_resource_update(message)
                    _, output_path = self._export_strds(
                        strds_name=file_name,
                        format=resource["export"]["format"],
                    )
                else:
                    raise AsyncProcessTermination(
                        "Unknown export format %s" % output_type
                    )

                message = "Moving generated resources to final destination"
                self._send_resource_update(message)

                # Store the temporary file in the resource storage
                # and receive the resource URL
                if output_path is not None:
                    resource_url = self.storage_interface.store_resource(
                        output_path
                    )
                    self.resource_url_list.append(resource_url)

                    if "metadata" in resource:
                        if resource["metadata"]["format"] == "STAC":
                            stac = STACExporter()

                            stac_catalog = stac.stac_builder(
                                resource_url, file_name, output_type
                            )
                            self.resource_url_list.append(stac_catalog)

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
        """
        Overwrite this function in subclasses to perform the final cleanup
        """
        # Clean up and remove the temporary gisdbase
        self._cleanup()
        # Remove resource directories
        if "error" in self.run_state or "terminated" in self.run_state:
            self.storage_interface.remove_resources()
