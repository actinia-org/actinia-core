Time-series sampling
====================

Sampling of a STRDS with vector points
--------------------------------------

The actinia REST API provides an API call to sample a space-time raster dataset (STRDS) at coordinate points.
The coordinates must be specified in JSON and must use the same coordinate reference system as the
location that contains the STRDS.

The following example shows the synchronous API call that samples the STRDS *temperature_mean_1950_2013_yearly_celsius*
at three different coordinates.

   .. code-block:: bash

      JSON='{"points":[["a", "-5.095406", "38.840583"],
                       ["b", "9.9681980", "51.666166"],
                       ["c", "24.859647", "52.699099"]]}'

      curl ${AUTH} -X POST -i "${ACTINIA_URL}/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius/sampling_sync" \
           -H  "accept: application/json" -H  "content-type: application/json" -d "$JSON"

The result of the sampling is a list of time stamped values, that are located in the
*process_results* section of the JSON response:

    .. code-block:: json

        {
          "accept_datetime": "2018-05-30 10:33:23.640702",
          "accept_timestamp": 1527676403.6407006,
          "api_info": {
            "endpoint": "syncephemeralstrdssamplingresource",
            "method": "POST",
            "path": "/api/v1/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius/sampling_sync",
            "request_url": "http://actinia.mundialis.de/api/v1/locations/ECAD/mapsets/PERMANENT/strds/temperature_mean_1950_2013_yearly_celsius/sampling_sync"
          },
          "datetime": "2018-05-30 10:33:24.503297",
          "http_code": 200,
          "message": "Processing successfully finished",
          "process_chain_list": [
            {
              "1": {
                "inputs": {
                  "column": "id text, x double precision, y double precision",
                  "format": "point",
                  "input": "/actinia/workspace/temp_db/gisdbase_1977514d0cc1415bac3a1722aa4f6e1e/.tmp/tmprpjtds__",
                  "x": 2,
                  "y": 3
                },
                "module": "v.in.ascii",
                "outputs": {
                  "output": {
                    "name": "input_points"
                  }
                }
              },
              "2": {
                "flags": "rn",
                "inputs": {
                  "column": "id",
                  "points": "input_points",
                  "strds": "temperature_mean_1950_2013_yearly_celsius@PERMANENT"
                },
                "module": "t.rast.sample",
                "outputs": {
                  "output": {
                    "name": "/actinia/workspace/temp_db/gisdbase_1977514d0cc1415bac3a1722aa4f6e1e/.tmp/tmpfsiu1fn1"
                  }
                },
                "overwrite": true,
                "verbose": true
              }
            }
          ],
          "process_log": [
            {
              "executable": "v.in.ascii",
              "parameter": [
                "input=/actinia/workspace/temp_db/gisdbase_1977514d0cc1415bac3a1722aa4f6e1e/.tmp/tmprpjtds__",
                "format=point",
                "column=id text, x double precision, y double precision",
                "x=2",
                "y=3",
                "output=input_points"
              ],
              "return_code": 0,
              "run_time": 0.051050662994384766,
              "stderr": [
                "Scanning input for column types...",
                "Number of columns: 3",
                "Number of rows: 3",
                "Importing points...",
                "0..33..66..100",
                "Populating table...",
                "Building topology for vector map <input_points@mapset_1977514d0cc1415bac3a1722aa4f6e1e>...",
                "Registering primitives...",
                "",
                ""
              ],
              "stdout": ""
            },
            {
              "executable": "t.rast.sample",
              "parameter": [
                "strds=temperature_mean_1950_2013_yearly_celsius@PERMANENT",
                "points=input_points",
                "column=id",
                "output=/actinia/workspace/temp_db/gisdbase_1977514d0cc1415bac3a1722aa4f6e1e/.tmp/tmpfsiu1fn1",
                "-rn",
                "--o",
                "--v"
              ],
              "return_code": 0,
              "run_time": 0.7098870277404785,
              "stderr": ["..."],
              "stdout": ""
            }
          ],
          "process_results": [
            [
              "start_time",
              "end_time",
              "a",
              "b",
              "c"
            ],
            [
              "1950-01-01 00:00:00",
              "1951-01-01 00:00:00",
              "16.41218887608807",
              "8.178182155657963",
              "7.176576932923706"
            ],
            [
              "..."
            ],
            [
              "2012-01-01 00:00:00",
              "2013-01-01 00:00:00",
              "16.55121792732666",
              "8.837787912495367",
              "7.872688635520949"
            ]
          ],
          "progress": {
            "num_of_steps": 2,
            "step": 2
          },
          "resource_id": "resource_id-ff89db3c-1cae-44e1-adb5-35ce1ab994bc",
          "status": "finished",
          "time_delta": 0.8626308441162109,
          "timestamp": 1527676404.5032735,
          "urls": {
            "resources": [],
            "status": "http://actinia.mundialis.de/api/v1/resources/superadmin/resource_id-ff89db3c-1cae-44e1-adb5-35ce1ab994bc"
          },
          "user_id": "superadmin"
        }

    ..
