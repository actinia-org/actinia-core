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
export ACTINIA_URL=https://actinia.mundialis.de/latest
export AUTH='-u demouser:gu3st!pa55w0rd'
# other user credentials can be provided in the same way
```

## Access to locations and mapsets in the persistent database

The following API call lists all available locations in the actinia
persistent database (the `-i` includes the HTTP response headers):

```bash
 curl ${AUTH} -X GET -i "${ACTINIA_URL}/locations"
```

The output should look similar to this:

```json
 {
   "locations": [
     "latlong_wgs84",
     "ECAD",
     "nc_spm_08"
   ],
   "status": "success"
 }
```

To show the region settings and the projection of the GRASS GIS standard
location *nc_spm_08* the following REST call must be used:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/locations/nc_spm_08/info"
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
     "endpoint": "locationmanagementresourceuser",
     "method": "GET",
     "path": "/api/v3/locations/nc_spm_08/info",
     "request_url": "http://actinia.mundialis.de/api/v3/locations/nc_spm_08/info"
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

To list all mapsets located in the location *nc_spm_08* the following
API call is used:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/locations/nc_spm_08/mapsets"
```

The response of this synchronous call lists all mapsets of the location
in the *process_results* section:

```json
 {
   "accept_datetime": "2019-08-01 20:31:11.325953",
   "accept_timestamp": 1564691471.325952,
   "api_info": {
     "endpoint": "listmapsetsresource",
     "method": "GET",
     "path": "/api/v3/locations/nc_spm_08/mapsets",
     "request_url": "http://actinia.mundialis.de/api/v3/locations/nc_spm_08/mapsets"
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
 curl ${AUTH} -X GET "${ACTINIA_URL}/locations/nc_spm_08/mapsets/PERMANENT/info"
```

The response shows the region of the mapset and the projection of the
location in the *process_results* section:

```json
 {
   "accept_datetime": "2019-08-01 20:31:51.665042",
   "accept_timestamp": 1564691511.6650407,
   "api_info": {
     "endpoint": "mapsetmanagementresourceuser",
     "method": "GET",
     "path": "/api/v3/locations/nc_spm_08/mapsets/PERMANENT/info",
     "request_url": "http://actinia.mundialis.de/api/v3/locations/nc_spm_08/mapsets/PERMANENT/info"
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

The location ECAD contains yearly climate data (precipitation and
temperature) of Europe for 60 years. We list all raster layers of the
location ECAD in mapset *PERMANENT*:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/locations/ECAD/mapsets/PERMANENT/raster_layers"
```

The response lists all raster layers of the mapset in the
*process_results* section:

```json
 {
   "accept_datetime": "2018-05-30 09:13:51.627853",
   "accept_timestamp": 1527671631.6278517,
   "api_info": {
     "endpoint": "rasterlayersresource",
     "method": "GET",
     "path": "/api/v3/locations/ECAD/mapsets/PERMANENT/raster_layers",
     "request_url": "http://actinia.mundialis.de/api/v3/locations/ECAD/mapsets/PERMANENT/raster_layers"
   },
   "datetime": "2018-05-30 09:13:51.745702",
   "http_code": 200,
   "message": "Processing successfully finished",
   "process_chain_list": [
     {
       "1": {
         "inputs": {
           "mapset": "PERMANENT",
           "type": "raster"
         },
         "module": "g.list"
       }
     }
   ],
   "process_log": [
     {
       "executable": "g.list",
       "parameter": [
         "mapset=PERMANENT",
         "type=raster"
       ],
       "return_code": 0,
       "run_time": 0.05105090141296387,
       "stderr": [
         ""
       ],
       "stdout": "..."
     }
   ],
   "process_results": [
     "precipitation_yearly_mm_0",
     "precipitation_yearly_mm_1",
     "...",
     "precipitation_yearly_mm_61",
     "precipitation_yearly_mm_62",
     "temperature_mean_yearly_celsius_0",
     "temperature_mean_yearly_celsius_1",
     "...",
     "temperature_mean_yearly_celsius_61",
     "temperature_mean_yearly_celsius_62",
   ],
   "progress": {
     "num_of_steps": 1,
     "step": 1
   },
   "resource_id": "resource_id-114c7229-da85-4866-a33e-38172835e05f",
   "status": "finished",
   "time_delta": 0.11787867546081543,
   "timestamp": 1527671631.745685,
   "urls": {
     "resources": [],
     "status": "http://actinia.mundialis.de/api/v3/resources/demouser/resource_id-114c7229-da85-4866-a33e-38172835e05f"
   },
   "user_id": "demouser"
 }
```

