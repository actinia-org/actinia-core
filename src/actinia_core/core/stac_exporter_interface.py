# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2021-2022 mundialis GmbH & Co. KG
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

__license__ = "GPLv3"
__author__ = "Jorge Herrera"
__copyright__ = "Copyright 2021, mundialis GmbH & Co. KG"
__maintainer__ = "__mundialis__"
__email__ = "info@mundialis.de"

from datetime import datetime
from pickle import TRUE
import numpy as np
import pyproj
from pystac import Item, read_dict, Catalog, Asset
from pystac.extensions.projection import ProjectionItemExt
from shapely.ops import transform

import rasterio
from shapely.geometry import Polygon, mapping

from actinia_core.core.common.exceptions import AsyncProcessTermination
from actinia_core.core.common.app import API_VERSION
from actinia_core.version import G_VERSION

try:
    from actinia_stac_plugin.core.stac_redis_interface import redis_actinia_interface
    has_plugin = True
except Exception:
    has_plugin = False


class STACExporter:

    def stac_collection_initializer():
        """
        Initilize the STAC Catalog for the different outputs in actinia
        Catalog allows to have versability on the spatio-temporal spectrum,
        in addition the properties are independent for each item stored

        Code uses pystac as base for the creation of stac catalogs
        """
        redis_actinia_interface.connect()

        result_catalog_validation = redis_actinia_interface.exists("result-catalog")

        if result_catalog_validation is not TRUE:
            results = Catalog(id="result-catalog", description="STAC catalog")

            redis_actinia_interface.create(
                "result-catalog",
                results.to_dict(),
            )
        else:
            raise AsyncProcessTermination("result-catalog is already created")

    def stac_builder(self, output_path: str = None, filename: str = None,
                     output_type: str = None):
        """
        This function build the STAC ITEM and implement the following extension:
            - Projection
            - Raster
        Parameter:
            Input:
                - output_path = Path to the source
                - filename =  name of the source
                - output_type =  type of object (raster, vector)
        """
        if output_type == "raster":

            # Get parameters for STAC item
            extra_values = self._get_raster_parameters(output_path)

            # Checking if the input has WGS 84 CRS
            geom, bbox_raster = self._get_wgs84_parameters(extra_values)

            # Start building the Item
            item = Item(id=f"STAC-result-{filename}",
                        geometry=geom,
                        bbox=bbox_raster,
                        datetime=datetime.utcnow(),
                        properties={
                            "gds": extra_values["gds"]
                            }
                        )

            # Adding Asset and Raster Ext
            asset_ = Asset(
                href=output_path,
                title=filename
            )

            item.add_asset(
                key='source',
                asset=asset_
            )

            # Adding the Projection Extension
            proj_ext = ProjectionItemExt(item)
            proj_ext.apply(
                    epsg=extra_values["crs"],
                    geometry=extra_values["geometry"],
                    shape=extra_values["shape"],
                    bbox=extra_values["bbox"],
                    transform=extra_values["transform"]
            )

            # Adding the Raster Extension
            item = self._set_raster_extention(output_path, item)

            # Adding the Processing Extension
            item = self._set_processing_extention(item)

            # Read catalog from REDIS
            catalog_dict = redis_actinia_interface.read("result-catalog")

            # Create Catalog Object
            catalog = read_dict(catalog_dict)

            # Add item to Catalog
            catalog.add_item(item)

            # Update redis catalog
            self._update_catalog_redis(catalog)

        # TODO
        elif output_type == "vector":
            raise AsyncProcessTermination("Still under developments")

    def _get_raster_parameters(self, raster_path):
        with rasterio.open(raster_path) as raster:
            gds = np.asarray(raster.transform[:])
            bounds = raster.bounds
            bbox = [bounds.left, bounds.bottom, bounds.right, bounds.top]
            geom = Polygon([
                [bounds.left, bounds.bottom],
                [bounds.left, bounds.top],
                [bounds.right, bounds.top],
                [bounds.right, bounds.bottom]
            ])
            crs = raster.crs.to_epsg()

            extra_values = {
                "gds": gds[0],
                "crs": crs,
                "bbox": bbox,
                "geometry": mapping(geom),
                "transform": gds,
                "shape": raster.shape,
                "datetime": "2021-12-09T16:41:39.985257Z"
            }

            return extra_values

    def _get_wgs84_parameters(self, extra_values):
        if extra_values["crs"] != 4326:
            wgs84 = pyproj.CRS('EPSG:4326')
            raster_proj = pyproj.CRS('EPSG:' + str(extra_values["crs"]))
            project = pyproj.Transformer.from_crs(
                    raster_proj, wgs84, always_xy=True
                ).transform
            geojson = Polygon(
                    [tuple(i) for i in extra_values["geometry"]['coordinates'][0]]
                )
            geom = transform(project, geojson)
            geom = mapping(geom)

            def bbox(coord_list):
                box = []
                for i in (0, 1):
                    res = sorted(coord_list, key=lambda x: x[i])
                    box.append((res[0][i], res[-1][i]))
                bbox = [box[0][0], box[1][0], box[0][1], box[1][1]]
                return bbox

            bbox_raster = bbox(list(geom["coordinates"]))
        else:
            geom = extra_values["geometry"]
            bbox_raster = extra_values["bbox"]

        return geom, bbox_raster

    def _update_catalog_redis(catalog):

        new_catalog = catalog.to_dict()
        redis_actinia_interface.update("result-catalog", new_catalog)

    # TODO Discuss if it is more convenient to implement new classes and translate to
    #      the implementation to a new plugin or Addon where STAC extentions can be
    #      customized

    def _set_processing_extention(item):
        input_item = item.to_dict()

        input_item["processing:facility"] = f"Actinia Core {API_VERSION}",
        input_item["processing:level"] = "L4"
        input_item["processing:derived_from"] = "https://actinia.mundialis.de/"
        input_item["processing:software"] = f" GRASS {G_VERSION}"
        proc_schema = "https://stac-extensions.github.io/processing/v1.1.0/schema.json"

        input_item["stac_extensions"].append(proc_schema)

        proc_ext_item = read_dict(input_item)

        return proc_ext_item

    def _set_raster_extention(self, raster_path, item):
        with rasterio.open(raster_path) as raster:
            band = raster.read(1)
            pixelSizeX, pixelSizeY = raster.res

            nodata = np.count_nonzero(np.isnan(band))
            spatial_resolution = pixelSizeX
            data_type = band.dtype

            input_item = item.to_dict()
            asset = input_item["assets"]["source"]
            asset["raster:nodata"] = nodata
            asset["raster:spatial_resolution"] = spatial_resolution
            asset["raster:data_type"] = data_type
            proc_schema = "https://stac-extensions.github.io/raster/v1.1.0/schema.json"
            input_item["stac_extensions"].append(proc_schema)

            ras_ext_item = read_dict(input_item)

        return ras_ext_item
