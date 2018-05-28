Database access
===============

The Actinia databases
---------------------

Actinia manage many GRASS GIS locations in its *persistent database*.
User are not permitted to modify data in a persistent database, but can access all data
read only for processing and visualization. Data in the persistent database can only accessed
via HTTP GET API calls.

The user can either process data in an *ephemeral databases*, that will be removed after
the processing is finished, or in a *user specific database*. A user specific database is persistent,
only visible to users of the same user-group and can contain any data the user
has imported.The user can read-access all data from the persistent database
while running analysis in the ephemeral database or user specific database.


In this short tutorial we will access the actinia persistent database analysing
raster and raster-time-series data.  We will use the the import and export features of actinia
specific process chains to process Sentinel2A scenes with several GRASS GIS modules and
export the result as GeoTiff files.

The following examples shows the REST service access using the command line tool **curl** [#curl]_.
**Curl** should be available on many Linux systems.
However, tools like *postman* [#post]_ allow a more comfortable way to access
Actinia.

.. rubric:: Footnotes

.. [#curl] https://en.wikipedia.org/wiki/CURL
.. [#post] https://www.getpostman.com/apps

Using curl for HTTP requests
----------------------------

We will use the Unix shell and curl to access the REST API.
First open a shell of choice (we use bash here) and setup the login information,
the IP address and the port on which the Actinia service is running,
so you can simply change the IP and Port if your sever uses a different
address:

    .. code-block:: bash

        export PORT=5000
        export HOST=http://localhost
        export AUTH='-u superadmin:abcdefgh'

Access to locations and mapsets in the persistent database
----------------------------------------------------------

The following API call lists all available locations in the Actinia persistent database:

   .. code-block:: bash

      curl ${AUTH} -X GET -i "${HOST}:${PORT}/locations"

The output should look similar to this:

    .. code-block:: json

        {
          "locations": [
            "ECAD",
            "LL",
            "nc_spm_08"
          ],
          "status": "success"
        }

To show the region settings and the projection of the GRASS GIS standard location
*nc_spm_08* the following REST call must be used:

   .. code-block:: bash

        curl ${AUTH} -X GET -i "${HOST}:${PORT}/locations/nc_spm_08/info"

   ..

The JSON response is the standard response of the Actinia REST API. Most API calls
response using this JSON structure. The difference between API calls is the result part that
is located in the JSON section with the name *process_results*.
The response includes all steps that were executed
to receive the projection information and the region information. It is located in
the *process_log* section of the JSON response. In addition API specific
information as well as the processing time are available in the response:

   .. code-block:: json

        {
          "accept_datetime": "2018-05-02 20:43:41.933931",
          "accept_timestamp": 1525286621.9339273,
          "api_info": {
            "endpoint": "locationmanagementresourceuser",
            "method": "GET",
            "path": "/locations/nc_spm_08/info",
            "request_url": "http://localhost:5000/locations/nc_spm_08/info"
          },
          "datetime": "2018-05-02 20:43:42.065771",
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
              "run_time": 0.05019521713256836,
              "stderr": [
                ""
              ],
              "stdout": "..."
            },
            {
              "executable": "g.proj",
              "parameter": [
                "-fw"
              ],
              "return_code": 0,
              "run_time": 0.05019712448120117,
              "stderr": [
                ""
              ],
              "stdout": "..."
            }
          ],
          "process_results": {
            "projection": "PROJCS[\"NAD83(HARN) / North Carolina\",GEOGCS[\"NAD83(HARN)\",DATUM[\"NAD83_High_Accuracy_Reference_Network\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6152\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4152\"]],PROJECTION[\"Lambert_Conformal_Conic_2SP\"],PARAMETER[\"standard_parallel_1\",36.16666666666666],PARAMETER[\"standard_parallel_2\",34.33333333333334],PARAMETER[\"latitude_of_origin\",33.75],PARAMETER[\"central_meridian\",-79],PARAMETER[\"false_easting\",609601.22],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"X\",EAST],AXIS[\"Y\",NORTH],AUTHORITY[\"EPSG\",\"3358\"]]\n",
            "region": {
              "b": 0.0,
              "cells": 29535,
              "cells3": 29535,
              "cols": 179,
              "cols3": 179,
              "depths": 1,
              "e": 639530.0,
              "ewres": 10.0,
              "ewres3": 10.0,
              "n": 221230.0,
              "nsres": 10.0,
              "nsres3": 10.0,
              "projection": 99,
              "rows": 165,
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
          "resource_id": "resource_id-ad4299e9-7c2f-44a6-84f5-d435df1a0019",
          "status": "finished",
          "time_delta": 0.13188838958740234,
          "timestamp": 1525286622.0657547,
          "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/superadmin/resource_id-ad4299e9-7c2f-44a6-84f5-d435df1a0019"
          },
          "user_id": "superadmin"
        }


   ..

To list all mapsets located in the location *nc_spm_08* the following API call is used:

   .. code-block:: bash

      curl ${AUTH} -X GET -i "${HOST}:${PORT}/locations/nc_spm_08/mapsets"

   ..

The response of this synchronous call lists all mapsets of the location in the *process_results* section:

   .. code-block:: json

        {
          "accept_datetime": "2018-05-02 20:46:04.793194",
          "accept_timestamp": 1525286764.7931914,
          "api_info": {
            "endpoint": "listmapsetsresource",
            "method": "GET",
            "path": "/locations/nc_spm_08/mapsets",
            "request_url": "http://localhost:5000/locations/nc_spm_08/mapsets"
          },
          "datetime": "2018-05-02 20:46:04.929313",
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
              "run_time": 0.05016946792602539,
              "stderr": [
                "Available mapsets:",
                ""
              ],
              "stdout": "PERMANENT\nSource_A\nSource_B\nTarget\nlandsat\nraster_test_mapset\nuser1\n"
            }
          ],
          "process_results": [
            "PERMANENT",
            "landsat",
            "user1"
          ],
          "progress": {
            "num_of_steps": 1,
            "step": 1
          },
          "resource_id": "resource_id-1bfde762-1c29-48d7-b516-617246185d30",
          "status": "finished",
          "time_delta": 0.13616585731506348,
          "timestamp": 1525286764.9292982,
          "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/superadmin/resource_id-1bfde762-1c29-48d7-b516-617246185d30"
          },
          "user_id": "superadmin"
        }

   ..

