# Tutorial

In the following tutorial we will access the persistent database
analysing raster and raster-time-series data. We will use the import and
export features of actinia-specific process chains to process
Sentinel-2A scenes with several GRASS GIS modules and export the result
as GeoTiff files.

The following examples shows the REST service access using the command
line tool **curl**[^1]. **Curl** should be available on many Linux
systems. However, tools like *postman*[^2] allow a more comfortable way
to access actinia.

## Using curl for HTTP requests

We will use the Unix shell and curl to access the REST API. First open a
shell of choice (we use bash here) and setup the login information, the
IP address and the port on which the actinia service is running, so you
can simply change the IP and port if your server uses a different
address:

```bash
export ACTINIA_URL=https://actinia.mundialis.de/api/v3
export AUTH='-u demouser:gu3st!pa55w0rd'
# other user credentials can be provided in the same way
```

## Access to projects and mapsets in the persistent database

The following API call lists all available projects in the actinia
persistent database (the `-i` includes the HTTP response headers):

```bash
 curl ${AUTH} -X GET -i "${ACTINIA_URL}/projects"
```

The output should look similar to this:

```json
 {
   "projects": [
     "latlong_wgs84",
     "nc_spm_08"
   ],
   "status": "success"
 }
```

To show the region settings and the projection of the GRASS GIS standard
project *nc_spm_08* the following REST call must be used:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/projects/nc_spm_08/info"
```

The JSON response is the standard response of the actinia REST API. Most
API calls respond using this JSON structure. The difference between API
calls is the result part that is located in the JSON section with the
name *process_results*. The response includes all steps that were
executed to receive the projection information and the region
information. It is located in the *process_log* section of the JSON
response. In addition API specific information as well as the processing
time are available in the response. To make the JSON response more readable you can use parsing-tools like jq.

The output should look similar to this then:

```json
 {
   "accept_datetime": "2019-08-01 20:30:05.717499",
   "accept_timestamp": 1564691405.7174985,
   "api_info": {
     "endpoint": "projectmanagementresourceuser",
     "method": "GET",
     "path": "/api/v3/projects/nc_spm_08/info",
     "request_url": "http://actinia.mundialis.de/api/v3/projects/nc_spm_08/info"
   },
   "datetime": "2019-08-01 20:30:05.881138",
   "http_code": 200,
   "message": "Processing successfully finished",
   "process_chain_list": [
     {
       "1": {
         "flags": "ug3",
         "module": "g.region"
       },
       "2": {
         "flags": "fw",
         "module": "g.proj"
       }
     }
   ],
   "process_log": [
     {
       "executable": "g.region",
       "parameter": [
         "-ug3"
       ],
       "return_code": 0,
       "run_time": 0.05028104782104492,
       "stderr": [
         ""
       ],
       "stdout": "projection=99\nzone=0\nn=221230\ns=219580\nw=637740\ne=639530\nt=1\nb=0\nnsres=1650\nnsres3=10\newres=1790\newres3=10\ntbres=1\nrows=1\nrows3=165\ncols=1\ncols3=179\ndepths=1\ncells=1\ncells3=29535\n"
     },
     {
       "executable": "g.proj",
       "parameter": [
         "-fw"
       ],
       "return_code": 0,
       "run_time": 0.05027127265930176,
       "stderr": [
         ""
       ],
       "stdout": "PROJCS[\"NAD83(HARN) / North Carolina\",GEOGCS[\"NAD83(HARN)\",DATUM[\"NAD83_High_Accuracy_Reference_Network\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6152\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4152\"]],PROJECTION[\"Lambert_Conformal_Conic_2SP\"],PARAMETER[\"standard_parallel_1\",36.16666666666666],PARAMETER[\"standard_parallel_2\",34.33333333333334],PARAMETER[\"latitude_of_origin\",33.75],PARAMETER[\"central_meridian\",-79],PARAMETER[\"false_easting\",609601.22],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"X\",EAST],AXIS[\"Y\",NORTH],AUTHORITY[\"EPSG\",\"3358\"]]\n"
     }
   ],
   "process_results": {
     "projection": "PROJCS[\"NAD83(HARN) / North Carolina\",GEOGCS[\"NAD83(HARN)\",DATUM[\"NAD83_High_Accuracy_Reference_Network\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6152\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4152\"]],PROJECTION[\"Lambert_Conformal_Conic_2SP\"],PARAMETER[\"standard_parallel_1\",36.16666666666666],PARAMETER[\"standard_parallel_2\",34.33333333333334],PARAMETER[\"latitude_of_origin\",33.75],PARAMETER[\"central_meridian\",-79],PARAMETER[\"false_easting\",609601.22],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"X\",EAST],AXIS[\"Y\",NORTH],AUTHORITY[\"EPSG\",\"3358\"]]\n",
     "region": {
       "b": 0.0,
       "cells": 1,
       "cells3": 29535,
       "cols": 1,
       "cols3": 179,
       "depths": 1,
       "e": 639530.0,
       "ewres": 1790.0,
       "ewres3": 10.0,
       "n": 221230.0,
       "nsres": 1650.0,
       "nsres3": 10.0,
       "projection": 99,
       "rows": 1,
       "rows3": 165,
       "s": 219580.0,
       "t": 1.0,
       "tbres": 1.0,
       "w": 637740.0,
       "zone": 0
     }
   },
   "progress": {
     "num_of_steps": 2,
     "step": 2
   },
   "resource_id": "resource_id-181a0936-9deb-481c-a1a6-6c9f46f97594",
   "status": "finished",
   "time_delta": 0.16365694999694824,
   "timestamp": 1564691405.8811285,
   "urls": {
     "resources": [],
     "status": "http://actinia.mundialis.de/api/v3/resources/demouser/resource_id-181a0936-9deb-481c-a1a6-6c9f46f97594"
   },
   "user_id": "demouser"
 }
