#!flask/bin/python
# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2024 Sören Gebbert and mundialis GmbH & Co. KG
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
from actinia_core.rest.strds_management import (
    STRDSManagementResource,
    SyncSTRDSListerResource,
)
from actinia_core.rest.strds_raster_management import STRDSRasterManagement
from actinia_core.rest.raster_layer import RasterLayerResource
from actinia_core.rest.map_layer_management import RasterLayersResource
from actinia_core.rest.map_layer_management import VectorLayersResource
from actinia_core.rest.vector_layer import VectorLayerResource
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
from actinia_core.rest.vector_renderer import (
    SyncEphemeralVectorRendererResource,
)
from actinia_core.rest.raster_legend import SyncEphemeralRasterLegendResource
from actinia_core.rest.raster_colors import SyncPersistentRasterColorsResource
from actinia_core.rest.raster_renderer import (
    SyncEphemeralRasterRendererResource,
)
from actinia_core.rest.raster_renderer import (
    SyncEphemeralRasterRGBRendererResource,
)
from actinia_core.rest.raster_renderer import (
    SyncEphemeralRasterShapeRendererResource,
)
from actinia_core.rest.strds_renderer import SyncEphemeralSTRDSRendererResource
from actinia_core.rest.process_chain_monitoring import (
    MaxMapsetSizeResource,
    MapsetSizeResource,
    MapsetSizeRenderResource,
    MapsetSizeDiffResource,
    MapsetSizeDiffRenderResource,
)


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def get_endpoint_class_name(endpoint_class, projects_url_part="projects"):
    endpoint_class_name = endpoint_class.__name__.lower()
    if projects_url_part != "projects":
        name = f"{endpoint_class_name}_{projects_url_part}"
    else:
        name = endpoint_class_name
    return name


