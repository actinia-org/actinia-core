# -*- coding: utf-8 -*-
"""This module manages a raster layer resource as geotiff file that
will be created asynchronously.

The region settings of the mapset
or the raster layer region are used for export.
"""
from flask import jsonify, make_response
import pickle
from flask_restful_swagger_2 import swagger, Schema
from .resource_base import ResourceBase
from .ephemeral_processing_with_export import EphemeralProcessingWithExport
from .common.redis_interface import enqueue_job
from .common.response_models import ProcessingResponseModel, ProcessingErrorResponseModel

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class AsyncEphemeralRasterLayerExporterResource(ResourceBase):
    """This class represents a raster layer resource as geotiff file that
    will be created asynchronously and streamed with the resource streamer.

    The region settings of the mapset is used for export.
    """
    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc({
        'tags': ['Raster Management'],
        'description': 'Export an existing raster map layer as GeoTiff. The link to the exported raster map '
                       'layer is located in the JSON response. The current region settings of the mapset'
                       'are used to export the raster layer. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The location name',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset that contains the required raster map layer',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            },
            {
                'name': 'raster_name',
                'description': 'The name of the raster map layer to export',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'elevation'
            }
        ],
        'consumes': ['application/json'],
        'produces': ["application/json"],
        'responses': {
            '200': {
                'description': 'The response including the URL to the raster map layer GeoTiff file',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why gathering raster map '
                               'layer information did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def post(self, location_name, mapset_name, raster_name):
        """Export an existing raster map layer as GeoTiff.
        """
        return self._execute(location_name, mapset_name, raster_name, False)

    def _execute(self, location_name, mapset_name, raster_name, use_raster_region):

        rdc = self.preprocess(has_json=False,
                              location_name=location_name,
                              mapset_name=mapset_name,
                              map_name=raster_name)
        if rdc:
            rdc.set_user_data(use_raster_region)
            enqueue_job(self.job_timeout, start_job, rdc)

        html_code, response_model = pickle.loads(self.response_data)
        return make_response(jsonify(response_model), html_code)


class AsyncEphemeralRasterLayerRegionExporterResource(AsyncEphemeralRasterLayerExporterResource):
    """This class represents a raster layer resource as geotiff file that
    will be created asynchronously.

    The region settings of the raster
    layer is used for export. A temporary mapset is used to modify
    the region settings.
    """
    def __init__(self):
        ResourceBase.__init__(self)

    @swagger.doc({
        'tags': ['Raster Management'],
        'description': 'Export an existing raster map layer as GeoTiff using the raster map layer specific region. '
                       'The link to the exported raster map '
                       'layer is located in the JSON response. Minimum required user role: user.',
        'parameters': [
            {
                'name': 'location_name',
                'description': 'The location name',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'nc_spm_08'
            },
            {
                'name': 'mapset_name',
                'description': 'The name of the mapset that contains the required raster map layer',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'PERMANENT'
            },
            {
                'name': 'raster_name',
                'description': 'The name of the raster map layer to export',
                'required': True,
                'in': 'path',
                'type': 'string',
                'default': 'elevation'
            }
        ],
        'consumes': ['application/json'],
        'produces': ["application/json"],
        'responses': {
            '200': {
                'description': 'The response including the URL to the raster map layer GeoTiff file',
                'schema': ProcessingResponseModel
            },
            '400': {
                'description': 'The error message and a detailed log why gathering raster map '
                               'layer information did not succeeded',
                'schema': ProcessingErrorResponseModel
            }
        }
    })
    def post(self, location_name, mapset_name, raster_name):
        """Export an existing raster map layer as GeoTiff using the raster map specific region.
        """
        return self._execute(location_name, mapset_name, raster_name, True)


def start_job(*args):
    processing = EphemeralRasterLayerExporter(*args)
    processing.run()


class EphemeralRasterLayerExporter(EphemeralProcessingWithExport):
    """Export a raster layer from a specific mapset as geotiff file.

    The region of tha raster layer can be used for export. In this case a
    temporary mapset will be created to modify the region settings safely.
    Hence, this works also in write protected mapsets.
    """
    def __init__(self, rdc):
        """Setup the variables of this class

        Args:
            rdc (ResourceDataContainer): The data container that contains all required variables for processing

        """

        EphemeralProcessingWithExport.__init__(self, rdc)

        self.raster_name = self.map_name
        self.use_raster_region = self.rdc.user_data

    def _execute(self):
        """Overwrite this function in subclasses

        - Create the resource directory
        - Initialize and create the temporal database and mapset
        - Export the raster layer
        - Cleanup

        """
        # Setup the user credentials and logger
        self._setup()

        # Create and check the resource directory
        self.storage_interface.setup()

        # Check if we have access and create the temporary storage
        self.required_mapsets.append(self.mapset_name)
        self._create_temporary_grass_environment(source_mapset_name="PERMANENT")

        export_dict = {"name":self.raster_name + "@" + self.mapset_name,
                       "export":{"format":"GTiff",
                                 "type":"raster"}}

        self.resource_export_list.append(export_dict)
        self._export_resources(self.use_raster_region)
