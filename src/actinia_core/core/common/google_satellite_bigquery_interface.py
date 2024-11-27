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
import os
from google.cloud import bigquery
from google.cloud import storage
import xml.etree.ElementTree as eTree
from .exceptions import GoogleCloudAPIError
import dateutil.parser as dtparser


__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

GML_BODY = """<?xml version="1.0" encoding="utf-8" ?>
<ogr:FeatureCollection
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xmlns:ogr="http://ogr.maptools.org/"
     xmlns:gml="http://www.opengis.net/gml">
  <gml:featureMember>
    <ogr:footprint fid="footprint">
      <ogr:geometryProperty>
        <gml:Polygon srsName="EPSG:4326">
          <gml:outerBoundaryIs>
            <gml:LinearRing>
              <gml:coordinates>%s</gml:coordinates>
            </gml:LinearRing>
          </gml:outerBoundaryIs>
        </gml:Polygon>
      </ogr:geometryProperty>
    </ogr:footprint>
  </gml:featureMember>
</ogr:FeatureCollection>
"""


def extract_sensor_id_from_scene_id(scene_id):
    """Extract the sensor id from a Landsat scene id

    Args:
        scene_id (str): The landsat scene id

    Returns:
        (str)
        The sencor id

    """
    return "%s0%s" % (scene_id[0:2], scene_id[2:3])


def get_landsat_query(scene_id, spacecraft_id):
    """Extract the sensor id from a Landsat scene id

    Args:
        scene_id (str): The landsat scene id
        spacecraft_id (str): The landsat spacecraft id

    Returns:
        query (str): The landsat query
        scene_id_query (str): The scene id query
        spacecraft_id_query (str): the spacecraft id query
        has_where_statement (bool): If True scene_id and/or spacecraft_id is
                                    set and a WHERE part in the query is
                                    required

    """
    has_where_statement = False
    query = (
        "SELECT scene_id,sensing_time,north_lat,south_lat,east_lon,"
        "west_lon,cloud_cover,total_size FROM `bigquery-public-data"
        ".cloud_storage_geo_index.landsat_index` "
    )

    if scene_id:
        scene_id_query = "scene_id = '%s'" % scene_id
        has_where_statement = True

    if spacecraft_id:
        spacecraft_id_query = "spacecraft_id = '%s'" % spacecraft_id
        has_where_statement = True
    return query, scene_id_query, spacecraft_id_query, has_where_statement


def get_sentinel_query(scene_id):
    """Extract the sensor id from a Sentinel scene id

    Args:
        scene_id (str): The Sentinel scene id

    Returns:
        query (str): The Sentinel query
        scene_id_query (str): The scene id query
        has_where_statement (bool): If True scene_id is set and a WHERE part
                                    in the query is required

    """
    # Select specific columns from the sentinel table
    query = (
        "SELECT product_id,sensing_time,north_lat,south_lat,east_lon,"
        "west_lon,cloud_cover,total_size FROM `bigquery-public-data"
        ".cloud_storage_geo_index.sentinel_2_index` "
    )

    if scene_id:
        scene_id_query = "product_id = '%s'" % scene_id
        has_where_statement = True
    return query, scene_id_query, has_where_statement


def get_where_query(
    scene_id_query,
    spacecraft_id_query,
    temporal_query,
    spatial_query,
    cloud_cover_query,
):
    """Create where query to request the satellite archive

    Args:
        scene_id_query (str): The scene id query
        spacecraft_id_query (str): The spacecraft id query
        temporal_query (str): The temporal query
        spatial_query (str): The spatial query
        cloud_cover_query (str): The cloud cover query

    Returns:
        query (str): The WHERE part of the query
    """

    query = " WHERE "
    statement_count = 0

    if scene_id_query:
        query += f" ({scene_id_query}) "
        statement_count += 1

    if spacecraft_id_query:
        query += (
            f" AND ({spacecraft_id_query}) "
            if statement_count > 0
            else f" ({spacecraft_id_query}) "
        )
        statement_count += 1

    if temporal_query:
        query += (
            f" AND ({temporal_query}) "
            if statement_count > 0
            else f" ({temporal_query}) "
        )
        statement_count += 1

    if spatial_query:
        query += (
            f" AND ({spatial_query}) "
            if statement_count > 0
            else f" ({spatial_query}) "
        )
        statement_count += 1

    if cloud_cover_query:
        query += (
            f" AND ({cloud_cover_query}) "
            if statement_count > 0
            else f" ({cloud_cover_query}) "
        )
        statement_count += 1
    return query


