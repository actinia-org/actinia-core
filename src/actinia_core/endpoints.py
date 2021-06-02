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
from actinia_core.core.common.app import flask_api
from actinia_core.core.common.config import global_config
from actinia_core.core.logging_interface import log
from actinia_core.rest.location_management import \
    ListLocationsResource, LocationManagementResourceUser
from actinia_core.rest.location_management import LocationManagementResourceAdmin
from actinia_core.rest.mapsets import AllMapsetsListingResourceAdmin
from actinia_core.rest.mapset_management import \
    ListMapsetsResource, MapsetManagementResourceUser
from actinia_core.rest.mapset_management import \
    MapsetLockManagementResource, MapsetManagementResourceAdmin
from actinia_core.rest.strds_management import \
    STRDSManagementResource, SyncSTRDSListerResource
from actinia_core.rest.strds_raster_management import STRDSRasterManagement
from actinia_core.rest.raster_layer import RasterLayerResource
from actinia_core.rest.map_layer_management import RasterLayersResource
from actinia_core.rest.map_layer_management import VectorLayersResource
from actinia_core.rest.vector_layer import VectorLayerResource
from actinia_core.rest.ephemeral_processing import AsyncEphemeralResource
from actinia_core.rest.ephemeral_processing_with_export import \
     AsyncEphemeralExportResource
from actinia_core.rest.ephemeral_processing_with_export import \
     AsyncEphemeralExportS3Resource
from actinia_core.rest.ephemeral_processing_with_export import \
     AsyncEphemeralExportGCSResource
from actinia_core.rest.persistent_mapset_merger import \
     AsyncPersistentMapsetMergerResource
from actinia_core.rest.raster_export import \
     AsyncEphemeralRasterLayerRegionExporterResource
from actinia_core.rest.raster_export import AsyncEphemeralRasterLayerExporterResource
from actinia_core.rest.persistent_processing import AsyncPersistentResource
from actinia_core.rest.ephemeral_custom_processing import AsyncEphemeralCustomResource
from actinia_core.rest.process_validation import AsyncProcessValidationResource
from actinia_core.rest.process_validation import SyncProcessValidationResource
from actinia_core.rest.user_management import \
     UserListResource, UserManagementResource
from actinia_core.rest.api_log_management import APILogResource
from actinia_core.rest.user_api_key import TokenCreationResource, APIKeyCreationResource
from actinia_core.rest.resource_management \
    import ResourceManager, ResourcesManager, ResourceIterationManager
from actinia_core.rest.resource_streamer import RequestStreamerResource
from actinia_core.rest.download_cache_management import SyncDownloadCacheResource
from actinia_core.rest.resource_storage_management import SyncResourceStorageResource
from actinia_core.rest.vector_renderer import SyncEphemeralVectorRendererResource
from actinia_core.rest.raster_legend import SyncEphemeralRasterLegendResource
from actinia_core.rest.raster_colors import SyncPersistentRasterColorsResource
from actinia_core.rest.raster_renderer import SyncEphemeralRasterRendererResource
from actinia_core.rest.raster_renderer import SyncEphemeralRasterRGBRendererResource
from actinia_core.rest.raster_renderer import SyncEphemeralRasterShapeRendererResource
from actinia_core.rest.strds_renderer import SyncEphemeralSTRDSRendererResource
from actinia_core.rest.process_chain_monitoring import \
    MaxMapsetSizeResource, MapsetSizeResource, MapsetSizeRenderResource, \
    MapsetSizeDiffResource, MapsetSizeDiffRenderResource


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