```

To list all mapsets located in the project *nc_spm_08* the following
API call is used:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/projects/nc_spm_08/mapsets"
```

The response of this synchronous call lists all mapsets of the project
in the *process_results* section:

```json
 {
   "accept_datetime": "2019-08-01 20:31:11.325953",
   "accept_timestamp": 1564691471.325952,
   "api_info": {
     "endpoint": "listmapsetsresource",
     "method": "GET",
     "path": "/api/v3/projects/nc_spm_08/mapsets",
     "request_url": "http://actinia.mundialis.de/api/v3/projects/nc_spm_08/mapsets"
   },
   "datetime": "2019-08-01 20:31:11.430294",
   "http_code": 200,
   "message": "Processing successfully finished",
   "process_chain_list": [
     {
       "1": {
         "flags": "l",
         "inputs": {
           "separator": "newline"
         },
         "module": "g.mapsets"
       }
     }
   ],
   "process_log": [
     {
       "executable": "g.mapsets",
       "parameter": [
         "separator=newline",
         "-l"
       ],
       "return_code": 0,
       "run_time": 0.05030035972595215,
       "stderr": [
         "Available mapsets:",
         ""
       ],
       "stdout": "PERMANENT\nlandsat\nnew_user_mapset\n"
     }
   ],
   "process_results": [
     "PERMANENT",
     "landsat",
     "new_user_mapset"
   ],
   "progress": {
     "num_of_steps": 1,
     "step": 1
   },
   "resource_id": "resource_id-8365e42b-8111-4026-abb0-df86677ff3b9",
   "status": "finished",
   "time_delta": 0.10437250137329102,
   "timestamp": 1564691471.4302812,
   "urls": {
     "resources": [],
     "status": "http://actinia.mundialis.de/api/v3/resources/demouser/resource_id-8365e42b-8111-4026-abb0-df86677ff3b9"
   },
   "user_id": "demouser"
 }
```

