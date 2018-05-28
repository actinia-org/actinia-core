Introduction
============

Actinia is a REST service to process geographical data that can be managed by
the GRASS GIS software system. The software is designed to expose a GRASS GIS database
and many GRASS GIS [#GRASS]_ processing tool as REST service [#REST]_. Hence, access
to GRASS resources like raster maps, space-time raster datasets,
processing and analysis modules are available via URL.  In addition
Actinia allows the processing of cloud based data, for example all Landsat 4-8 scenes as well as all
Sentinel2A scenes in an ephemeral databases. The computational results of ephemeral processing
are available via object storage as GeoTIFF files.

The Actinia service consists of the *Actinia Core* that provides the basic but sophisticated processing service
and *Actinia plugins* that provide problem specific services like Sentinel 2A and Landsat NDVI computation,
spatio-temporal statistical analysis and many more.

This documentation focus on the basic processing services that are provided by the *Actinia Core*
service.

.. rubric:: Footnotes

.. [#GRASS] https://grass.osgeo.org/
.. [#REST] https://en.wikipedia.org/wiki/Representational_State_Transfer

To use Actinia the user must have an understanding of the GRASS GIS concept [#grassloc]_
of location, mapsets, raster maps, space-time datasets and modules.
The URLs that provide access to the GRASS database reflect
these concepts. Hence, the location, the mapset, the required raster
map are part of the URL to access the service.

Howto use the REST API
----------------------

The REST approach uses the HTTP [#http]_ method GET [#method]_,
DELETE [#method]_, POST [#method]_ and PUT [#method]_ to manipulate and receive resource.

While GET requests can be send easily from a browser, POST, PUT or DELETE request can not.
To access the full potential of Actinia you will need a HTTP client, that talks
all HTTP communication methods.

The following examples shows the REST service access using the command line tool **curl** [#curl]_.
**Curl** should be available on many Linux systems.
However, tools like *postman* [#post]_ allow a more comfortable way to access
Actinia.

.. rubric:: Footnotes

.. [#curl] https://en.wikipedia.org/wiki/CURL
.. [#post] https://www.getpostman.com/apps
.. [#http] https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
.. [#method] https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
.. [#grassloc] https://grass.osgeo.org/grass72/manuals/helptext.html#2.-background:-grass-gis-location-structure


The Actinia databases
---------------------

Actinia manage many GRASS GIS locations in its *persistent database*.
User are not permitted to modify data in a persistent database, but can access all data
read only for processing and visualization. Data in the persistent database can only accessed
via HTTP GET API calls.

The user can either process data in an *ephemeral databases*, that will be removed after
the processing is finished, or in a *user specific database*. A user specific database is persistent,
only visible to users of the same user-group and can contain any data the user
has imported.The user can read-access all data from the persistent database
while running analysis in the ephemeral database or user specific database.
