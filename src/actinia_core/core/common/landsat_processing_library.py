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
Landsat processing commands
"""
import os
from .process_object import Process
from actinia_core.core.geodata_download_importer import (
    GeoDataDownloadImportSupport,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

SUPPORTED_MIMETYPES = [
    "application/zip",
    "application/tiff",
    "application/gml",
]

SCENE_SUFFIXES = {
    "LT04": [
        "_B1.TIF",
        "_B2.TIF",
        "_B3.TIF",
        "_B4.TIF",
        "_B5.TIF",
        "_B6.TIF",
        "_B7.TIF",
        "_MTL.txt",
    ],
    "LT05": [
        "_B1.TIF",
        "_B2.TIF",
        "_B3.TIF",
        "_B4.TIF",
        "_B5.TIF",
        "_B6.TIF",
        "_B7.TIF",
        "_MTL.txt",
    ],
    "LE07": [
        "_B1.TIF",
        "_B2.TIF",
        "_B3.TIF",
        "_B4.TIF",
        "_B5.TIF",
        "_B6_VCID_2.TIF",
        "_B6_VCID_1.TIF",
        "_B7.TIF",
        "_B8.TIF",
        "_MTL.txt",
    ],
    "LC08": [
        "_B1.TIF",
        "_B2.TIF",
        "_B3.TIF",
        "_B4.TIF",
        "_B5.TIF",
        "_B6.TIF",
        "_B7.TIF",
        "_B8.TIF",
        "_B9.TIF",
        "_B10.TIF",
        "_B11.TIF",
        "_MTL.txt",
    ],
}

RASTER_SUFFIXES = {
    "LT04": [".1", ".2", ".3", ".4", ".5", ".6", ".7"],
    "LT05": [".1", ".2", ".3", ".4", ".5", ".6", ".7"],
    "LE07": [".1", ".2", ".3", ".4", ".5", ".61", ".62", ".7", ".8"],
    "LC08": [
        ".1",
        ".2",
        ".3",
        ".4",
        ".5",
        ".6",
        ".7",
        ".8",
        ".9",
        ".10",
        ".11",
    ],
}


SCENE_BANDS = {
    "LT04": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "MTL"],
    "LT05": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "MTL"],
    "LE07": [
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6_VCID_2",
        "B6_VCID_1",
        "B7",
        "B8",
        "MTL",
    ],
    "LC08": [
        "B1",
        "B2",
        "B3",
        "B4",
        "B5",
        "B6",
        "B7",
        "B8",
        "B9",
        "B10",
        "B11",
        "MTL",
    ],
}


def extract_sensor_id_from_scene_id(scene_id):
    """Extract the sensor id from a Landsat scene id

    Args:
        scene_id (str): The landsat scene id

    Returns:
        (str)
        The sencor id

    """
    return scene_id.split("_")[0]


def scene_id_to_google_url(scene_id, suffix):
    """Convert a landsat scene id into the public google download URL for the
    required file

    Args:
        scene_id (str): The Landsat scene id
        suffix (str): The suffix of the file to create the url for,  i.e.:
                      "_B1.TIF" or "_MTL.txt"
    Returns:
        (str)
        The URL to the scene file
    """
    # new URL example
    # https://storage.googleapis.com/gcp-public-data-landsat/LC08/01/001/004/
    # LC08_L1GT_001004_20130910_20170502_01_T2/
    # LC08_L1GT_001004_20130910_20170502_01_T2_B1.TIF

    # Create the download URL components from the Landsat scene id
    landsat_sensor_id = extract_sensor_id_from_scene_id(scene_id)
    path = scene_id.split("_")[2][:3]
    row = scene_id.split("_")[2][3:]

    url = (
        "https://storage.googleapis.com/gcp-public-data-landsat/"
        f"{landsat_sensor_id}/01/{path}/{row}/{scene_id}/{scene_id}{suffix}"
    )
    return url


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


class LandsatProcessing(GeoDataDownloadImportSupport):
    """"""

    def __init__(
        self,
        config,
        scene_id,
        temp_file_path,
        download_cache,
        send_resource_update,
        message_logger,
    ):
        """A collection of functions to generate Landsat4-8 scene related
        import and processing commands. Each function returns a process chain
        that can be executed by the async processing classes.

        Args:
            config: The Actinia Core configuration object
            scene_id (str): The scene id for which all bands should be
                            downloaded
            temp_file_path: The path to the temporary directory to store
                            temporary files. It is assumed that this path is
                            available when the generated commands are executed.
            download_cache (str): The path to the download cache
            send_resource_update: The function to call for resource updates
            message_logger: The message logger to be used

        """

        GeoDataDownloadImportSupport.__init__(
            self,
            config,
            temp_file_path,
            download_cache,
            send_resource_update,
            message_logger,
            None,
        )

        self.scene_id = scene_id
        self.landsat_sensor_id = None
        self.url_list = []
        self.raster_names = []
        self.band_raster_names = {}
        self.ndvi_name = None

    def _setup(self):
        """
        Setup the download of the required Landsat scene from the Google Cloud
        Storage.

        Check the download cache if the file already exists, to avoid redundant
        downloads. The downloaded files will be stored in a temporary
        directory. After the download of all files completes, the downloaded
        files will be moved to the download cache. This avoids broken files in
        case a download was interrupted or stopped by termination.

        This method uses wget to gather the landsat scenes from the Google
        Cloud Storage landsat archive using public https address.
        """

        GeoDataDownloadImportSupport._setup(self)
        self.landsat_sensor_id = extract_sensor_id_from_scene_id(self.scene_id)

        count = 0
        # Create file names, urls and check the download cache
        for suffix in SCENE_SUFFIXES[self.landsat_sensor_id]:
            file_name = "%s%s" % (self.scene_id, suffix)
            # This is the file path in the download cache directory
            file_path = os.path.join(self.user_download_cache_path, file_name)
            self.file_list.append(file_path)
            # This is the download path
            temp_file_path = os.path.join(self.temp_file_path, file_name)
            # Create the download URL
            url = scene_id_to_google_url(self.scene_id, suffix)

            self.url_list.append(url)
            self.copy_file_list.append((temp_file_path, file_path))
            count += 1

    def get_import_process_list(self):
        count = 0
        import_commands = []

        for file_path in self.file_list:
            if "_MTL.TXT" not in file_path.upper():
                raster_name = "%s%s" % (
                    self.scene_id,
                    RASTER_SUFFIXES[self.landsat_sensor_id][count],
                )
                self.raster_names.append(raster_name)
                self.band_raster_names[
                    SCENE_BANDS[self.landsat_sensor_id][count]
                ] = raster_name
                p = self.get_raster_import_command(
                    file_path=file_path, raster_name=raster_name
                )
                import_commands.append(p)
                count += 1

        return import_commands

    def get_i_landsat_toar_process_list(self, atcor_method):
        option = "uncorrected"

        if atcor_method == "DOS4":
            option = "dos4"

        if atcor_method == "DOS1":
            option = "dos1"

        toar_commands = []

        p = Process(
            exec_type="grass",
            executable="i.landsat.toar",
            executable_params=[
                "input=%s." % self.scene_id,
                "metfile=%s_%s"
                % (
                    os.path.join(self.user_download_cache_path, self.scene_id),
                    "MTL.txt",
                ),
                "method=%s" % option,
                "output=%s_%s." % (self.scene_id, atcor_method),
                "--q",
            ],
            id=f"top_of_atmosphere_{self.scene_id}",
            skip_permission_check=True,
        )
        toar_commands.append(p)
        return toar_commands

    def get_i_vi_process_list(self, atcor_method, processing_method):
        self.ndvi_name = "%s_%s_%s" % (
            self.scene_id,
            atcor_method,
            processing_method,
        )

        ndvi_commands = []

        ivi = "i.vi"
        ivi_params = list()
        if self.landsat_sensor_id == "LC08":
            ivi_params.append(
                "red=%s_%s%s" % (self.scene_id, atcor_method, ".4")
            )
            ivi_params.append(
                "nir=%s_%s%s" % (self.scene_id, atcor_method, ".5")
            )
            ivi_params.append(
                "green=%s_%s%s" % (self.scene_id, atcor_method, ".3")
            )
            ivi_params.append(
                "blue=%s_%s%s" % (self.scene_id, atcor_method, ".2")
            )
            ivi_params.append(
                "band5=%s_%s%s" % (self.scene_id, atcor_method, ".7")
            )
            ivi_params.append(
                "band7=%s_%s%s" % (self.scene_id, atcor_method, ".8")
            )
        else:
            ivi_params.append(
                "red=%s_%s%s" % (self.scene_id, atcor_method, ".3")
            )
            ivi_params.append(
                "nir=%s_%s%s" % (self.scene_id, atcor_method, ".4")
            )
            ivi_params.append(
                "green=%s_%s%s" % (self.scene_id, atcor_method, ".2")
            )
            ivi_params.append(
                "blue=%s_%s%s" % (self.scene_id, atcor_method, ".1")
            )
            ivi_params.append(
                "band5=%s_%s%s" % (self.scene_id, atcor_method, ".5")
            )
            ivi_params.append(
                "band7=%s_%s%s" % (self.scene_id, atcor_method, ".7")
            )

        ivi_params.append("viname=%s" % processing_method.lower())
        ivi_params.append("output=%s" % self.ndvi_name)

        p = Process(
            exec_type="grass",
            executable=ivi,
            executable_params=ivi_params,
            id=f"i_vi_{processing_method.lower()}_{self.ndvi_name}",
            skip_permission_check=True,
        )
        ndvi_commands.append(p)

        p = Process(
            exec_type="grass",
            executable="r.colors",
            executable_params=["map=%s" % self.ndvi_name, "color=ndvi"],
            id=f"set_colors_{processing_method.lower()}_{self.ndvi_name}",
            skip_permission_check=True,
        )
        ndvi_commands.append(p)

        return ndvi_commands