Show info about the raster layer
*temperature_mean_yearly_celsius_60*:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/locations/ECAD/mapsets/PERMANENT/raster_layers/temperature_mean_yearly_celsius_60"
```

The response lists information about the raster layer
*temperature_mean_yearly_celsius_60* in the *process_results*
section:

```json
 {
   "accept_datetime": "2018-05-30 09:17:15.303480",
   "accept_timestamp": 1527671835.3034775,
   "api_info": {
     "endpoint": "rasterlayerresource",
     "method": "GET",
     "path": "/api/v3/locations/ECAD/mapsets/PERMANENT/raster_layers/temperature_mean_yearly_celsius_60",
     "request_url": "http://actinia.mundialis.de/api/v3/locations/ECAD/mapsets/PERMANENT/raster_layers/temperature_mean_yearly_celsius_60"
   },
   "datetime": "2018-05-30 09:17:15.437797",
   "http_code": 200,
   "message": "Processing successfully finished",
   "process_chain_list": [
     {
       "1": {
         "flags": "gre",
         "inputs": {
           "map": "temperature_mean_yearly_celsius_60@PERMANENT"
         },
         "module": "r.info"
       }
     }
   ],
   "process_log": [
     {
       "executable": "r.info",
       "parameter": [
         "map=temperature_mean_yearly_celsius_60@PERMANENT",
         "-gre"
       ],
       "return_code": 0,
       "run_time": 0.05033993721008301,
       "stderr": [
         ""
       ],
       "stdout": "..."
     }
   ],
   "process_results": {
     "cells": "93264",
     "cols": "464",
     "comments": "\"r.in.gdal --overwrite input=\"temperature_mean_yearly_celsius_60.tif\"\\ output=\"temperature_mean_yearly_celsius_60\" memory=300 offset=0 num\\_digits=0\"",
     "creator": "\"soeren\"",
     "database": "/actinia/workspace/temp_db/gisdbase_db61f5f149474744ab31bbf86f49b5dc",
     "datatype": "DCELL",
     "date": "\"Fri Dec 29 15:58:10 2017\"",
     "description": "\"generated by r.in.gdal\"",
     "east": "75.5",
     "ewres": "0.25",
     "location": "ECAD",
     "map": "temperature_mean_yearly_celsius_60",
     "mapset": "PERMANENT",
     "max": "29.406963562753",
     "min": "-16.208384568171",
     "ncats": "0",
     "north": "75.5",
     "nsres": "0.25",
     "rows": "201",
     "source1": "\"\"",
     "source2": "\"\"",
     "south": "25.25",
     "timestamp": "\"1 Jan 2010 00:00:00 / 1 Jan 2011 00:00:00\"",
     "title": "\"temperature_mean_yearly_celsius_60\"",
     "units": "\"none\"",
     "vdatum": "\"none\"",
     "west": "-40.5"
   },
   "progress": {
     "num_of_steps": 1,
     "step": 1
   },
   "resource_id": "resource_id-7d4f36ba-3410-4281-b3e4-7b4aeff5f978",
   "status": "finished",
   "time_delta": 0.13434433937072754,
   "timestamp": 1527671835.4377818,
   "urls": {
     "resources": [],
     "status": "http://actinia.mundialis.de/api/v3/resources/demouser/resource_id-7d4f36ba-3410-4281-b3e4-7b4aeff5f978"
   },
   "user_id": "demouser"
 }
```

## Access to raster time-series in the persistent database

Actinia supports the analysis of time-series data based on the temporal
framework of GRASS GIS[^3], [^4]. A time-series datatype is located in
location *ECAD* with mapsets *PERMANENT*. The time-series datatype is
called space-time raster dataset (strds) and represents a time-stamped
series of yearly temperature and precipitation data for Europe.

We list all strds with the following API call:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/locations/ECAD/mapsets/PERMANENT/strds"
```

We receive two strds in the *process_results* section of the JSON
response:

