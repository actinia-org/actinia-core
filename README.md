# Actinia — The GRASS GIS REST API

Software [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5879231.svg)](https://doi.org/10.5281/zenodo.5879231)
Article [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2631917.svg)](https://doi.org/10.5281/zenodo.2631917)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Docker pulls](https://img.shields.io/docker/pulls/mundialis/actinia-core.svg)](https://hub.docker.com/r/mundialis/actinia-core)

## Project Overview

[Actinia](https://actinia.mundialis.de/) is an open-source REST API for scalable, distributed, high-performance processing of geographical data that mainly uses [GRASS GIS](https://grass.osgeo.org/) for computational tasks.

**Key Features:**

- REST API for processing satellite images, raster and vector data, including time-series.
- Access and manipulate GRASS GIS database via HTTP GET, PUT, POST, and DELETE requests.
- Process cloud-based data, including Landsat 4-9 and Sentinel-2 scenes.
- Output raster data results as GeoTIFF files as resources or in object storage.
- Output vector data results as GeoPackage files as resources or in object storage.

**Links:**

<!---
a more complete API documentation generated with Spinx was here: https://actinia.mundialis.de/api_docs
but no longer exists
--->

- [Software DOI](https://doi.org/10.5281/zenodo.5879231)
- [Article DOI](https://doi.org/10.5281/zenodo.2631917)
- [API Documentation](https://redocly.github.io/redoc/?url=https://actinia.mundialis.de/latest/swagger.json&nocors)
- [Discussion forum](https://github.com/orgs/actinia-org/discussions)

## Prerequisites

To use actinia, ensure you have the following installed:

- Alpine Linux: `apk add python3 py3-pip`
- Ubuntu: `apt install -y python3 python3-pip`

Additional system packages required for Alpine:

```bash
apk add python3-dev gcc musl-dev linux-headers build-base gdal gdal-tools gdal-dev proj proj-util proj-dev geos-dev py3-numpy-dev
```

## Installation Steps

### Option 1: Manual Installation

Install actinia from PyPI:

```bash
pip install actinia-core
```

### Option 2: Using Docker

Pull the Docker image:

```bash
docker pull mundialis/actinia-core
```

For custom deployments or local setups, refer to the `docker/` subfolder.

### Verification

To verify a successful installation, check API accessibility via the provided endpoints or the `swagger.json`.

## API Documentation

The full API documentation is available [here](https://redocly.github.io/redoc/?url=https://actinia.mundialis.de/latest/swagger.json&nocors).

## Examples

### Data management

- List all projects that are available in the actinia persistent database:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X GET "https://actinia.mundialis.de/api/v3/projects"
```

- List all mapsets in the project `latlong_wgs84`:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X GET "https://actinia.mundialis.de/api/v3/projects/latlong_wgs84/mapsets"
```

- List all space-time raster datasets (STRDS) in project `latlong_wgs84` and mapset `Sentinel_timeseries`:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X GET "https://actinia.mundialis.de/api/v3/projects/latlong_wgs84/mapsets/modis_ndvi_global/strds"
```

- List all raster map layers of the STRDS:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X GET "https://actinia.mundialis.de/api/v3/projects/latlong_wgs84/mapsets/modis_ndvi_global/strds/ndvi_16_5600m/raster_layers"
```

### Landsat and Sentinel-2 NDVI computation

- Compute NDVI for a specific Landsat scene:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X POST "https://actinia.mundialis.de/api/v3/landsat_process/<scene_id>/TOAR/NDVI"
```

- Compute NDVI for a specific Sentinel-2A scene:

```bash
curl -u 'demouser:gu3st!pa55w0rd' -X POST "https://actinia.mundialis.de/api/v3/sentinel2_process/ndvi/<scene_id>"
```

The results of the asynchronous computations are available as GeoTIFF file in a cloud storage for download.

### List of available endpoints

To see a simple **list of endpoints** (and more), consult the "paths" section in the [API JSON](https://actinia.mundialis.de/api/v3/swagger.json).

To list the available endpoints on command line, run

```bash
# sudo npm install -g json
curl -u 'demouser:gu3st!pa55w0rd' -X GET https://actinia.mundialis.de/api/v3/swagger.json | json paths | json -ka
```

### Development

#### Pre-Commit Hooks

Install [pre-commit](https://pre-commit.com) for automated code checks and formatting before
submitting any new or modified code. Pre-commit installs all necessary tools in a virtual environment
upon first use:

```bash
pip install pre-commit

# activate pre-commit in the code repository
cd <actinia-core_source_dir>
pre-commit install
```

Pre-commit will then be automatically triggered by the `git commit` command. If
it finds any problem it will abort the commit and try to solve it automatically.
In that case review the changes and run again `git add` and
`git commit`.

It is also possible to run pre-commit manually, e.g:

```bash
pre-commit run flake8 --all-files
pre-commit run black --all-files
# pre-commit run yamllint --all-files
# pre-commit run markdownlint --all-files
```

The pre-commit hook set is defined in
[.pre-commit-config.yaml](.pre-commit-config.yaml).

## External Documents

- actinia is also available on [OSGeoLive](https://live.osgeo.org/en/overview/actinia_overview.html)

## Contributors

Thanks to all contributors ❤
[![actinia-core contributors](https://contrib.rocks/image?repo=actinia-org/actinia-core "actinia-core contributors")](https://github.com/actinia-org/actinia-core/graphs/contributors)
