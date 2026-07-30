#!flask/bin/python
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

"""
Actinia core Endpoint definitions
"""

import traceback
import sys
from pprint import pprint
from flask_restful import Resource

from actinia_core.core.common.app import flask_api
from actinia_core.core.common.config import global_config
from actinia_core.core.logging_interface import log
from actinia_core.rest.project_management import (
    ListProjectsResource,
    ProjectManagementResourceAdminUser,
    ProjectManagementResourceUser,
)
from actinia_core.rest.mapsets import AllMapsetsListingResourceAdmin
from actinia_core.rest.mapset_management import (
    ListMapsetsResource,
    MapsetManagementResourceUser,
)
from actinia_core.rest.mapset_management import (
    MapsetLockManagementResource,
    MapsetManagementResourceAdmin,
)
from actinia_core.rest.ephemeral_processing import AsyncEphemeralResource
from actinia_core.rest.ephemeral_processing_with_export import (
    AsyncEphemeralExportResource,
)
from actinia_core.rest.ephemeral_processing_with_export import (
    AsyncEphemeralExportS3Resource,
)
from actinia_core.rest.ephemeral_processing_with_export import (
    AsyncEphemeralExportGCSResource,
)
from actinia_core.rest.persistent_mapset_merger import (
    AsyncPersistentMapsetMergerResource,
)
from actinia_core.rest.raster_export import (
    AsyncEphemeralRasterLayerRegionExporterResource,
)
from actinia_core.rest.raster_export import (
    AsyncEphemeralRasterLayerExporterResource,
)
from actinia_core.rest.persistent_processing import AsyncPersistentResource
from actinia_core.rest.ephemeral_custom_processing import (
    AsyncEphemeralCustomResource,
)
from actinia_core.rest.process_validation import AsyncProcessValidationResource
from actinia_core.rest.process_validation import SyncProcessValidationResource
from actinia_core.rest.user_management import (
    UserListResource,
    UserManagementResource,
)
from actinia_core.rest.api_log_management import APILogResource
from actinia_core.rest.user_api_key import (
    TokenCreationResource,
    APIKeyCreationResource,
)
from actinia_core.rest.resource_management import (
    ResourceManager,
    ResourcesManager,
    ResourceIterationManager,
)
from actinia_core.rest.resource_streamer import RequestStreamerResource
from actinia_core.rest.download_cache_management import (
    SyncDownloadCacheResource,
)
from actinia_core.rest.resource_storage_management import (
    SyncResourceStorageResource,
)
from actinia_core.rest.process_chain_monitoring import (
    MaxMapsetSizeResource,
    MapsetSizeResource,
    MapsetSizeRenderResource,
    MapsetSizeDiffResource,
    MapsetSizeDiffRenderResource,
)

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = "Copyright 2016-2024, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def get_endpoint_class_name(
    endpoint_class: Resource,
    projects_url_part: str = "projects",
) -> str:
    """Create the name for the given endpoint class."""
    return endpoint_class.__name__.lower()


def create_project_endpoints():
    """Function to add resources with "project" inside the endpoint url."""
    project_mapsets_url = "/projects/<string:project_name>/mapsets/"
    location_mapsets_url = "/locations/<string:project_name>/mapsets/"
    # Project management
    flask_api.add_resource(
        ListProjectsResource,
        "/projects",
        "/locations",
        endpoint=get_endpoint_class_name(ListProjectsResource),
    )
    flask_api.add_resource(
        ProjectManagementResourceUser,
        "/projects/<string:project_name>/info",
        "/locations/<string:project_name>/info",
        endpoint=get_endpoint_class_name(ProjectManagementResourceUser),
    )
    flask_api.add_resource(
        ProjectManagementResourceAdminUser,
        "/projects/<string:project_name>",
        "/locations/<string:project_name>",
        endpoint=get_endpoint_class_name(ProjectManagementResourceAdminUser),
    )

    # Mapset management
    flask_api.add_resource(
        ListMapsetsResource,
        "/projects/<string:project_name>/mapsets",
        "/locations/<string:project_name>/mapsets",
        endpoint=get_endpoint_class_name(ListMapsetsResource),
    )

    flask_api.add_resource(
        MapsetManagementResourceUser,
        project_mapsets_url + "<string:mapset_name>/info",
        location_mapsets_url + "<string:mapset_name>/info",
        endpoint=get_endpoint_class_name(MapsetManagementResourceUser),
    )

    flask_api.add_resource(
        MapsetManagementResourceAdmin,
        project_mapsets_url + "<string:mapset_name>",
        location_mapsets_url + "<string:mapset_name>",
        endpoint=get_endpoint_class_name(MapsetManagementResourceAdmin),
    )

    flask_api.add_resource(
        MapsetLockManagementResource,
        project_mapsets_url + "<string:mapset_name>/lock",
        location_mapsets_url + "<string:mapset_name>/lock",
        endpoint=get_endpoint_class_name(MapsetLockManagementResource),
    )

    # Validation
    flask_api.add_resource(
        AsyncProcessValidationResource,
        "/projects/<string:project_name>/" "process_chain_validation_async",
        "/locations/<string:project_name>/" "process_chain_validation_async",
        endpoint=get_endpoint_class_name(AsyncProcessValidationResource),
    )

    flask_api.add_resource(
        SyncProcessValidationResource,
        "/projects/<string:project_name>/" "process_chain_validation_sync",
        "/locations/<string:project_name>/" "process_chain_validation_sync",
        endpoint=get_endpoint_class_name(SyncProcessValidationResource),
    )

    # Async processing
    flask_api.add_resource(
        AsyncEphemeralResource,
        "/projects/<string:project_name>/processing_async",
        "/locations/<string:project_name>/processing_async",
        endpoint=get_endpoint_class_name(AsyncEphemeralResource),
    )
    flask_api.add_resource(
        AsyncEphemeralExportResource,
        "/projects/<string:project_name>/processing_async_export",
        "/locations/<string:project_name>/processing_async_export",
        endpoint=get_endpoint_class_name(AsyncEphemeralExportResource),
    )

    flask_api.add_resource(
        AsyncEphemeralExportS3Resource,
        "/projects/<string:project_name>/" "processing_async_export_s3",
        "/locations/<string:project_name>/" "processing_async_export_s3",
        endpoint=get_endpoint_class_name(AsyncEphemeralExportS3Resource),
    )
    flask_api.add_resource(
        AsyncEphemeralExportGCSResource,
        "/projects/<string:project_name>/" "processing_async_export_gcs",
        "/locations/<string:project_name>/" "processing_async_export_gcs",
        endpoint=get_endpoint_class_name(AsyncEphemeralExportGCSResource),
    )

    flask_api.add_resource(
        AsyncPersistentResource,
        project_mapsets_url + "<string:mapset_name>/processing_async",
        location_mapsets_url + "<string:mapset_name>/processing_async",
        endpoint=get_endpoint_class_name(AsyncPersistentResource),
    )
    flask_api.add_resource(
        AsyncPersistentMapsetMergerResource,
        project_mapsets_url + "<string:mapset_name>/merging_async",
        location_mapsets_url + "<string:mapset_name>/merging_async",
        endpoint=get_endpoint_class_name(AsyncPersistentMapsetMergerResource),
    )

    flask_api.add_resource(
        AsyncEphemeralRasterLayerExporterResource,
        project_mapsets_url + "<string:mapset_name>/raster_layers/"
        "<string:raster_name>/geotiff_async",
        location_mapsets_url
        + "<string:mapset_name>/raster_layers/<string:raster_name>/"
        "geotiff_async",
        endpoint=get_endpoint_class_name(
            AsyncEphemeralRasterLayerExporterResource,
        ),
    )
    flask_api.add_resource(
        AsyncEphemeralRasterLayerRegionExporterResource,
        project_mapsets_url + "<string:mapset_name>/raster_layers/"
        "<string:raster_name>/geotiff_async_orig",
        location_mapsets_url
        + "<string:mapset_name>/raster_layers/<string:raster_name>/"
        "geotiff_async_orig",
        endpoint=get_endpoint_class_name(
            AsyncEphemeralRasterLayerRegionExporterResource
        ),
    )