Using the following API call will show all information about the mapset
*PERMANENT*:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/projects/nc_spm_08/mapsets/PERMANENT/info"
```

The response shows the region of the mapset and the projection of the
project in the *process_results* section:

```json
 {
   "accept_datetime": "2019-08-01 20:31:51.665042",
   "accept_timestamp": 1564691511.6650407,
   "api_info": {
     "endpoint": "mapsetmanagementresourceuser",
     "method": "GET",
     "path": "/api/v3/projects/nc_spm_08/mapsets/PERMANENT/info",
     "request_url": "http://actinia.mundialis.de/api/v3/projects/nc_spm_08/mapsets/PERMANENT/info"
   },
   "datetime": "2019-08-01 20:31:51.810266",
   "http_code": 200,
   "message": "Processing successfully finished",
   "process_chain_list": [
     {
       "1": {
         "flags": "ug3",
         "module": "g.region"
       },
       "2": {
         "flags": "fw",
         "module": "g.proj"
       }
     }
   ],
   "process_log": [
     {
       "executable": "g.region",
       "parameter": [
         "-ug3"
       ],
       "return_code": 0,
       "run_time": 0.05028796195983887,
       "stderr": [
         ""
       ],
       "stdout": "projection=99\nzone=0\nn=221230\ns=219580\nw=637740\ne=639530\nt=1\nb=0\nnsres=1650\nnsres3=10\newres=1790\newres3=10\ntbres=1\nrows=1\nrows3=165\ncols=1\ncols3=179\ndepths=1\ncells=1\ncells3=29535\n"
     },
     {
       "executable": "g.proj",
       "parameter": [
         "-fw"
       ],
       "return_code": 0,
       "run_time": 0.05027055740356445,
       "stderr": [
         ""
       ],
       "stdout": "PROJCS[\"NAD83(HARN) / North Carolina\",GEOGCS[\"NAD83(HARN)\",DATUM[\"NAD83_High_Accuracy_Reference_Network\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6152\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4152\"]],PROJECTION[\"Lambert_Conformal_Conic_2SP\"],PARAMETER[\"standard_parallel_1\",36.16666666666666],PARAMETER[\"standard_parallel_2\",34.33333333333334],PARAMETER[\"latitude_of_origin\",33.75],PARAMETER[\"central_meridian\",-79],PARAMETER[\"false_easting\",609601.22],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"X\",EAST],AXIS[\"Y\",NORTH],AUTHORITY[\"EPSG\",\"3358\"]]\n"
     }
   ],
   "process_results": {
     "projection": "PROJCS[\"NAD83(HARN) / North Carolina\",GEOGCS[\"NAD83(HARN)\",DATUM[\"NAD83_High_Accuracy_Reference_Network\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6152\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4152\"]],PROJECTION[\"Lambert_Conformal_Conic_2SP\"],PARAMETER[\"standard_parallel_1\",36.16666666666666],PARAMETER[\"standard_parallel_2\",34.33333333333334],PARAMETER[\"latitude_of_origin\",33.75],PARAMETER[\"central_meridian\",-79],PARAMETER[\"false_easting\",609601.22],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"X\",EAST],AXIS[\"Y\",NORTH],AUTHORITY[\"EPSG\",\"3358\"]]\n",
     "region": {
       "b": 0.0,
       "cells": 1,
       "cells3": 29535,
       "cols": 1,
       "cols3": 179,
       "depths": 1,
       "e": 639530.0,
       "ewres": 1790.0,
       "ewres3": 10.0,
       "n": 221230.0,
       "nsres": 1650.0,
       "nsres3": 10.0,
       "projection": 99,
       "rows": 1,
       "rows3": 165,
       "s": 219580.0,
       "t": 1.0,
       "tbres": 1.0,
       "w": 637740.0,
       "zone": 0
     }
   },
   "progress": {
     "num_of_steps": 2,
     "step": 2
   },
   "resource_id": "resource_id-d949c5c7-9ab9-4ca9-afbf-6b91d7abec5a",
   "status": "finished",
   "time_delta": 0.14524579048156738,
   "timestamp": 1564691511.8102555,
   "urls": {
     "resources": [],
     "status": "http://actinia.mundialis.de/api/v3/resources/demouser/resource_id-d949c5c7-9ab9-4ca9-afbf-6b91d7abec5a"
   },
   "user_id": "demouser"
 }
