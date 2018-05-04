================================
Actinia - The GRASS GIS REST API
================================

Actinia is an open source REST API for scalable, distributed, high performance
processing of geographical data that uses GRASS GIS for computational tasks.

It provides a REST API to process satellite images, time series of satellite images,
arbitrary raster data with geographical relations and vector data.

Introduction
============

Actinia is a REST service to process geographical data that can be managed by
the GRASS GIS software system. The software is designed to expose a GRASS GIS database
and many GRASS GIS [#GRASS]_ processing tool as REST service [#REST]_. Hence, access
to GRASS resources like raster maps, space-time raster datasets,
processing and analysis modules are available via URL.  In addition
Actinia allows the processing of cloud based data, for example all Landsat 4-8 scenes as well as all
Sentinel2A scenes in an ephemeral databases. The computational results of ephemeral processing
are available via object storage as GeoTIFF files.

The Actinia service consists of the *Actinia Core* that provides the basic but sophisticated processing service
and *Actinia plugins* that provide problem specific services like Sentinel 2A and Landsat NDVI computation,
spatio-temporal statistical analysis and many more.

This documentation focus on the basic processing services that are provided by the *Actinia Core*
service.

.. rubric:: Footnotes

.. [#GRASS] https://grass.osgeo.org/
.. [#REST] https://en.wikipedia.org/wiki/Representational_State_Transfer

To use Actinia the user must have an understanding of the GRASS GIS concept [#grassloc]_
of location, mapsets, raster maps, space-time datasets and modules.
The URLs that provide access to the GRASS database reflect
these concepts. Hence, the location, the mapset, the required raster
map are part of the URL to access the service.

Howto use the REST API
----------------------

The REST approach uses the HTTP [#http]_ method GET [#method]_,
DELETE [#method]_, POST [#method]_ and PUT [#method]_ to manipulate and receive resource.

While GET requests can be send easily from a browser, POST, PUT or DELETE request can not.
To access the full potential of Actinia you will need a HTTP client, that talks
all HTTP communication methods.

The following examples shows the REST service access using the command line tool **curl** [#curl]_.
**Curl** should be available on many Linux systems.
However, tools like *postman* [#post]_ allow a more comfortable way to access
Actinia.

.. rubric:: Footnotes

.. [#curl] https://en.wikipedia.org/wiki/CURL
.. [#post] https://www.getpostman.com/apps
.. [#http] https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
.. [#method] https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
.. [#grassloc] https://grass.osgeo.org/grass72/manuals/helptext.html#2.-background:-grass-gis-location-structure


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

Installation
============

A local installation requires a full GRASS GIS installation. Make sure all
requirements are fulfilled to compile GRASS GIS from the svn repository.

First install Proj4 and GRASS GIS by downloading the latest svn version and compile it.

1. Install the latest projection library.

    .. code-block:: bash

        cd /tmp

        wget http://download.osgeo.org/proj/proj-4.9.3.tar.gz

        tar xzvf proj-4.9.3.tar.gz

        cd proj-4.9.3/nad

        wget http://download.osgeo.org/proj/proj-datumgrid-1.6.zip

        unzip proj-datumgrid-1.6.zip

        cd ..

        ./configure
        make -j4
        sudo make install
    ..

2. Install GRASS GIS and additional modules:

    .. code-block:: bash

        cd /tmp

        wget https://grass.osgeo.org/grass75/source/snapshot/grass-7.5.svn_src_snapshot_2018_03_10.tar.gz
        tar xzvf grass-7.5.svn_src_snapshot_2018_03_10.tar.gz
        mv grass-7.5.svn_src_snapshot_2018_03_10 grass_trunk

        cd grass_trunk
        svn cleanup
        svn up

        export INTEL="-march=native -std=gnu99 -fexceptions -fstack-protector -m64"
        export MYCFLAGS="-Wall -ggdb -fno-fast-math -fno-common $INTEL $MYGCC"
        export MYLDFLAGS="-Wl,--no-undefined"
        export LD_LIBRARY_PATH="/usr/local/lib"
        export LDFLAGS="$MYLDFLAGS"
        export CFLAGS="$MYCFLAGS"
        export CXXFLAGS="$MYCXXFLAGS"

        ./configure \
          --with-cxx \
          --enable-largefile \
          --with-proj=/usr/local/lib \
          --with-proj-share=/usr/local/share/proj \
          --with-gdal \
          --with-python \
          --with-geos \
          --with-sqlite \
          --with-cairo --with-cairo-ldflags=-lfontconfig \
          --with-fftw \
          --with-netcdf \
          --with-bzlib \
          --with-zstd \
          --without-postgres \
          --without-freetype \
          --without-openmp \
          --without-opengl \
          --without-nls \
          --without-mysql \
          --without-odbc \
          --without-openmp \
          --without-ffmpeg \
          --prefix=/usr/local

        make -j16
        sudo make install

        cd temporal
        git clone https://bitbucket.org/huhabla/temporal-raster-sampling.git t.rast.sample
        cd t.rast.sample
        make
        sudo make install
        cd ..

        git clone https://github.com/huhabla/t_rast_aggr_func.git t.rast.aggr_func
        cd t.rast.aggr_func
        make
        sudo make install

        cd ../../display/
        git clone https://bitbucket.org/huhabla/d_rast_multi.git d.rast.multi
        cd d.rast.multi
        make
        sudo make install

    ..

3. Download the test locations and place them into a specific directory that will
   be used by actinia as persistent database:

    .. code-block:: bash

        mkdir -p $HOME/actinia/grassdb
        cd $HOME/actinia/grassdb
        wget https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_grass7.tar.gz
        tar xzvf nc_spm_08_grass7.tar.gz
        rm -f nc_spm_08_grass7.tar.gz
        mv nc_spm_08_grass7 nc_spm_08

        wget https://storage.googleapis.com/datentransfer/ECAD.tar.gz
        tar xzvf ECAD.tar.gz
        rm -f ECAD.tar.gz

        wget https://storage.googleapis.com/datentransfer/LL.tar.gz
        tar xzvf LL.tar.gz
        rm -f LL.tar.gz

    ..


4. Actinia Core must be run within a virtual python3 environment:

    .. code-block:: bash

        mkdir -p $HOME/actinia/workspace/tmp

        cd /tmp

        git clone https://github.com/mundialis/actinia_core.git actinia_core
        virtualenv -p python3.5 actinia_venv
        source actinia_venv/bin/activate
        cd actinia_core
        pip install -r requirements.txt
        python setup.py install
        deactivate

    ..

5. GRASS GIS requires a Python2 environment for running, so we create one.
   This environment must be specified in the actinia config file:

    .. code-block:: bash

        cd /tmp

        virtualenv -p python2.7 grass_venv
        source grass_venv/bin/activate
        cd actinia_core
        pip install -r requirements-grass-gis.txt

    ..

6. Make sure that a redis service is running and create a user with actinia-user tool


    .. code-block:: bash

        cd /tmp
        source actinia_venv/bin/activate

        # Create the superuser
        actinia-user create -u superadmin -w abcdefgh -r superadmin -g group -c 100000000000 -n 1000 -t 6000

        # Start the actinia service with
        actinia_server --host 0.0.0.0 --port 5000

    ..

7. Check the service with curl

    .. code-block:: bash

        export PORT=5000
        export IP=http://localhost
        export AUTH='-u superadmin:abcdefgh'

        curl -u superadmin:abcdefgh -X GET http://localhost:5000/locations

    ..


Tutorial
========

In this short tutorial we will access the Actinia persistent database analysing
raster and time-series data.  We will use the the import and export features of Actinia
specific process chains to process Sentinel2A scenes with several GRASS GIS modules and
export the result as GeoTiff files.

Preparation
-----------

Actinia is fully documented using the OpenAPI standard [#openapi]_,
better known as swagger [#swagger]_.
The JSON definition of the API can be accessed here:

      https://actinia.mundialis.de/api/v0/swagger.json

To generate a readable documentation out of the swagger.json file, the spectacle
tool can be used:

    .. code-block:: bash

        # Download the latest swagger definition from the actinia service
        wget  https://actinia.mundialis.de/api/v0/swagger.json -O /tmp/actinia.json

        # Run spectacle docker image to generate the HTML documentation
        docker run -v /tmp:/tmp -t sourcey/spectacle spectacle /tmp/actinia.json -t /tmp

        # Start Firefox to show the documentation
        firefox /tmp/index.html

The petstore swagger UI creator [#swaggerui]_ can be used to show
all available REST API calls and all response models in a convenient way.

First open a shell of choice (we use bash here) and setup the login information,
the IP address and the port on which the Actinia service is running,
so you can simply change the IP and Port if your sever uses a different
address:

    .. code-block:: bash

        export PORT=5000
        export HOST=http://localhost
        export AUTH='-u superadmin:abcdefgh'

.. rubric:: Footnotes

.. [#openapi] https://www.openapis.org/
.. [#swagger] https://swagger.io
.. [#swaggerui] https://petstore.swagger.io


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

Process chains and ephemeral processing
---------------------------------------

Actinia supports the definition of process chains to specify import, processing and export of geo-data
using the Actinia processing system. The processing is performed in an ephemeral database that use
locations of the persistent database as computational environment.
The ephemeral database will be removed after computation,
so that any results must be exported to access them.
Within a process chain we have read only access to all raster maps of the base location that
is used as computational environment.

In the following example we define a process chain
using JSON. We use the latitude/longitude location **LL** as processing
environment. We create a process chain that computes the NDVI
from a Sentinel2A scene based on the bands 8 and 4
with the GRASS GIS module r.mapcalc. We use the computational region of sentinel band B04
for the NDVI computation. Then we calculate univariate statistics for the Sentinel2A scene
and the corresponding MODIS map at the region
of the Sentinel2A scene for comparison.
The computed NDVI raster layer will be exported as geotiff file that can be accessed via an URL.

The following JSON code has 56 process definitions:

   1. Import of two bands (B04 and B08) of the Sentinel2A scene *S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749*
   2. Set the computational region to imported raster layer B04
   3. Use r.mapcalc to compute the NDVI
   4. Use r.univar to compute univariate statistics of the computed NDVI raster layer
   5. Export the computed NDVI as GeoTiff

   .. code-block:: json

      {
       "list": [{"id": "importer_1",
                "module": "importer",
                "inputs": [{"import_descr": {"source": "S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                                             "type": "sentinel2",
                                             "sentinel_band": "B04"},
                            "param": "map",
                            "value": "B04"},
                           {"import_descr": {"source": "S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                                             "type": "sentinel2",
                                             "sentinel_band": "B08"},
                            "param": "map",
                            "value": "B08"}]},
               {"id": "g_region_1",
                "module": "g.region",
                "inputs": [{"param": "raster",
                            "value": "B04"}],
                "flags": "g"},
               {"id": "rmapcalc_1",
                "module": "r.mapcalc",
                "inputs": [{"param": "expression",
                            "value": "NDVI = float((B08 - B04)/(B08 + B04))"}]},
               {"id": "r_univar_sentinel2",
                "module": "r.univar",
                "inputs": [{"param": "map",
                            "value": "NDVI"}],
                "flags": "g"},
               {"id": "exporter_1",
                "module": "exporter",
                "outputs": [{"export": {"type": "raster", "format": "GTiff"},
                             "param": "map",
                             "value": "NDVI"}]}
               ],
       "version": "1"
      }

Run the process chain asynchronously:

   .. code-block:: bash

      JSON='{
      "list": [{"id": "importer_1",
                "module": "importer",
                "inputs": [{"import_descr": {"source": "S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                                             "type": "sentinel2",
                                             "sentinel_band": "B04"},
                            "param": "map",
                            "value": "B04"},
                           {"import_descr": {"source": "S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                                             "type": "sentinel2",
                                             "sentinel_band": "B08"},
                            "param": "map",
                            "value": "B08"}]},
               {"id": "g_region_1",
                "module": "g.region",
                "inputs": [{"param": "raster",
                            "value": "B04"}],
                "flags": "g"},
               {"id": "rmapcalc_1",
                "module": "r.mapcalc",
                "inputs": [{"param": "expression",
                            "value": "NDVI = float((B08 - B04)/(B08 + B04))"}]},
               {"id": "r_univar_sentinel2",
                "module": "r.univar",
                "inputs": [{"param": "map",
                            "value": "NDVI"}],
                "flags": "g"},
               {"id": "exporter_1",
                "module": "exporter",
                "outputs": [{"export": {"type": "raster", "format": "GTiff"},
                             "param": "map",
                             "value": "NDVI"}]}
               ],
      "version": "1"}'

      curl ${AUTH} -X POST -i "${HOST}:${PORT}/locations/LL/processing_async_export" \
           -H  "accept: application/json" -H  "content-type: application/json" -d "$JSON"

The response requires the polling of the status URL, since the API call works asynchronously:

   .. code-block:: json

        {
          "accept_datetime": "2018-05-02 21:05:34.873031",
          "accept_timestamp": 1525287934.8730297,
          "api_info": {
            "endpoint": "asyncephemeralexportresource",
            "method": "POST",
            "path": "/locations/LL/processing_async_export",
            "request_url": "http://localhost:5000/locations/LL/processing_async_export"
          },
          "datetime": "2018-05-02 21:05:34.873754",
          "http_code": 200,
          "message": "Resource accepted",
          "process_chain_list": [],
          "process_results": {},
          "resource_id": "resource_id-60f3f012-4220-46ec-9110-694df49006c4",
          "status": "accepted",
          "time_delta": 0.0007345676422119141,
          "timestamp": 1525287934.873754,
          "urls": {
            "resources": [],
            "status": "http://localhost:5000/resources/superadmin/resource_id-60f3f012-4220-46ec-9110-694df49006c4"
          },
          "user_id": "superadmin"
        }


Poll the status of the Sentinel2A NDVI job and view the result of the computation:

   .. code-block:: bash

      curl ${AUTH} -X GET -i "${HOST}:${PORT}/resources/superadmin/resource_id-60f3f012-4220-46ec-9110-694df49006c4"

The finished response should look like this:

   .. code-block:: json

        {
          "accept_datetime": "2018-05-02 21:05:34.873031",
          "accept_timestamp": 1525287934.8730297,
          "api_info": {
            "endpoint": "asyncephemeralexportresource",
            "method": "POST",
            "path": "/locations/LL/processing_async_export",
            "request_url": "http://localhost:5000/locations/LL/processing_async_export"
          },
          "datetime": "2018-05-02 21:09:39.823857",
          "http_code": 200,
          "message": "Processing successfully finished",
          "process_chain_list": [
            {
              "list": [
                {
                  "id": "importer_1",
                  "inputs": [
                    {
                      "import_descr": {
                        "sentinel_band": "B04",
                        "source": "S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                        "type": "sentinel2"
                      },
                      "param": "map",
                      "value": "B04"
                    },
                    {
                      "import_descr": {
                        "sentinel_band": "B08",
                        "source": "S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                        "type": "sentinel2"
                      },
                      "param": "map",
                      "value": "B08"
                    }
                  ],
                  "module": "importer"
                },
                {
                  "flags": "g",
                  "id": "g_region_1",
                  "inputs": [
                    {
                      "param": "raster",
                      "value": "B04"
                    }
                  ],
                  "module": "g.region"
                },
                {
                  "id": "rmapcalc_1",
                  "inputs": [
                    {
                      "param": "expression",
                      "value": "NDVI = float((B08 - B04)/(B08 + B04))"
                    }
                  ],
                  "module": "r.mapcalc"
                },
                {
                  "flags": "g",
                  "id": "r_univar_sentinel2",
                  "inputs": [
                    {
                      "param": "map",
                      "value": "NDVI"
                    }
                  ],
                  "module": "r.univar"
                },
                {
                  "id": "exporter_1",
                  "module": "exporter",
                  "outputs": [
                    {
                      "export": {
                        "format": "GTiff",
                        "type": "raster"
                      },
                      "param": "map",
                      "value": "NDVI"
                    }
                  ]
                }
              ],
              "version": "1"
            }
          ],
          "process_log": [
            {
              "executable": "/usr/bin/wget",
              "parameter": [
                "-t5",
                "-c",
                "-q",
                "https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/50/R/KR/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749.SAFE/GRANULE/L1C_T50RKR_A007608_20161206T030749/IMG_DATA/T50RKR_20161206T030112_B04.jp2"
              ],
              "return_code": 0,
              "run_time": 26.578389167785645,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "/bin/mv",
              "parameter": [
                "/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/T50RKR_20161206T030112_B04.jp2",
                "/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04"
              ],
              "return_code": 0,
              "run_time": 0.05015993118286133,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "v.import",
              "parameter": [
                "input=/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749.gml",
                "output=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                "--q"
              ],
              "return_code": 0,
              "run_time": 0.150557279586792,
              "stderr": [
                "WARNING: Width for column fid set to 255 (was not specified by OGR), some strings may be truncated!",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "v.timestamp",
              "parameter": [
                "map=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                "date=06 dec 2016 03:07:49"
              ],
              "return_code": 0,
              "run_time": 0.05015850067138672,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "/usr/bin/gdal_translate",
              "parameter": [
                "-projwin",
                "113.949663",
                "28.011816",
                "115.082607",
                "27.001706",
                "-of",
                "vrt",
                "-projwin_srs",
                "EPSG:4326",
                "/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04",
                "/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04.vrt"
              ],
              "return_code": 0,
              "run_time": 0.050154685974121094,
              "stderr": [
                "Warning 1: Computed -srcwin 5 -225 10971 11419 falls partially outside raster extent. Going on however.",
                ""
              ],
              "stdout": "Input file size is 10980, 10980\n"
            },
            {
              "executable": "r.import",
              "parameter": [
                "input=/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04.vrt",
                "output=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04_uncropped",
                "--q"
              ],
              "return_code": 0,
              "run_time": 47.980000257492065,
              "stderr": [
                "WARNING: Projection of dataset does not appear to match current location.",
                "",
                "Location PROJ_INFO is:",
                "name: WGS 84",
                "datum: wgs84",
                "ellps: wgs84",
                "proj: ll",
                "no_defs: defined",
                "",
                "Dataset PROJ_INFO is:",
                "name: WGS 84 / UTM zone 50N",
                "datum: wgs84",
                "ellps: wgs84",
                "proj: utm",
                "zone: 50",
                "no_defs: defined",
                "",
                "ERROR: proj",
                "",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "g.region",
              "parameter": [
                "align=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04_uncropped",
                "vector=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                "-g"
              ],
              "return_code": 0,
              "run_time": 0.05019974708557129,
              "stderr": [
                ""
              ],
              "stdout": "projection=3\nzone=0\nn=28.0118772817232\ns=27.0016255440191\nw=113.949598991944\ne=115.082625141434\nnsres=9.36719274644538e-05\newres=9.36694898718473e-05\nrows=10785\ncols=12096\ncells=130455360\n"
            },
            {
              "executable": "r.mask",
              "parameter": [
                "vector=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749"
              ],
              "return_code": 0,
              "run_time": 7.319561243057251,
              "stderr": [
                "Reading areas...",
                "0..100",
                "Writing raster map...",
                "0..3..6..9..12..15..18..21..24..27..30..33..36..39..42..45..48..51..54..57..60..63..66..69..72..75..78..81..84..87..90..93..96..99..100",
                "Reading areas...",
                "0..100",
                "Writing raster map...",
                "0..3..6..9..12..15..18..21..24..27..30..33..36..39..42..45..48..51..54..57..60..63..66..69..72..75..78..81..84..87..90..93..96..99..100",
                "Reading areas...",
                "0..100",
                "Writing raster map...",
                "0..3..6..9..12..15..18..21..24..27..30..33..36..39..42..45..48..51..54..57..60..63..66..69..72..75..78..81..84..87..90..93..96..99..100",
                "All subsequent raster operations will be limited to the MASK area. Removing or renaming raster map named 'MASK' will restore raster operations to normal.",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "r.mapcalc",
              "parameter": [
                "expression=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04 = float(S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04_uncropped)"
              ],
              "return_code": 0,
              "run_time": 11.935151815414429,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "r.timestamp",
              "parameter": [
                "map=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04",
                "date=06 dec 2016 03:07:49"
              ],
              "return_code": 0,
              "run_time": 0.05023622512817383,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "g.remove",
              "parameter": [
                "type=raster",
                "name=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04_uncropped",
                "-f"
              ],
              "return_code": 0,
              "run_time": 0.05019116401672363,
              "stderr": [
                "Removing raster <S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04_uncropped>",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "r.mask",
              "parameter": [
                "-r"
              ],
              "return_code": 0,
              "run_time": 0.10028839111328125,
              "stderr": [
                "Raster MASK removed",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "g.rename",
              "parameter": [
                "raster=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04,B04"
              ],
              "return_code": 0,
              "run_time": 0.0501711368560791,
              "stderr": [
                "Rename raster <S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B04> to <B04>",
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
                "https://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/50/R/KR/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749.SAFE/GRANULE/L1C_T50RKR_A007608_20161206T030749/IMG_DATA/T50RKR_20161206T030112_B08.jp2"
              ],
              "return_code": 0,
              "run_time": 35.301382303237915,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "/bin/mv",
              "parameter": [
                "/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/T50RKR_20161206T030112_B08.jp2",
                "/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08"
              ],
              "return_code": 0,
              "run_time": 0.05019092559814453,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "v.import",
              "parameter": [
                "input=/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749.gml",
                "output=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                "--q"
              ],
              "return_code": 0,
              "run_time": 0.1504042148590088,
              "stderr": [
                "WARNING: Vector map <S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749> already exists and will be overwritten",
                "WARNING: Width for column fid set to 255 (was not specified by OGR), some strings may be truncated!",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "v.timestamp",
              "parameter": [
                "map=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                "date=06 dec 2016 03:07:49"
              ],
              "return_code": 0,
              "run_time": 0.05019021034240723,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "/usr/bin/gdal_translate",
              "parameter": [
                "-projwin",
                "113.949663",
                "28.011816",
                "115.082607",
                "27.001706",
                "-of",
                "vrt",
                "-projwin_srs",
                "EPSG:4326",
                "/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08",
                "/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08.vrt"
              ],
              "return_code": 0,
              "run_time": 0.05018925666809082,
              "stderr": [
                "Warning 1: Computed -srcwin 5 -225 10971 11419 falls partially outside raster extent. Going on however.",
                ""
              ],
              "stdout": "Input file size is 10980, 10980\n"
            },
            {
              "executable": "r.import",
              "parameter": [
                "input=/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08.vrt",
                "output=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08_uncropped",
                "--q"
              ],
              "return_code": 0,
              "run_time": 46.33052468299866,
              "stderr": [
                "WARNING: Projection of dataset does not appear to match current location.",
                "",
                "Location PROJ_INFO is:",
                "name: WGS 84",
                "datum: wgs84",
                "ellps: wgs84",
                "proj: ll",
                "no_defs: defined",
                "",
                "Dataset PROJ_INFO is:",
                "name: WGS 84 / UTM zone 50N",
                "datum: wgs84",
                "ellps: wgs84",
                "proj: utm",
                "zone: 50",
                "no_defs: defined",
                "",
                "ERROR: proj",
                "",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "g.region",
              "parameter": [
                "align=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08_uncropped",
                "vector=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749",
                "-g"
              ],
              "return_code": 0,
              "run_time": 0.05030989646911621,
              "stderr": [
                ""
              ],
              "stdout": "projection=3\nzone=0\nn=28.0118772817232\ns=27.0016255440191\nw=113.949598991944\ne=115.082625141434\nnsres=9.36719274644538e-05\newres=9.36694898718473e-05\nrows=10785\ncols=12096\ncells=130455360\n"
            },
            {
              "executable": "r.mask",
              "parameter": [
                "vector=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749"
              ],
              "return_code": 0,
              "run_time": 7.324517488479614,
              "stderr": [
                "Reading areas...",
                "0..100",
                "Writing raster map...",
                "0..3..6..9..12..15..18..21..24..27..30..33..36..39..42..45..48..51..54..57..60..63..66..69..72..75..78..81..84..87..90..93..96..99..100",
                "Reading areas...",
                "0..100",
                "Writing raster map...",
                "0..3..6..9..12..15..18..21..24..27..30..33..36..39..42..45..48..51..54..57..60..63..66..69..72..75..78..81..84..87..90..93..96..99..100",
                "Reading areas...",
                "0..100",
                "Writing raster map...",
                "0..3..6..9..12..15..18..21..24..27..30..33..36..39..42..45..48..51..54..57..60..63..66..69..72..75..78..81..84..87..90..93..96..99..100",
                "All subsequent raster operations will be limited to the MASK area. Removing or renaming raster map named 'MASK' will restore raster operations to normal.",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "r.mapcalc",
              "parameter": [
                "expression=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08 = float(S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08_uncropped)"
              ],
              "return_code": 0,
              "run_time": 12.890670776367188,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "r.timestamp",
              "parameter": [
                "map=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08",
                "date=06 dec 2016 03:07:49"
              ],
              "return_code": 0,
              "run_time": 0.05022931098937988,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "g.remove",
              "parameter": [
                "type=raster",
                "name=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08_uncropped",
                "-f"
              ],
              "return_code": 0,
              "run_time": 0.050171613693237305,
              "stderr": [
                "Removing raster <S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08_uncropped>",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "r.mask",
              "parameter": [
                "-r"
              ],
              "return_code": 0,
              "run_time": 0.10028266906738281,
              "stderr": [
                "Raster MASK removed",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "g.rename",
              "parameter": [
                "raster=S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08,B08"
              ],
              "return_code": 0,
              "run_time": 0.05016207695007324,
              "stderr": [
                "Rename raster <S2A_MSIL1C_20161206T030112_N0204_R032_T50RKR_20161206T030749_B08> to <B08>",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "g.region",
              "parameter": [
                "raster=B04",
                "-g"
              ],
              "return_code": 0,
              "run_time": 0.05024123191833496,
              "stderr": [
                ""
              ],
              "stdout": "projection=3\nzone=0\nn=28.0118772816667\ns=27.0016255438889\nw=113.949598991944\ne=115.082625141389\nnsres=9.36719274712822e-05\newres=9.36694898680925e-05\nrows=10785\ncols=12096\ncells=130455360\n"
            },
            {
              "executable": "r.mapcalc",
              "parameter": [
                "expression=NDVI = float((B08 - B04)/(B08 + B04))"
              ],
              "return_code": 0,
              "run_time": 25.169322967529297,
              "stderr": [
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "r.univar",
              "parameter": [
                "map=NDVI",
                "-g"
              ],
              "return_code": 0,
              "run_time": 4.662879705429077,
              "stderr": [
                ""
              ],
              "stdout": "n=125210913\nnull_cells=5244447\ncells=130455360\nmin=-0.96863466501236\nmax=0.80298912525177\nrange=1.77162379026413\nmean=0.345240281310971\nmean_of_abs=0.347942456759571\nstddev=0.135376600339386\nvariance=0.0183268239194499\ncoeff_var=39.2122842170458\nsum=43227850.8273235\n"
            },
            {
              "executable": "r.out.gdal",
              "parameter": [
                "-fm",
                "input=NDVI",
                "format=GTiff",
                "createopt=COMPRESS=LZW",
                "output=/home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/NDVI.tiff"
              ],
              "return_code": 0,
              "run_time": 12.83556079864502,
              "stderr": [
                "Checking GDAL data type and nodata value...",
                "2..5..8..11..14..17..20..23..26..29..32..35..38..41..44..47..50..53..56..59..62..65..68..71..74..77..80..83..86..89..92..95..98..100",
                "Using GDAL data type <Float32>",
                "Input raster map contains cells with NULL-value (no-data). The value -nan will be used to represent no-data values in the input map. You can specify a nodata value with the nodata option.",
                "Exporting raster data to GTiff format...",
                "ERROR 6: SetColorTable() only supported for Byte or UInt16 bands in TIFF format.",
                "2..5..8..11..14..17..20..23..26..29..32..35..38..41..44..47..50..53..56..59..62..65..68..71..74..77..80..83..86..89..92..95..98..100",
                "r.out.gdal complete. File </home/soeren/actinia/workspace/temp_db/gisdbase_d7f340e070934294bdd908be975953a5/.tmp/NDVI.tiff> created.",
                ""
              ],
              "stdout": ""
            }
          ],
          "process_results": {},
          "progress": {
            "num_of_steps": 30,
            "step": 30
          },
          "resource_id": "resource_id-60f3f012-4220-46ec-9110-694df49006c4",
          "status": "finished",
          "time_delta": 244.95086097717285,
          "timestamp": 1525288179.8238533,
          "urls": {
            "resources": [
              "http://localhost:5000/resource/superadmin/resource_id-60f3f012-4220-46ec-9110-694df49006c4/NDVI.tiff"
            ],
            "status": "http://localhost:5000/resources/superadmin/resource_id-60f3f012-4220-46ec-9110-694df49006c4"
          },
          "user_id": "superadmin"
        }