def create_core_endpoints():

    # Endpoints for project/location, mapset, raster, STRDS, vector management
    # and processing including validation
    create_project_endpoints()
    resource_url = "/resources/<string:user_id>/<string:resource_id>"
    # Async processing
    flask_api.add_resource(
        AsyncEphemeralCustomResource, "/custom_process/<string:executable>"
    )

    # all mapsets across all projects listing
    flask_api.add_resource(AllMapsetsListingResourceAdmin, "/mapsets")

    # User management
    flask_api.add_resource(UserListResource, "/users")
    flask_api.add_resource(UserManagementResource, "/users/<string:user_id>")
    flask_api.add_resource(
        TokenCreationResource,
        "/token",
    )
    flask_api.add_resource(
        APIKeyCreationResource,
        "/api_key",
    )
    flask_api.add_resource(APILogResource, "/api_log/<string:user_id>")

    # Resource management
    """
    The endpoint '/resources/<string:user_id>/<string:resource_id>' has two
    different answers depending on the resource_id. If the resoucre_id starts
    with 'resoucre-id' the latest iteration of the resoucre is given back.
    If the resocue_id is only the id then all iterations of the resource are
    given in the response.
    """
    flask_api.add_resource(ResourceManager, resource_url)
    flask_api.add_resource(ResourcesManager, "/resources/<string:user_id>")
    flask_api.add_resource(
        ResourceIterationManager,
        resource_url + "/<int:iteration>",
    )
    flask_api.add_resource(
        RequestStreamerResource,
        resource_url + "/<string:file_name>",
    )

    # Download and resource management
    flask_api.add_resource(SyncDownloadCacheResource, "/download_cache")
    flask_api.add_resource(SyncResourceStorageResource, "/resource_storage")

    # Endpoints for monitoring a process chain
    flask_api.add_resource(
        MapsetSizeResource,
        resource_url + "/mapsetsizes",
    )
    flask_api.add_resource(
        MaxMapsetSizeResource,
        resource_url + "/mapsetsizes/max",
    )
    flask_api.add_resource(
        MapsetSizeRenderResource,
        resource_url + "/mapsetsizes/render",
    )
    flask_api.add_resource(
        MapsetSizeDiffResource,
        resource_url + "/mapsetsizes/diffs",
    )
    flask_api.add_resource(
        MapsetSizeDiffRenderResource,
        resource_url + "/mapsetsizes/diffs/render",
    )


def check_import_plugins():
    import_str = (
        "from {}.endpoints import create_endpoints as create_plugin_endpoints"
        "\ncreate_plugin_endpoints(flask_api=flask_api)\n"
    )
    for plugin in global_config.PLUGINS:
        import_run_str = import_str.format(plugin)
        log.info("Loading plugin %s", plugin)
        exec(import_run_str)


def create_endpoints():
    create_core_endpoints()
    try:
        check_import_plugins()
    except Exception:
        e_type, e_value, e_tb = sys.exc_info()
        pprint(
            dict(
                message=str(e_value),
                traceback=str(traceback.format_tb(e_tb)),
                type=str(e_type),
            )
        )
