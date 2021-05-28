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

The full API documentation is available here:

 <https://actinia.mundialis.de/api_docs/>

::: {.toctree maxdepth="2"}
Introduction \<introduction\> Introduction \<actinia\_concepts\>
Installation \<installation\> Actinia database access
\<tutorial\_data\_access\> Time-series sampling
\<tutorial\_strds\_sampling\> Landsat NDVI computation
\<tutorial\_landsat\_ndvi\> Sentinel-2A NDVI computation
\<tutorial\_sentinel2a\_ndvi\> User defined processing
\<tutorial\_process\_chain\> License \<license\> Authors \<authors\>
:::
