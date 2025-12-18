#!/bin/bash

#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2018 Sören Gebbert and mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

## local installation
#export PORT=5000
#export IP=http://localhost
#export AUTH='-u user:abcdefgh'
#export actinia="${IP}:${PORT}"

## demo server
export actinia_version="v3"
export actinia="https://actinia.mundialis.de"
export actinia_url="${actinia}/api/${actinia_version}"
export AUTH='-u demouser:gu3st!pa55w0rd'

# check actinia version
# https://actinia.mundialis.de/api/v3/version | https://actinia.mundialis.de/latest/version

#####
# Show all projects in the GRASS database
curl ${AUTH} -X GET -i ${actinia_url}/projects_wgs84

# Create a new project based on an EPSG code
echo '{
  "epsg": "4326"
}' > /tmp/pc_project_epsg4326.json

curl ${AUTH} -H "Content-Type: application/json" -X POST "${actinia_url}/projects/latlong_TEST" -d @/tmp/pc_project_epsg4326.json

# Check if the project is listed
curl ${AUTH} -X GET ${actinia_url}/projects_wgs84

# Delete the new project, careful!
curl ${AUTH} -X DELETE ${actinia_url}/projects/latlong_TEST
rm -f /tmp/pc_project_epsg4326.json

# Get information of the NC project
curl ${AUTH} -X GET -i ${actinia_url}/projects/nc_spm_08/info

# List all mapsets in that project
curl ${AUTH} -X GET -i ${actinia_url}/projects/nc_spm_08/mapsets

# Create a new mapset
curl ${AUTH} -X POST -i ${actinia_url}/projects/nc_spm_08/mapsets/temporary # Success

# Check if the new mapset is listed
curl ${AUTH} -X GET -i ${actinia_url}/projects/nc_spm_08/mapsets

# Get a list of all raster layers in the PERMANENT project
curl ${AUTH} -X GET -i ${actinia_url}/projects/nc_spm_08/mapsets/PERMANENT/raster_layers

# Get a list of all raster layer using a g.list pattern
curl ${AUTH} -X GET -i "${actinia_url}/projects/nc_spm_08/mapsets/PERMANENT/raster_layers?pattern=lsat*"

# Get the information about the elevation
curl ${AUTH} -X GET -i ${actinia_url}/projects/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation

# Render an image of the elevation raster layer
curl ${AUTH} -d "n=228500&s=215000&w=630000&e=645000&ewres=50&nsres=50" \
    -X GET ${actinia_url}/projects/nc_spm_08/mapsets/PERMANENT/raster_layers/elevation/render > elevation_NC.png

# Get information about the new created raster layer
curl ${AUTH} -X GET -i ${actinia_url}/projects/nc_spm_08/mapsets/temporary/raster_layers/my_slope
curl ${AUTH} -X GET -i ${actinia_url}/projects/nc_spm_08/mapsets/temporary/raster_layers/my_aspect

# Delete the temporary mapset
curl ${AUTH} -X DELETE -i ${actinia_url}/projects/nc_spm_08/mapsets/temporary # Success


###############################################################################
###############  STDRS  #######################################################
###############################################################################

# Get a list or raster layers from a STRDS
curl ${AUTH} -X GET -i "${actinia_url}/projects/ECAD/mapsets/PERMANENT/strds/precipitation_1950_2013_yearly_mm/raster_layers?where=start_time>2013-05-01"

###############################################################################
###############  Vector  ######################################################
###############################################################################

curl ${AUTH} -X GET -i "${actinia_url}/projects/nc_spm_08/mapsets/PERMANENT/vector_layers/geology"


###############################################################################
################# ASYNC REST API CALLS ########################################
###############################################################################

PROCESS_CHAIN='{
  "version": "1",
  "list": [
    {
      "module": "g.region",
      "id": "g.region_1804289383",
      "flags": "p",
      "inputs": [
        {
          "param": "raster",
          "value": "elevation@PERMANENT"
        },
        {
          "param": "res",
          "value": "10"
        }
      ]
    },
    {
      "module": "r.slope.aspect",
      "id": "r.slope.aspect_1804289383",
      "flags": "a",
      "inputs": [
        {
          "param": "elevation",
          "value": "elevation@PERMANENT"
        },
        {
          "param": "format",
          "value": "degrees"
        },
        {
          "param": "precision",
          "value": "FCELL"
        },
        {
          "param": "zscale",
          "value": "1.0"
        },
        {
          "param": "min_slope",
          "value": "0.0"
        }
      ],
      "outputs": [
        {
          "param": "slope",
          "value": "my_slope"
        },
        {
          "param": "aspect",
          "value": "my_aspect"
        }
      ]
    }
  ]
}
'

# Validation of process chain (using sync call)
curl ${AUTH} -H "Content-Type: application/json" -X POST \
    -d "${PROCESS_CHAIN}" ${actinia_url}/projects/nc_spm_08/process_chain_validation_sync

# Start the module r.slope.aspect (using async call)
curl ${AUTH} -H "Content-Type: application/json" -X POST \
    -d "${PROCESS_CHAIN}" ${actinia_url}/projects/nc_spm_08/processing_async_export

# Get status (add resource URL)
# curl ${AUTH} -X GET -i
# Get the resource (add resource URL)
# curl ${AUTH} -X GET -i

