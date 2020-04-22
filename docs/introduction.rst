Introduction
============

Actinia is a REST service to process geographical data that can be managed by
the GRASS GIS software system. The software is designed to expose a GRASS GIS database
and many GRASS GIS [#GRASS]_ processing tool as REST service [#REST]_. Hence, access
to GRASS resources like raster maps, space-time raster datasets,
processing and analysis modules are available via URL.  In addition
Actinia allows the processing of cloud based data, for example all Landsat 4-8 scenes as well as all
Sentinel-2A scenes in an ephemeral databases. The computational results of ephemeral processing
are available via object storage as GeoTIFF files.

The actinia service consists of the *actinia core* that provides the basic but sophisticated processing service
and *actinia plugins* that provide problem specific services like Sentinel-2 and Landsat NDVI computation,
spatio-temporal statistical analysis and many more.

To use actinia the user must have an understanding of the GRASS GIS concept [#grassloc]_
of location, mapsets, raster maps, space-time datasets and modules.
The URLs that provide access to the GRASS database reflect
these concepts. Hence, the location, the mapset, the required raster
map are part of the URL to access the service.

What is REST?
-------------

The Representational state transfer (REST) [#REST]_ is an architectural style
based on HTTP [#http]_ that uses GET [#method]_,
DELETE [#method]_, POST [#method]_ and PUT [#method]_ methods to manipulate and receive resource
with stateless operations.

While GET requests can be send easily from a browser, POST, PUT or DELETE request can not.
To access the full potential of actinia you will need a HTTP client, that talks
all HTTP communication methods.


Examples
--------

**Data management**

- List all locations that are available in the actinia persistent database:

        curl -X GET "https://actinia.mundialis.de/api/v1/locations" -H  "authorization: Basic ..."

- List all mapsets in the location latlong_wgs84:

        curl -X GET "https://actinia.mundialis.de/api/v1/locations/latlong_wgs84/mapsets" -H  "authorization: Basic ..."

- List all space-time raster datasets (STRDS) in location latlong_wgs84 and mapset Sentinel_timeseries:

        curl -X GET "https://actinia.mundialis.de/api/v1/locations/latlong_wgs84/mapsets/Sentinel_timeseries/strds" -H  "authorization: Basic ..."

- List all raster map layers of the STRDS:

        curl -X GET "https://actinia.mundialis.de/api/v1/locations/latlong_wgs84/mapsets/Sentinel_timeseries/strds/S2A_B04/raster_layers" -H  "authorization: Basic ..."

**Landsat and Sentinel-2A NDVI computation**

This API call will compute the NDVI of the top of athmosphere (TOAR)
corrected Landsat4 scene LC80440342016259LGN00:

    curl -X POST "https://actinia.mundialis.de/api/v1/landsat_process/LC80440342016259LGN00/TOAR/NDVI" -H  "authorization: Basic ..."

NDVI computation of Sentinel-2A scene S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138:

    curl -X POST "https://actinia.mundialis.de/api/v1/sentinel2_process/ndvi/S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138" -H  "authorization: Basic ..."

The results of the asynchronous computations are available as GeoTIFF file in a cloud storage for download.


.. rubric:: Footnotes

.. [#GRASS] https://grass.osgeo.org/
.. [#REST] https://en.wikipedia.org/wiki/Representational_State_Transfer
.. [#curl] https://en.wikipedia.org/wiki/CURL
.. [#post] https://www.getpostman.com/apps
.. [#http] https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
.. [#method] https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
.. [#grassloc] https://grass.osgeo.org/grass78/manuals/helptext.html#2.-background:-grass-gis-location-structure
