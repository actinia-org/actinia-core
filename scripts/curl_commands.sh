#!/bin/bash

## local installation
#export PORT=5000
#export IP=http://localhost
#export AUTH='-u user:abcdefgh'
#export actinia="${IP}:${PORT}"

## demo server
export actinia="https://actinia.mundialis.de"
export AUTH='-u demouser:gu3st!pa55w0rd'

#####
# Show all locations in the GRASS database
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations

# Create a new location based on an EPSG code
# curl -d "epsg=4326" -X POST -i ${actinia}/locations/LL_new # BUG

# Check if the location is listed
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations

# Delete the new location
# curl -X DELETE -i ${actinia}/locations/LL_new # BUG

# Get information of the NC location
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/info

# List all mapsets in that location
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets

# Create a new mapset
curl ${AUTH} -X POST -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/temporary # Success

# Check if the new mapset is listed
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets

# Get a list of all raster layers in the PERMANENT location
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/PERMANENT/raster_layers

# Get a list of all raster layer using a g.list pattern  (TODO: failing)
curl ${AUTH} -d "pattern=*lsat*" \
    -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/PERMANENT/raster_layers

# Get the information about the elevation
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation

# Render an image of the elevation raster layer  (TODO: how to visualize?)
curl ${AUTH} -d "n=228500&s=215000&w=630000&e=645000&ewres=50&nsres=50" \
    -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/render > /dev/null

# Get the interface description of r.slope.aspect (TODO: failing)
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/modules/r.slope.aspect

# Run g.region in the new mapset to set the extent and resolution for computation (TODO: failing)
curl ${AUTH} -H "Content-Type: application/json" -X POST \
    -d '{"inputs":{"raster":"elevation@PERMANENT"}, "flags":"g"}' \
    ${actinia}/api/v1/locations/nc_spm_08/mapsets/temporary/modules/g.region

# Start the module r.slope.aspect
curl ${AUTH} -H "Content-Type: application/json" -X POST \
    -d '{"inputs":{"elevation":"elevation@PERMANENT"},"outputs":{"slope":"my_slope", "aspect":"my_aspect"}}' \
    ${actinia}/api/v1/locations/nc_spm_08/mapsets/temporary/modules/r.slope.aspect

# Get information about the new created raster layer
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/temporary/raster_layers/my_slope
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/temporary/raster_layers/my_aspect

# Delete the temporary mapset
curl ${AUTH} -X DELETE -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/temporary # Success


###############################################################################
###############  STDRS  #######################################################
###############################################################################

# Get a list or raster layers from a STRDS
curl ${AUTH} -X GET -i "${actinia}/api/v1/locations/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm/raster_layers?where=start_time>2013-05-01"

###############################################################################
###############  Vector  ######################################################
###############################################################################

curl ${AUTH} -X GET -i "${actinia}/api/v1/locations/nc_spm_08/mapsets/PERMANENT/vector_layers/geology"


###############################################################################
################# ASYNC REST API CALLS ########################################
###############################################################################

PROCESS_CHAIN='{
   "1":{
        "module":"g.region",
        "inputs":{
            "raster":"elevation@PERMANENT",
            "res":"0.5"
        },
        "flags":"p",
        "verbose":"True"
   },
   "2":{
        "module":"r.slope.aspect",
        "inputs":{
            "elevation":"elevation@PERMANENT",
            "format":"degrees",
            "min_slope":"0.0"
        },
        "outputs":{
            "aspect":{
                "name":"my_aspect"
            },
            "slope":{
                "name":"my_slope",
                "export":{
                    "format":"GTiff",
                    "type":"raster"
                }
            }
        },
        "flags":"a",
        "overwrite":"True",
        "verbose":"True"
   }
}
'

# Start the module r.slope.aspect
curl ${AUTH} -H "Content-Type: application/json" -X POST \
    -d "${PROCESS_CHAIN}" ${actinia}/api/v1/locations/nc_spm_08/processing_async_export

# Get status
curl ${AUTH} -X GET -i
# Get the resource
curl ${AUTH} -X GET -i

PROCESS_CHAIN_LONG='{
   "1":{
        "module":"g.region",
        "inputs":{
            "raster":"elevation@PERMANENT",
            "res":"4"
        },
        "flags":"p",
        "verbose":"True"
   },
   "2":{
        "module":"r.slope.aspect",
        "inputs":{
            "elevation":"elevation@PERMANENT",
            "format":"degrees",
            "min_slope":"0.0"
        },
        "outputs":{
            "aspect":{
                "name":"my_aspect"
            },
            "slope":{
                "name":"my_slope"
            }
        },
        "flags":"a",
        "overwrite":"True",
        "verbose":"True"
   },
   "3":{
        "module":"r.watershed",
        "inputs":{
            "elevation":"elevation@PERMANENT"
        },
        "outputs":{
            "accumulation":{
                "name":"my_accumulation"
            }
        }
   },
   "4":{
        "module":"r.info",
        "inputs":{
            "map":"my_aspect"
        },
        "flags":"gr",
        "verbose":"True"
   }
}
'

