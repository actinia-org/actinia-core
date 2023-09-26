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
Sentinel-2A processing commands
"""
import os
import requests
import dateutil.parser as dtparser
from .google_satellite_bigquery_interface import (
    GoogleSatelliteBigQueryInterface,
)
from .aws_sentinel_interface import AWSSentinel2AInterface
from .exceptions import AsyncProcessError
from .process_object import Process


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Guido Riembauer"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"


def datetime_to_grass_datetime_string(dt):
    """Convert a python datetime object into a GRASS datetime string"""
    # GRASS datetime month names
    month_names = [
        "",
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ]

    # Check for time zone info in the datetime object
    if dt.tzinfo is not None:
        tz = dt.tzinfo.utcoffset(0)
        if tz.seconds > 86400 / 2:
            tz = (tz.seconds - 86400) / 60
        else:
            tz = tz.seconds / 60

        string = "%.2i %s %.2i %.2i:%.2i:%.2i %+.4i" % (
            dt.day,
            month_names[dt.month],
            dt.year,
            dt.hour,
            dt.minute,
            dt.second,
            tz,
        )
    else:
        string = "%.2i %s %.4i %.2i:%.2i:%.2i" % (
            dt.day,
            month_names[dt.month],
            dt.year,
            dt.hour,
            dt.minute,
            dt.second,
        )

    return string


class Sentinel2Processing(object):
    """"""

    def __init__(
        self,
        product_id,
        bands,
        download_cache,
        send_resource_update,
        message_logger,
        use_google=True,
        temp_file_path=None,
        config=None,
        query_result=None,
    ):
        """A collection of functions to generate Sentinel2 related import and
        processing commands. Each function returns a process chain that can be
        executed by the async processing classes.

        Args:
            config: The Actinia Core configuration object
            product_id (str): The scene id for which all bands should be
                              downloaded
            query_result (dict): The result of the BigQuery request
            bands (list): A list of band names
            temp_file_path: The path to the temporary directory to store
                            temporary files. It is assumed that this path is
                            available when the generated commands are executed.
            download_cache (str): The path to the download cache
            send_resource_update: The function to call for resource updates
            message_logger: The message logger to be used

        """
        self.config = config
        self.product_id = product_id
        self.query_result = query_result
        self.bands = bands
        self.temp_file_path = temp_file_path
        self.user_download_cache_path = download_cache
        self.send_resource_update = send_resource_update
        self.message_logger = message_logger
        self.gml_cache_file_name = None
        self.import_file_info = {}
        self.gml_temp_file_name = None
        self.timestamp = None
        self.bbox = None
        self.band_pattern = None
        self.use_google = use_google

    def _setup_download_import_google_without_query(self):
        """Setup the map name info for later renaming and the band pattern for
        importing.
        """
        level = self.product_id.split("_")[1]
        tile_block = self.product_id.split("_")[-2]
        date_block = self.product_id.split("_")[2]
        band_pattern = "("
        # Create file names, urls and check the download cache
        for band in self.bands:
            # kept here only for consistency:
            file_path = None
            # build the map name, here the highest possible resolution for each
            # band is assumed
            if band in ["B02", "B03", "B04", "B08"]:
                res = "10"
            elif band in ["B05", "B06", "B07", "B8A", "B11", "B12"]:
                res = "20"
            elif band in ["B1", "B9", "B10"]:
                res = "60"
            else:
                raise AsyncProcessError(
                    f"Band {band} is unknown. Please "
                    "provide band as 'BXY', e.g. "
                    "'B02', 'B8A', or 'B12'"
                )
            if level == "MSIL1C":
                band_pattern += f"{band}|"
                map_name = f"{tile_block}_{date_block}_{band}"
            elif level == "MSIL2A":
                band_pattern += f"{band}_{res}m|"
                map_name = f"{tile_block}_{date_block}_{band}_{res}m"
            self.import_file_info[band] = (file_path, map_name)
        band_pattern = band_pattern[:-1] + ")"
        self.band_pattern = band_pattern

    def _setup_download_import_google(self):
        """Setup the download, import and preprocessing of a
        sentinel2 scene from the Google Cloud Storage.

        1. Query Google BogQuery to gather the scene information
        2. Create URL list of files that must be downloaded and copied to the
           download cache
        3. Create the GML file that represents the footprint of the scene
        4. Check if the requested files exist

        Returns:
            (url_list, copy_file_list)
        """

        if self.query_result is None:
            self.query_interface = GoogleSatelliteBigQueryInterface(
                self.config
            )
            try:
                self.query_result = self.query_interface.get_sentinel_urls(
                    [
                        self.product_id,
                    ],
                    self.bands,
                )
            except Exception as e:
                raise AsyncProcessError(
                    "Error in querying Sentinel-2 product <%s> "
                    "in Google BigQuery Sentinel-2 database. "
                    "Error: %s" % (self.product_id, str(e))
                )

            if not self.query_result:
                raise AsyncProcessError(
                    "Unable to find Sentinel-2 product <%s> "
                    "in Google BigQuery Sentinel-2 database" % self.product_id
                )

        if self.product_id not in self.query_result:
            raise AsyncProcessError(
                "Unable to find Sentinel-2 product <%s> "
                "in Google BigQuery Sentinel-2 database" % self.product_id
            )

        # Switch into the tempfile directory
        os.chdir(self.temp_file_path)

        url_list = []
        copy_file_list = []

        gml_footprint = self.query_result[self.product_id]["gml_footprint"]
        self.timestamp = self.query_result[self.product_id]["timestamp"]
        self.bbox = self.query_result[self.product_id]["bbox"]

        # Write the gml footprint into a temporary file
        # The file name is the product id that will also be copied into the
        # download cache
        self.gml_cache_file_name = os.path.join(
            self.user_download_cache_path, self.product_id + ".gml"
        )

        self.import_file_info["footprint"] = (
            self.gml_cache_file_name,
            self.product_id,
        )

        if os.path.exists(self.gml_cache_file_name) is False:
            gml_temp_file_name = os.path.join(
                self.temp_file_path, self.product_id + ".gml"
            )
            gml_file = open(gml_temp_file_name, "w")
            gml_file.write(gml_footprint)
            gml_file.close()
            copy_file_list.append(
                (gml_temp_file_name, self.gml_cache_file_name)
            )
            self.message_logger.info(
                (gml_temp_file_name, self.gml_cache_file_name)
            )

        # Create file names, urls and check the download cache
        for band in self.bands:
            file_name = self.query_result[self.product_id][band]["file"]
            tile_name = self.query_result[self.product_id][band]["tile"]
            public_url = self.query_result[self.product_id][band]["public_url"]

            # This is the file path in the download cache directory
            file_path = os.path.join(self.user_download_cache_path, file_name)

            self.import_file_info[band] = (file_path, file_name)

            # This is the download path
            temp_file = os.path.join(self.temp_file_path, tile_name)

            # Check if the file already exists in the download cache
            # if not add the file to the download list and copy list
            if os.path.exists(file_path) is False:
                self.message_logger.info(public_url)
                url_list.append(public_url)
                copy_file_list.append((temp_file, file_path))

        # Check the urls for access. If all files are already in the download
        # cache, then nothing needs to be downloaded and checked.
        for url in url_list:
            # Send a resource update
            self.send_resource_update(
                message="Checking access to URL: %s" % url
            )

            # Check if thr URL exists by investigating the HTTP header
            resp = requests.head(url)
            self.message_logger.info(
                "%i %s %s" % (resp.status_code, resp.text, resp.headers)
            )

            if resp.status_code != 200:
                raise AsyncProcessError(
                    "Scene <%s> is not available. "
                    "The URL <%s> can not be accessed."
                    % (self.product_id, url)
                )

        return url_list, copy_file_list

    def _setup_download_import_aws(self):
        """Setup the download, import and preprocessing of a
        sentinel2 scene from the AWS Storage.

        Returns:
            (url_list, copy_file_list)

        TODO:  The implementation is still in progress, thr AWS download does
               not word yet.
        """

        if self.query_result is None:
            self.query_interface = AWSSentinel2AInterface(self.config)
            try:
                self.query_result = self.query_interface.get_sentinel_urls(
                    [
                        self.product_id,
                    ],
                    self.bands,
                )
            except Exception as e:
                raise AsyncProcessError(
                    "Error in querying Sentinel-2 product <%s> "
                    "in AWS Sentinel-2 database. "
                    "Error: %s" % (self.product_id, str(e))
                )

            if not self.query_result:
                raise AsyncProcessError(
                    "Unable to find Sentinel-2 product <%s> "
                    "in AWS Sentinel-2 database" % self.product_id
                )

        if self.product_id not in self.query_result:
            raise AsyncProcessError(
                "Unable to find Sentinel-2 product <%s> "
                "in AWS Sentinel-2 database" % self.product_id
            )

        # Switch into the tempfile directory
        os.chdir(self.temp_file_path)

        url_list = []
        copy_file_list = []

        gml_footprint = self.query_result[self.product_id]["gml_footprint"]
        self.timestamp = self.query_result[self.product_id]["timestamp"]
        self.bbox = self.query_result[self.product_id]["bbox"]

        # Write the gml footprint into a temporary file
        # The file name is the product id that will also be copied into the
        # download cache
        self.gml_cache_file_name = os.path.join(
            self.user_download_cache_path, self.product_id + ".gml"
        )

        self.import_file_info["footprint"] = (
            self.gml_cache_file_name,
            self.product_id,
        )

        if os.path.exists(self.gml_cache_file_name) is False:
            gml_temp_file_name = os.path.join(
                self.temp_file_path, self.product_id + ".gml"
            )
            gml_file = open(gml_temp_file_name, "w")
            gml_file.write(gml_footprint)
            gml_file.close()
            copy_file_list.append(
                (gml_temp_file_name, self.gml_cache_file_name)
            )
            self.message_logger.info(
                (gml_temp_file_name, self.gml_cache_file_name)
            )

        # Create file names, urls and check the download cache
        for band in self.bands:
            file_name = self.query_result[self.product_id][band]["file"]
            tile_name = self.query_result[self.product_id][band]["tile"]
            public_url = self.query_result[self.product_id][band]["public_url"]

            # This is the file path in the download cache directory
            file_path = os.path.join(self.user_download_cache_path, file_name)

            self.import_file_info[band] = (file_path, file_name)

            # This is the download path
            temp_file = os.path.join(self.temp_file_path, tile_name)

            # Check if the file already exists in the download cache
            # if not add the file to the download list and copy list
            if os.path.exists(file_path) is False:
                self.message_logger.info(public_url)
                url_list.append(public_url)
                copy_file_list.append((temp_file, file_path))

        # Check the urls for access. If all files are already in the download
        # cache, then nothing needs to be downloaded and checked.
        for url in url_list:
            # Send a resource update
            self.send_resource_update(
                message="Checking access to URL: %s" % url
            )

            # Check if thr URL exists by investigating the HTTP header
            resp = requests.head(url)
            self.message_logger.info(
                "%i %s %s" % (resp.status_code, resp.text, resp.headers)
            )

            if resp.status_code != 200:
                raise AsyncProcessError(
                    "Scene <%s> is not available. "
                    "The URL <%s> can not be accessed."
                    % (self.product_id, url)
                )

        return url_list, copy_file_list

    def _setup_download_import(self):
        if self.use_google:
            return self._setup_download_import_google()
        else:
            return self._setup_download_import_aws()

    def get_sentinel2_download_process_list_without_query(self):
        """Create the process list to download sentinel2 scenes
        from the Google Cloud Storage.
        """
        download_commands = []

        p = Process(
            exec_type="grass",
            executable="i.sentinel.download",
            executable_params=[
                "datasource=GCS",
                f"query=identifier={self.product_id}",
                f"output={self.user_download_cache_path}",
            ],
            id=f"i_sentinel_download_{self.product_id}",
            skip_permission_check=True,
        )
        download_commands.append(p)

        # The renaming step needs to know the map name(s). They can be put
        # together from the filename
        self._setup_download_import_google_without_query()

        return download_commands, self.import_file_info

    def get_sentinel2_import_process_list_without_query(self):
        """Generate Sentinel2A import process list

        1. Import required bands using i.sentinel.import
        """
        import_commands = []

        p = Process(
            exec_type="grass",
            executable="i.sentinel.import",
            executable_params=[
                f"input={self.user_download_cache_path}",
                f"pattern={self.band_pattern}",
                "-r",
            ],
            id=f"i_sentinel_import_{self.product_id}",
            skip_permission_check=True,
        )
        import_commands.append(p)
        return import_commands

    def get_sentinel2_download_process_list(self):
        """Create the process list to download, import and preprocess
        sentinel2 scene from the Google Cloud Storage.

        The downloaded files will be stored in a temporary directory. After the
        download of all files completes, the downloaded files will be moved to
        the download cache. This avoids broken files in case a download was
        interrupted or stopped by termination.

        This method creates wget calls to gather the sentinel2 scenes from the
        Google Cloud Storage sentinel2 archive using public https address.

        Returns:
            (import_commands, import_file_info)

            Example:

                import_file_info = {"footprint": (gml_file_name, product_id),
                               "B01":(file_path, file_name),
                               "B02":(file_path, file_name)}
        """
        url_list, copy_file_list = self._setup_download_import()

        download_commands = []

        # Create the download commands and update process chain
        for url in url_list:
            wget = "/usr/bin/wget"
            wget_params = list()
            wget_params.append("-t5")
            wget_params.append("-c")
            wget_params.append("-q")
            wget_params.append(url)

            p = Process(
                exec_type="exec",
                executable=wget,
                executable_params=wget_params,
                id=f"wget_{url.split('/')[-1]}",
                skip_permission_check=True,
            )

            download_commands.append(p)

        # Create the commands to move the downloaded files to the download
        # cache
        for source, dest in copy_file_list:
            if source != dest:
                copy = "/bin/mv"
                copy_params = list()
                copy_params.append(source)
                copy_params.append(dest)

                p = Process(
                    exec_type="exec",
                    executable=copy,
                    executable_params=copy_params,
                    id=f"mv_{os.path.basename(dest)}",
                    skip_permission_check=True,
                )
                download_commands.append(p)

        return download_commands, self.import_file_info

    def get_sentinel2_import_process_list(self):
        """Generate Senteinel2A import and preprocessing process list

        1. Import footprint with v.import
        2. Set the timestamp of the footprint with v.timestamp

        For each band:

            0. Use gdaltrans to select the footprint bbox
               that should be imported from the raster layer
            1. Import band with r.import
            2. Use g.region to set the region to footprint
            3. Create a mask with r.mask
            4. Compute the cropped version of the band with r.mapcalc
            5. Set the timestamp with r.timestamp
            6. Remove uncropped version with g.remove
            7. Remove the mask with r.mask

        Returns:
            list[Process]:
            The list of import commands

        """

        import_commands = []

        p = Process(
            exec_type="grass",
            executable="v.import",
            executable_params=[
                "input=%s" % self.gml_cache_file_name,
                "output=%s" % self.product_id,
                "--q",
            ],
            id=f"v_import_{self.product_id}",
            skip_permission_check=True,
        )
        import_commands.append(p)

        dt = dtparser.parse(self.timestamp.split(".")[0])
        timestamp = datetime_to_grass_datetime_string(dt)

        # Attach a the time stamp
        p = Process(
            exec_type="grass",
            executable="v.timestamp",
            executable_params=[
                "map=%s" % self.product_id,
                "date=%s" % timestamp,
            ],
            id=f"v_timestamp_{self.product_id}",
            skip_permission_check=True,
        )
        import_commands.append(p)

        # Import and update
        for key in self.import_file_info:
            if key == "footprint":
                continue
            input_file, map_name = self.import_file_info[key]
            temp_map_name = map_name + "_uncropped"
            cropped_input_file = input_file + ".vrt"

            # Create a boundingbox around the footprint to avoid
            # the projection of the scene with unused values
            gdal_translate = "/usr/bin/gdal_translate"
            gdal_translate_params = list()
            # -projwin ulx uly lrx lry
            gdal_translate_params.append("-projwin")
            gdal_translate_params.append("%f" % self.bbox[0])
            gdal_translate_params.append("%f" % self.bbox[1])
            gdal_translate_params.append("%f" % self.bbox[2])
            gdal_translate_params.append("%f" % self.bbox[3])
            gdal_translate_params.append("-of")
            gdal_translate_params.append("vrt")
            gdal_translate_params.append("-projwin_srs")
            gdal_translate_params.append("EPSG:4326")
            gdal_translate_params.append(input_file)
            gdal_translate_params.append(cropped_input_file)

            p = Process(
                exec_type="exec",
                executable=gdal_translate,
                executable_params=gdal_translate_params,
                id=f"gdal_translate_{self.product_id}",
                skip_permission_check=True,
            )
            import_commands.append(p)

            p = Process(
                exec_type="grass",
                executable="r.import",
                executable_params=[
                    "input=%s" % cropped_input_file,
                    "output=%s" % temp_map_name,
                    "--q",
                ],
                id=f"r_import_{self.product_id}",
                skip_permission_check=True,
            )
            import_commands.append(p)

            p = Process(
                exec_type="grass",
                executable="g.region",
                executable_params=[
                    "align=%s" % temp_map_name,
                    "vector=%s" % self.product_id,
                    "-g",
                ],
                id=f"set_g_region_to_{self.product_id}",
                skip_permission_check=True,
            )
            import_commands.append(p)

            p = Process(
                exec_type="grass",
                executable="r.mask",
                executable_params=["vector=%s" % self.product_id],
                id=f"r_mask_{self.product_id}",
                skip_permission_check=True,
            )
            import_commands.append(p)

            p = Process(
                exec_type="grass",
                executable="r.mapcalc",
                executable_params=[
                    "expression=%s = float(%s)" % (map_name, temp_map_name)
                ],
                id=f"create_float_rastermap_{self.product_id}",
                skip_permission_check=True,
            )
            import_commands.append(p)

            p = Process(
                exec_type="grass",
                executable="r.timestamp",
                executable_params=["map=%s" % map_name, "date=%s" % timestamp],
                id=f"r_timestamp_{self.product_id}",
                skip_permission_check=True,
            )
            import_commands.append(p)

            p = Process(
                exec_type="grass",
                executable="g.remove",
                executable_params=[
                    "type=raster",
                    "name=%s" % temp_map_name,
                    "-f",
                ],
                id=f"remove_tmp_map_{self.product_id}",
                skip_permission_check=True,
            )
            import_commands.append(p)

            p = Process(
                exec_type="grass",
                executable="r.mask",
                executable_params=["-r"],
                id=f"remove_mask_{self.product_id}",
                skip_permission_check=True,
            )
            import_commands.append(p)

        return import_commands

    def get_ndvi_r_mapcalc_process_list(
        self, red, nir, raster_result_name="ndvi"
    ):
        """Create NDVI r.mapcalc command and set the color table accordingly

        NDVI formular: (nir - red) / (nir + red)

        Args:
            red (str): The map name of the red band
            nir (str): The map name of the near infrared band
            raster_result_name (str): The result raster map name

        Returns:
            ndvi_commands

        """

        ndvi_commands = []

        p = Process(
            exec_type="grass",
            executable="r.mapcalc",
            executable_params=[
                "expression=%(ndvi)s = (float(%(nir)s) - float(%(red)s))/"
                "(float(%(nir)s) + float(%(red)s))"
                % {"ndvi": raster_result_name, "nir": nir, "red": red}
            ],
            id=f"compute_NDVI_{raster_result_name}",
            skip_permission_check=True,
        )
        ndvi_commands.append(p)

        p = Process(
            exec_type="grass",
            executable="r.colors",
            executable_params=["color=ndvi", "map=%s" % raster_result_name],
            id=f"set_color_{raster_result_name}",
            skip_permission_check=True,
        )
        ndvi_commands.append(p)

        return ndvi_commands
