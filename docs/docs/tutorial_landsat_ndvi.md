# Landsat NDVI computation

Actinia provides several API calls to compute satellite specific
parameters:

<https://redocly.github.io/redoc/?url=https://actinia.mundialis.de/latest/swagger.json#tag-Satellite-Image-Algorithms>

We will use the Unix shell and curl to access the REST API. First open a shell of choice (we use bash here) and setup the login information, the  IP address and the port on which the actinia service is running, so you can simply change the IP and port if your server uses a different
address:

```bash
export ACTINIA_URL=https://actinia.mundialis.de/latest
export AUTH='-u demouser:gu3st!pa55w0rd'
# other user credentials can be provided in the same way
```

The NDVI is an important parameter that is derived from multi-spectral
satellite images. The following asynchronous API call computes the NDVI
of the Landsat8 scene **LC80440342016259LGN00** with TOAR top of
atmosphere correction. It is designed to hide the complexity of Landsat
scene downloading, reprojection, atmospheric correction, statistical
analysis and preview rendering in a single call using a self describing
url.

```bash
 curl ${AUTH} -X POST "${ACTINIA_URL}/landsat_process/LC80440342016259LGN00/TOAR/NDVI"
```

The response contains the status URL that must be polled using a GET
request to show the current processing status and eventually the
processing result.

```json
 {
   "accept_datetime": "2018-05-30 10:52:19.545323",
   "accept_timestamp": 1527677539.5453222,
   "api_info": {
     "endpoint": "asyncephemerallandsatprocessingresource",
     "method": "POST",
     "path": "/api/v3/landsat_process/LC80440342016259LGN00/TOAR/NDVI",
     "request_url": "http://actinia.mundialis.de/api/v3/landsat_process/LC80440342016259LGN00/TOAR/NDVI"
   },
   "datetime": "2018-05-30 10:52:19.545774",
   "http_code": 200,
   "message": "Resource accepted",
   "process_chain_list": [],
   "process_results": {},
   "resource_id": "resource_id-a12d80c1-539a-45b9-a78c-ee4014f50d03",
   "status": "accepted",
   "time_delta": 0.000457763671875,
   "timestamp": 1527677539.5457737,
   "urls": {
     "resources": [],
     "status": "https://actinia.mundialis.de/api/v3/resources/demouser/resource_id-a12d80c1-539a-45b9-a78c-ee4014f50d03"
   },
   "user_id": "demouser"
 }
```

Request the status of the asynchronous API call by polling the status
URL. Be aware that you have to use your status url as the resource id will change for different NDVI API
calls.

```bash
 curl -L ${AUTH} -X GET "https://actinia.mundialis.de/api/v3/resources/demouser/resource_id-a12d80c1-539a-45b9-a78c-ee4014f50d03"
```

The final result will contain a complete processing list as well as
URL's to the resulting PNG preview image, the created NDVI GeoTiff file
as well as univariate statistics of the computed NDVI scene.

