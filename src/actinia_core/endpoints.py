#!flask/bin/python
# -*- coding: utf-8 -*-
"""
Actinia core Endpoint definitions
"""

from actinia_core.resources.common.app import flask_api
from actinia_core.resources.location_management import ListLocationsResource, LocationManagementResourceUser
from actinia_core.resources.location_management import LocationManagementResourceAdmin
from actinia_core.resources.mapset_management import ListMapsetsResource, MapsetManagementResourceUser
from actinia_core.resources.mapset_management import MapsetLockManagementResource, MapsetManagementResourceAdmin
from actinia_core.resources.strds_management import STRDSManagementResource, ListSTRDSResource
from actinia_core.resources.strds_raster_management import STRDSRasterManagement
from actinia_core.resources.raster_layer import RasterLayerResource
from actinia_core.resources.map_layer_management import RasterLayersResource
from actinia_core.resources.map_layer_management import VectorLayersResource
from actinia_core.resources.vector_layer import VectorLayerResource
from actinia_core.resources.async_ephemeral_processing import AsyncEphemeralResource
from actinia_core.resources.async_ephemeral_processing_with_export import AsyncEphemeralExportResource
from actinia_core.resources.async_ephemeral_processing_with_export import AsyncEphemeralExportS3Resource
from actinia_core.resources.async_ephemeral_processing_with_export import AsyncEphemeralExportGCSResource
from actinia_core.resources.persistent_mapset_merger import AsyncPersistentMapsetMergingResource
from actinia_core.resources.raster_export import  AsyncEphemeralRasterLayerRegionExportResource
from actinia_core.resources.raster_export import AsyncEphemeralRasterLayerExportResource
from actinia_core.resources.async_persistent_processing import AsyncPersistentResource
from actinia_core.resources.async_ephemeral_custom_processing import AsyncEphemeralCustomResource
from actinia_core.resources.async_process_validation import AsyncProcessValidationResource
from actinia_core.resources.async_process_validation import SyncProcessValidationResource
from actinia_core.resources.user_management import UserListResource, UserManagementResource
from actinia_core.resources.api_log_management import APILogResource
from actinia_core.resources.user_api_key import TokenCreationResource, APIKeyCreationResource
from actinia_core.resources.resource_management import ResourceManager, ResourcesManager
from actinia_core.resources.resource_streamer import RequestStreamerResource
from actinia_core.resources.download_cache_management import SyncDownloadCacheResource
from actinia_core.resources.resource_storage_management import SyncResourceStorageResource

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


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
    # STRDS management
    flask_api.add_resource(ListSTRDSResource, '/locations/<string:location_name>/mapsets/'
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
    flask_api.add_resource(AsyncPersistentMapsetMergingResource, '/locations/<string:location_name>/mapsets/'
                                                                 '<string:mapset_name>/merging_async')
    flask_api.add_resource(AsyncEphemeralRasterLayerExportResource, '/locations/<string:location_name>/mapsets/'
                                                                    '<string:mapset_name>/raster_layers/'
                                                                    '<string:raster_name>/geotiff_async')
    flask_api.add_resource(AsyncEphemeralRasterLayerRegionExportResource, '/locations/<string:location_name>'
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
    flask_api.add_resource(RequestStreamerResource, '/resource/<string:user_id>/<string:resource_id>/'
                                                    '<string:file_name>')
    # Download and resource management
    flask_api.add_resource(SyncDownloadCacheResource, '/download_cache')
    flask_api.add_resource(SyncResourceStorageResource, '/resource_storage')


def create_endpoints():
    create_core_endpoints()



