# Introduction to ace - actinia command execution

The `ace` tool allows the execution of single GRASS GIS command 
or a list of GRASS GIS commands on an actinia REST service (https://actinia.mundialis.de/).
In addition it provides job management, the ability to
list locations, mapsets and map layer the user has access to as
well as the creation and deletion of mapsets.

Th `ace` tool must be executed in an active GRASS GIS session and will use the current location
of this session to access the actinia service. 
The current location can be overwritten by the `--location LOCATION_NAME` option.
All commands will be executed per default in an **ephemeral** database.
Hence, generated output must be exported using augmented GRASS commands.

The option `--persistent MAPSET_NAME` allows the execution of commands in the
**persistent** user database. It can be used with `--location LOCATION_NAME`option.

The user must setup the following environmental variables to specify the actinia
server and credentials:

```bash
# set credentials and REST server URL
export ACTINIA_USER='demouser'
export ACTINIA_PASSWORD='gu3st!pa55w0rd'
export ACTINIA_URL='https://actinia.mundialis.de/latest'
```

GRASS GIS commands can be augmented with actinia specific extensions.
The `+` operator can be specified for an input parameter
to import a web located resource and to specify the export of an
output parameter.


## Available data

Importantly, the name of the local location and mapset must correspond to
that on the actinia REST server.

Currently available datasets are (organized by projections):

* North Carolina sample dataset (NC State-Plane metric CRS, EPSG: 3358):
    * base cartography (`nc_spm_08/PERMANENT`; source: https://grassbook.org/datasets/datasets-3rd-edition/)
    * Landsat subscenes (`nc_spm_08/landsat`; source: https://grass.osgeo.org/download/sample-data/)
* Latitude-Longitude location (LatLong WGS84, EPSG:4326):
    * empty (`latlong_wgs84/PERMANENT/`)
    * 16-days NDVI, MOD13C1, V006, CMG 0.05 deg res. (`latlong_wgs84/modis_ndvi_global/`; source: https://lpdaac.usgs.gov/dataset_discovery/modis/modis_products_table/mod13c1_v006)
    * LST growing degree days asia 2017 (`latlong_wgs84/asia_gdd_2017/`; source: https://www.mundialis.de/en/temperature-data/)
    * LST tropical days asia 2017 (`latlong_wgs84/asia_tropical_2017/`)
    * LST temperature daily asia 2017, including min, max and avg (`latlong_wgs84/asia_lst_daily_2017/`)
* Europe (EU LAEA CRS, EPSG:3035):
    * EU DEM 25m V1.1 (`eu_laea/PERMANENT/`; source: https://land.copernicus.eu/imagery-in-situ/eu-dem)
    * CORINE Landcover 2012, g100_clc12_V18_5 (`eu_laea/corine_2012/`; source: https://land.copernicus.eu/pan-european/corine-land-cover/clc-2012)
* World Mollweide (EPSG 54009):
    * GHS_POP_GPW42015_GLOBE_R2015A_54009_250_v1_0 (`world_mollweide/pop_jrc`; source: https://ghsl.jrc.ec.europa.eu/ghs_pop.php)

Not all data is available for the demo user.

### List locations, mapsets and maps

In order to list the locations the user has access to, run

```bash
ace --list-locations
['latlong', 'nc_spm_08', 'utm_32n', 'latlong_wgs84']
```

The following command lists mapsets of current location in the active GRASS GIS session (nc_spm_08):

```bash
# running ace in the "nc_spm_08" location:
ace --list-mapsets
['PERMANENT', 'landsat']
```

All following commands can be executed in any active GRASS GIS location, since
the location name at the actinia server is explicitly provided. 
In case the location option is not provided, the active location will be used.
The following command lists mapsets of the provided location **latlong**:

```bash
ace --location latlong --list-mapsets
['PERMANENT']
```

To list all raster maps available in the specified mapset belonging to the provided location **latlong**, run:

```bash
ace --location latlong --list-raster PERMANENT
['dem_gmted', 'hwsd_stghws1a', 'lulc_globc']
```

To list all vector maps available in the specified mapset belonging to the
current or a provided location, run:

```bash
ace --location latlong --list-vector PERMANENT
['world_countries']
```

List all raster maps in a location/mapset different from the current session
location:

```bash
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

## Acessing maps in a different mapset

Simply use `@name_of_mapset`.

## Job management

The `ace` tool can list jobs, choose from `all`, `accepted`, `running`,
`terminated`, `finished`, `error`.

Show finished job(s) (note: the actual response may differ):

```bash
ace --list-jobs finished

resource_id-7a94b416-6f19-40c0-96c2-e62ce133ff89 finished 2018-12-17 11:33:58.965602
resource_id-87965ced-7242-43d2-b6da-5ded47b10702 finished 2018-12-18 08:45:29.959495
resource_id-b633740f-e0c5-4549-a663-9d58f9499531 finished 2018-12-18 08:52:36.669777
resource_id-0f9d6382-b8d2-4ff8-b41f-9b16e4d6bfe2 finished 2018-12-17 11:14:00.283710
```

Show running job(s):

```bash
ace --list-jobs running
resource_id-30fff8d6-5294-4f03-a2f9-fd7c857bf153 running 2018-12-18 21:58:04.107389
```

Show details about a specific job:

```bash
ace --info-job resource_id-30fff8d6-5294-4f03-a2f9-fd7c857bf153

{'accept_datetime': '2018-12-18 21:47:41.094534',
 'accept_timestamp': 1545169661.0945334,
 'api_info': {'endpoint': 'asyncephemeralexportresource',
              'method': 'POST',
              'path': '/api/v1/locations/latlong/processing_async_export',
              'request_url': 'http://actinia.mundialis.de/api/v1/locations/latlong/processing_async_export'},
 'datetime': '2018-12-18 21:58:14.133485',
 'http_code': 200,
 'message': 'Running executable v.rast.stats with parameters '
            "['map=canada_provinces', 'layer=1', 'raster=srtmgl ... "
            "average,range,stddev,percentile', 'percentile=95'] for 631.702 "
            'seconds',
 'process_chain_list': [],
 'progress': {'num_of_steps': 5, 'step': 5},
 'resource_id': 'resource_id-30fff8d6-5294-4f03-a2f9-fd7c857bf153',
 'status': 'running',
 'time_delta': 633.0389630794525,
 'timestamp': 1545170294.1334834,
 'urls': {'resources': [],
          'status': 'https://actinia.mundialis.de/api/v1/resources/markus/resource_id-30fff8d6-5294-4f03-a2f9-fd7c857bf153'},
 'user_id': 'markus'}
```

## Available export formats

At time the following export formats are currently supported:

* raster: `GTiff`
* vector: `ESRI_Shapefile`, `GeoJSON`, `GML`
* table: `CSV`, `TXT`

The vector formats will be extended in future versions of actina with geopackage and sqlite formats.

## Examples for ephemeral processing

Ephemeral processing is the default processing approach of actinia. Each single command 
or all commands in a shell script, will be executed in an ephemeral mapset. This mapset will be removed
after processing. The output of GRASS GIS modules can be marked for export, to store
the computational result for download and further analysis.

### Command line examples

Run the module `g.list` in the location defined by the active GRASS GIS session
in an ephemeral mapset, that has only the PERMANENT mapset in its search path:

```bash
ace g.list raster

Resource status accepted
Polling: https://actinia.mundialis.de/api/v1/resources/demouser/resource_id-db96cd83-dbc2-40c6-b550-20e265e51c1b
Resource poll status: finished
Processing successfully finished
Resource status finished
--------------------------------------------------------------------------
aspect
basin_50K
boundary_county_500m
cfactorbare_1m
cfactorgrow_1m
el_D782_6m
el_D783_6m
el_D792_6m
el_D793_6m
elev_lid792_1m
elev_ned_30m
elev_srtm_30m
elev_state_500m
elevation
elevation_shade
facility
geology_30m
lakes
landclass96
landcover_1m
landuse96_28m
lsat7_2002_10
lsat7_2002_20
lsat7_2002_30
lsat7_2002_40
lsat7_2002_50
lsat7_2002_61
lsat7_2002_62
lsat7_2002_70
lsat7_2002_80
ncmask_500m
ortho_2001_t792_1m
roadsmajor
slope
soilsID
soils_Kfactor
streams_derived
towns
urban
zipcodes
zipcodes_dbl

{'resources': [],
 'status': 'https://actinia.mundialis.de/api/v1/resources/demouser/resource_id-db96cd83-dbc2-40c6-b550-20e265e51c1b'}
```

Run the module `g.region` in a new ephemeral location, to show the default region of a temporary mapset:

```bash
ace g.region -p

Resource status accepted
Polling: https://actinia.mundialis.de/api/v1/resources/demouser/resource_id-b398b4dd-a47c-4443-a07d-7814cc737973
Resource poll status: finished
Processing successfully finished
Resource status finished
--------------------------------------------------------------------------
projection: 99 (Lambert Conformal Conic)
zone:       0
datum:      nad83
ellipsoid:  a=6378137 es=0.006694380022900787
north:      320000
south:      10000
west:       120000
east:       935000
nsres:      500
ewres:      500
rows:       620
cols:       1630
cells:      1010600

{'resources': [],
 'status': 'https://actinia.mundialis.de/api/v1/resources/demouser/resource_id-b398b4dd-a47c-4443-a07d-7814cc737973'}
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
# Import the web resource and set the region to the imported map
g.region raster=elev+https://storage.googleapis.com/graas-geodata/elev_ned_30m.tif -ap
# Compute univariate statistics
r.univar map=elev
r.info elev
# Compute the slope of the imported map and mark it for export as geotiff file
r.slope.aspect elevation=elev slope=slope_elev+GTiff
r.info slope_elev
```
Save the script in the text file to `/tmp/ace_dtm_statistics.sh`
and run the saved script as

```bash
ace --script /tmp/ace_dtm_statistics.sh
```

The results are provided as REST resources.

To generate the actinia process chain JSON request simply add the --dry-run flag

```bash
ace --dry-run --script /tmp/ace_dtm_statistics.sh
```
The output should look like this:
```json
{
  "version": "1",
  "list": [
    {
      "module": "g.region",
      "id": "g.region_1804289383",
      "flags": "pa",
      "inputs": [
        {
          "import_descr": {
            "source": "https://storage.googleapis.com/graas-geodata/elev_ned_30m.tif",
            "type": "raster"
          },
          "param": "raster", "value": "elev"
        }
      ]
    },
    {
      "module": "r.univar",
      "id": "r.univar_1804289383",
      "inputs": [
        {"param": "map", "value": "elev"},
        {"param": "percentile", "value": "90"},
        {"param": "separator", "value": "pipe"}
      ]
    },
    {
      "module": "r.info",
      "id": "r.info_1804289383",
      "inputs": [{"param": "map", "value": "elev"}]
    },
    {
      "module": "r.slope.aspect",
      "id": "r.slope.aspect_1804289383",
      "inputs": [
        {"param": "elevation", "value": "elev"},
        {"param": "format", "value": "degrees"},
        {"param": "precision", "value": "FCELL"},
        {"param": "zscale", "value": "1.0"},
        {"param": "min_slope", "value": "0.0"}
      ],
      "outputs": [
        {
          "export": {"format": "GTiff", "type": "raster"},
          "param": "slope", "value": "slope_elev"
        }
      ]
    },
    {
      "module": "r.info",
      "id": "r.info_1804289383",
      "inputs": [{"param": "map", "value": "slope_elev"}]
    }
  ]
}
```

#### Example 2: Orthophoto image segmentation with export

Store the following script as text file `/tmp/ace_segmentation.sh`:

```bash
# grass77 ~/grassdata/nc_spm_08/user1/
# Import the web resource and set the region to the imported map
# we apply a trick for the import of multi-band GeoTIFFs:
# install with: g.extension importer
importer raster=ortho2010+https://apps.mundialis.de/workshops/osgeo_ireland2017/north_carolina/ortho2010_t792_subset_20cm.tif
# The importer has created three new raster maps, one for each band in the geotiff file
# stored them in an image group
r.info map=ortho2010.1
r.info map=ortho2010.2
r.info map=ortho2010.3
# Set the region and resolution
g.region raster=ortho2010.1 res=1 -p
# Note: the RGB bands are organized as a group
i.segment group=ortho2010 threshold=0.25 output=ortho2010_segment_25+GTiff goodness=ortho2010_seg_25_fit+GTiff
# Finally vectorize segments with r.to.vect and export as a GeoJSON file
r.to.vect input=ortho2010_segment_25 type=area output=ortho2010_segment_25+GeoJSON
```

Run the script saved in a text file as

```bash
ace --script /tmp/ace_segmentation.sh
```

The results are provided as REST resources.


## Examples for persistent processing

GRASS GIS commands can be executed in a user specific persistent database.
The user must create a mapset in an existing location. This mapsets can be accessed
via `ace`. All processing results of commands run in this mapset, will be stored
persistently. Be aware that the processing will be performed in an ephemeral database
that will be moved to the persistent storage using the correct name after processing.

To create a new mapset in the **nc_spm_08** location with the name **test_mapset**
the following command must be executed

```bash
ace --location nc_spm_08 --create-mapset test_mapset
```

Run the commands from the statistic script in the new persistent mapset

```bash
ace --location nc_spm_08 --persistent test_mapset --script /path/to/ace_dtm_statistics.sh
```

Show all raster maps that have been created with the script in test_mapset

```bash
ace --location nc_spm_08 --persistent test_mapset g.list type=raster mapset=test_mapset
```

Show information about raster map elev and slope_elev

```bash
ace --location nc_spm_08 --persistent test_mapset r.info elev@test_mapset
ace --location nc_spm_08 --persistent test_mapset r.info slope_elev@test_mapset
```

Delete the test_mapset

```bash
ace --location nc_spm_08 --delete-mapset test_mapset
```

If the active GRASS GIS session has identical location/mapset settings, then an alias
can be used to avoid the persistent option in each single command call:

```bash
alias acp="ace --persistent `g.mapset -p`"
```

We assume that in the active GRASS GIS session the 
current location is **nc_spm_08** and the current mapset is **test_mapset**.
Then the commands from above can be executed in the following way:

```bash
ace --create-mapset test_mapset
acp --script /path/to/ace_dtm_statistics.sh
acp g.list type=raster mapset=test_mapset
acp r.info elev@test_mapset
acp r.info slope_elev@test_mapset
```