Use the following API call shows all information about the mapset *PERMANENT*:

   .. code-block:: bash

      curl ${AUTH} -X GET -i "${HOST}:${PORT}/locations/nc_spm_08/mapsets/PERMANENT/info"

The response shows the region of the mapset and the projection of the location in the *process_results*
section:

   .. code-block:: json

        {
          "accept_datetime": "2018-05-02 20:48:11.349668",
          "accept_timestamp": 1525286891.349665,
          "api_info": {
            "endpoint": "mapsetmanagementresourceuser",
            "method": "GET",
            "path": "/locations/nc_spm_08/mapsets/PERMANENT/info",
            "request_url": "http://localhost:5000/locations/nc_spm_08/mapsets/PERMANENT/info"
          },
          "datetime": "2018-05-02 20:48:11.509428",
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
              "run_time": 0.05018758773803711,
              "stderr": [
                ""
              ],
              "stdout": "..."
            },
            {
              "executable": "g.proj",
              "parameter": [
                "-fw"
              ],
              "return_code": 0,
              "run_time": 0.050147294998168945,
              "stderr": [
                ""
              ],
              "stdout": "..."
            }
          ],
          "process_results": {
            "projection": "PROJCS[\"NAD83(HARN) / North Carolina\",GEOGCS[\"NAD83(HARN)\",DATUM[\"NAD83_High_Accuracy_Reference_Network\",SPHEROID[\"GRS 1980\",6378137,298.257222101,AUTHORITY[\"EPSG\",\"7019\"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY[\"EPSG\",\"6152\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4152\"]],PROJECTION[\"Lambert_Conformal_Conic_2SP\"],PARAMETER[\"standard_parallel_1\",36.16666666666666],PARAMETER[\"standard_parallel_2\",34.33333333333334],PARAMETER[\"latitude_of_origin\",33.75],PARAMETER[\"central_meridian\",-79],PARAMETER[\"false_easting\",609601.22],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"X\",EAST],AXIS[\"Y\",NORTH],AUTHORITY[\"EPSG\",\"3358\"]]\n",
            "region": {
              "b": 0.0,
              "cells": 29535,
              "cells3": 29535,
              "cols": 179,
              "cols3": 179,
              "depths": 1,
              "e": 639530.0,
              "ewres": 10.0,
              "ewres3": 10.0,
              "n": 221230.0,
              "nsres": 10.0,
              "nsres3": 10.0,
              "projection": 99,
              "rows": 165,
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
          "resource_id": "resource_id-dd4a722b-312c-471c-a39f-23cc59c54027",
          "status": "finished",
          "time_delta": 0.1598050594329834,
          "timestamp": 1525286891.5094137,
          "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/superadmin/resource_id-dd4a722b-312c-471c-a39f-23cc59c54027"
          },
          "user_id": "superadmin"
        }

   ..