```

## Access to raster layers in the persistent database

The `modis_lst` mapset of the `nc_spm_08` project contains monthly
MODIS land surface temperature data. The space-time raster dataset
`LST_Day_monthly` consists of 24 raster layers covering the period
from January 2015 to January 2017. We list all raster layers available
in this mapset:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/projects/nc_spm_08/mapsets/modis_lst/raster_layers"
```

The response lists all raster layers of the mapset in the
*process_results* section:

```json
 {
  "accept_datetime": "2026-07-14 13:03:50.622823",
  "accept_timestamp": 1784034230.6228213,
  "api_info": {
    "endpoint": "rasterlayersresource",
    "method": "GET",
    "path": "/api/v3/projects/nc_spm_08/mapsets/modis_lst/raster_layers",
    "request_url": "http://actinia.mundialis.de/api/v3/projects/nc_spm_08/mapsets/modis_lst/raster_layers"
  },
  "datetime": "2026-07-14 13:03:50.837373",
  "http_code": 200,
  "message": "Processing successfully finished",
  "process_chain_list": [
    {
      "1": {
        "inputs": {
          "mapset": "modis_lst",
          "type": "raster"
        },
        "module": "g.list"
      }
    }
  ],
  "process_log": [
    {
      "executable": "g.list",
      "id": "1",
      "parameter": [
        "mapset=modis_lst",
        "type=raster"
      ],
      "return_code": 0,
      "run_time": 0.15046429634094238,
      "stderr": [
        ""
      ],
      "stdout": "..."
    }
  ],
  "process_results": [
    "MOD11B3.A2015001.h11v05.single_LST_Day_6km",
    "MOD11B3.A2015032.h11v05.single_LST_Day_6km",
    "...",
    "MOD11B3.A2016306.h11v05.single_LST_Day_6km",
    "MOD11B3.A2016336.h11v05.single_LST_Day_6km"
  ],
  "process_time_delta": 0.15128397941589355,
  "progress": {
    "num_of_steps": 1,
    "step": 1
  },
  "queue": "local",
  "resource_id": "resource_id-0aea41a9-be71-4248-a12e-9378d193fbb6",
  "start_datetime": "2026-07-14 13:03:50.686130",
  "start_timestamp": 1784034230.6861298,
  "status": "finished",
  "time_delta": 0.21456289291381836,
  "timestamp": 1784034230.8373697,
  "urls": {
    "resources": [],
    "status": "https://actinia.mundialis.de/api/v3/resources/demouser/resource_id-0aea41a9-be71-4248-a12e-9378d193fbb6"
  },
  "user_id": "demouser"
}

```

