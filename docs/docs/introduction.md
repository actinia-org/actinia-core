Introduction
============

Actinia is a REST service to process geographical data that can be
managed by the GRASS GIS software system. The software is designed to
expose a GRASS GIS database and many GRASS GIS[^1] processing tools as
REST service[^2]. Hence, access to GRASS resources like raster maps,
space-time raster datasets, processing and analysis modules are
available via URL. In addition Actinia allows the processing of cloud
based data, for example all Landsat 4-8 scenes as well as all
Sentinel-2A scenes in an ephemeral database. The computational results
of ephemeral processing are available via object storage as GeoTIFF
files.

The actinia service consists of the *actinia core* that provides the
basic but sophisticated processing service and *actinia plugins* that
provide problem specific services like Sentinel-2 and Landsat NDVI
computation, spatio-temporal statistical analysis and many more.

To use actinia the user must have an understanding of the GRASS GIS
concept[^3] of location, mapsets, raster maps, space-time datasets and
modules. The URLs that provide access to the GRASS database reflect
these concepts. Hence, the location, the mapset and the required raster map
are part of the URL to access the service.

What is REST?
-------------

The Representational state transfer (REST)[^4] is an architectural style
based on HTTP[^5] that uses GET[^6], DELETE[^7], POST[^8] and PUT[^9]
methods to manipulate and receive resources with stateless operations.

While GET requests can be send easily from a browser, POST, PUT or
DELETE request can not. To access the full potential of actinia you will
need a HTTP client, that talks all HTTP communication methods.

Examples
--------

**Data management**

List all locations that are available in the actinia persistent database:

```bash
 curl -X GET "https://actinia.mundialis.de/api/v1/locations" -H "authorization: Basic ..."
```

List all mapsets in the location latlong\_wgs84:

```bash
 curl -X GET "https://actinia.mundialis.de/api/v1/locations/latlong_wgs84/mapsets" -H "authorization: Basic ..."
```

List all space-time raster datasets (STRDS) in location
latlong\_wgs84 and mapset Sentinel\_timeseries:

```bash
 curl -X GET "https://actinia.mundialis.de/api/v1/locations/latlong_wgs84/mapsets/Sentinel_timeseries/strds" -H "authorization: Basic ..."
```

List all raster map layers of the STRDS:

```bash
curl -X GET "https://actinia.mundialis.de/api/v1/locations/latlong_wgs84/mapsets/Sentinel_timeseries/strds/S2A_B04/raster_layers" -H "authorization: Basic ..."
```

**Landsat and Sentinel-2A NDVI computation**

This API call will compute the NDVI of the top of athmosphere (TOAR)
corrected Landsat4 scene LC80440342016259LGN00:

```bash
curl -X POST "https://actinia.mundialis.de/api/v1/landsat_process/LC80440342016259LGN00/TOAR/NDVI" -H "authorization: Basic ..."
```

NDVI computation of Sentinel-2A scene
S2A\_MSIL1C\_20170212T104141\_N0204\_R008\_T31TGJ\_20170212T104138:

```bash
curl -X POST "https://actinia.mundialis.de/api/v1/sentinel2_process/ndvi/S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138" -H "authorization: Basic ..."
```

The results of the asynchronous computations are available as GeoTIFF
file in a cloud storage for download.

**Footnotes**

[^1]: <https://grass.osgeo.org/>

[^2]: <https://en.wikipedia.org/wiki/Representational_State_Transfer>

[^3]: <https://grass.osgeo.org/grass-stable/manuals/helptext.html#2.-background:-grass-gis-location-structure>

[^4]: <https://en.wikipedia.org/wiki/Representational_State_Transfer>

[^5]: <https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol>

[^6]: <https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods>

[^7]: <https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods>

[^8]: <https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods>

[^9]: <https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods>