Access to raster layers in the persistent database
--------------------------------------------------

The location ECAD contains yearly climate data (precipitation and temperatur) of Europe
for 60 years. We list all raster layers of the location ECAD in mapset *PERMANENT*:

   .. code-block:: bash

      curl ${AUTH} -X GET -i "${HOST}:${PORT}/locations/ECAD/mapsets/PERMANENT/raster_layers"

The response list all raster layers of the mapset in the *process_results* section:

   .. code-block:: json

        {
          "accept_datetime": "2018-05-02 20:49:48.835417",
          "accept_timestamp": 1525286988.8354142,
          "api_info": {
            "endpoint": "rasterlayersresource",
            "method": "GET",
            "path": "/locations/ECAD/mapsets/PERMANENT/raster_layers",
            "request_url": "http://localhost:5000/locations/ECAD/mapsets/PERMANENT/raster_layers"
          },
          "datetime": "2018-05-02 20:49:48.947005",
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
                "type=raster",
                "mapset=PERMANENT"
              ],
              "return_code": 0,
              "run_time": 0.05018734931945801,
              "stderr": [
                ""
              ],
              "stdout": "..."
            }
          ],
          "process_results": [
            "precipitation_yearly_mm_0",
            "precipitation_yearly_mm_1",
            "precipitation_yearly_mm_10",
            "precipitation_yearly_mm_11",
            "precipitation_yearly_mm_12",
            "precipitation_yearly_mm_13",
            "precipitation_yearly_mm_14",
            "precipitation_yearly_mm_15",
            "precipitation_yearly_mm_16",
            "precipitation_yearly_mm_17",
            "precipitation_yearly_mm_18",
            "precipitation_yearly_mm_19",
            "precipitation_yearly_mm_2",
            "precipitation_yearly_mm_20",
            "precipitation_yearly_mm_21",
            "precipitation_yearly_mm_22",
            "precipitation_yearly_mm_23",
            "precipitation_yearly_mm_24",
            "precipitation_yearly_mm_25",
            "precipitation_yearly_mm_26",
            "precipitation_yearly_mm_27",
            "precipitation_yearly_mm_28",
            "precipitation_yearly_mm_29",
            "precipitation_yearly_mm_3",
            "precipitation_yearly_mm_30",
            "precipitation_yearly_mm_31",
            "precipitation_yearly_mm_32",
            "precipitation_yearly_mm_33",
            "precipitation_yearly_mm_34",
            "precipitation_yearly_mm_35",
            "precipitation_yearly_mm_36",
            "precipitation_yearly_mm_37",
            "precipitation_yearly_mm_38",
            "precipitation_yearly_mm_39",
            "precipitation_yearly_mm_4",
            "precipitation_yearly_mm_40",
            "precipitation_yearly_mm_41",
            "precipitation_yearly_mm_42",
            "precipitation_yearly_mm_43",
            "precipitation_yearly_mm_44",
            "precipitation_yearly_mm_45",
            "precipitation_yearly_mm_46",
            "precipitation_yearly_mm_47",
            "precipitation_yearly_mm_48",
            "precipitation_yearly_mm_49",
            "precipitation_yearly_mm_5",
            "precipitation_yearly_mm_50",
            "precipitation_yearly_mm_51",
            "precipitation_yearly_mm_52",
            "precipitation_yearly_mm_53",
            "precipitation_yearly_mm_54",
            "precipitation_yearly_mm_55",
            "precipitation_yearly_mm_56",
            "precipitation_yearly_mm_57",
            "precipitation_yearly_mm_58",
            "precipitation_yearly_mm_59",
            "precipitation_yearly_mm_6",
            "precipitation_yearly_mm_60",
            "precipitation_yearly_mm_61",
            "precipitation_yearly_mm_62",
            "precipitation_yearly_mm_7",
            "precipitation_yearly_mm_8",
            "precipitation_yearly_mm_9",
            "temperature_mean_yearly_celsius_0",
            "temperature_mean_yearly_celsius_1",
            "temperature_mean_yearly_celsius_10",
            "temperature_mean_yearly_celsius_11",
            "temperature_mean_yearly_celsius_12",
            "temperature_mean_yearly_celsius_13",
            "temperature_mean_yearly_celsius_14",
            "temperature_mean_yearly_celsius_15",
            "temperature_mean_yearly_celsius_16",
            "temperature_mean_yearly_celsius_17",
            "temperature_mean_yearly_celsius_18",
            "temperature_mean_yearly_celsius_19",
            "temperature_mean_yearly_celsius_2",
            "temperature_mean_yearly_celsius_20",
            "temperature_mean_yearly_celsius_21",
            "temperature_mean_yearly_celsius_22",
            "temperature_mean_yearly_celsius_23",
            "temperature_mean_yearly_celsius_24",
            "temperature_mean_yearly_celsius_25",
            "temperature_mean_yearly_celsius_26",
            "temperature_mean_yearly_celsius_27",
            "temperature_mean_yearly_celsius_28",
            "temperature_mean_yearly_celsius_29",
            "temperature_mean_yearly_celsius_3",
            "temperature_mean_yearly_celsius_30",
            "temperature_mean_yearly_celsius_31",
            "temperature_mean_yearly_celsius_32",
            "temperature_mean_yearly_celsius_33",
            "temperature_mean_yearly_celsius_34",
            "temperature_mean_yearly_celsius_35",
            "temperature_mean_yearly_celsius_36",
            "temperature_mean_yearly_celsius_37",
            "temperature_mean_yearly_celsius_38",
            "temperature_mean_yearly_celsius_39",
            "temperature_mean_yearly_celsius_4",
            "temperature_mean_yearly_celsius_40",
            "temperature_mean_yearly_celsius_41",
            "temperature_mean_yearly_celsius_42",
            "temperature_mean_yearly_celsius_43",
            "temperature_mean_yearly_celsius_44",
            "temperature_mean_yearly_celsius_45",
            "temperature_mean_yearly_celsius_46",
            "temperature_mean_yearly_celsius_47",
            "temperature_mean_yearly_celsius_48",
            "temperature_mean_yearly_celsius_49",
            "temperature_mean_yearly_celsius_5",
            "temperature_mean_yearly_celsius_50",
            "temperature_mean_yearly_celsius_51",
            "temperature_mean_yearly_celsius_52",
            "temperature_mean_yearly_celsius_53",
            "temperature_mean_yearly_celsius_54",
            "temperature_mean_yearly_celsius_55",
            "temperature_mean_yearly_celsius_56",
            "temperature_mean_yearly_celsius_57",
            "temperature_mean_yearly_celsius_58",
            "temperature_mean_yearly_celsius_59",
            "temperature_mean_yearly_celsius_6",
            "temperature_mean_yearly_celsius_60",
            "temperature_mean_yearly_celsius_61",
            "temperature_mean_yearly_celsius_62",
            "temperature_mean_yearly_celsius_7",
            "temperature_mean_yearly_celsius_8",
            "temperature_mean_yearly_celsius_9"
          ],
          "progress": {
            "num_of_steps": 1,
            "step": 1
          },
          "resource_id": "resource_id-2d0cd22e-3db6-45b7-9069-d1347d2a8bf5",
          "status": "finished",
          "time_delta": 0.1116323471069336,
          "timestamp": 1525286988.9469898,
          "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/superadmin/resource_id-2d0cd22e-3db6-45b7-9069-d1347d2a8bf5"
          },
          "user_id": "superadmin"
        }

   ..