```json
 {
   "accept_datetime": "2018-05-30 09:18:16.737226",
   "accept_timestamp": 1527671896.737225,
   "api_info": {
     "endpoint": "syncstrdslisterresource",
     "method": "GET",
     "path": "api/v3/locations/ECAD/mapsets/PERMANENT/strds",
     "request_url": "http://actinia.mundialis.de/api/v3/locations/ECAD/mapsets/PERMANENT/strds"
   },
   "datetime": "2018-05-30 09:18:17.351918",
   "http_code": 200,
   "message": "Processing successfully finished",
   "process_chain_list": [
     {
       "1": {
         "inputs": {
           "column": "name",
           "type": "strds",
           "where": "mapset='PERMANENT'"
         },
         "module": "t.list"
       }
     }
   ],
   "process_log": [
     {
       "executable": "t.list",
       "parameter": [
         "type=strds",
         "column=name",
         "where=mapset='PERMANENT'"
       ],
       "return_code": 0,
       "run_time": 0.5758285522460938,
       "stderr": [
         "----------------------------------------------",
         "Space time raster datasets with absolute time available in mapset <PERMANENT>:",
         ""
       ],
       "stdout": "precipitation_1950_2013_yearly_mm\ntemperature_mean_1950_2013_yearly_celsius\n"
     }
   ],
   "process_results": [
     "precipitation_1950_2013_yearly_mm",
     "temperature_mean_1950_2013_yearly_celsius"
   ],
   "progress": {
     "num_of_steps": 1,
     "step": 1
   },
   "resource_id": "resource_id-827f9272-9aa1-467e-8eba-def7003522e3",
   "status": "finished",
   "time_delta": 0.6147146224975586,
   "timestamp": 1527671897.3519022,
   "urls": {
     "resources": [],
     "status": "http://actinia.mundialis.de/api/v3/resources/demouser/resource_id-827f9272-9aa1-467e-8eba-def7003522e3"
   },
   "user_id": "demouser"
 }
```

Use the following API call to receive information about the strds
*temperature_mean_1950_2013_yearly_celsius*.

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius"
```

All relevant information about strds
*temperature_mean_1950_2013_yearly_celsius* is located in the
*process_results* section of the JSON response:

```json
 {
   "accept_datetime": "2018-05-30 09:19:24.941032",
   "accept_timestamp": 1527671964.9410288,
   "api_info": {
     "endpoint": "strdsmanagementresource",
     "method": "GET",
     "path": "/api/v3/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius",
     "request_url": "http://actinia.mundialis.de/api/v3/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius"
   },
   "datetime": "2018-05-30 09:19:25.519419",
   "http_code": 200,
   "message": "Information gathering for STRDS <temperature_mean_1950_2013_yearly_celsius> successful",
   "process_chain_list": [
     {
       "1": {
         "flags": "g",
         "inputs": {
           "input": "temperature_mean_1950_2013_yearly_celsius",
           "type": "strds"
         },
         "module": "t.info"
       }
     }
   ],
   "process_log": [
     {
       "executable": "t.info",
       "parameter": [
         "type=strds",
         "input=temperature_mean_1950_2013_yearly_celsius",
         "-g"
       ],
       "return_code": 0,
       "run_time": 0.513615608215332,
       "stderr": [
         ""
       ],
       "stdout": "..."
     }
   ],
   "process_results": {
     "aggregation_type": "None",
     "bottom": "0.0",
     "creation_time": "2017-12-29 15:58:06.446519",
     "creator": "soeren",
     "east": "75.5",
     "end_time": "2013-01-01 00:00:00",
     "ewres_max": "0.25",
     "ewres_min": "0.25",
     "granularity": "1 year",
     "id": "temperature_mean_1950_2013_yearly_celsius@PERMANENT",
     "map_time": "interval",
     "mapset": "PERMANENT",
     "max_max": "31.193529",
     "max_min": "19.189924",
     "min_max": "-6.724322",
     "min_min": "-21.672401",
     "modification_time": "2017-12-29 15:58:10.919466",
     "name": "temperature_mean_1950_2013_yearly_celsius",
     "north": "75.5",
     "nsres_max": "0.25",
     "nsres_min": "0.25",
     "number_of_maps": "63",
     "raster_register": "raster_map_register_522689142dfe42cbab0721934d66dac3",
     "semantic_type": "mean",
     "south": "25.25",
     "start_time": "1950-01-01 00:00:00",
     "temporal_type": "absolute",
     "top": "0.0",
     "west": "-40.5"
   },
   "progress": {
     "num_of_steps": 1,
     "step": 1
   },
   "resource_id": "resource_id-15acb503-5ef9-4a89-89df-3a1291811a5d",
   "status": "finished",
   "time_delta": 0.5784096717834473,
   "timestamp": 1527671965.519405,
   "urls": {
     "resources": [],
     "status": "http://actinia.mundialis.de/api/v3/resources/demouser/resource_id-15acb503-5ef9-4a89-89df-3a1291811a5d"
   },
   "user_id": "demouser"
 }
