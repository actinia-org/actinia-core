# Actinia — The GRASS GIS REST API

Software [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5879231.svg)](https://doi.org/10.5281/zenodo.5879231)
Article [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2631917.svg)](https://doi.org/10.5281/zenodo.2631917)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Docker pulls](https://img.shields.io/docker/pulls/mundialis/actinia-core.svg)](https://hub.docker.com/r/mundialis/actinia-core)


**[Actinia](https://actinia.mundialis.de/)** is an open source REST API for scalable, distributed, high performance
processing of geographical data that mainly uses [GRASS GIS](https://grass.osgeo.org/) for computational tasks.

It provides a REST API to process satellite images, time series of satellite images,
arbitrary raster data with geographical relations and vector data.

The REST interface allows to access, manage and manipulate the GRASS GIS
database via HTTP GET, PUT, POST and DELETE requests and to process raster, vector and
time series data located in a persistent GRASS GIS database.
**Actinia** allows the processing of cloud based data, for example all Landsat 4-8 scenes as well as all
Sentinel-2 scenes in an ephemeral databases. The computational results of ephemeral processing
are available via object storage as GeoTIFF files.

## API documentation
<!---
a more complete API documentation generated with Spinx was here: https://actinia.mundialis.de/api_docs
but no longer exists
--->

The full API documentation is available [here](https://redocly.github.io/redoc/?url=https://actinia.mundialis.de/latest/swagger.json&nocors)

## actinia command execution - actinia shell

There is also an option to interactively control actinia. For details,
see [here](https://github.com/mundialis/actinia_core/tree/main/scripts).

## Installation

Docker images are available from https://hub.docker.com/r/mundialis/actinia-core

```
docker pull mundialis/actinia-core
```

For own deployments or local dev-setup, see the `docker/` subfolder.

Actinia is also available on [OSGeoLive](https://live.osgeo.org/en/overview/actinia_overview.html).

## Examples

### Data management

* List all locations that are available in the actinia persistent database:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X GET "https://actinia.mundialis.de/api/v3/locations"
```

* List all mapsets in the location latlong_wgs84:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X GET "https://actinia.mundialis.de/api/v3/locations/latlong_wgs84/mapsets"
```

* List all space-time raster datasets (STRDS) in location latlong_wgs84 and mapset Sentinel_timeseries:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X GET "https://actinia.mundialis.de/api/v3/locations/latlong_wgs84/mapsets/modis_ndvi_global/strds"
```

* List all raster map layers of the STRDS:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X GET "https://actinia.mundialis.de/api/v3/locations/latlong_wgs84/mapsets/modis_ndvi_global/strds/ndvi_16_5600m/raster_layers"
```

### Landsat and Sentinel-2 NDVI computation

* Compute the NDVI of the top of athmosphere (TOAR) corrected Landsat4 scene LC80440342016259LGN00:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X POST "https://actinia.mundialis.de/api/v3/landsat_process/LC80440342016259LGN00/TOAR/NDVI"
```

* NDVI computation of Sentinel-2A scene S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X POST "https://actinia.mundialis.de/api/v3/sentinel2_process/ndvi/S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138"
```

The results of the asynchronous computations are available as GeoTIFF file in a cloud storage for download.

### List of available endpoints

To see a simple **list of endpoints** (and more), consult the "paths" section in the [API JSON](https://actinia.mundialis.de/api/v3/swagger.json); or, to list the available endpoints on command line, run

```bash
# sudo npm install -g json
curl -u 'demouser:gu3st!pa55w0rd' -X GET https://actinia.mundialis.de/api/v3/swagger.json | json paths | json -ka
```