Show info about the raster layer *temperature_mean_yearly_celsius_60*:

   .. code-block:: bash

      curl ${AUTH} -X GET -i "${HOST}:${PORT}/locations/ECAD/mapsets/PERMANENT/raster_layers/temperature_mean_yearly_celsius_60"

The response list information about the raster layer *temperature_mean_yearly_celsius_60*
in the *process_results* section:

   .. code-block:: json

        {
          "accept_datetime": "2018-05-02 20:52:58.445026",
          "accept_timestamp": 1525287178.4450228,
          "api_info": {
            "endpoint": "rasterlayerresource",
            "method": "GET",
            "path": "/locations/ECAD/mapsets/PERMANENT/raster_layers/temperature_mean_yearly_celsius_60",
            "request_url": "http://localhost:5000/locations/ECAD/mapsets/PERMANENT/raster_layers/temperature_mean_yearly_celsius_60"
          },
          "datetime": "2018-05-02 20:52:58.543142",
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
              "run_time": 0.050164222717285156,
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
            "database": "/home/soeren/actinia/workspace/temp_db/gisdbase_31ab9ca7e3234d7389d2d6f1f53a73ff",
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
          "resource_id": "resource_id-e8d1d67d-25ed-4218-a16f-4e96a465fa80",
          "status": "finished",
          "time_delta": 0.0981595516204834,
          "timestamp": 1525287178.5431273,
          "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/superadmin/resource_id-e8d1d67d-25ed-4218-a16f-4e96a465fa80"
          },
          "user_id": "superadmin"
        }



