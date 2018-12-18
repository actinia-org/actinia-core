# Introduction to ace - actinia command execution

The `ace` tool allows the execution of single GRASS GIS command or a list
of GRASS GIS commands on an actinia REST service (https://actinia.mundialis.de/).

The `ace` tool must be executed in an active GRASS GIS session and will
use the current location settings to access the actinia service. All
commands will be executed in an ephemeral database, hence generated output
must be exported using augmented GRASS GIS commands. This tool takes a
GRASS GIS command as argument or a list of commands from an input script file.

GRASS GIS commands can be augmented with actinia specific extensions.
The `+` operator can be specified for an input parameter to import a web
ocated resource and to specify the export of an output parameter.

## Available data

Importantly, the name of the local location and mapset must correspond to
that on the actinia REST server.

Currently available datasets are (organized by projections):

* North Carolina sample dataset (NC State-Plane metric CRS, EPSG: 3358):
    * base cartography (`nc_spm_08/PERMANENT`)
    * Landsat subscenes (`nc_spm_08/landsat`)
* Latitude-Longitude location (LatLong WGS84, EPSG:4326):
    * empty (`latlong_wgs84/PERMANENT/`)
    * 16-days NDVI, MOD13C1, V006, CMG 0.05 deg res. (`latlong_wgs84/modis_ndvi_global/`)
    * LST growing degree days asia 2017 (`latlong_wgs84/asia_gdd_2017/`)
    * LST tropical days asia 2017 (`latlong_wgs84/asia_tropical_2017/`)
    * LST temperature daily asia 2017, including min, max and avg (`latlong_wgs84/asia_lst_daily_2017/`)
* Europe (EU LAEA CRS, EPSG:3035):
    * EU DEM 25m V1.1 (`eu_laea/PERMANENT/`)
    * CORINE Landcover 2012, g100_clc12_V18_5 (`eu_laea/corine_2012/`)

In order to list the locations the user has access to, run

```bash
# note: the actual response may differ
ace --list-locations
['latlong', 'nc_spm_08', 'utm_32n', 'eu_laea', 'latlong_wgs84', 'LL']
```

The following command lists mapsets of the current or a provided location:

```bash
# running ace in the "latlong" location:
# note: the actual response may differ
ace --list-mapsets
['PERMANENT',
 'chelsa_climate',
 'etopo1',
 'globcover',
 'gmted2010',
 'loss_global_forest_cover_loss_2000_2015',
 'nightlight',
 'soil_hwsd_unused',
 'soil_taxnrwb',
 'srtmgl1_30m']
```

To list all raster maps available in the specified mapset belonging to the
current or a provided location, run:

```bash
# running ace in the "latlong" location:
# note: the actual response may differ
ace --list-raster PERMANENT
['dem_gmted', 'hwsd_stghws1a', 'lulc_globc']
```

To list all vector maps available in the specified mapset belonging to the
current or a provided location, run:

```bash
# running ace in the "latlong" location:
# note: the actual response may differ
ace --list-vector PERMANENT
['world_countries']
```

List all raster maps in a location/mapset different from the current session
location:

```bash
# running ace in the "latlong" location but querying the nc_spm_08 location:
ace --location nc_spm_08 --list-raster PERMANENT
['aspect',
 'basin_50K',
 'boundary_county_500m',
 'cfactorbare_1m',
 'cfactorgrow_1m',
 'el_D782_6m',
 'el_D783_6m',
 'el_D792_6m',
 'el_D793_6m',
 'elev_lid792_1m',
 'elev_ned_30m',
 ...
 'lsat7_2002_70',
 'lsat7_2002_80',
 'ncmask_500m',
 'ortho_2001_t792_1m',
 'roadsmajor',
 'slope',
 'soilsID',
 'soils_Kfactor',
 'streams_derived',
 'towns',
 'urban',
 'zipcodes',
 'zipcodes_dbl']
```

## Job management

The `ace` tool can list jobs, choose from `all`, `accepted`, `running`,
`terminated`, `finished`, `error`:

```bash
ace --list-jobs finished
# note: the actual response may differ
resource_id-7a94b416-6f19-40c0-96c2-e62ce133ff89 finished 2018-12-17 11:33:58.965602
resource_id-87965ced-7242-43d2-b6da-5ded47b10702 finished 2018-12-18 08:45:29.959495
resource_id-b633740f-e0c5-4549-a663-9d58f9499531 finished 2018-12-18 08:52:36.669777
resource_id-0f9d6382-b8d2-4ff8-b41f-9b16e4d6bfe2 finished 2018-12-17 11:14:00.283710
```

## Available export formats

At time the following export formats are currently supported:

* raster: `GTiff`
* vector: `ESRI_Shapefile`, `GeoJSON`, `GML`, `GPKG`, `PostgreSQL`, `SQLite`
* table: `CSV`, `TXT`


## Examples

### Command line examples

```bash
ace g.list raster
ace g.region -p
```

### Script examples

#### Example 1: computing slope and aspect and univariate statistics from an elevation model

The following commands (to be stored in a script and executed with
`ace`) will import a raster layer from an internet source as raster map
`elev`, sets the computational region to the map and computes the
slope. Additional information about the raster layer are requested with
`r.info`.

Store the following script as text file `ace_dtm_statistics.sh`:

```bash
# grass77 ~/grassdata/nc_spm_08/user1/
# set credentials and REST server URL
export ACTINIA_USER='demouser'
export ACTINIA_PASSWORD='gu3st!pa55w0rd'
export ACTINIA_URL='https://actinia.mundialis.de/latest'
# Import the web resource and set the region to the imported map
g.region raster=elev+https://storage.googleapis.com/graas-geodata/elev_ned_30m.tif -ap
# Compute univariate statistics
r.univar map=elev
r.info elev
# Compute the slope of the imported map and mark it for export
r.slope.aspect elevation=elev slope=slope_elev+GTiff
r.info slope_elev
```

Run the script saved in a text file as

```bash
ace -s /path/to/ace_dtm_statistics.sh
```

The results are provided as REST resources.

#### Example 2: Orthophoto image segmentation with export

Store the following script as text file `ace_segmentation.sh`:

```bash
# grass77 ~/grassdata/nc_spm_08/user1/
# set credentials and REST server URL
export ACTINIA_USER='demouser'
export ACTINIA_PASSWORD='gu3st!pa55w0rd'
export ACTINIA_URL='https://actinia.mundialis.de/latest'
# Import the web resource and set the region to the imported map
# we apply a trick for the import of multi-band GeoTIFFs:
# install with: g.extension importer
importer raster=ortho2010+https://apps.mundialis.de/workshops/osgeo_ireland2017/north_carolina/ortho2010_t792_subset_20cm.tif
#r.info map=ortho2010.1
#r.info map=ortho2010.2
#r.info map=ortho2010.3
g.region raster=ortho2010.1 res=1 -p
# Note: the RGB bands are organized as a group
i.segment group=ortho2010 threshold=0.25 output=ortho2010_segment_25+GTiff goodness=ortho2010_seg_25_fit+GTiff
# Finally vectorize segments with r.to.vect and export as a Geopackage file
r.to.vect input=ortho2010_segment_25 type=area output=ortho2010_segment_25+GPKG
```

Run the script saved in a text file as

```bash
ace -s /path/to/ace_segmentation.sh
```

The results are provided as REST resources.
