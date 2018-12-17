# Introduction to ace - actinia command execution

The `ace` tool allows the execution of single GRASS GIS command or a list of GRASS GIS commands on an actinia REST service (https://actinia.mundialis.de/).

The `ace` tool must be executed in an active GRASS GIS session and will use the current location settings to access the actinia service. All commands will be executed in an ephemeral database, hence generated output must be exported using augmented GRASS GIS commands. This tool takes a GRASS GIS command as argument or a list of commands from an input script file.

GRASS GIS commands can be augmented with actinia specific extensions. The `+` operator can be specified for an input parameter to import a web located resource and to specify the export of an output parameter.

## Notes

Importantly, the name of the local location and mapset must correspond to that on the actinia REST server.

Currently available are:

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


## Examples

### Command line examples

    ace g.list raster
    ace g.region -p

### Script examples

Example 1:

The following commands (to be stored in a script and executed with `ace`) will import a raster layer from an internet source as raster map `elev`, sets the computational region to the map and computes the slope. Additional information about the raster layer are requested with `r.info`:

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

Example 2: Image segmentation

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
    # Finally vectorize with r.to.vect, export to Geopackage
    r.to.vect input=ortho2010_segment_25 type=area output=ortho2010_segment_25+ESRI_Shapefile