Show info about the raster layer
*MOD11B3.A2016336.h11v05.single_LST_Day_6km*:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/projects/nc_spm_08/mapsets/modis_lst/raster_layers/MOD11B3.A2016336.h11v05.single_LST_Day_6km"
```

The response lists information about the raster layer
*MOD11B3.A2016336.h11v05.single_LST_Day_6km* in the *process_results*
section:

```json
{
  "accept_datetime": "2026-07-14 13:14:42.341554",
  "accept_timestamp": 1784034882.3415532,
  "api_info": {
    "endpoint": "rasterlayerresource",
    "method": "GET",
    "path": "/api/v3/projects/nc_spm_08/mapsets/modis_lst/raster_layers/MOD11B3.A2016336.h11v05.single_LST_Day_6km",
    "request_url": "http://actinia.mundialis.de/api/v3/projects/nc_spm_08/mapsets/modis_lst/raster_layers/MOD11B3.A2016336.h11v05.single_LST_Day_6km"
  },
  "datetime": "2026-07-14 13:14:42.525335",
  "http_code": 200,
  "message": "Processing successfully finished",
  "process_chain_list": [
    {
      "1": {
        "flags": "gre",
        "inputs": {
          "map": "MOD11B3.A2016336.h11v05.single_LST_Day_6km@modis_lst"
        },
        "module": "r.info"
      }
    }
  ],
  "process_log": [
    {
      "executable": "r.info",
      "id": "1",
      "mapset_size": 481,
      "parameter": [
        "map=MOD11B3.A2016336.h11v05.single_LST_Day_6km@modis_lst",
        "-gre"
      ],
      "return_code": 0,
      "run_time": 0.10122942924499512,
      "stderr": [
        ""
      ],
      "stdout": "north=760180.12411493\nsouth=-415819.87588507\neast=1550934.46411531\nwest=-448265.53588469\nnsres=5600\newres=5600\nrows=210\ncols=357\ncells=74970\ndatatype=CELL\nncats=0\nmin=13429\nmax=14564\nmap=MOD11B3.A2016336.h11v05.single_LST_Day_6km\nmaptype=raster\nmapset=modis_lst\nlocation=nc_spm_08\nproject=nc_spm_08\ndatabase=/actinia_core/workspace/temp_db/gisdbase_a1be8b7dcb6646b79bbb6d12b9b96cff\ndate=\"Tue May 23 11:12:16 2017\"\ncreator=\"veroandreo\"\ntitle=\"MOD11B3.A2016336.h11v05.single_LST_Day_6km\"\ntimestamp=\"1 Dec 2016 00:00:00 / 1 Jan 2017 00:00:00\"\nunits=\"none\"\nvdatum=\"none\"\nsemantic_label=\"none\"\nsource1=\"MODIS NASA\"\nsource2=\"\"\ndescription=\"generated by r.in.gdal\"\ncomments=\"r.in.gdal --overwrite --quiet input=\"/home/veroandreo/MOD11B3.A20163\\36.h11v05.single_LST_Day_6km.tif\" output=\"MOD11B3.A2016336.h11v05.si\\ngle_LST_Day_6km\" memory=300 offset=0 num_digits=0Imported with r.modis.import\"\n"
    }
  ],
  "process_results": {
    "cells": "74970",
    "cols": "357",
    "comments": "\"r.in.gdal --overwrite --quiet input=\"/home/veroandreo/MOD11B3.A20163\\36.h11v05.single_LST_Day_6km.tif\" output=\"MOD11B3.A2016336.h11v05.si\\ngle_LST_Day_6km\" memory=300 offset=0 num_digits=0Imported with r.modis.import\"",
    "creator": "\"veroandreo\"",
    "database": "/actinia_core/workspace/temp_db/gisdbase_a1be8b7dcb6646b79bbb6d12b9b96cff",
    "datatype": "CELL",
    "date": "\"Tue May 23 11:12:16 2017\"",
    "description": "\"generated by r.in.gdal\"",
    "east": "1550934.46411531",
    "ewres": "5600",
    "location": "nc_spm_08",
    "map": "MOD11B3.A2016336.h11v05.single_LST_Day_6km",
    "mapset": "modis_lst",
    "maptype": "raster",
    "max": "14564",
    "min": "13429",
    "ncats": "0",
    "north": "760180.12411493",
    "nsres": "5600",
    "project": "nc_spm_08",
    "rows": "210",
    "semantic_label": "\"none\"",
    "source1": "\"MODIS NASA\"",
    "source2": "\"\"",
    "south": "-415819.87588507",
    "timestamp": "\"1 Dec 2016 00:00:00 / 1 Jan 2017 00:00:00\"",
    "title": "\"MOD11B3.A2016336.h11v05.single_LST_Day_6km\"",
    "units": "\"none\"",
    "vdatum": "\"none\"",
    "west": "-448265.53588469"
  },
  "process_time_delta": 0.10262918472290039,
  "progress": {
    "num_of_steps": 1,
    "step": 1
  },
  "queue": "local",
  "resource_id": "resource_id-3588f1c6-7d49-4233-9a18-0618a81ee129",
  "start_datetime": "2026-07-14 13:14:42.422749",
  "start_timestamp": 1784034882.4227493,
  "status": "finished",
  "time_delta": 0.18379592895507812,
  "timestamp": 1784034882.5253313,
  "urls": {
    "resources": [],
    "status": "https://actinia.mundialis.de/api/v3/resources/demouser/resource_id-3588f1c6-7d49-4233-9a18-0618a81ee129"
  },
  "user_id": "demouser"
}
```

## Access to raster time-series in the persistent database

Actinia supports the analysis of time-series data based on the temporal
framework of GRASS GIS[^3], [^4]. A time-series dataset is available in
the `modis_lst` mapset of the `nc_spm_08` project. The time-series datatype is
called space-time raster dataset (strds) named `LST_Day_monthly`. 
It consists of 24 monthly raster layers covering the period from January 
2015 through December 2016.

We list all strds with the following API call:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/projects/nc_spm_08/mapsets/modis_lst/strds"
```