# Start the module r.slope.aspect
curl ${AUTH} -H "Content-Type: application/json" -X POST \
    -d "${PROCESS_CHAIN_LONG}" ${actinia}/api/v1/locations/nc_spm_08/mapsets/test_mapset/processing_async

# Get status
curl ${AUTH} -X GET -i

# List all raster layer in the new mapset
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/test_mapset/raster_layers

# Info about my_accumulation
curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/test_mapset/raster_layers/my_accumulation/info

# Remove the new mapset
curl ${AUTH} -X DELETE -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/test_mapset

# Parallel computation
LIST="1
2
3
4"
for i in ${LIST} ; do
    echo "Run local process ${i}"
    curl ${AUTH} -H "Content-Type: application/json" -X POST \
        -d "${PROCESS_CHAIN_LONG}" ${actinia}/api/v1/locations/nc_spm_08/processing_async
done

# Export Parallel computation
LIST="1
2
3
4
5
6"
for i in ${LIST} ; do
    echo "Run export process ${i}"
    curl ${AUTH} -H "Content-Type: application/json" -X POST \
        -d "${PROCESS_CHAIN}" ${actinia}/api/v1/locations/nc_spm_08/processing_async_export
done

# New mapsets in massive parallel computation
LIST="1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16"
for i in ${LIST} ; do
    echo "Run new mapset process ${i}"
    curl ${AUTH} -H "Content-Type: application/json" -X POST \
        -d "${PROCESS_CHAIN_LONG}" ${actinia}/api/v1/locations/nc_spm_08/mapsets/test_mapset_${i}/processing_async
done

curl ${AUTH} -X GET -i ${actinia}/locations/nc_spm_08/mapsets

for i in ${LIST} ; do
    echo "Run ${i}"
    curl ${AUTH} -X GET -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/test_mapset_${i}/raster_layers
    curl ${AUTH} -X GET -i ${actinia}/locations/nc_spm_08/mapsets/test_mapset_${i}/raster_layers/my_accumulation/info
    curl ${AUTH} -X DELETE -i ${actinia}/api/v1/locations/nc_spm_08/mapsets/test_mapset_${i}
done

# Spatio-Temporal sampling
curl ${AUTH} -H "Content-Type: application/json" -X POST \
    -d '[["a", 10.5, 52.5], ["b", 10, 52], ["c", 11, 53]]' \
     ${actinia}/api/v1/locations/ECAD/mapsets/PERMANENT/strds/P_sum_yearly_mm/sampling_sync


JSON='{"bands":["B04", "B08"],
"strds":["S2A_B04", "S2A_B08"],
"product_ids":[
"S2B_MSIL1C_20170929T102009_N0205_R065_T32UPC_20170929T102007",
"S2A_MSIL1C_20170904T102021_N0205_R065_T32UPC_20170904T102511",
"S2B_MSIL1C_20170830T102019_N0205_R065_T32UPC_20170830T102531",
"S2A_MSIL1C_20170825T102021_N0205_R065_T32UPC_20170825T102114",
"S2B_MSIL1C_20170731T102019_N0205_R065_T32UPC_20170731T102348",
"S2B_MSIL1C_20170711T102029_N0205_R065_T32UPC_20170711T102309",
"S2A_MSIL1C_20170706T102021_N0205_R065_T32UPC_20170706T102301"]}'

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia}/api/v1/locations/LL/mapsets/Sentinel2A/sentinel2_import


JSON='{"bands": ["B04", "B08"],
         "scene_ids": ["S2A_MSIL1C_20170202T090201_N0204_R007_T36TVT_20170202T090155",
                       "S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_V20151207T003302_20151207T003302",
                       "S2A_MSIL1C_20170218T143751_N0204_R096_T20PRT_20170218T143931"]}'

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia}/api/v1/sentinel2a_aws_query


