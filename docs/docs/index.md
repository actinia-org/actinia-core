Actinia - The GRASS GIS REST API
================================

**Actinia** is an open source REST API for scalable, distributed, high
performance processing of geographical data that uses GRASS GIS for
computational tasks.

It provides a REST API to process satellite images, time series of
satellite images, arbitrary raster data with geographical relations and
vector data.

The REST interface allows to access, manage and manipulate the GRASS GIS
database via HTTP GET, PUT, POST and DELETE requests and to process
raster, vector and time series data located in a persistent GRASS GIS
database. **Actinia** allows the processing of cloud based data, for
example all Landsat 4-8 scenes as well as all Sentinel-2 scenes in an
ephemeral databases. The computational results of ephemeral processing
are available via object storage as GeoTIFF files.

The full API documentation is available here: <https://actinia.mundialis.de/api_docs/>.
The source code is available here: <https://github.com/mundialis/actinia_core>.

* Introduction
    * What is REST?
    * Examples
* Actinia concepts
    * Actinia REST API documentation
    * User, user-roles and user-groups
    * The Actinia databases 
* Installation
* Actinia database access
    * Using curl for HTTP requests 
    * Access to locations and mapsets in the persistent database 
    * Access to raster layers in the persistent database 
    * Access to raster time-series in the persistent database 
* Time-series sampling 
    * Sampling of a STRDS with vector points 
* Landsat NDVI computation 
* Sentinel-2 NDVI computation 
* User defined processing  
    * The actinia process chain 
    * Sentinel-2A NDVI process chain 
* License 
* Authors
