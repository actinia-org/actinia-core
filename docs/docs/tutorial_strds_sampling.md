# Time-series sampling

## Sampling of a STRDS with vector points

The actinia REST API provides an API call to sample a space-time raster
dataset (STRDS) at coordinate points. The coordinates must be specified
in JSON and must use the same coordinate reference system as the
project that contains the STRDS.

We will use the Unix shell and curl to access the REST API. First open a shell of choice (we use bash here) and setup the login information, the  IP address and the port on which the actinia service is running, so you can simply change the IP and port if your server uses a different
address:

```bash
export ACTINIA_URL=https://actinia.mundialis.de/api/v3
export AUTH='-u demouser:gu3st!pa55w0rd'
# other user credentials can be provided in the same way
```

The following example shows the synchronous API call that samples the
MODIS land surface temperature STRDS `LST_Day_monthly` at three
different coordinate points in the `nc_spm_08` project.

```bash
 JSON='{"points":[["a", "637000", "221000"],
                  ["b", "642000", "224000"],
                  ["c", "647000", "227000"]]}'

 curl ${AUTH} -X POST "${ACTINIA_URL}/projects/nc_spm_08/mapsets/modis_lst/strds/LST_Day_monthly/sampling_sync" -H  "accept: application/json" -H  "content-type: application/json" -d "$JSON"
```




The result of the sampling is a list of time stamped values, that are
located in the *process_results* section of the JSON response:

```json
 {
  "accept_datetime": "2026-07-14 12:42:55.526473",
  "accept_timestamp": 1784032975.5264723,
  "api_info": {
    "endpoint": "syncephemeralstrdssamplingresource",
    "method": "POST",
    "path": "/api/v3/projects/nc_spm_08/mapsets/modis_lst/strds/LST_Day_monthly/sampling_sync",
    "request_url": "http://actinia.mundialis.de/api/v3/projects/nc_spm_08/mapsets/modis_lst/strds/LST_Day_monthly/sampling_sync"
  },
  "datetime": "2026-07-14 12:42:56.442646",
  "http_code": 200,
  "message": "Processing successfully finished",
  "process_chain_list": [
    {
      "list": [
        {
          "id": "v_in_ascii_1",
          "inputs": [
            {
              "param": "input",
              "value": "/actinia_core/workspace/temp_db/gisdbase_0fb7182eebde474eb93fd5e413bab9d0/.tmp/tmp6eq5k07c"
            },
            {
              "param": "format",
              "value": "point"
            },
            {
              "param": "column",
              "value": "id text, x double precision, y double precision"
            },
            {
              "param": "x",
              "value": "2"
            },
            {
              "param": "y",
              "value": "3"
            }
          ],
          "module": "v.in.ascii",
          "outputs": [
            {
              "param": "output",
              "value": "input_points"
            }
          ],
          "superquiet": true
        },
        {
          "flags": "rn",
          "id": "t_rast_sample_2",
          "inputs": [
            {
              "param": "strds",
              "value": "LST_Day_monthly@modis_lst"
            },
            {
              "param": "points",
              "value": "input_points"
            },
            {
              "param": "column",
              "value": "id"
            }
          ],
          "module": "t.rast.sample",
          "outputs": [
            {
              "param": "output",
              "value": "/actinia_core/workspace/temp_db/gisdbase_0fb7182eebde474eb93fd5e413bab9d0/.tmp/tmpnqvxp9me"
            }
          ],
          "superquiet": true
        }
      ],
      "version": "1"
    }
  ],
  "process_log": [
    {
      "executable": "v.in.ascii",
      "id": "v_in_ascii_1",
      "mapset_size": 15867,
      "parameter": [
        "input=/actinia_core/workspace/temp_db/gisdbase_0fb7182eebde474eb93fd5e413bab9d0/.tmp/tmp6eq5k07c",
        "format=point",
        "column=id text, x double precision, y double precision",
        "x=2",
        "y=3",
        "output=input_points",
        "--qq"
      ],
      "return_code": 0,
      "run_time": 0.15046954154968262,
      "stderr": [
        ""
      ],
      "stdout": ""
    },
    {
      "executable": "t.rast.sample",
      "id": "t_rast_sample_2",
      "mapset_size": 495186,
      "parameter": [
        "strds=LST_Day_monthly@modis_lst",
        "points=input_points",
        "column=id",
        "output=/actinia_core/workspace/temp_db/gisdbase_0fb7182eebde474eb93fd5e413bab9d0/.tmp/tmpnqvxp9me",
        "-rn",
        "--qq"
      ],
      "return_code": 0,
      "run_time": 0.6018619537353516,
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
      "2015-01-01 00:00:00",
      "2015-02-01 00:00:00",
      "14072",
      "14130",
      "14136"
    ],
    [
      "..."
    ],
    [
      "2016-12-01 00:00:00",
      "2017-01-01 00:00:00",
      "14224",
      "14250",
      "14267"
    ]
  ],
  "process_time_delta": 0.756260871887207,
  "progress": {
    "num_of_steps": 2,
    "step": 2
  },
  "queue": "local",
  "resource_id": "resource_id-f06b8015-cc36-44d7-8919-dd87c489f3d1",
  "start_datetime": "2026-07-14 12:42:55.686427",
  "start_timestamp": 1784032975.686427,
  "status": "finished",
  "time_delta": 0.9161863327026367,
  "timestamp": 1784032976.4426425,
  "urls": {
    "resources": [],
    "status": "https://actinia.mundialis.de/api/v3/resources/demouser/resource_id-f06b8015-cc36-44d7-8919-dd87c489f3d1"
  },
  "user_id": "demouser"
}

```