JSON='{"bands":["B04", "B08"],
"scene_ids":[
"S2A_MSIL1C_20170208T092131_N0204_R093_T35TLF_20170208T092143",
"S2A_MSIL1C_20170208T092131_N0204_R093_T35TMJ_20170208T092143",
"S2A_MSIL1C_20170208T092131_N0204_R093_T35UMB_20170208T092143",
"S2A_MSIL1C_20170208T092131_N0204_R093_T35UPB_20170208T092143",
"S2A_MSIL1C_20170208T092131_N0204_R093_T35UPR_20170208T092143",
"S2A_MSIL1C_20170208T092131_N0204_R093_T35VMC_20170208T092143",
"S2A_MSIL1C_20170208T092131_N0204_R093_T35VNC_20170208T092143",
"S2A_MSIL1C_20170208T092131_N0204_R093_T36UUG_20170208T092143"]}'

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia}/api/v1/sentinel2a_aws_query

# OpenEO use cases
JSON='{"bands":["B04", "B08"],
"strds":["S2A_B04", "S2A_B08"],
"product_ids":["S2B_MSIL1C_20170904T110619_N0205_R137_T30SUJ_20170904T111825",
"S2A_MSIL1C_20170820T110651_N0205_R137_T30SUJ_20170820T111220",
"S2A_MSIL1C_20170731T110651_N0205_R137_T30SUJ_20170731T111220",
"S2A_MSIL1C_20170721T110621_N0205_R137_T30SUJ_20170721T110758",
"S2A_MSIL1C_20170701T111051_N0205_R137_T30SUJ_20170701T111746",
"S2A_MSIL1C_20170621T110651_N0205_R137_T30SUJ_20170621T111222",
"S2A_MSIL1C_20170412T110621_N0204_R137_T30SUJ_20170412T111708"]}'

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia}/api/v1/locations/LL/mapsets/sentinel2A_openeo_subset/sentinel2_import


JSON='{
 "list": [
         {"id": "g_region_1",
          "module": "g.region",
          "inputs": [{"param": "raster",
                      "value": "S2A_MSIL1C_20170412T110621_N0204_R137_T30SUJ_20170412T111708_B04"}],
          "flags": "g"},
         {"id": "t_rast_mapcalc",
          "module": "t.rast.mapcalc",
          "inputs": [{"param": "expression",
                      "value": "NDVI = float((S2A_B08@sentinel2A_openeo_subset - S2A_B04@sentinel2A_openeo_subset)/(S2A_B08@sentinel2A_openeo_subset + S2A_B04@sentinel2A_openeo_subset))"},
                      {"param": "inputs",
                      "value": "S2A_B04@sentinel2A_openeo_subset,S2A_B08@sentinel2A_openeo_subset"},
                      {"param": "basename",
                      "value": "ndvi"},
                      {"param": "output",
                      "value": "NDVI"}]},
         {"id": "t_rast_color",
          "module": "t.rast.colors",
          "inputs": [{"param": "input",
                      "value": "NDVI"},
                     {"param": "color",
                      "value": "ndvi"}]}],
 "version": "1"
}'

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia}/api/v1/locations/LL/mapsets/sentinel2A_openeo_subset_ndvi/processing_async


JSON='{
 "list": [
         {"id": "g_region_1",
          "module": "g.region",
          "inputs": [{"param": "raster",
                      "value": "ndvi_1"}],
          "flags": "g"},
         {"id": "t_rast_aggr_func",
          "module": "t.rast.aggr_func",
          "inputs": [{"import_descr": {"source": "https://storage.googleapis.com/datentransfer/aggr_func.py",
                      "type": "file"},
			          "param": "pyfile",
			          "value": "$file::my_py_func"},
                      {"param": "input",
                       "value": "NDVI@sentinel2A_openeo_subset_ndvi"},
                      {"param": "output",
                       	"value": "aggr_ndvi"}]},
         {"id": "r_info",
          "module": "r.info",
          "inputs": [{"param": "map",
                      "value": "aggr_ndvi"}],
          "flags":"g"
         }],
 "version": "1"
}
'


curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia}/api/v1/locations/LL/mapsets/sentinel2A_openeo_subset_ndvi/processing_async


JSON='{"list": [{
            "id": "importer_1",
            "module": "importer",
            "inputs": [{
                "import_descr": {
                    "source": "https://storage.googleapis.com/graas-geodata/rio.json",
                    "type": "vector"
                },
                "param": "map",
                "value": "input_point"
            }]
        }, {
            "id": "v_buffer",
            "module": "v.buffer",
            "inputs": [{
                "param": "input",
                "value": "map"
            }, {
                "param": "output",
                "value": "buf_point"
            }, {
                "param": "distance",
                "value": "100"
            }, {
                "param": "units",
                "value": "meters"
            }]
        },
        {
            "id": "exporter_1",
            "module": "exporter",
            "outputs": [{
                "export": {
                    "type": "vector",
                    "format": "GeoJSON"
                },
                "param": "map",
                "value": "buf_point"
            }]
        },
    ],
    "version": "1"}
'

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia}/api/v1/locations/LL/process_chain_validation_async
