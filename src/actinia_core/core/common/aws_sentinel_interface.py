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
Storage base class
"""
from urllib.request import urlopen
from flask.json import loads as json_loads
from flask.json import dumps as json_dumps

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def get_sentinel_date(product_id):
    """
    Returns year month and day of a (AWS) Sentinel scene from the Sentinel
    product-id.

    Args:
        product_ids (str): The Sentinel product id

    Returns:
        year (str): The recording year of the Sentinel product
        month (str): The recording month of the Sentinel product
        day (str): The recording day of the Sentinel product
    """
    if "S2A_OPER" in product_id:
        year = product_id[63:67]
        month = product_id[67:69]
        day = product_id[69:71]
    else:
        year = product_id[45:49]
        month = product_id[49:51]
        day = product_id[51:53]
    if month != "10":
        month = month.replace("0", "")
    if day not in ["10", "20", "30"]:
        day = day.replace("0", "")
    return year, month, day


class AWSSentinel2AInterface(object):
    """Query interface to the Sentinel2 and Landsat public geo-data
    available in the google cloud storage
    """

    def __init__(self, config):
        """
        Interface to the Sentinel2 and Landsat data in the google cloud storage

        Args:
            config: The configuration of Actinia Core
        """
        self.aws_sentinel_base_url = "http://sentinel-s2-l1c.s3.amazonaws.com"
        self.aws_sentinel_base_eu_central_url = (
            "http://sentinel-s2-l1c.s3-website.eu-central-1.amazonaws.com"
        )
        self.config = config

        self.sentinel_bands = [
            "B01",
            "B02",
            "B03",
            "B04",
            "B05",
            "B06",
            "B07",
            "B08",
            "B8A",
            "B09",
            "B10",
            "B11",
            "B12",
        ]

    def get_sentinel_urls(self, product_ids, bands=None):
        """Receive the download urls and time stamps for a list of Sentinel2
        product ids from AWS service

        1. Transform the Sentinel ID into the path of the productInfo.json url
           that is required to get the tile urls
        2. Parse the productInfo.json file and extract the tile urls
        3. Create the download links for each tile based on each band
        4. Include the tileInfo.json, xml and preview url's

        Args:
            product_ids: A list of sentinel product ids
            bands: A list of band names

        Returns:
            dict
            A dictionary that contains the time stamp, the tile names, the map
            names in GRASS, the aws cloud storage urls, the tile GeoJSON
            footprint and the XML metadata file path download url's.

        Example:

            [{'product_id': 'S2A_MSIL1C_20170202T090201_N0204_R007_T36TVT_'
                            '20170202T090155',
              'tiles':[{
                'B04': {
                    'file_name' : 'S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_'
                                  'R102_V20151207T003302_20151207T003302_tile_'
                                  '14_band_B04.jp2',
                    'map_name'  : 'S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_'
                                  'R102_V20151207T003302_20151207T003302_tile_'
                                  '14_band_B04',
                    'public_url': 'http://sentinel-s2-l1c.s3.amazonaws.com/'
                                  'tiles/57/V/XE/2015/12/7/0/B04.jp2'},
                'B08': {
                    'file_name' : 'S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_'
                                  'R102_V20151207T003302_20151207T003302_tile_'
                                  '14_band_B08.jp2',
                    'map_name'  : 'S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_'
                                  'R102_V20151207T003302_20151207T003302_tile_'
                                  '14_band_B08',
                    'public_url': 'http://sentinel-s2-l1c.s3.amazonaws.com/'
                                  'tiles/57/V/XE/2015/12/7/0/B08.jp2'},
                'info'      : 'http://sentinel-s2-l1c.s3.amazonaws.com/tiles/'
                              '57/V/XE/2015/12/7/0/tileInfo.json',
                'metadata'  : 'http://sentinel-s2-l1c.s3.amazonaws.com/tiles/'
                              '57/V/XE/2015/12/7/0/metadata.xml',
                'preview'   : 'http://sentinel-s2-l1c.s3.amazonaws.com/tiles/'
                              '57/V/XE/2015/12/7/0/preview.jpg',
                'timestamp' : '2015-12-07T00:33:02.634Z',
                'url'       : 'http://sentinel-s2-l1c.s3-website.eu-central-1.'
                              'amazonaws.com/#tiles/57/V/XE/2015/12/7/0/'}]}]

        """
        # Old format
        # products/2015/12/7/S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_
        # V20151207T003302_20151207T003302

        # https://sentinel-s2-l1c.s3.amazonaws.com/products/2015/10/1/S2A_OPER
        # _PRD_MSIL1C_PDMC_20161220T003744_R006_V20151001T071826_20151001T07
        # 1826/productInfo.json

        # New format
        # products/2017/10/31/S2A_MSIL1C_20171031T000721_N0206_R016_T01WCP_
        # 20171031T015145

        #           1         2         3         4         5         6
        # 7         8
        # 0123456789012345678901234567890123456789012345678901234567890
        # 12345678901234567890
        # S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_V20151207T003302
        # _20151207T003302

        #           1         2         3         4         5         6
        # 7         8
        # 0123456789012345678901234567890123456789012345678901234567890
        # 12345678901234567890
        # S2A_MSIL1C_20171031T000721_N0206_R016_T01WCP_20171031T015145

        # Assign default bands
        if bands is None:
            bands = ["B04", "B08"]

        try:
            for band in bands:
                if band not in self.sentinel_bands:
                    raise Exception("Unknown Sentinel-2 band name <%s>" % band)

            result = []

            for product_id in product_ids:
                product_id = product_id.replace(".SAFE", "")

                year, month, day = get_sentinel_date(product_id)

                # Get the product info JSON file
                json_url = (
                    "%(base)s/products/%(year)s/%(month)s/%(day)s/%(id)s/"
                    "productInfo.json"
                    % {
                        "base": self.aws_sentinel_base_url,
                        "year": year,
                        "month": month,
                        "day": day,
                        "id": product_id,
                    }
                )

                response = urlopen(json_url)
                product_info = response.read()

                try:
                    info = json_loads(product_info)
                except Exception:
                    raise Exception(
                        "Unable to read the productInfo.json file from URL: "
                        "%s. Error: %s" % (json_url, product_info)
                    )

                if info:
                    scene_entry = self._parse_scene_info(
                        bands, product_id, info
                    )
                    result.append(scene_entry)

            return result

        except Exception:
            raise

    def _parse_scene_info(self, bands, product_id, info):
        """Helpher method to parse the Sentinel-2 scene info:
        1. Parse the product info and extract the tile urls
        2. Create the download links for each tile based on each band
        3. Include the tileInfo.json, xml and preview url's

        Args:
            bands (list): A list of band names
            product_id (list): The Sentinel product id
            info (dict): A dictionary with the information of the Sentinel
                         product

        Returns:
            scene_entry (dict): A dictionary that contains the time stamp, the
                                tile names, the map names in GRASS, the aws
                                cloud storage urls, the tile GeoJSON footprint
                                and the XML metadata file path download url's.

        Example:

            {'product_id': 'S2A_MSIL1C_20170202T090201_N0204_R007_T36TVT_'
                            '20170202T090155',
              'tiles':[{
                'B04': {
                    'file_name' : 'S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_'
                                  'R102_V20151207T003302_20151207T003302_tile_'
                                  '14_band_B04.jp2',
                    'map_name'  : 'S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_'
                                  'R102_V20151207T003302_20151207T003302_tile_'
                                  '14_band_B04',
                    'public_url': 'http://sentinel-s2-l1c.s3.amazonaws.com/'
                                  'tiles/57/V/XE/2015/12/7/0/B04.jp2'},
                'B08': {
                    'file_name' : 'S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_'
                                  'R102_V20151207T003302_20151207T003302_tile_'
                                  '14_band_B08.jp2',
                    'map_name'  : 'S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_'
                                  'R102_V20151207T003302_20151207T003302_tile_'
                                  '14_band_B08',
                    'public_url': 'http://sentinel-s2-l1c.s3.amazonaws.com/'
                                  'tiles/57/V/XE/2015/12/7/0/B08.jp2'},
                'info'      : 'http://sentinel-s2-l1c.s3.amazonaws.com/tiles/'
                              '57/V/XE/2015/12/7/0/tileInfo.json',
                'metadata'  : 'http://sentinel-s2-l1c.s3.amazonaws.com/tiles/'
                              '57/V/XE/2015/12/7/0/metadata.xml',
                'preview'   : 'http://sentinel-s2-l1c.s3.amazonaws.com/tiles/'
                              '57/V/XE/2015/12/7/0/preview.jpg',
                'timestamp' : '2015-12-07T00:33:02.634Z',
                'url'       : 'http://sentinel-s2-l1c.s3-website.eu-central-1.'
                              'amazonaws.com/#tiles/57/V/XE/2015/12/7/0/'}]}

        """
        scene_entry = {}
        scene_entry["product_id"] = product_id
        scene_entry["tiles"] = []
        tile_num = 0
        for tile in info["tiles"]:
            tile_num += 1
            tile_info = {}
            tile_info["timestamp"] = info["timestamp"]

            # http://sentinel-s2-l1c.s3.amazonaws.com/tiles/58/V/CK/2015/12/7/
            # 0/metadata.xml,
            # http://sentinel-s2-l1c.s3.amazonaws.com/tiles/58/V/CK/2015/12/7/
            # 0/tileInfo.json,
            # http://sentinel-s2-l1c.s3.amazonaws.com/tiles/58/V/CK/2015/12/7/
            # 0/preview.jpg

            metadata_url = (
                f'{self.aws_sentinel_base_url}/{tile["path"]}/metadata.xml'
            )
            info_url = (
                f'{self.aws_sentinel_base_url}/{tile["path"]}/tileInfo.json'
            )
            preview_url = (
                f'{self.aws_sentinel_base_url}/{tile["path"]}/preview.jpg'
            )
            tile_info["url"] = (
                f'{self.aws_sentinel_base_eu_central_url}/#{tile["path"]}/'
            )

            tile_info["metadata"] = metadata_url
            tile_info["info"] = info_url
            tile_info["preview"] = preview_url
            public_url = f'{self.aws_sentinel_base_url}/{tile["path"]}'

            for band in bands:
                tile_name = f"{product_id}_tile_{tile_num}_band_{band}.jp2"
                map_name = f"{product_id}_tile_{tile_num}_band_{band}"
                tile_info[band] = {}
                tile_info[band]["file_name"] = tile_name
                tile_info[band]["map_name"] = map_name
                tile_info[band]["public_url"] = f"{public_url}/{band}.jp2"
            scene_entry["tiles"].append(tile_info)
        return scene_entry

    def get_sentinel_tile_footprint(self, tile_entry):
        """
        Downloads the tileInfo.json file and extracts/returns the tile geometry
        aka footprint

        Args:
            tile_entry:

        Returns:
            The geojson string that represents the tile footprint

        """
        # Get the tile info url that contains the tile footprint geojson
        response = urlopen(tile_entry["info"])
        tile_info = response.read()

        try:
            info = json_loads(tile_info)
        except Exception:
            raise Exception(
                "Unable to read the info json file from URL: %s. Error: %s"
                % (tile_entry["info"], tile_info)
            )
        return json_dumps(info["tileDataGeometry"])
