# Actinia — The GRASS GIS REST API

**[Actinia](https://actinia.mundialis.de/)** is an open source REST API for scalable, distributed, high performance
processing of geographical data that uses [GRASS GIS](https://grass.osgeo.org/) for computational tasks.

It provides a REST API to process satellite images, time series of satellite images,
arbitrary raster data with geographical relations and vector data.

The REST interface allows to access, manage and manipulate the GRASS GIS
database via HTTP GET, PUT, POST and DELETE requests and to process raster, vector and
time series data located in a persistent GRASS GIS database.
**Actinia** allows the processing of cloud based data, for example all Landsat 4-8 scenes as well as all
Sentinel2A scenes in an ephemeral databases. The computational results of ephemeral processing
are available via object storage as GeoTIFF files.

The full API documentation is available here: https://actinia.mundialis.de/api_docs/

## Examples

### Data management

* List all locations that are available in the actinia persistent database:

```bash
curl -X GET "https://actinia.mundialis.de/api/v1/locations" -H "authorization: Basic …"
```

* List all mapsets in the location LL:

```bash
curl -X GET "https://actinia.mundialis.de/api/v1/locations/LL/mapsets" -H "authorization: Basic …"
```

* List all space-time raster datasets (STRDS) in location LL and mapset Sentinel_timeseries:

```bash
curl -X GET "https://actinia.mundialis.de/api/v1/locations/LL/mapsets/Sentinel_timeseries/strds" -H "authorization: Basic …"
```

* List all raster map layers of the STRDS:

```bash
curl -X GET "https://actinia.mundialis.de/api/v1/locations/LL/mapsets/Sentinel_timeseries/strds/S2A_B04/raster_layers" -H "authorization: Basic …"
```

### Landsat and Sentinel2A NDVI computation

* Compute the NDVI of the top of athmosphere (TOAR) corrected Landsat4 scene LC80440342016259LGN00:

```bash
curl -X POST "https://actinia.mundialis.de/api/v1/landsat_process/LC80440342016259LGN00/TOAR/NDVI" -H "authorization: Basic …"
```

* NDVI computation of Sentinel2A scene S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138:

```bash
curl -X POST "https://actinia.mundialis.de/api/v1/sentinel2_process/ndvi/S2A_MSIL1C_20170212T104141_N0204_R008_T31TGJ_20170212T104138" -H "authorization: Basic …"
```

The results of the asynchronous computations are available as GeoTIFF file in a cloud storage for download.
