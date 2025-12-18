# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2024 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""This module manages a raster layer resource as geotiff file that
will be created asynchronously.

The region settings of the mapset
or the raster layer region are used for export.
"""

from actinia_processing_lib.ephemeral_processing_with_export import (
    EphemeralProcessingWithExport,
)

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2024, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class EphemeralRasterLayerExporter(EphemeralProcessingWithExport):
    """Export a raster layer from a specific mapset as geotiff file.

    The region of the raster layer can be used for export. In this case a
    temporary mapset will be created to modify the region settings safely.
    Hence, this works also in write protected mapsets.
    """

    def __init__(self, rdc):
        """Setup the variables of this class

        Args:
            rdc (ResourceDataContainer): The data container that contains all
                                         required variables for processing

        """

        EphemeralProcessingWithExport.__init__(self, rdc)

        self.raster_name = self.map_name
        self.use_raster_region = self.rdc.user_data

    def _execute(self):
        """Overwrite this function in subclasses

        - Create the resource directory
        - Initialize and create the temporal database and mapset
        - Export the raster layer
        - Cleanup

        """
        # Setup the user credentials and logger
        self._setup()

        # Create and check the resource directory
        self.storage_interface.setup()

        # Check if we have access and create the temporary storage
        self.required_mapsets.append(self.mapset_name)
        self._create_temporary_grass_environment(
            source_mapset_name="PERMANENT"
        )

        format = "COG"
        from osgeo import gdal

        if "COG" not in [
            gdal.GetDriver(i).ShortName for i in range(gdal.GetDriverCount())
        ]:
            format = "GTiff"

        export_dict = {
            "name": self.raster_name + "@" + self.mapset_name,
            "export": {"format": format, "type": "raster"},
        }

        self.resource_export_list.append(export_dict)
        self._export_resources(self.use_raster_region)