We receive two strds in the *process_results* section of the JSON
response:

```json
{
  "accept_datetime": "2026-07-14 13:29:09.482702",
  "accept_timestamp": 1784035749.4826996,
  "api_info": {
    "endpoint": "syncstrdslisterresource",
    "method": "GET",
    "path": "/api/v3/projects/nc_spm_08/mapsets/modis_lst/strds",
    "request_url": "http://actinia.mundialis.de/api/v3/projects/nc_spm_08/mapsets/modis_lst/strds"
  },
  "datetime": "2026-07-14 13:29:10.271687",
  "http_code": 200,
  "message": "Processing successfully finished",
  "process_chain_list": [
    {
      "1": {
        "inputs": {
          "column": "name",
          "type": "strds",
          "where": "mapset='modis_lst'"
        },
        "module": "t.list"
      }
    }
  ],
  "process_log": [
    {
      "executable": "t.list",
      "id": "1",
      "parameter": [
        "type=strds",
        "column=name",
        "where=mapset='modis_lst'"
      ],
      "return_code": 0,
      "run_time": 0.6523523330688477,
      "stderr": [
        "----------------------------------------------",
        "Space time raster datasets with absolute time available in mapset <modis_lst>:",
        ""
      ],
      "stdout": "LST_Day_monthly\n"
    }
  ],
  "process_results": [
    "LST_Day_monthly"
  ],
  "process_time_delta": 0.6531558036804199,
  "progress": {
    "num_of_steps": 1,
    "step": 1
  },
  "queue": "local",
  "resource_id": "resource_id-03597408-9f04-4d4b-9d88-0d7dc60a723f",
  "start_datetime": "2026-07-14 13:29:09.618572",
  "start_timestamp": 1784035749.618572,
  "status": "finished",
  "time_delta": 0.7889983654022217,
  "timestamp": 1784035750.271684,
  "urls": {
    "resources": [],
    "status": "https://actinia.mundialis.de/api/v3/resources/demouser/resource_id-03597408-9f04-4d4b-9d88-0d7dc60a723f"
  },
  "user_id": "demouser"
}

```

Use the following API call to retrieve information about the strds
`LST_Day_monthly`:
```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/projects/nc_spm_08/mapsets/modis_lst/strds/LST_Day_monthly"

```

All relevant information about strds `LST_Day_monthly` is located in the
`process_results` section of the JSON response:

```json
 {
  "accept_datetime": "2026-07-14 13:39:07.173213",
  "accept_timestamp": 1784036347.1732125,
  "api_info": {
    "endpoint": "strdsmanagementresource",
    "method": "GET",
    "path": "/api/v3/projects/nc_spm_08/mapsets/modis_lst/strds/LST_Day_monthly",
    "request_url": "http://actinia.mundialis.de/api/v3/projects/nc_spm_08/mapsets/modis_lst/strds/LST_Day_monthly"
  },
  "datetime": "2026-07-14 13:39:07.922543",
  "http_code": 200,
  "message": "Information gathering for STRDS <LST_Day_monthly> successful",
  "process_chain_list": [
    {
      "1": {
        "flags": "g",
        "inputs": {
          "input": "LST_Day_monthly",
          "type": "strds"
        },
        "module": "t.info"
      }
    }
  ],
  "process_log": [
    {
      "executable": "t.info",
      "id": "1",
      "parameter": [
        "type=strds",
        "input=LST_Day_monthly",
        "-g"
      ],
      "return_code": 0,
      "run_time": 0.6018106937408447,
      "stderr": [
        ""
      ],
      "stdout": "id=LST_Day_monthly@modis_lst\nname=LST_Day_monthly\nmapset=modis_lst\ncreator=mneteler\ntemporal_type=absolute\ncreation_time='2019-09-02 13:03:42.173278'\nmodification_time='2019-09-02 13:04:01.703962'\nsemantic_type=mean\nstart_time='2015-01-01 00:00:00'\nend_time='2017-01-01 00:00:00'\ngranularity='1 month'\nmap_time=interval\nnorth=760180.124115\nsouth=-415819.875885\neast=1550934.464115\nwest=-448265.535885\ntop=0.0\nbottom=0.0\nraster_register=raster_map_register_78a1d5e30c904a5db2d15b939b5b0a3b\nnsres_min=5600.0\nnsres_max=5600.0\newres_min=5600.0\newres_max=5600.0\nmin_min=12950.0\nmin_max=14714.0\nmax_min=14360.0\nmax_max=15650.0\naggregation_type=None\nnumber_of_semantic_labels=None\nsemantic_labels=None\nnumber_of_maps=24\n"
    }
  ],
  "process_results": {
    "aggregation_type": "None",
    "bottom": "0.0",
    "creation_time": "'2019-09-02 13:03:42.173278'",
    "creator": "mneteler",
    "east": "1550934.464115",
    "end_time": "'2017-01-01 00:00:00'",
    "ewres_max": "5600.0",
    "ewres_min": "5600.0",
    "granularity": "'1 month'",
    "id": "LST_Day_monthly@modis_lst",
    "map_time": "interval",
    "mapset": "modis_lst",
    "max_max": "15650.0",
    "max_min": "14360.0",
    "min_max": "14714.0",
    "min_min": "12950.0",
    "modification_time": "'2019-09-02 13:04:01.703962'",
    "name": "LST_Day_monthly",
    "north": "760180.124115",
    "nsres_max": "5600.0",
    "nsres_min": "5600.0",
    "number_of_maps": "24",
    "number_of_semantic_labels": "None",
    "raster_register": "raster_map_register_78a1d5e30c904a5db2d15b939b5b0a3b",
    "semantic_labels": "None",
    "semantic_type": "mean",
    "south": "-415819.875885",
    "start_time": "'2015-01-01 00:00:00'",
    "temporal_type": "absolute",
    "top": "0.0",
    "west": "-448265.535885"
  },
  "process_time_delta": 0.6027548313140869,
  "progress": {
    "num_of_steps": 1,
    "step": 1
  },
  "queue": "local",
  "resource_id": "resource_id-91c3d30e-74b1-47c6-b086-27f90ce3dec4",
  "start_datetime": "2026-07-14 13:39:07.319824",
  "start_timestamp": 1784036347.3198245,
  "status": "finished",
  "time_delta": 0.7493431568145752,
  "timestamp": 1784036347.9225404,
  "urls": {
    "resources": [],
    "status": "https://actinia.mundialis.de/api/v3/resources/demouser/resource_id-91c3d30e-74b1-47c6-b086-27f90ce3dec4"
  },
  "user_id": "demouser"
}

```

List all raster layers registered in the stdrs `LST_Day_monthly`,
including their timestamps:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/projects/nc_spm_08/mapsets/modis_lst/strds/LST_Day_monthly/raster_layers"