class GoogleSatelliteBigQueryInterface(object):
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
        self.gcs_url = "https://storage.googleapis.com/"
        self.sentinel_xml_metadata_file = "MTD_MSIL1C.xml"
        self.config = config
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
            self.config.GOOGLE_APPLICATION_CREDENTIALS
        )
        os.environ["GOOGLE_CLOUD_PROJECT"] = self.config.GOOGLE_CLOUD_PROJECT

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

        self.landsat_scene_bands = {
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

        self.raster_suffixes = {
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

    def _start_clients(self):
        self.bigquery_client = bigquery.Client()
        self.storage_client = storage.Client()

    def query_landsat_archive(
        self,
        start_time,
        end_time,
        lat=None,
        lon=None,
        cloud_cover=None,
        scene_id=None,
        spacecraft_id=None,
    ):
        return self._query_satellite_archive(
            satellite="landsat",
            start_time=start_time,
            end_time=end_time,
            lat=lat,
            lon=lon,
            cloud_cover=cloud_cover,
            scene_id=scene_id,
            spacecraft_id=spacecraft_id,
        )

    def query_sentinel2_archive(
        self,
        start_time,
        end_time,
        lat=None,
        lon=None,
        cloud_cover=None,
        scene_id=None,
    ):
        return self._query_satellite_archive(
            satellite="sentinel2",
            start_time=start_time,
            end_time=end_time,
            lat=lat,
            lon=lon,
            cloud_cover=cloud_cover,
            scene_id=scene_id,
        )

    def _query_satellite_archive(
        self,
        satellite,
        start_time,
        end_time,
        lat=None,
        lon=None,
        cloud_cover=None,
        scene_id=None,
        spacecraft_id=None,
    ):
        """
        Query the landsat or sentinel archive by time interval and coordinates
        and return a list of scenes with metadata

        Args:
            satellite (str): The satellite that should be used for querying
                             landsat or sentinel2
            start_time (datetime.datetime): datetime object of the start time
                                            to query
            end_time (datetime.datetime): datetime object of the end time to
                                          query
            lat (float): Latitude coordinates that should intersect the landsat
                         scenes
            lon (float): Longitude coordinates that should intersect the
                         landsat scenes
            cloud_cover (float): The maximum cloud cover 0-100
            scene_id (str): The scene id to search for
            spacecraft_id (str): The spacecraft id of the landsat scene

        Returns:
            (list)
            A list of dict
            [
              {
                "cloud_cover": 99.0,
                "east_lon": 140.41507,
                "north_lat": -6.28158,
                "scene_id": "LE71010652001001EDC01",
                "sensing_time": "2001-01-01T00:41:06.1272135Z",
                "south_lat": -8.17417,
                "total_size": 74683859,
                "west_lon": 138.29205
              },
              {
                "cloud_cover": 73.0,
                "east_lon": 156.75294,
                "north_lat": 52.69982,
                "scene_id": "LE71010242001001EDC01",
                "sensing_time": "2001-01-01T00:24:46.2473502Z",
                "south_lat": 50.67277,
                "total_size": 161222513,
                "west_lon": 153.20544
              }
            ]
        """
        try:
            self._start_clients()
            scene_id_query = None
            spacecraft_id_query = None
            temporal_query = None
            spatial_query = None
            cloud_cover_query = None
            has_where_statement = False

            if satellite == "landsat":
                (
                    query,
                    scene_id_query,
                    spacecraft_id_query,
                    has_where_statement,
                ) = get_landsat_query(scene_id, spacecraft_id)
            else:
                (
                    query,
                    scene_id_query,
                    has_where_statement,
                ) = get_sentinel_query(scene_id)

            if start_time and end_time:
                start_time = dtparser.parse(start_time)
                end_time = dtparser.parse(end_time)
                temporal_query = (
                    "sensing_time >= '%(start)s' "
                    "AND sensing_time <= '%(end)s'"
                    % {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                    }
                )
                has_where_statement = True

            if lon and lat:
                spatial_query = (
                    "west_lon <= %(lon)f AND east_lon >= %(lon)f AND "
                    "north_lat >= %(lat)f AND south_lat <= %(lat)f"
                    % {"lon": float(lon), "lat": float(lat)}
                )
                has_where_statement = True

            if cloud_cover:
                cloud_cover_query = "cloud_cover <= %s" % str(cloud_cover)
                has_where_statement = True

            if has_where_statement is True:
                query += get_where_query(
                    scene_id_query,
                    spacecraft_id_query,
                    temporal_query,
                    spatial_query,
                    cloud_cover_query,
                )

            query_results = self.bigquery_client.query(query)
            result = []

            if query_results.result():
                for row in query_results.result():
                    (
                        scene_id,
                        sensing_time,
                        north_lat,
                        south_lat,
                        east_lon,
                        west_lon,
                        cloud_cover,
                        total_size,
                    ) = row
                    result.append(
                        dict(
                            scene_id=scene_id,
                            sensing_time=sensing_time,
                            north_lat=north_lat,
                            south_lat=south_lat,
                            east_lon=east_lon,
                            west_lon=west_lon,
                            cloud_cover=cloud_cover,
                            total_size=total_size,
                        )
                    )

            return result

        except Exception as e:
            raise GoogleCloudAPIError(
                "An error occurred while querying "
                "google archive. Error message: %s" % str(e)
            )

    def get_landsat_urls(self, scene_ids, bands=None):
        """
        Receive the Google Cloud Storage (GCS) download urls and time stamps
        for a list of Landsat scene ids with additional metadata.

        The download urls include the public address and the google cloud
        storage address. The resulting dictionary has as keys the scene ids
        that contain the file name, the tile name and the urls per band.

        Args:
            scene_ids: A list of scene ids that should be collected
            bands: The bands to create the download urls for

        Returns:
            (dict)
            A dictionary of scene entries

            Example:

            {u'LC80440342013106LGN01': {
                'B1': {'map': u'LC80440342013106LGN01_B1',
                        'gcs_url': u'gs://gcp-public-data-landsat/LC08/PRE/044'
                                    '/034/LC80440342013106LGN01/LC804403420131'
                                    '06LGN01_B1.TIF',
                        'public_url': u'https://storage.googleapis.com/gcp-'
                                       'public-data-landsat/LC08/PRE/044/034/'
                                       'LC80440342013106LGN01/LC80440342013106'
                                       'LGN01_B1.TIF',
                        'file': u'LC80440342013106LGN01_B1.TIF'},
                'MTL': {'map': u'LC80440342013106LGN01_MTL',
                        'gcs_url': u'gs://gcp-public-data-landsat/LC08/PRE/044'
                                    '/034/LC80440342013106LGN01/LC804403420131'
                                    '06LGN01_MTL.txt',
                        'public_url': u'https://storage.googleapis.com/gcp-'
                                       'public-data-landsat/LC08/PRE/044/034/'
                                       'LC80440342013106LGN01/LC80440342013106'
                                       'LGN01_MTL.txt',
                        'file': u'LC80440342013106LGN01_MTL.txt'},
                'timestamp': u'2013-04-16T18:47:53.5577434Z'},
             u'LC80440342016259LGN00': {
                'B1': {'map': u'LC80440342016259LGN00_B1',
                       'gcs_url': u'gs://gcp-public-data-landsat/LC08/PRE/044/'
                                   '034/LC80440342016259LGN00/LC80440342016259'
                                   'LGN00_B1.TIF',
                       'public_url': u'https://storage.googleapis.com/gcp-'
                                      'public-data-landsat/LC08/PRE/044/034/'
                                      'LC80440342016259LGN00/LC80440342016259'
                                      'LGN00_B1.TIF',
                       'file': u'LC80440342016259LGN00_B1.TIF'},
                'MTL': {'map': u'LC80440342016259LGN00_MTL',
                        'gcs_url': u'gs://gcp-public-data-landsat/LC08/PRE/044'
                                    '/034/LC80440342016259LGN00/LC804403420162'
                                    '59LGN00_MTL.txt',
                        'public_url': u'https://storage.googleapis.com/gcp-'
                                       'public-data-landsat/LC08/PRE/044/034/'
                                       'LC80440342016259LGN00/'
                                       'LC80440342016259LGN00_MTL.txt',
                        'file': u'LC80440342016259LGN00_MTL.txt'},
                'timestamp': u'2016-09-15T18:46:18.6867380Z'}}

        """

        # Google BigQuery landsat table SQL query
        # SELECT * FROM [bigquery-public-data:cloud_storage_geo_index.
        # landsat_index]
        #          WHERE sensing_time > '2000-01-01T00:00:00' LIMIT 1;
        #
        # [
        #   {
        #     "scene_id": "LE72210652016307CUB00",
        #     "product_id": "LE07_L1TP_221065_20161102_20161128_01_T1",
        #     "spacecraft_id": "LANDSAT_7",
        #     "sensor_id": "ETM",
        #     "date_acquired": "2016-11-02",
        #     "sensing_time": "2016-11-02T13:14:58.9749958Z",
        #     "collection_number": "01",
        #     "collection_category": "T1",
        #     "data_type": "L1TP",
        #     "wrs_path": "221",
        #     "wrs_row": "65",
        #     "cloud_cover": "1.0",
        #     "north_lat": "-6.28415",
        #     "south_lat": "-8.16646",
        #     "west_lon": "-47.15011",
        #     "east_lon": "-44.96096",
        #     "total_size": "235109281",
        #     "base_url": "gs://gcp-public-data-landsat/LE07/01/221/065/"
        #                 "LE07_L1TP_221065_20161102_20161128_01_T1"
        #   }
        # ]

        # Assign default bands
        if bands is None:
            bands = ["B1", "B2"]

        try:
            self._start_clients()

            for scene_id in scene_ids:
                sensor_id = extract_sensor_id_from_scene_id(scene_id)
                for band in bands:
                    if band not in self.landsat_scene_bands[sensor_id]:
                        raise Exception(
                            "Unknown landsat band name <%s>" % band
                        )

            # Select specific columns from the sentinel table
            query = (
                "SELECT scene_id,sensing_time,base_url FROM "
                "`bigquery-public-data.cloud_storage_geo_index.landsat_index` "
                'WHERE scene_id IN ("%s");' % '","'.join(scene_ids)
            )

            query_results = self.bigquery_client.query(query)
            result = {}

            if query_results.result():
                for row in query_results.result():
                    scene_id, sensing_time, base_url = row
                    public_url = self.gcs_url + base_url[5:]
                    sensor_id = extract_sensor_id_from_scene_id(scene_id)

                    result[scene_id] = {}
                    result[scene_id]["timestamp"] = sensing_time

                    for band in bands:
                        suffix = "TIF"
                        if band == "MTL":
                            suffix = "txt"

                        file_name = "%s_%s.%s" % (scene_id, band, suffix)
                        map_name = "%s_%s" % (scene_id, band)
                        if band != "MTL":
                            index = self.landsat_scene_bands[sensor_id].index(
                                band
                            )
                            raster_suffix = self.raster_suffixes[sensor_id][
                                index
                            ]
                            map_name = "%s%s" % (scene_id, raster_suffix)

                        result[scene_id][band] = {}
                        result[scene_id][band]["file"] = file_name
                        result[scene_id][band]["map"] = map_name
                        result[scene_id][band]["public_url"] = (
                            public_url + "/" + file_name
                        )
                        result[scene_id][band]["gcs_url"] = (
                            base_url + "/" + file_name
                        )

            return result

        except Exception as e:
            raise GoogleCloudAPIError(
                "An error occurred while fetching "
                "Landsat download URL's. Error message: %s" % str(e)
            )

    def get_sentinel_urls(self, product_ids, bands=None):
        """Receive the download urls and time stamps for a list of Sentinel2
        product ids from Google Big Query service

        The download urls include the public address and the google cloud
        storage address. The resulting dictionary has as keys the product ids
        that contain the file name, the tile name and the urls per band. In
        addition the time stamp, the GML footprint and the XML download path
        is included.

        Args:
            product_ids: A list of sentinel product ids
            bands: A list of band names

        Returns:
            dict
            A dictionary that contains the time stamp, the tile names, the map
            names in GRASS the goggle cloud storage urls, the public urls, the
            GML footprint and the XML file download path.

            Boundingbox = (min_x, max_y, max_x, min_y)

            Example:

            u'S2A_MSIL1C_20170301T225331_N0204_R115_T56DNG_20170301T225347': {
                'B04': {'file': u'S2A_MSIL1C_20170301T225331_N0204_R115_T56DNG'
                                 '_20170301T225347_B04',
                        'gcs_url': u'gs://gcp-public-data-sentinel-2/tiles/56/'
                                    'D/NG/S2A_MSIL1C_20170301T225331_N0204_'
                                    'R115_T56DNG_20170301T225347.SAFE/GRANULE/'
                                    'L1C_T56DNG_A008835_20170301T225347/'
                                    'IMG_DATA/T56DNG_20170301T225331_B04.jp2',
                        'public_url': u'https://storage.googleapis.com/gcp-'
                                       'public-data-sentinel-2/tiles/56/D/NG/'
                                       'S2A_MSIL1C_20170301T225331_N0204_R115_'
                                       'T56DNG_20170301T225347.SAFE/GRANULE/'
                                       'L1C_T56DNG_A008835_20170301T225347/'
                                       'IMG_DATA/T56DNG_20170301T225331_'
                                       'B04.jp2',
                        'tile': u'T56DNG_20170301T225331_B04.jp2'},
                'B08': {'file': u'S2A_MSIL1C_20170301T225331_N0204_R115_T56DNG'
                                 '_20170301T225347_B08',
                        'gcs_url': u'gs://gcp-public-data-sentinel-2/tiles/56/'
                                    'D/NG/S2A_MSIL1C_20170301T225331_N0204_'
                                    'R115_T56DNG_20170301T225347.SAFE/GRANULE/'
                                    'L1C_T56DNG_A008835_20170301T225347/IMG_'
                                    'DATA/T56DNG_20170301T225331_B08.jp2',
                        'public_url': u'https://storage.googleapis.com/gcp-'
                                       'public-data-sentinel-2/tiles/56/D/NG/'
                                       'S2A_MSIL1C_20170301T225331_N0204_R115_'
                                       'T56DNG_20170301T225347.SAFE/GRANULE/'
                                       'L1C_T56DNG_A008835_20170301T225347/'
                                       'IMG_DATA/T56DNG_20170301T225331_'
                                       'B08.jp2',
                        'tile': u'T56DNG_20170301T225331_B08.jp2'},
                'bbox': (-70.45384256042797,
                         153.19042365887816,
                         -70.30447316127372,
                         152.99946420488922),
                'gcs_xml_metadata_url': u'gs://gcp-public-data-sentinel-2/'
                                         'tiles/56/D/NG/S2A_MSIL1C_20170301T22'
                                         '5331_N0204_R115_T56DNG_20170301T2253'
                                         '47.SAFE/MTD_MSIL1C.xml',
                'gml_footprint': '<?xml version="1.0" encoding="utf-8" ?>\n'
                                 '<ogr:FeatureCollection\n'
                                 '     xmlns:xsi="http://www.w3.org/2001/'
                                 'XMLSchema-instance"\n'
                                 '     xmlns:ogr="http://ogr.maptools.org/"\n'
                                 '     xmlns:gml="http://www.opengis.net/gml">'
                                 '\n  <gml:featureMember>\n'
                                 '    <ogr:footprint fid="footprint">\n'
                                 '      <ogr:geometryProperty>'
                                 '<gml:Polygon srsName="EPSG:4326">'
                                 '<gml:outerBoundaryIs>'
                                 '<gml:LinearRing>'
                                 '<gml:coordinates>153.19042365887816,'
                                 '-70.30447316127372 153.08861867314772,'
                                 '-70.38450125221787 152.99946420488922,'
                                 '-70.45384256042797 152.99946824095414,'
                                 '-70.30601749291662 153.19042365887816,'
                                 '-70.30447316127372 153.19042365887816,'
                                 '-70.30447316127372</gml:coordinates>'
                                 '</gml:LinearRing></gml:outerBoundaryIs>'
                                 '</gml:Polygon></ogr:geometryProperty>\n'
                                 '    </ogr:footprint>\n'
                                 '  </gml:featureMember>\n'
                                 '</ogr:FeatureCollection>\n',
                'public_xml_metadata_url': u'https://storage.googleapis.com/'
                                            'gcp-public-data-sentinel-2/tiles/'
                                            '56/D/NG/S2A_MSIL1C_20170301T2253'
                                            '31_N0204_R115_T56DNG_20170301'
                                            'T225347.SAFE/MTD_MSIL1C.xml',
                'timestamp': u'2017-03-01T22:53:47.503000Z'}

        """

        # Google BigQuery landsat table SQL query
        # SELECT * FROM [bigquery-public-data:cloud_storage_geo_index.
        # sentinel_2_index]
        #  where product_id =
        #  "S2A_MSIL1C_20170208T092131_N0204_R093_T35TLF_20170208T092143"
        #
        # Result:
        # [
        #   {
        #     "granule_id": "L1C_T35TLF_A008527_20170208T092143",
        #     "product_id": "S2A_MSIL1C_20170208T092131_N0204_R093_T35TLF_"
        #                   "20170208T092143",
        #     "datatake_identifier": "GS2A_20170208T092131_008527_N02.04",
        #     "mgrs_tile": "35TLF",
        #     "sensing_time": "2017-02-08T09:21:43.890000Z",
        #     "geometric_quality_flag": "PASSED",
        #     "generation_time": "2017-02-08T09:21:43.000000Z",
        #     "north_lat": "41.5297704546",
        #     "south_lat": "41.1784693962",
        #     "west_lon": "24.6026969474",
        #     "east_lon": "24.7426671934",
        #     "base_url": "gs://gcp-public-data-sentinel-2/tiles/35/T/LF/S2A"
        #                 "_MSIL1C_20170208T092131_N0204_R093_T35TLF_"#
        #                 "20170208T092143.SAFE",
        #     "total_size": "30544232",
        #     "cloud_cover": "0.0"
        #   }
        # ]
        # Public link:
        # https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/35/
        # T/LF/S2A_MSIL1C_20170208T092131_N0204_R093_T35TLF_20170208T092143.
        # SAFE/GRANULE/L1C_T35TLF_A008527_20170208T092143/IMG_DATA/T35TLF_
        # 20170208T092131_B01.jp2

        # Assign default bands
        if bands is None:
            bands = ["B04", "B08"]

        try:
            self._start_clients()

            for band in bands:
                if band not in self.sentinel_bands:
                    raise Exception("Unknown Sentinel-2 band name <%s>" % band)

            # Select specific columns from the sentinel table
            query = (
                "SELECT granule_id,product_id,sensing_Time,datatake_identifier"
                ",base_url FROM `bigquery-public-data.cloud_storage_geo_index"
                ".sentinel_2_index` "
                'WHERE product_id IN ("%s");' % '","'.join(product_ids)
            )

            rows = list(self.bigquery_client.query(query))  # API request

            result = {}

            if rows:
                for row in rows:
                    (
                        granule_id,
                        product_id,
                        sensing_time,
                        datatake_identifier,
                        base_url,
                    ) = row
                    tile_base_name = (
                        granule_id[4:10] + datatake_identifier[4:20]
                    )
                    gcs_url = (
                        base_url + "/GRANULE/" + granule_id + "/IMG_DATA/"
                    )
                    public_url = (
                        self.gcs_url
                        + base_url[5:]
                        + "/GRANULE/"
                        + granule_id
                        + "/IMG_DATA/"
                    )

                    result[product_id] = {}
                    result[product_id]["timestamp"] = sensing_time
                    result[product_id]["public_xml_metadata_url"] = (
                        self.gcs_url
                        + base_url[5:]
                        + "/"
                        + self.sentinel_xml_metadata_file
                    )
                    result[product_id]["gcs_xml_metadata_url"] = (
                        base_url + "/" + self.sentinel_xml_metadata_file
                    )

                    # Generate the GML file from the sentinel product footprint
                    # The whole XML content is returned as well
                    (
                        gml,
                        _,
                        bbox,
                    ) = self._generate_sentinel2_footprint(base_url=base_url)
                    result[product_id]["gml_footprint"] = gml
                    result[product_id]["bbox"] = bbox
                    # The xml content is currently not needed
                    # result[product_id]["xml_metadata"] = xml_metadata

                    for band in bands:
                        tile_name = "%s_%s.jp2" % (tile_base_name, band)
                        map_name = "%s_%s" % (product_id, band)

                        result[product_id][band] = {}
                        result[product_id][band]["tile"] = tile_name
                        result[product_id][band]["file"] = map_name
                        result[product_id][band]["public_url"] = (
                            public_url + tile_name
                        )
                        result[product_id][band]["gcs_url"] = (
                            gcs_url + tile_name
                        )

            return result

        except Exception as e:
            raise GoogleCloudAPIError(
                "An error occurred while fetching "
                "Sentinel-2 download URL's. Error message: %s" % str(e)
            )

    def _generate_sentinel2_footprint(self, base_url):
        """Download the sentinel XML metadata and parse it for the footprint

        Args:
            base_url: The google cloud storage base url of the required
                      product_id

        Returns: a tuple of strings
            (str, str)
            The first string is the footprint as GML code,
            The second string the the metadata XML document

        """

        # Download the XML file from the google cloud storage using the cloud
        # API
        bucket = self.storage_client.get_bucket("gcp-public-data-sentinel-2")
        blob = bucket.blob(
            base_url.replace("gs://gcp-public-data-sentinel-2/", "")
            + "/"
            + self.sentinel_xml_metadata_file
        )

        xml_content = blob.download_as_string()

        # Find the coordinates in the XML string
        root = eTree.fromstring(xml_content)
        # The namespace will hopefully not change
        geo_info = root.find(
            "{https://psd-14.sentinel2.eo.esa.int/PSD/"
            "User_Product_Level-1C.xsd}Geometric_Info"
        )
        global_footprint = (
            geo_info.find("Product_Footprint")
            .find("Product_Footprint")
            .find("Global_Footprint")
        )
        coordinates = global_footprint.find("EXT_POS_LIST").text

        # Extract the coordinates from the text and convert it into lat/lon
        # tuples
        coord_list = coordinates.split()
        gml_coord_list = []

        min_x = 10000000
        max_x = -10000000
        min_y = 10000000
        max_y = -10000000

        i = 0
        while i < len(coord_list):
            y = coord_list[i]
            if float(y) > max_y:
                max_y = float(y)
            if float(y) < min_y:
                min_y = float(y)
            i += 1
            x = coord_list[i]
            if float(x) > max_x:
                max_x = float(x)
            if float(x) < min_x:
                min_x = float(x)
            i += 1
            gml_coord_list.append("%s,%s" % (x, y))

        return (
            GML_BODY % " ".join(gml_coord_list),
            xml_content,
            (min_x, max_y, max_x, min_y),
        )