PROCESS_CHAIN_LONG='{
  "version": "1",
  "list": [
    {
      "module": "g.region",
      "id": "g.region_1804289383",
      "flags": "p",
      "inputs": [
        {
          "param": "raster",
          "value": "elevation@PERMANENT"
        },
        {
          "param": "res",
          "value": "4"
        }
      ]
    },
    {
      "module": "r.slope.aspect",
      "id": "r.slope.aspect_1804289383",
      "flags": "a",
      "inputs": [
        {
          "param": "elevation",
          "value": "elevation@PERMANENT"
        },
        {
          "param": "format",
          "value": "degrees"
        },
        {
          "param": "precision",
          "value": "FCELL"
        },
        {
          "param": "zscale",
          "value": "1.0"
        },
        {
          "param": "min_slope",
          "value": "0.0"
        }
      ],
      "outputs": [
        {
          "param": "slope",
          "value": "my_slope"
        },
        {
          "param": "aspect",
          "value": "my_aspect"
        }
      ]
    },
    {
      "module": "r.watershed",
      "id": "r.watershed_1804289383",
      "inputs": [
        {
          "param": "elevation",
          "value": "elevation@PERMANENT"
        },
        {
          "param": "convergence",
          "value": "5"
        },
        {
          "param": "memory",
          "value": "300"
        }
      ],
      "outputs": [
        {
          "param": "accumulation",
          "value": "my_accumulation"
        }
      ]
    },
    {
      "module": "r.info",
      "id": "r.info_1804289383",
      "flags": "gr",
      "inputs": [
        {
          "param": "map",
          "value": "my_aspect"
        }
      ]
    }
  ]
}
'

# Validation of process chain (using sync call)
curl ${AUTH} -H "Content-Type: application/json" -X POST \
    -d "${PROCESS_CHAIN_LONG}" ${actinia_url}/projects/nc_spm_08/process_chain_validation_sync

# Start the module r.slope.aspect (using async call)
curl ${AUTH} -H "Content-Type: application/json" -X POST \
    -d "${PROCESS_CHAIN_LONG}" ${actinia_url}/projects/nc_spm_08/mapsets/test_mapset/processing_async

# Get status (add resource URL)
# curl ${AUTH} -X GET -i

# List all raster layer in the new mapset
curl ${AUTH} -X GET -i ${actinia_url}/projects/nc_spm_08/mapsets/test_mapset/raster_layers

# Info about my_accumulation
curl ${AUTH} -X GET -i ${actinia_url}/projects/nc_spm_08/mapsets/test_mapset/raster_layers/my_accumulation

# Remove the new mapset
curl ${AUTH} -X DELETE -i ${actinia_url}/projects/nc_spm_08/mapsets/test_mapset

# Parallel computation
LIST="1
2
3
4"
for i in ${LIST} ; do
    echo "Run local process ${i}"
    curl ${AUTH} -H "Content-Type: application/json" -X POST \
        -d "${PROCESS_CHAIN_LONG}" ${actinia_url}/projects/nc_spm_08/processing_async
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
        -d "${PROCESS_CHAIN}" ${actinia_url}/projects/nc_spm_08/processing_async_export
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
        -d "${PROCESS_CHAIN_LONG}" ${actinia_url}/projects/nc_spm_08/mapsets/test_mapset_${i}/processing_async
done

curl ${AUTH} -X GET -i ${actinia}/projects/nc_spm_08/mapsets

for i in ${LIST} ; do
    echo "Run ${i}"
    curl ${AUTH} -X GET -i ${actinia_url}/projects/nc_spm_08/mapsets/test_mapset_${i}/raster_layers
    curl ${AUTH} -X GET -i ${actinia}/projects/nc_spm_08/mapsets/test_mapset_${i}/raster_layers/my_accumulation
    curl ${AUTH} -X DELETE -i ${actinia_url}/projects/nc_spm_08/mapsets/test_mapset_${i}
done

# Spatio-Temporal sampling
curl ${AUTH} -H "Content-Type: application/json" -X POST \
    -d '[["a", 10.5, 52.5], ["b", 10, 52], ["c", 11, 53]]' \
     ${actinia_url}/projects/ECAD/mapsets/PERMANENT/strds/P_sum_yearly_mm/sampling_sync


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

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia_url}/projects/latlong_wgs84/mapsets/Sentinel2A/sentinel2_import


JSON='{"bands": ["B04", "B08"],
         "scene_ids": ["S2A_MSIL1C_20170202T090201_N0204_R007_T36TVT_20170202T090155",
                       "S2A_OPER_PRD_MSIL1C_PDMC_20151207T031157_R102_V20151207T003302_20151207T003302",
                       "S2A_MSIL1C_20170218T143751_N0204_R096_T20PRT_20170218T143931"]}'

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia_url}/sentinel2a_aws_query


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

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia_url}/sentinel2a_aws_query

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

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia_url}/projects/latlong_wgs84/mapsets/sentinel2A_openeo_subset/sentinel2_import

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

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia_url}/projects/latlong_wgs84/mapsets/sentinel2A_openeo_subset_ndvi/processing_sync

# shellcheck disable=SC2016
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


curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia_url}/projects/latlong_wgs84/mapsets/sentinel2A_openeo_subset_ndvi/processing_async


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

curl ${AUTH} -H "Content-Type: application/json" -X POST -d "${JSON}" ${actinia_url}/projects/latlong_wgs84/process_chain_validation_sync
