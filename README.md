# Actinia — The GRASS GIS REST API

Software [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5879231.svg)](https://doi.org/10.5281/zenodo.5879231)
Article [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2631917.svg)](https://doi.org/10.5281/zenodo.2631917)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Docker pulls](https://img.shields.io/docker/pulls/mundialis/actinia-core.svg)](https://hub.docker.com/r/mundialis/actinia-core)

## Project Overview
Actinia is an open-source REST API for scalable, distributed, high-performance processing of geographical data that mainly uses GRASS GIS for computational tasks.

**Key Features:**
- REST API for processing satellite images, time-series data, and vector data.
- Access and manipulate GRASS GIS database via HTTP GET, PUT, POST, and DELETE requests.
- Process cloud-based data, including Landsat 4-8 and Sentinel-2 scenes.
- Output results as GeoTIFF files in object storage.

**Links:**
- [Software DOI](https://doi.org/10.5281/zenodo.5879231)
- [Article DOI](https://doi.org/10.5281/zenodo.2631917)
- [API Documentation](https://redocly.github.io/redoc/?url=https://actinia.mundialis.de/latest/swagger.json&nocors)

## Prerequisites
To use Actinia, ensure you have the following installed:
- Alpine Linux: `apk add python3 py3-pip`
- Ubuntu: `apt install -y python3 python3-pip`

Additional system packages required for Alpine:
```
apk add python3-dev gcc musl-dev linux-headers build-base gdal gdal-tools gdal-dev proj proj-util proj-dev geos-dev py3-numpy-dev
```

## Installation Steps
### Option 1: Manual Installation
Install Actinia from PyPI:
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
### Data Management
List all locations available in the persistent database:
```bash
curl -u 'demouser:gu3st!pa55w0rd' -X GET "https://actinia.mundialis.de/api/v3/locations"
```

For more detailed examples, see the original API documentation.

### Landsat and Sentinel-2 NDVI Computation
Compute NDVI for a specific scene:
```bash
curl -u 'demouser:gu3st!pa55w0rd' -X POST "https://actinia.mundialis.de/api/v3/landsat_process/<scene_id>/TOAR/NDVI"
```

### Development
#### Pre-Commit Hooks
Install [pre-commit](https://pre-commit.com) for automated code checks and formatting:
```bash
pip install pre-commit
cd <actinia-core_source_dir>
pre-commit install
```

Run hooks manually:
```bash
pre-commit run --all-files
```

## External Documents
- [OSGeoLive Overview](https://live.osgeo.org/en/overview/actinia_overview.html)

## Contributors
Thanks to all contributors ❤  
[![actinia-core contributors](https://contrib.rocks/image?repo=actinia-org/actinia-core "actinia-core contributors")](https://github.com/actinia-org/actinia-core/graphs/contributors)