def create_project_endpoints(projects_url_part="projects"):
    """Function to add resources with "project" inside the endpoint url.

    Args:
        projects_url_part (str): The name of the projects inside the endpoint
                                 URL; to add deprecated location endpoints set
                                 it to "locations"
    """
    # Project management
    flask_api.add_resource(
        ListProjectsResource,
        f"/{projects_url_part}",
        endpoint=get_endpoint_class_name(
            ListProjectsResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        ProjectManagementResourceUser,
        f"/{projects_url_part}/<string:project_name>/info",
        endpoint=get_endpoint_class_name(
            ProjectManagementResourceUser, projects_url_part
        ),
    )
    flask_api.add_resource(
        ProjectManagementResourceAdminUser,
        f"/{projects_url_part}/<string:project_name>",
        endpoint=get_endpoint_class_name(
            ProjectManagementResourceAdminUser, projects_url_part
        ),
    )

    # Mapset management
    flask_api.add_resource(
        ListMapsetsResource,
        f"/{projects_url_part}/<string:project_name>/mapsets",
        endpoint=get_endpoint_class_name(
            ListMapsetsResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        MapsetManagementResourceUser,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/info",
        endpoint=get_endpoint_class_name(
            MapsetManagementResourceUser, projects_url_part
        ),
    )
    flask_api.add_resource(
        MapsetManagementResourceAdmin,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>",
        endpoint=get_endpoint_class_name(
            MapsetManagementResourceAdmin, projects_url_part
        ),
    )
    flask_api.add_resource(
        MapsetLockManagementResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/lock",
        endpoint=get_endpoint_class_name(
            MapsetLockManagementResource, projects_url_part
        ),
    )

    # Raster management
    flask_api.add_resource(
        RasterLayersResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers",
        endpoint=get_endpoint_class_name(
            RasterLayersResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        RasterLayerResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers/<string:raster_name>",
        endpoint=get_endpoint_class_name(
            RasterLayerResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralRasterLegendResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers/<string:raster_name>/legend",
        endpoint=get_endpoint_class_name(
            SyncEphemeralRasterLegendResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncPersistentRasterColorsResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers/<string:raster_name>/colors",
        endpoint=get_endpoint_class_name(
            SyncPersistentRasterColorsResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralRasterRendererResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers/<string:raster_name>/render",
        endpoint=get_endpoint_class_name(
            SyncEphemeralRasterRendererResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralRasterRGBRendererResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/render_rgb",
        endpoint=get_endpoint_class_name(
            SyncEphemeralRasterRGBRendererResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralRasterShapeRendererResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/render_shade",
        endpoint=get_endpoint_class_name(
            SyncEphemeralRasterShapeRendererResource, projects_url_part
        ),
    )
    # STRDS management
    flask_api.add_resource(
        SyncSTRDSListerResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/strds",
        endpoint=get_endpoint_class_name(
            SyncSTRDSListerResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        STRDSManagementResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/strds/<string:strds_name>",
        endpoint=get_endpoint_class_name(
            STRDSManagementResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        STRDSRasterManagement,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/strds/<string:strds_name>/raster_layers",
        endpoint=get_endpoint_class_name(
            STRDSRasterManagement, projects_url_part
        ),
    )
    # Vector management
    flask_api.add_resource(
        VectorLayersResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/vector_layers",
        endpoint=get_endpoint_class_name(
            VectorLayersResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        VectorLayerResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/vector_layers/<string:vector_name>",
        endpoint=get_endpoint_class_name(
            VectorLayerResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralVectorRendererResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/vector_layers/<string:vector_name>/render",
        endpoint=get_endpoint_class_name(
            SyncEphemeralVectorRendererResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralSTRDSRendererResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/strds/<string:strds_name>/render",
        endpoint=get_endpoint_class_name(
            SyncEphemeralSTRDSRendererResource, projects_url_part
        ),
    )

    # Validation
    flask_api.add_resource(
        AsyncProcessValidationResource,
        f"/{projects_url_part}/<string:project_name>/"
        "process_chain_validation_async",
        endpoint=get_endpoint_class_name(
            AsyncProcessValidationResource, projects_url_part
        ),
    )

    flask_api.add_resource(
        SyncProcessValidationResource,
        f"/{projects_url_part}/<string:project_name>/"
        "process_chain_validation_sync",
        endpoint=get_endpoint_class_name(
            SyncProcessValidationResource, projects_url_part
        ),
    )

    # Async processing
    flask_api.add_resource(
        AsyncEphemeralResource,
        f"/{projects_url_part}/<string:project_name>/processing_async",
        endpoint=get_endpoint_class_name(
            AsyncEphemeralResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        AsyncEphemeralExportResource,
        f"/{projects_url_part}/<string:project_name>/processing_async_export",
        endpoint=get_endpoint_class_name(
            AsyncEphemeralExportResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        AsyncEphemeralExportS3Resource,
        f"/{projects_url_part}/<string:project_name>/"
        "processing_async_export_s3",
        endpoint=get_endpoint_class_name(
            AsyncEphemeralExportS3Resource, projects_url_part
        ),
    )
    flask_api.add_resource(
        AsyncEphemeralExportGCSResource,
        f"/{projects_url_part}/<string:project_name>/"
        "processing_async_export_gcs",
        endpoint=get_endpoint_class_name(
            AsyncEphemeralExportGCSResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        AsyncPersistentResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/processing_async",
        endpoint=get_endpoint_class_name(
            AsyncPersistentResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        AsyncPersistentMapsetMergerResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/merging_async",
        endpoint=get_endpoint_class_name(
            AsyncPersistentMapsetMergerResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        AsyncEphemeralRasterLayerExporterResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers/<string:raster_name>/"
        "geotiff_async",
        endpoint=get_endpoint_class_name(
            AsyncEphemeralRasterLayerExporterResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        AsyncEphemeralRasterLayerRegionExporterResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers/<string:raster_name>/"
        "geotiff_async_orig",
        endpoint=get_endpoint_class_name(
            AsyncEphemeralRasterLayerRegionExporterResource, projects_url_part
        ),
    )


def create_core_endpoints():

    # Endpoints for project/location, mapset, raster, STRDS, vector management
    # and processing including validation
    create_project_endpoints()
    create_project_endpoints(projects_url_part="locations")

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
    flask_api.add_resource(
        ResourceManager, "/resources/<string:user_id>/<string:resource_id>"
    )
    flask_api.add_resource(ResourcesManager, "/resources/<string:user_id>")
    flask_api.add_resource(
        ResourceIterationManager,
        "/resources/<string:user_id>/<string:resource_id>/<int:iteration>",
    )
    flask_api.add_resource(
        RequestStreamerResource,
        "/resources/<string:user_id>/<string:resource_id>/<string:file_name>",
    )

    # Download and resource management
    flask_api.add_resource(SyncDownloadCacheResource, "/download_cache")
    flask_api.add_resource(SyncResourceStorageResource, "/resource_storage")

    # Endpoints for monitoring a process chain
    flask_api.add_resource(
        MapsetSizeResource,
        "/resources/<string:user_id>/<string:resource_id>/mapsetsizes",
    )
    flask_api.add_resource(
        MaxMapsetSizeResource,
        "/resources/<string:user_id>/<string:resource_id>/mapsetsizes/max",
    )
    flask_api.add_resource(
        MapsetSizeRenderResource,
        "/resources/<string:user_id>/<string:resource_id>/mapsetsizes/render",
    )
    flask_api.add_resource(
        MapsetSizeDiffResource,
        "/resources/<string:user_id>/<string:resource_id>/mapsetsizes/diffs",
    )
    flask_api.add_resource(
        MapsetSizeDiffRenderResource,
        "/resources/<string:user_id>/<string:resource_id>/mapsetsizes/diffs/"
        "render",
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