```

A list of about 24 registered raster layers, including their minimum and
maximum values, timestamps and spatial extent, is returned in the
process_results section of the JSON response:

```json
 {
  "accept_datetime": "2026-07-14 13:45:06.487105",
  "accept_timestamp": 1784036706.4871035,
  "api_info": {
    "endpoint": "strdsrastermanagement",
    "method": "GET",
    "path": "/api/v3/projects/nc_spm_08/mapsets/modis_lst/strds/LST_Day_monthly/raster_layers",
    "request_url": "http://actinia.mundialis.de/api/v3/projects/nc_spm_08/mapsets/modis_lst/strds/LST_Day_monthly/raster_layers"
  },
  "datetime": "2026-07-14 13:45:07.221363",
  "http_code": 200,
  "message": "Processing successfully finished",
  "process_chain_list": [
    {
      "1": {
        "flags": "u",
        "inputs": {
          "columns": "id,start_time,end_time,north,south,east,west,min,max,rows,cols",
          "input": "LST_Day_monthly@modis_lst",
          "separator": "|"
        },
        "module": "t.rast.list",
        "outputs": {
          "output": {
            "name": "/actinia_core/workspace/temp_db/gisdbase_94372f9dd3054f79b77b1759549de0c0/.tmp/tmp9hk2ewvh"
          }
        }
      }
    }
  ],
  "process_log": [
    {
      "executable": "t.rast.list",
      "id": "1",
      "parameter": [
        "input=LST_Day_monthly@modis_lst",
        "columns=id,start_time,end_time,north,south,east,west,min,max,rows,cols",
        "separator=|",
        "output=/actinia_core/workspace/temp_db/gisdbase_94372f9dd3054f79b77b1759549de0c0/.tmp/tmp9hk2ewvh",
        "-u"
      ],
      "return_code": 0,
      "run_time": 0.601790189743042,
      "stderr": [
        ""
      ],
      "stdout": ""
    }
  ],
  "process_results": [
    {
      "cols": "210",
      "east": "1550934.464115",
      "end_time": "2015-02-01 00:00:00",
      "id": "MOD11B3.A2015001.h11v05.single_LST_Day_6km@modis_lst",
      "max": "14396.0",
      "min": "13022.0",
      "north": "760180.124115",
      "rows": "357",
      "south": "-415819.875885",
      "start_time": "2015-01-01 00:00:00",
      "west": "-448265.535885"
    },
    {
      "..."
    },
    {
      "cols": "210",
      "east": "1550934.464115",
      "end_time": "2017-01-01 00:00:00",
      "id": "MOD11B3.A2016336.h11v05.single_LST_Day_6km@modis_lst",
      "max": "14564.0",
      "min": "13429.0",
      "north": "760180.124115",
      "rows": "357",
      "south": "-415819.875885",
      "start_time": "2016-12-01 00:00:00",
      "west": "-448265.535885"
    }
  ],
  "process_time_delta": 0.6028850078582764,
  "progress": {
    "num_of_steps": 1,
    "step": 1
  },
  "queue": "local",
  "resource_id": "resource_id-1f3b625a-e546-4a27-91ab-b353e0e66822",
  "start_datetime": "2026-07-14 13:45:06.618505",
  "start_timestamp": 1784036706.6185048,
  "status": "finished",
  "time_delta": 0.7342710494995117,
  "timestamp": 1784036707.2213552,
  "urls": {
    "resources": [],
    "status": "https://actinia.mundialis.de/api/v3/resources/demouser/resource_id-1f3b625a-e546-4a27-91ab-b353e0e66822"
  },
  "user_id": "demouser"
}

```

## Footnotes

[^1]: https://en.wikipedia.org/wiki/CURL
[^2]: https://www.getpostman.com/apps
[^3]: http://www.sciencedirect.com/science/article/pii/S136481521300282X
[^4]: http://www.tandfonline.com/doi/abs/10.1080/13658816.2017.1306862?journalCode=tgis20