```json
 {
   "accept_datetime": "2018-05-30 11:16:03.033305",
   "accept_timestamp": 1527678963.033304,
   "api_info": {
     "endpoint": "asyncephemerallandsatprocessingresource",
     "method": "POST",
     "path": "/api/v3/landsat_process/LC80440342016259LGN00/TOAR/NDVI",
     "request_url": "http:///actinia.mundialis.de/api/v3/landsat_process/LC80440342016259LGN00/TOAR/NDVI"
   },
   "datetime": "2018-05-30 11:22:58.315162",
   "http_code": 200,
   "message": "Processing successfully finished",
   "process_chain_list": [
     {
       "1": {
         "flags": "g",
         "inputs": {
           "map": "LC80440342016259LGN00_TOAR_NDVI"
         },
         "module": "r.univar",
         "outputs": {
           "output": {
             "name": "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/tmpkiv0uv6z.univar"
           }
         }
       }
     },
     {
       "1": {
         "flags": "n",
         "inputs": {
           "map": "LC80440342016259LGN00_TOAR_NDVI"
         },
         "module": "d.rast"
       },
       "2": {
         "flags": "n",
         "inputs": {
           "at": "8,92,0,7",
           "raster": "LC80440342016259LGN00_TOAR_NDVI"
         },
         "module": "d.legend"
       }
     }
   ],
   "process_log": [
     {
       "executable": "/usr/bin/wget",
       "parameter": [
         "-t5",
         "-c",
         "-q",
         "-O",
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B6.TIF",
         "https://storage.googleapis.com/gcp-public-data-landsat/LC08/PRE/044/034/LC80440342016259LGN00/LC80440342016259LGN00_B6.TIF"
       ],
       "return_code": 0,
       "run_time": 23.63347291946411,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/bin/mv",
       "parameter": [
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B6.TIF",
         "/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B6.TIF"
       ],
       "return_code": 0,
       "run_time": 0.05022144317626953,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/usr/bin/wget",
       "parameter": [
         "-t5",
         "-c",
         "-q",
         "-O",
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B7.TIF",
         "https://storage.googleapis.com/gcp-public-data-landsat/LC08/PRE/044/034/LC80440342016259LGN00/LC80440342016259LGN00_B7.TIF"
       ],
       "return_code": 0,
       "run_time": 22.89448094367981,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/bin/mv",
       "parameter": [
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B7.TIF",
         "/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B7.TIF"
       ],
       "return_code": 0,
       "run_time": 0.051961421966552734,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/usr/bin/wget",
       "parameter": [
         "-t5",
         "-c",
         "-q",
         "-O",
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B8.TIF",
         "https://storage.googleapis.com/gcp-public-data-landsat/LC08/PRE/044/034/LC80440342016259LGN00/LC80440342016259LGN00_B8.TIF"
       ],
       "return_code": 0,
       "run_time": 83.04966020584106,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/bin/mv",
       "parameter": [
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B8.TIF",
         "/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B8.TIF"
       ],
       "return_code": 0,
       "run_time": 0.05012321472167969,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/usr/bin/wget",
       "parameter": [
         "-t5",
         "-c",
         "-q",
         "-O",
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B9.TIF",
         "https://storage.googleapis.com/gcp-public-data-landsat/LC08/PRE/044/034/LC80440342016259LGN00/LC80440342016259LGN00_B9.TIF"
       ],
       "return_code": 0,
       "run_time": 11.948487043380737,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/bin/mv",
       "parameter": [
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B9.TIF",
         "/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B9.TIF"
       ],
       "return_code": 0,
       "run_time": 0.05081939697265625,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/usr/bin/wget",
       "parameter": [
         "-t5",
         "-c",
         "-q",
         "-O",
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B10.TIF",
         "https://storage.googleapis.com/gcp-public-data-landsat/LC08/PRE/044/034/LC80440342016259LGN00/LC80440342016259LGN00_B10.TIF"
       ],
       "return_code": 0,
       "run_time": 15.688527345657349,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/bin/mv",
       "parameter": [
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B10.TIF",
         "/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B10.TIF"
       ],
       "return_code": 0,
       "run_time": 0.05163097381591797,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/usr/bin/wget",
       "parameter": [
         "-t5",
         "-c",
         "-q",
         "-O",
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B11.TIF",
         "https://storage.googleapis.com/gcp-public-data-landsat/LC08/PRE/044/034/LC80440342016259LGN00/LC80440342016259LGN00_B11.TIF"
       ],
       "return_code": 0,
       "run_time": 15.100370645523071,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/bin/mv",
       "parameter": [
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_B11.TIF",
         "/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B11.TIF"
       ],
       "return_code": 0,
       "run_time": 0.05057358741760254,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/usr/bin/wget",
       "parameter": [
         "-t5",
         "-c",
         "-q",
         "-O",
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_MTL.txt",
         "https://storage.googleapis.com/gcp-public-data-landsat/LC08/PRE/044/034/LC80440342016259LGN00/LC80440342016259LGN00_MTL.txt"
       ],
       "return_code": 0,
       "run_time": 0.25395917892456055,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "/bin/mv",
       "parameter": [
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_MTL.txt",
         "/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_MTL.txt"
       ],
       "return_code": 0,
       "run_time": 0.05015206336975098,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "python3",
       "parameter": [
         "/usr/local/bin/grass",
         "-e",
         "-c",
         "/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B1.TIF",
         "/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/Landsat"
       ],
       "return_code": 0,
       "run_time": 0.15161657333374023,
       "stderr": [
         "Default locale settings are missing. GRASS running with C locale.WARNING: Searched for a web browser, but none found",
         "Creating new GRASS GIS location/mapset...",
         "Cleaning up temporary files...",
         ""
       ],
       "stdout": "Default locale not found, using UTF-8\n"
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B1.TIF",
         "output=LC80440342016259LGN00.1",
         "--q"
       ],
       "return_code": 0,
       "run_time": 3.093010902404785,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B2.TIF",
         "output=LC80440342016259LGN00.2",
         "--q"
       ],
       "return_code": 0,
       "run_time": 3.020535707473755,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B3.TIF",
         "output=LC80440342016259LGN00.3",
         "--q"
       ],
       "return_code": 0,
       "run_time": 2.9988090991973877,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B4.TIF",
         "output=LC80440342016259LGN00.4",
         "--q"
       ],
       "return_code": 0,
       "run_time": 3.0504379272460938,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B5.TIF",
         "output=LC80440342016259LGN00.5",
         "--q"
       ],
       "return_code": 0,
       "run_time": 3.0378293991088867,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B6.TIF",
         "output=LC80440342016259LGN00.6",
         "--q"
       ],
       "return_code": 0,
       "run_time": 3.1231300830841064,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B7.TIF",
         "output=LC80440342016259LGN00.7",
         "--q"
       ],
       "return_code": 0,
       "run_time": 3.0385892391204834,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B8.TIF",
         "output=LC80440342016259LGN00.8",
         "--q"
       ],
       "return_code": 0,
       "run_time": 11.727607488632202,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B9.TIF",
         "output=LC80440342016259LGN00.9",
         "--q"
       ],
       "return_code": 0,
       "run_time": 3.531238317489624,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B10.TIF",
         "output=LC80440342016259LGN00.10",
         "--q"
       ],
       "return_code": 0,
       "run_time": 3.1895594596862793,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.import",
       "parameter": [
         "input=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_B11.TIF",
         "output=LC80440342016259LGN00.11",
         "--q"
       ],
       "return_code": 0,
       "run_time": 3.1583566665649414,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "i.landsat.toar",
       "parameter": [
         "input=LC80440342016259LGN00.",
         "metfile=/actinia/workspace/download_cache/demouser/LC80440342016259LGN00_MTL.txt",
         "method=uncorrected",
         "output=LC80440342016259LGN00_TOAR.",
         "--q"
       ],
       "return_code": 0,
       "run_time": 101.34896063804626,
       "stderr": [
         "WARNING: ESUN evaluated from REFLECTANCE_MAXIMUM_BAND",
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "i.vi",
       "parameter": [
         "red=LC80440342016259LGN00_TOAR.4",
         "nir=LC80440342016259LGN00_TOAR.5",
         "green=LC80440342016259LGN00_TOAR.3",
         "blue=LC80440342016259LGN00_TOAR.2",
         "band5=LC80440342016259LGN00_TOAR.7",
         "band7=LC80440342016259LGN00_TOAR.8",
         "viname=ndvi",
         "output=LC80440342016259LGN00_TOAR_NDVI"
       ],
       "return_code": 0,
       "run_time": 45.43833112716675,
       "stderr": [
         "0..3..6..9..12..15..18..21..24..27..30..33..36..39..42..45..48..51..54..57..60..63..66..69..72..75..78..81..84..87..90..93..96..99..100",
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.colors",
       "parameter": [
         "map=LC80440342016259LGN00_TOAR_NDVI",
         "color=ndvi"
       ],
       "return_code": 0,
       "run_time": 0.050219058990478516,
       "stderr": [
         "Color table for raster map <LC80440342016259LGN00_TOAR_NDVI> set to 'ndvi'",
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "r.univar",
       "parameter": [
         "map=LC80440342016259LGN00_TOAR_NDVI",
         "output=/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/tmpkiv0uv6z.univar",
         "-g"
       ],
       "return_code": 0,
       "run_time": 2.5560226440429688,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "d.rast",
       "parameter": [
         "map=LC80440342016259LGN00_TOAR_NDVI",
         "-n"
       ],
       "return_code": 0,
       "run_time": 1.2287390232086182,
       "stderr": [
         "0..3..6..9..12..15..18..21..24..27..30..33..36..39..42..45..48..51..54..57..60..63..66..69..72..75..78..81..84..87..90..93..96..99..100",
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "d.legend",
       "parameter": [
         "raster=LC80440342016259LGN00_TOAR_NDVI",
         "at=8,92,0,7",
         "-n"
       ],
       "return_code": 0,
       "run_time": 0.37291598320007324,
       "stderr": [
         ""
       ],
       "stdout": ""
     },
     {
       "executable": "g.region",
       "parameter": [
         "raster=LC80440342016259LGN00_TOAR_NDVI",
         "-g"
       ],
       "return_code": 0,
       "run_time": 0.051508188247680664,
       "stderr": [
         ""
       ],
       "stdout": "projection=1\nzone=10\nn=4264515\ns=4030185\nw=464385\ne=694515\nnsres=30\newres=30\nrows=7811\ncols=7671\ncells=59918181\n"
     },
     {
       "executable": "r.out.gdal",
       "parameter": [
         "-fm",
         "input=LC80440342016259LGN00_TOAR_NDVI",
         "format=GTiff",
         "createopt=COMPRESS=LZW",
         "output=/actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_TOAR_NDVI.tiff"
       ],
       "return_code": 0,
       "run_time": 8.784564018249512,
       "stderr": [
         "Checking GDAL data type and nodata value...",
         "2..5..8..11..14..17..20..23..26..29..32..35..38..41..44..47..50..53..56..59..62..65..68..71..74..77..80..83..86..89..92..95..98..100",
         "Using GDAL data type <Float64>",
         "Input raster map contains cells with NULL-value (no-data). The value -nan will be used to represent no-data values in the input map. You can specify a nodata value with the nodata option.",
         "Exporting raster data to GTiff format...",
         "ERROR 6: SetColorTable() only supported for Byte or UInt16 bands in TIFF format.",
         "2..5..8..11..14..17..20..23..26..29..32..35..38..41..44..47..50..53..56..59..62..65..68..71..74..77..80..83..86..89..92..95..98..100",
         "r.out.gdal complete. File </actinia/workspace/temp_db/gisdbase_4e879f3951334a559612abab4352b069/.tmp/LC80440342016259LGN00_TOAR_NDVI.tiff> created.",
         ""
       ],
       "stdout": ""
     }
   ],
   "process_results": [
     {
       "cells": 59918181.0,
       "coeff_var": 125.4796560716,
       "max": 1.31488464218245,
       "mean": 0.215349514428788,
       "mean_of_abs": 0.272685223860196,
       "min": -1.35084534300324,
       "n": 41612094.0,
       "name": "LC80440342016259LGN00_TOAR_NDVI",
       "null_cells": 18306087.0,
       "range": 2.6657299851857,
       "stddev": 0.270219830057103,
       "sum": 8961144.23726506,
       "variance": 0.0730187565560894
     }
   ],
   "progress": {
     "num_of_steps": 35,
     "step": 34
   },
   "resource_id": "resource_id-6282c634-42e1-417c-a092-c9b21c3283cc",
   "status": "finished",
   "time_delta": 415.2818741798401,
   "timestamp": 1527679378.31516,
   "urls": {
     "resources": [
       "http://actinia.mundialis.de/api/v3/resource/demouser/resource_id-6282c634-42e1-417c-a092-c9b21c3283cc/tmp80apvh0h.png",
       "http://actinia.mundialis.de/api/v3/resource/demouser/resource_id-6282c634-42e1-417c-a092-c9b21c3283cc/LC80440342016259LGN00_TOAR_NDVI.tiff"
     ],
     "status": "http://actinia.mundialis.de/api/v3/resources/demouser/resource_id-6282c634-42e1-417c-a092-c9b21c3283cc"
   },
   "user_id": "demouser"
 }
```

The statistical analysis of the resulting NDVI raster map layer is
available in the *process_results* section:

```json
 {
   "cells": 59918181.0,
   "coeff_var": 125.4796560716,
   "max": 1.31488464218245,
   "mean": 0.215349514428788,
   "mean_of_abs": 0.272685223860196,
   "min": -1.35084534300324,
   "n": 41612094.0,
   "name": "LC80440342016259LGN00_TOAR_NDVI",
   "null_cells": 18306087.0,
   "range": 2.6657299851857,
   "stddev": 0.270219830057103,
   "sum": 8961144.23726506,
   "variance": 0.0730187565560894
 }
```

The following links can be found in the **urls** section of the JSON
response that point to the created resources:

<http://actinia.mundialis.de/api/v3/resource/demouser/resource_id-6282c634-42e1-417c-a092-c9b21c3283cc/tmp80apvh0h.png>

<http://actinia.mundialis.de/api/v3/resource/demouser/resource_id-6282c634-42e1-417c-a092-c9b21c3283cc/LC80440342016259LGN00_TOAR_NDVI.tiff>

The preview image should look like this:

![image](landsat_ndvi.png)
