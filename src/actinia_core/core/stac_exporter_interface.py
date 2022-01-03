# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2021 mundialis GmbH & Co. KG
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
This code shows the STACExporter model which help actinia core
to export and manage the STAC items a global collection configuration

"""

# from PyQt4.QtCore import *
# from PyQt4.QtXml import *
# from config import global_config

__license__ = "GPLv3"
__author__ = "Jorge Herrera"
__copyright__ = "Copyright 2021, mundialis GmbH & Co. KG"
__maintainer__ = "__mundialis__"
__email__ = "info@mundialis.de"

from datetime import datetime
from pickle import TRUE
import pystac
import rasterio
from shapely.geometry import Polygon, mapping

from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.core.common.exceptions import AsyncProcessTermination
from actinia_core.core.common.process_object import Process
try:
    from actinia_stac_plugin.core.stac_redis_interface import redis_actinia_interface
    has_plugin = True
except Exception:
    has_plugin = False


class STACExporter:

    def stac_collection_initializer(self):
        """
        Initilize the STAC Catalog for the different outputs in actinia
        Catalog allows to have versability on the spatio-temporal spectrum,
        in addition the properties are independent for each item stored

        Code uses pystac as base for the creation of stac catalogs
        """

        redis_actinia_interface.connect()

        result_catalog_validation = redis_actinia_interface.exists("result-catalog")

        if result_catalog_validation is not TRUE:
            results = pystac.Catalog(id="result-catalog", description="STAC catalog")

            redis_actinia_interface.create(
                "result-catalog",
                results.to_dict(),
            )
        else:
            raise AsyncProcessTermination("result-catalog is already created")

    def stac_builder(self, output_path=None, filename=None,
                     output_type=None, extra_values=None,):

        if output_type == "raster":
            bbox, geom = self._get_bbox_and_geometry(output_path)
            item = pystac.Item(id=f"STAC-result-{filename}",
                               geometry=geom,
                               bbox=bbox,
                               datetime=datetime.utcnow(),
                               properties=self._stac_metadata(extra_values))
            # Read catalog from REDIS
            catalog_dict = redis_actinia_interface.read("result-catalog")

            # Create Catalog Object
            catalog = pystac.read_dict(catalog_dict)

            # Add item to Catalog
            catalog.add_item(item)

            # Update redis catalog
            self._update_catalog_redis(catalog)

    def _stac_metadata(self, properties):

        print("here stand the metadata")

    def _get_bbox_and_geometry(self, raster_path):
        with rasterio.open(raster_path) as raster:
            bounds = raster.bounds
            bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
            geom = Polygon([
                [bounds.left, bounds.bottom],
                [bounds.left, bounds.top],
                [bounds.right, bounds.top],
                [bounds.right, bounds.bottom]
            ])

            return (bbox, mapping(geom))

    def _update_catalog_redis(catalog):

        new_catalog = catalog.to_dict()
        redis_actinia_interface.update("result-catalog", new_catalog)