Access to raster time-series in the persistent database
-------------------------------------------------------

Actinia supports the analysis of time-series data based on the temporal framework of GRASS GIS [#tgrass]_, [#tframew]_.
A time-series datatype is located in location *ECAD* with mapsets *PERMANENT*.
The time-series datatype is called space-time raster dataset (strds) and represents a time-stamped
series of yearly temperature and precipitation data for Europe.

.. rubric:: Footnotes

.. [#tgrass] http://www.sciencedirect.com/science/article/pii/S136481521300282X
.. [#tframew] http://www.tandfonline.com/doi/abs/10.1080/13658816.2017.1306862?journalCode=tgis20

We list all strds with the following API call:

   .. code-block:: bash

      curl ${AUTH} -X GET -i "${HOST}:${PORT}/locations/ECAD/mapsets/PERMANENT/strds"

We receive two strds in the *process_results* section of the JSON response:

   .. code-block:: json

        {
          "accept_datetime": "2018-05-02 20:56:30.077592",
          "accept_timestamp": 1525287390.0775914,
          "api_info": {
            "endpoint": "liststrdsresource",
            "method": "GET",
            "path": "/locations/ECAD/mapsets/PERMANENT/strds",
            "request_url": "http://localhost:5000/locations/ECAD/mapsets/PERMANENT/strds"
          },
          "datetime": "2018-05-02 20:56:30.626030",
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
                "column=name",
                "type=strds",
                "where=mapset='PERMANENT'"
              ],
              "return_code": 0,
              "run_time": 0.5021917819976807,
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
          "resource_id": "resource_id-4461257e-b5d7-4fc8-9763-99a2e3b00ed1",
          "status": "finished",
          "time_delta": 0.548475980758667,
          "timestamp": 1525287390.6260166,
          "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/superadmin/resource_id-4461257e-b5d7-4fc8-9763-99a2e3b00ed1"
          },
          "user_id": "superadmin"
        }

Use the following API call to receive information about the strds *temperature_mean_1950_2013_yearly_celsius*.

   .. code-block:: bash

      curl ${AUTH} -X GET -i "${HOST}:${PORT}/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius"

All relevant information about strds *temperature_mean_1950_2013_yearly_celsius* is located in
the *process_results* section of the JSON response:

   .. code-block:: json

        {
          "accept_datetime": "2018-05-02 20:57:27.039624",
          "accept_timestamp": 1525287447.0396235,
          "api_info": {
            "endpoint": "strdsmanagementresource",
            "method": "GET",
            "path": "/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius",
            "request_url": "http://localhost:5000/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius"
          },
          "datetime": "2018-05-02 20:57:27.492341",
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
              "run_time": 0.4009056091308594,
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
          "resource_id": "resource_id-c01ff6e7-38cd-41ad-9de1-6f034fa71202",
          "status": "finished",
          "time_delta": 0.4527604579925537,
          "timestamp": 1525287447.4923265,
          "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/superadmin/resource_id-c01ff6e7-38cd-41ad-9de1-6f034fa71202"
          },
          "user_id": "superadmin"
        }