```

List all raster layers that are registered in the strds
*temperature_mean_1950_2013_yearly_celsius* with time-stamps:

```bash
 curl ${AUTH} -X GET "${ACTINIA_URL}/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius/raster_layers"
```

A list of about 60 raster layers with minimum, maximum values,
time-stamps and spatial extent will be located in the *process_results*
section of the JSON response:

```json
 {
   "accept_datetime": "2018-05-30 09:20:30.633439",
   "accept_timestamp": 1527672030.6334376,
   "api_info": {
     "endpoint": "strdsrastermanagement",
     "method": "GET",
     "path": "/api/v3/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius/raster_layers",
     "request_url": "http://actinia.mundialis.de/api/v3/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius/raster_layers"
   },
   "datetime": "2018-05-30 09:20:31.197637",
   "http_code": 200,
   "message": "Processing successfully finished",
   "process_chain_list": [
     {
       "1": {
         "flags": "u",
         "inputs": {
           "columns": "id,start_time,end_time,north,south,east,west,min,max,rows,cols",
           "input": "temperature_mean_1950_2013_yearly_celsius@PERMANENT",
           "separator": "|"
         },
         "module": "t.rast.list",
         "outputs": {
           "output": {
             "name": "/actinia/workspace/temp_db/gisdbase_ec60c0dd721947e38348f4a07e563b5e/.tmp/tmpah7edtxb"
           }
         }
       }
     }
   ],
   "process_log": [
     {
       "executable": "t.rast.list",
       "parameter": [
         "input=temperature_mean_1950_2013_yearly_celsius@PERMANENT",
         "columns=id,start_time,end_time,north,south,east,west,min,max,rows,cols",
         "separator=|",
         "output=/actinia/workspace/temp_db/gisdbase_ec60c0dd721947e38348f4a07e563b5e/.tmp/tmpah7edtxb",
         "-u"
       ],
       "return_code": 0,
       "run_time": 0.5160176753997803,
       "stderr": [
         ""
       ],
       "stdout": ""
     }
   ],
   "process_results": [
     {
       "cols": "201",
       "east": "75.5",
       "end_time": "1951-01-01 00:00:00",
       "id": "temperature_mean_yearly_celsius_0@PERMANENT",
       "max": "20.893369",
       "min": "-7.705292",
       "north": "75.5",
       "rows": "464",
       "south": "25.25",
       "start_time": "1950-01-01 00:00:00",
       "west": "-40.5"
     },
     {
       "..."
     },
     {
       "cols": "201",
       "east": "75.5",
       "end_time": "2013-01-01 00:00:00",
       "id": "temperature_mean_yearly_celsius_62@PERMANENT",
       "max": "28.581454",
       "min": "-18.443574",
       "north": "75.5",
       "rows": "464",
       "south": "25.25",
       "start_time": "2012-01-01 00:00:00",
       "west": "-40.5"
     }
   ],
   "progress": {
     "num_of_steps": 1,
     "step": 1
   },
   "resource_id": "resource_id-3661533a-cb2b-4875-ac7a-be97a99e90da",
   "status": "finished",
   "time_delta": 0.5642266273498535,
   "timestamp": 1527672031.1976202,
   "urls": {
     "resources": [],
     "status": "http://actinia.mundialis.de/api/v3/resources/demouser/resource_id-3661533a-cb2b-4875-ac7a-be97a99e90da"
   },
   "user_id": "demouser"
 }
```

**Footnotes**

[^1]: https://en.wikipedia.org/wiki/CURL
[^2]: https://www.getpostman.com/apps
[^3]: http://www.sciencedirect.com/science/article/pii/S136481521300282X
[^4]: http://www.tandfonline.com/doi/abs/10.1080/13658816.2017.1306862?journalCode=tgis20
