# Introduction to ace - actinia command execution

The `ace` tool allows the execution of single GRASS GIS command or a list of GRASS GIS commands on an actinia REST service (https://actinia.mundialis.de/).

The `ace` tool must be executed in an active GRASS GIS session and will use the current location settings to access the actinia service. All commands will be executed in an ephemeral database, hence generated output must be exported using augmented GRASS GIS commands. This tool takes a GRASS GIS command as argument or a list of commands from an input script file.

GRASS GIS commands can be augmented with actinia specific extensions. The `+` operator can be specified for an input parameter to import a web located resource and to specify the export of an output parameter.

## Examples

### Command line examples

    ace g.list raster
    ace g.region -p

### Script examples

Example 1:

The following commands (to be stored in a script and executed with `ace`) will import a raster layer from an internet source as raster map `elev`, sets the computational region to the map and computes the slope. Additional information about the raster layer are requested with `r.info`:

    # grass77 ~/grassdata/nc_spm_08_grass7/user1/
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

    # grass77 ~/grassdata/nc_spm_08_grass7/user1/
    # set credentials and REST server URL
    export ACTINIA_USER='demouser'
    export ACTINIA_PASSWORD='gu3st!pa55w0rd'
    export ACTINIA_URL='https://actinia.mundialis.de/latest'
    # Import the web resource and set the region to the imported map
    g.region raster=ortho2010_20cm+https://apps.mundialis.de/workshops/osgeo_ireland2017/north_carolina/ortho2010_t792_subset_20cm.tif
    # set comp. region to orthophoto (extent), but only at 1m resolution (just for speed reasons for this demo)
    g.region raster=ortho2010_t792_subset_20cm.blue res=1 -p
    # Note: the RGB bands are organized as a group
    i.segment group=ortho2010_t792_subset_20cm threshold=0.25 output=ortho2010_t792_subset_20cm_segment_25+GTiff goodness=ortho2010_t792_subset_20cm_seg_25_fit+GTiff
    # Finally vectorize with r.to.vect, export to Geopackage
    r.to.vect input=ortho2010_t792_subset_20cm_segment_25 type=area output=ortho2010_t792_subset_20cm_segment_25+GPKG
