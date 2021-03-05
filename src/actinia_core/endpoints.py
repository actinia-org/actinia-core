#!flask/bin/python
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
Actinia core Endpoint definitions
"""
import traceback
import sys
from pprint import pprint
from .resources.common.app import flask_api
from .resources.common.config import global_config
from .resources.common.logging_interface import log
from .resources.location_management import ListLocationsResource, LocationManagementResourceUser
from .resources.location_management import LocationManagementResourceAdmin
from .resources.mapset_management import ListMapsetsResource, MapsetManagementResourceUser
from .resources.mapset_management import MapsetLockManagementResource, MapsetManagementResourceAdmin
from .resources.strds_management import STRDSManagementResource, SyncSTRDSListerResource
from .resources.strds_raster_management import STRDSRasterManagement
from .resources.raster_layer import RasterLayerResource
from .resources.map_layer_management import RasterLayersResource
from .resources.map_layer_management import VectorLayersResource
from .resources.vector_layer import VectorLayerResource
from .resources.ephemeral_processing import AsyncEphemeralResource
from .resources.ephemeral_processing_with_export import AsyncEphemeralExportResource
from .resources.ephemeral_processing_with_export import AsyncEphemeralExportS3Resource
from .resources.ephemeral_processing_with_export import AsyncEphemeralExportGCSResource
from .resources.persistent_mapset_merger import AsyncPersistentMapsetMergerResource
from .resources.raster_export import AsyncEphemeralRasterLayerRegionExporterResource
from .resources.raster_export import AsyncEphemeralRasterLayerExporterResource
from .resources.persistent_processing import AsyncPersistentResource
from .resources.ephemeral_custom_processing import AsyncEphemeralCustomResource
from .resources.process_validation import AsyncProcessValidationResource
from .resources.process_validation import SyncProcessValidationResource
from .resources.user_management import UserListResource, UserManagementResource
from .resources.api_log_management import APILogResource
from .resources.user_api_key import TokenCreationResource, APIKeyCreationResource
from .resources.resource_management import ResourceManager, ResourcesManager
from .resources.resource_streamer import RequestStreamerResource
from .resources.download_cache_management import SyncDownloadCacheResource
from .resources.resource_storage_management import SyncResourceStorageResource
from .resources.vector_renderer import SyncEphemeralVectorRendererResource
from .resources.raster_legend import SyncEphemeralRasterLegendResource
from .resources.raster_colors import SyncPersistentRasterColorsResource
from .resources.raster_renderer import SyncEphemeralRasterRendererResource
from .resources.raster_renderer import SyncEphemeralRasterRGBRendererResource
from .resources.raster_renderer import SyncEphemeralRasterShapeRendererResource
from .resources.strds_renderer import SyncEphemeralSTRDSRendererResource


__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


def create_core_endpoints():
    # Locationmanagement
    flask_api.add_resource(ListLocationsResource, '/locations')
    flask_api.add_resource(LocationManagementResourceUser, '/locations/<string:location_name>/info')
    flask_api.add_resource(LocationManagementResourceAdmin, '/locations/<string:location_name>')
    # Mapset management
    flask_api.add_resource(ListMapsetsResource, '/locations/<string:location_name>/mapsets')
    flask_api.add_resource(MapsetManagementResourceUser, '/locations/<string:location_name>/mapsets/<string:mapset_name>/info')
    flask_api.add_resource(MapsetManagementResourceAdmin, '/locations/<string:location_name>/mapsets/<string:mapset_name>')
    flask_api.add_resource(MapsetLockManagementResource, '/locations/<string:location_name>/mapsets/<string:mapset_name>/lock')
    # Raster management
    flask_api.add_resource(RasterLayersResource, '/locations/<string:location_name>/mapsets/'
                                                 '<string:mapset_name>/raster_layers')
    flask_api.add_resource(RasterLayerResource, '/locations/<string:location_name>/mapsets/'
                                                '<string:mapset_name>/raster_layers/<string:raster_name>')
    flask_api.add_resource(SyncEphemeralRasterLegendResource, '/locations/<string:location_name>/mapsets/'
                                                              '<string:mapset_name>/raster_layers/'
                                                              '<string:raster_name>/legend')
    flask_api.add_resource(SyncPersistentRasterColorsResource, '/locations/<string:location_name>/mapsets/'
                                                               '<string:mapset_name>/raster_layers/'
                                                               '<string:raster_name>/colors')
    flask_api.add_resource(SyncEphemeralRasterRendererResource, '/locations/<string:location_name>/mapsets/'
                                                                '<string:mapset_name>/raster_layers/'
                                                                '<string:raster_name>/render')
    flask_api.add_resource(SyncEphemeralRasterRGBRendererResource, '/locations/<string:location_name>/mapsets/'
                                                                   '<string:mapset_name>/render_rgb')
    flask_api.add_resource(SyncEphemeralRasterShapeRendererResource, '/locations/<string:location_name>/mapsets/'
                                                                     '<string:mapset_name>/render_shade')
    # STRDS management
    flask_api.add_resource(SyncSTRDSListerResource, '/locations/<string:location_name>/mapsets/'
                           '<string:mapset_name>/strds')
    flask_api.add_resource(STRDSManagementResource, '/locations/<string:location_name>/mapsets/<string:mapset_name>/strds/'
                           '<string:strds_name>')
    flask_api.add_resource(STRDSRasterManagement, '/locations/<string:location_name>/mapsets/'
                           '<string:mapset_name>/strds/<string:strds_name>/raster_layers')
    # Vector management
    flask_api.add_resource(VectorLayersResource, '/locations/<string:location_name>/mapsets/'
                                                 '<string:mapset_name>/vector_layers')
    flask_api.add_resource(VectorLayerResource, '/locations/<string:location_name>/mapsets/'
                                                '<string:mapset_name>/vector_layers/<string:vector_name>')
    flask_api.add_resource(SyncEphemeralVectorRendererResource, '/locations/<string:location_name>/mapsets/'
                                                                '<string:mapset_name>/vector_layers/'
                                                                '<string:vector_name>/render')
    flask_api.add_resource(SyncEphemeralSTRDSRendererResource, '/locations/<string:location_name>/mapsets/'
                                                               '<string:mapset_name>/strds/<string:strds_name>/render')

    # Validation
    flask_api.add_resource(AsyncProcessValidationResource,
                           '/locations/<string:location_name>/process_chain_validation_async')

    flask_api.add_resource(SyncProcessValidationResource,
                           '/locations/<string:location_name>/process_chain_validation_sync')
    # Async processing
    flask_api.add_resource(AsyncEphemeralCustomResource, '/custom_process/<string:executable>')
    flask_api.add_resource(AsyncEphemeralResource, '/locations/<string:location_name>/processing_async')
    flask_api.add_resource(AsyncEphemeralExportResource,
                           '/locations/<string:location_name>/processing_async_export')
    flask_api.add_resource(AsyncEphemeralExportS3Resource,
                           '/locations/<string:location_name>/processing_async_export_s3')
    flask_api.add_resource(AsyncEphemeralExportGCSResource,
                           '/locations/<string:location_name>/processing_async_export_gcs')
    flask_api.add_resource(AsyncPersistentResource, '/locations/<string:location_name>/mapsets/'
                                                    '<string:mapset_name>/processing_async')
    flask_api.add_resource(AsyncPersistentMapsetMergerResource, '/locations/<string:location_name>/mapsets/'
                           '<string:mapset_name>/merging_async')
    flask_api.add_resource(AsyncEphemeralRasterLayerExporterResource, '/locations/<string:location_name>/mapsets/'
                           '<string:mapset_name>/raster_layers/'
                           '<string:raster_name>/geotiff_async')
    flask_api.add_resource(AsyncEphemeralRasterLayerRegionExporterResource, '/locations/<string:location_name>'
                           '/mapsets/<string:mapset_name>'
                           '/raster_layers/<string:raster_name>'
                           '/geotiff_async_orig')
    # User management
    flask_api.add_resource(UserListResource, '/users')
    flask_api.add_resource(UserManagementResource, '/users/<string:user_id>')
    flask_api.add_resource(TokenCreationResource, '/token', )
    flask_api.add_resource(APIKeyCreationResource, '/api_key', )
    flask_api.add_resource(APILogResource, '/api_log/<string:user_id>')
    # Resource management
    flask_api.add_resource(ResourceManager, '/resources/<string:user_id>/<string:resource_id>')
    flask_api.add_resource(ResourcesManager, '/resources/<string:user_id>')
    flask_api.add_resource(RequestStreamerResource, '/resources/<string:user_id>/<string:resource_id>/'
                                                    '<string:file_name>')
    # Download and resource management
    flask_api.add_resource(SyncDownloadCacheResource, '/download_cache')
    flask_api.add_resource(SyncResourceStorageResource, '/resource_storage')


def check_import_plugins():
    import_str = """from {}.endpoints import create_endpoints as create_plugin_endpoints
create_plugin_endpoints(flask_api=flask_api)
    """
    for plugin in global_config.PLUGINS:
        import_run_str = import_str.format(plugin)
        log.info('Loading plugin %s', plugin)
        exec(import_run_str)


def create_endpoints():
    create_core_endpoints()
    try:
        check_import_plugins()
    except Exception:
        e_type, e_value, e_tb = sys.exc_info()
        pprint(dict(message=str(e_value), traceback=str(traceback.format_tb(e_tb)), type=str(e_type)))