def create_core_endpoints():
    # Locationmanagement
    flask_api.add_resource(ListLocationsResource, '/locations')
    flask_api.add_resource(LocationManagementResourceUser,
                           '/locations/<string:location_name>/info')
    flask_api.add_resource(LocationManagementResourceAdmin,
                           '/locations/<string:location_name>')
    # Mapset management
    flask_api.add_resource(ListMapsetsResource,
                           '/locations/<string:location_name>/mapsets')
    flask_api.add_resource(
        MapsetManagementResourceUser,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/info')
    flask_api.add_resource(
        MapsetManagementResourceAdmin,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>')
    flask_api.add_resource(
        MapsetLockManagementResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/lock')

    # Raster management
    flask_api.add_resource(
        RasterLayersResource, '/locations/<string:location_name>/mapsets/'
                              '<string:mapset_name>/raster_layers')
    flask_api.add_resource(
        RasterLayerResource,
        '/locations/<string:location_name>/mapsets/'
        '<string:mapset_name>/raster_layers/<string:raster_name>')
    flask_api.add_resource(
        SyncEphemeralRasterLegendResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/'
        'raster_layers/<string:raster_name>/legend')
    flask_api.add_resource(
        SyncPersistentRasterColorsResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/'
        'raster_layers/<string:raster_name>/colors')
    flask_api.add_resource(
        SyncEphemeralRasterRendererResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/'
        'raster_layers/<string:raster_name>/render')
    flask_api.add_resource(
        SyncEphemeralRasterRGBRendererResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/render_rgb')
    flask_api.add_resource(
        SyncEphemeralRasterShapeRendererResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/render_shade')
    # STRDS management
    flask_api.add_resource(
        SyncSTRDSListerResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/strds')
    flask_api.add_resource(
        STRDSManagementResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/strds/'
        '<string:strds_name>')
    flask_api.add_resource(
        STRDSRasterManagement,
        '/locations/<string:location_name>/mapsets/'
        '<string:mapset_name>/strds/<string:strds_name>/raster_layers')
    # Vector management
    flask_api.add_resource(
        VectorLayersResource,
        '/locations/<string:location_name>/mapsets/'
        '<string:mapset_name>/vector_layers')
    flask_api.add_resource(
        VectorLayerResource,
        '/locations/<string:location_name>/mapsets/'
        '<string:mapset_name>/vector_layers/<string:vector_name>')
    flask_api.add_resource(
        SyncEphemeralVectorRendererResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/'
        'vector_layers/<string:vector_name>/render')
    flask_api.add_resource(
        SyncEphemeralSTRDSRendererResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/'
        'strds/<string:strds_name>/render')

    # Validation
    flask_api.add_resource(
        AsyncProcessValidationResource,
        '/locations/<string:location_name>/process_chain_validation_async')

    flask_api.add_resource(
        SyncProcessValidationResource,
        '/locations/<string:location_name>/process_chain_validation_sync')
    # Async processing
    flask_api.add_resource(AsyncEphemeralCustomResource,
                           '/custom_process/<string:executable>')
    flask_api.add_resource(AsyncEphemeralResource,
                           '/locations/<string:location_name>/processing_async')
    flask_api.add_resource(
        AsyncEphemeralExportResource,
        '/locations/<string:location_name>/processing_async_export')
    flask_api.add_resource(
        AsyncEphemeralExportS3Resource,
        '/locations/<string:location_name>/processing_async_export_s3')
    flask_api.add_resource(
        AsyncEphemeralExportGCSResource,
        '/locations/<string:location_name>/processing_async_export_gcs')
    flask_api.add_resource(
        AsyncPersistentResource,
        '/locations/<string:location_name>/mapsets/'
        '<string:mapset_name>/processing_async')
    flask_api.add_resource(
        AsyncPersistentMapsetMergerResource,
        '/locations/<string:location_name>/mapsets/'
        '<string:mapset_name>/merging_async')
    flask_api.add_resource(
        AsyncEphemeralRasterLayerExporterResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>/'
        'raster_layers/<string:raster_name>/geotiff_async')
    flask_api.add_resource(
        AsyncEphemeralRasterLayerRegionExporterResource,
        '/locations/<string:location_name>/mapsets/<string:mapset_name>'
        '/raster_layers/<string:raster_name>/geotiff_async_orig')

    # all mapsets across all locations listing
    flask_api.add_resource(
        AllMapsetsListingResourceAdmin, '/mapsets')

    # User management
    flask_api.add_resource(UserListResource, '/users')
    flask_api.add_resource(UserManagementResource, '/users/<string:user_id>')
    flask_api.add_resource(TokenCreationResource, '/token', )
    flask_api.add_resource(APIKeyCreationResource, '/api_key', )
    flask_api.add_resource(APILogResource, '/api_log/<string:user_id>')

    # Resource management
    """
    The endpoint '/resources/<string:user_id>/<string:resource_id>' has two
    different answers depending on the resource_id. If the resoucre_id starts
    with 'resoucre-id' the latest iteration of the resoucre is given back.
    If the resocue_id is only the id then all iterations of the resource are
    given in the response.
    """
    flask_api.add_resource(
        ResourceManager, '/resources/<string:user_id>/<string:resource_id>')
    flask_api.add_resource(ResourcesManager, '/resources/<string:user_id>')
    flask_api.add_resource(
        ResourceIterationManager,
        '/resources/<string:user_id>/<string:resource_id>/<int:iteration>')
    flask_api.add_resource(
        RequestStreamerResource,
        '/resources/<string:user_id>/<string:resource_id>/<string:file_name>')

    # Download and resource management
    flask_api.add_resource(SyncDownloadCacheResource, '/download_cache')
    flask_api.add_resource(SyncResourceStorageResource, '/resource_storage')

    # Endpoints for monitoring a process chain
    flask_api.add_resource(
        MapsetSizeResource,
        '/resources/<string:user_id>/<string:resource_id>/mapsetsizes')
    flask_api.add_resource(
        MaxMapsetSizeResource,
        '/resources/<string:user_id>/<string:resource_id>/mapsetsizes/max')
    flask_api.add_resource(
        MapsetSizeRenderResource,
        '/resources/<string:user_id>/<string:resource_id>/mapsetsizes/render')
    flask_api.add_resource(
        MapsetSizeDiffResource,
        '/resources/<string:user_id>/<string:resource_id>/mapsetsizes/diffs')
    flask_api.add_resource(
        MapsetSizeDiffRenderResource,
        '/resources/<string:user_id>/<string:resource_id>/mapsetsizes/diffs/render')


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
        pprint(dict(message=str(e_value), traceback=str(
            traceback.format_tb(e_tb)), type=str(e_type)))
