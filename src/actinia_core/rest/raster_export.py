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

"""This module manages a raster layer resource as geotiff file that
will be created asynchronously.

The region settings of the mapset
or the raster layer region are used for export.
"""
from flask import jsonify, make_response
import pickle
from flask_restful_swagger_2 import swagger
from actinia_api.swagger2.actinia_core.apidocs import raster_export

from actinia_core.core.common.redis_interface import enqueue_job
from actinia_core.rest.base.endpoint_config import (
    check_endpoint,
    endpoint_decorator,
)
from actinia_core.rest.base.resource_base import ResourceBase
from actinia_core.processing.common.raster_export import start_job

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class AsyncEphemeralRasterLayerExporterResource(ResourceBase):
    """This class represents a raster layer resource as geotiff file that
    will be created asynchronously and streamed with the resource streamer.

    The region settings of the mapset is used for export.
    """

    def __init__(self):
        ResourceBase.__init__(self)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", raster_export.post_doc))
    def post(self, project_name, mapset_name, raster_name):
        """Export an existing raster map layer as GeoTiff."""
        return self._execute(project_name, mapset_name, raster_name, False)

    def _execute(
        self, project_name, mapset_name, raster_name, use_raster_region
    ):
        rdc = self.preprocess(
            has_json=False,
            project_name=project_name,
            mapset_name=mapset_name,
            map_name=raster_name,
        )
        if rdc:
            rdc.set_user_data(use_raster_region)
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


class AsyncEphemeralRasterLayerRegionExporterResource(
    AsyncEphemeralRasterLayerExporterResource
):
    """This class represents a raster layer resource as geotiff file that
    will be created asynchronously.

    The region settings of the raster
    layer is used for export. A temporary mapset is used to modify
    the region settings.
    """

    def __init__(self):
        ResourceBase.__init__(self)

    @endpoint_decorator()
    @swagger.doc(check_endpoint("post", raster_export.region_post_doc))
    def post(self, project_name, mapset_name, raster_name):
        """Export an existing raster map layer as GeoTiff using the raster
        map specific region.
        """
        return self._execute(project_name, mapset_name, raster_name, True)
