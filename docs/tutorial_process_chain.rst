User defined processing
=======================

The actinia process chain
-------------------------

Actinia provides the **process chain** approach to specify import, processing and export of geo-data
using the actinia GRASS GIS processing system. The process chain must be formulated in JSON.
The processing is always performed in an ephemeral database. The computational environment
is based on locations in the persistent database. If required, the ephemeral database can
be moved into the persistent user database, so that the computational results can be used in further processing
steps or visualized using the actinia rendering REST calls.

The ephemeral database will be removed after computation.
However, all raster and vector data that was generated during the processing can be exported
using gdal/ogr specific datatypes and stored in an object storage, outside the actinia environment.
Within a process chain we have read only access to all raster maps of the persistent database location that
is used as computational environment.

A process chain is a list of GRASS GIS modules [#grassmodulelist]_
that will executed in serial, based on the order of the list.
GRASS GIS modules are specified as process definitions [#grassmodule]_ that includes the name of the command,
the inputs [#inputs]_ and outputs [#outputs]_,
including import and export definitions as well as the module flags. The following example defines a single process
that runs the GRASS GIS module *r.slope.aspect* [#rlopeaspect]_ to compute the *slope*
for the raster map layer *elev_ned_30m* that is located in the mapset [#mapset]_ *PERMANENT*.
The output of the module is named *elev_ned_30m_slope* and should be exported as a GeoTiff file.

    .. code-block:: json

        {
          "module": "r.slope.aspect",
          "id": "r_slope_aspect_1",
          "inputs": [
            {
              "param": "elevation",
              "value": "elev_ned_30m@PERMANENT"
            }
          ],
          "outputs": [
            {
              "export": {
                "format": "GTiff",
                "type": "raster"
              },
              "param": "slope",
              "value": "elev_ned_30m_slope"
            }
          ],
          "flags": "a"
        }
    ..

The actinia process chain supports the specification of URL's to raster layers in the input definition.
The following process chain imports a raster map layer that is located
in an object storage with the name *elev_ned_30m_new* and sets the computational region
for the following processing step with the GRASS GIS module *g.region* [#gregion]_.
Then slope and aspect are computed with *r.slope.aspect* and specified for export as GeoTiff files.

    .. code-block:: json

        {
          "list": [
            {
              "module": "g.region",
              "id": "g_region_1",
              "inputs": [
                {
                  "import_descr": {
                    "source": "https://storage.googleapis.com/graas-geodata/elev_ned_30m.tif",
                    "type": "raster"
                  },
                  "param": "raster",
                  "value": "elev_ned_30m_new"
                }
              ],
              "flags": "p"
            },
            {
              "module": "r.slope.aspect",
              "id": "r_slope_aspect_1",
              "inputs": [
                {
                  "param": "elevation",
                  "value": "elev_ned_30m_new"
                }
              ],
              "outputs": [
                {
                  "export": {
                    "format": "GTiff",
                    "type": "raster"
                  },
                  "param": "slope",
                  "value": "elev_ned_30m_new_slope"
                }
              ],
              "flags": "a"
            }
          ],
          "version": "1"
        }
    ..

.. rubric:: Footnotes

.. [#grassmodulelist] https://grass.osgeo.org/grass74/manuals/index.html
.. [#grassmodule] https://actinia.mundialis.de/api_docs/#/definitions/GrassModule
.. [#inputs] https://actinia.mundialis.de/api_docs/#/definitions/InputParameter
.. [#outputs] https://actinia.mundialis.de/api_docs/#/definitions/OutputParameter
.. [#rlopeaspect] https://grass.osgeo.org/grass74/manuals/r.slope.aspect.html
.. [#mapset] https://grass.osgeo.org/grass74/manuals/grass_database.html
.. [#gregion] https://grass.osgeo.org/grass74/manuals/g.region.html

Sentiel2A NDVI processing
-------------------------

We create a process chain that computes the NDVI
from a Sentinel2A scene based on the bands 8 and 4
with the GRASS GIS module r.mapcalc.
We use the latitude/longitude location **LL** as processing environment.
and the computational region of sentinel band B04
for the NDVI processing. Then we calculate univariate statistics for the Sentinel2A scene.
The computed NDVI raster layer will be exported as geotiff file that can be accessed via an URL.

The following JSON code has 6 process definitions:

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