List all raster layers that are registered in the strds *temperature_mean_1950_2013_yearly_celsius* with time-stamps:

   .. code-block:: bash

      curl ${AUTH} -X GET -i "${HOST}:${PORT}/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius/raster_layers"

A list of about 60 raster layers with minimum, maximum values, time-stamps and spatial extent will be located in the
*process_results* section of the JSON response:

   .. code-block:: json

        {
          "accept_datetime": "2018-05-02 20:59:09.165859",
          "accept_timestamp": 1525287549.1658578,
          "api_info": {
            "endpoint": "strdsrastermanagement",
            "method": "GET",
            "path": "/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius/raster_layers",
            "request_url": "http://localhost:5000/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius/raster_layers"
          },
          "datetime": "2018-05-02 20:59:09.659853",
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
                    "name": "/home/soeren/actinia/workspace/temp_db/gisdbase_54755874286e486da89f208c3e8b3ac8/.tmp/tmpfuj3lrrz"
                  }
                }
              }
            }
          ],
          "process_log": [
            {
              "executable": "t.rast.list",
              "parameter": [
                "separator=|",
                "columns=id,start_time,end_time,north,south,east,west,min,max,rows,cols",
                "input=temperature_mean_1950_2013_yearly_celsius@PERMANENT",
                "output=/home/soeren/actinia/workspace/temp_db/gisdbase_54755874286e486da89f208c3e8b3ac8/.tmp/tmpfuj3lrrz",
                "-u"
              ],
              "return_code": 0,
              "run_time": 0.40091514587402344,
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
              "cols": "201",
              "east": "75.5",
              "end_time": "1952-01-01 00:00:00",
              "id": "temperature_mean_yearly_celsius_1@PERMANENT",
              "max": "19.189924",
              "min": "-7.90164",
              "north": "75.5",
              "rows": "464",
              "south": "25.25",
              "start_time": "1951-01-01 00:00:00",
              "west": "-40.5"
            },
            {
              "cols": "201",
              "east": "75.5",
              "end_time": "1953-01-01 00:00:00",
              "id": "temperature_mean_yearly_celsius_2@PERMANENT",
              "max": "19.709069",
              "min": "-9.244687",
              "north": "75.5",
              "rows": "464",
              "south": "25.25",
              "start_time": "1952-01-01 00:00:00",
              "west": "-40.5"
            },
            {
              "cols": "201",
              "east": "75.5",
              "end_time": "1954-01-01 00:00:00",
              "id": "temperature_mean_yearly_celsius_3@PERMANENT",
              "max": "20.833794",
              "min": "-7.287986",
              "north": "75.5",
              "rows": "464",
              "south": "25.25",
              "start_time": "1953-01-01 00:00:00",
              "west": "-40.5"
            },
            {
              "cols": "201",
              "east": "75.5",
              "end_time": "1955-01-01 00:00:00",
              "id": "temperature_mean_yearly_celsius_4@PERMANENT",
              "max": "20.471126",
              "min": "-6.724322",
              "north": "75.5",
              "rows": "464",
              "south": "25.25",
              "start_time": "1954-01-01 00:00:00",
              "west": "-40.5"
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
          "resource_id": "resource_id-4ff32404-cb0e-4085-9055-046bddcb9e2f",
          "status": "finished",
          "time_delta": 0.49403834342956543,
          "timestamp": 1525287549.6598372,
          "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/superadmin/resource_id-4ff32404-cb0e-4085-9055-046bddcb9e2f"
          },
          "user_id": "superadmin"
        }
