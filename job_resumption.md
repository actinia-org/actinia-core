# Job resumption

If you want to be able to resume a job in actinia, you must enable
`save_iterim_results`.

There are two possible options for this:

1. `save_iterim_results=True`: after each processing step
   the temporary mapset in which the calculation is done is saved.
   This requires a lot of memory depending on the calculated data and the amount
   of calculations.
1. `save_iterim_results=onError` saves only intermediate results if an error
   has occurred in the processing. This means that the temporary mapset is only
   saved if an error occurs. Here the job resumption can fail, if the failing step
   modifies the temporary mapset (e.g. deletion of data which are needed) so that
   the fixed module call can not be executed after that modification. In the event
   of such an error, the process chain can then be adjusted so that the missing
   data is generated again, or the entire process can be started as a new job.

The interim results will be saved in the resource storage. Which can be configured in the config:

```ini
[GRASS]
grass_resource_dir = /actinia/resources
```

The interim results will be deleted automatically if a job resource is successfully resumed. The resource storage can also be cleaned manually via the endpoint (see the example below).

## Dev setup

- adjust config, e.g. for option 1

  ```ini
  [MISC]
  save_interim_results = True
  save_interim_results_endpoints_cfg = /etc/default/actinia_interim_endpoints.csv
  ```

  or for option 2

  ```ini
  [MISC]
  save_interim_results = onError
  save_interim_results_endpoints_cfg = /etc/default/actinia_interim_endpoints.csv
  ```

  The `/etc/default/actinia_interim_endpoints.csv` file can be set if not only
  the interim results of the processing endpoints of actinia_core should be saved.
  If for example also for the processing endpoints of the actinia-module-plugin
  the interim results should be saved and resource resumption should be prossible
  the file should contain the following:

  ```text
  GdiAsyncEphemeralExportResource;AsyncEphemeralExportResource
  GdiAsyncPersistentResource;AsyncPersistentResource
  ```

  The first entry is the class of the actinia-module-plugin endpoint and the
  seconde one is the actinia_core class which is used to do the job resumption.
  Since these differ, the complete process chain without template must be
  specified for job resumption (see below in the examples).

- Startup actinia with above config in preferred way, e.g.
  `cd ~/repos/actinia` + press F5

## Additional mapsets

For parallelization on different regions some GRASS GIS processes might create
additional mapsets and use the data from these mapsets in further calculations
without copying them to the temporary mapsets. To add the possibility to also
resumpt jobs where such addional mapsets are created in a previous step you can
configure additional mapsets which should be included in the interim results
by setting a pattern for the mapset name, e.g.:

```ini
[MISC]
save_interim_results = onError
save_interim_results_endpoints_cfg = /etc/default/actinia_interim_endpoints.csv
include_additional_mapset_pattern = test_tmp_*
```

## Job resumption examples

```bash
actiniapost() {
    curl -X POST -H 'Content-Type: application/json' -H 'accept: application/json' -u $1 -d @$2 $3 > resp.json && cat resp.json | jq;     export STATUS_URL=$(cat resp.json | jq .urls.status | sed 's/"//g');     curl -L -u $1 $STATUS_URL_POST | jq;     echo 'curl -L -u '\'$1\'' $STATUS_URL_POST | jq'
    cat resp.json | json urls.status | xargs -I {} echo "curl -L -u '$1' -X GET {} | jq"
}

actiniaget() {
  curl -X GET -u $1 $2 | jq
}

actiniaput () {
  curl -X PUT -H 'Content-Type: application/json' -H 'accept: application/json' -u $1 -d @$2 $3 > resp.json && cat resp.json | jq;     export STATUS_URL=$(cat resp.json | jq .urls.status | sed 's/"//g');     curl -L -u $1 $STATUS_URL | jq;     echo 'curl -L -u '\'$1\'' $STATUS_URL | jq'
}

actiniadelete(){
  curl -X DELETE -u $1 $2 > resp.json && cat resp.json | jq;     export STATUS_URL=$(cat resp.json | jq .urls.status | sed 's/"//g');     curl -L -u $1 $STATUS_URL | jq;     echo 'curl -L -u '\'$1\'' $STATUS_URL | jq'
}
```

For local setup set e.g.:

```bash
export ACTINIA_USER='actinia-gdi'
export ACTINIA_PASSWORD='actinia-gdi'
export AUTH="$ACTINIA_USER:$ACTINIA_PASSWORD"

URL=http://127.0.0.1:8088/api/v3
```

### Job resumption execution

The job resumption works for the following endpoints:

- ephemeral processing: `ENDPOINT=locations/nc_spm_08/processing_async`
- ephemeral processing with export: `ENDPOINT=locations/nc_spm_08/processing_async_export`
- persistent processing: `ENDPOINT=locations/nc_spm_08/mapsets/test44/processing_async`

`pc_error.json`: process chain with error

```json
{
    "list": [
      {
          "id": "importer_1",
          "module": "importer",
          "inputs": [
              {
                  "import_descr": {
                      "source": "https://raw.githubusercontent.com/mmacata/pagestest/gh-pages/pointInBonn.geojson",
                      "type": "vector"
                  },
                  "param": "map",
                  "value": "point"
              }
          ]
      },
      {
          "id": "v_info1",
          "module": "v.info",
          "inputs": [
              {
                  "param": "map",
                  "value": "point"
              }
          ],
          "flags": "g",
          "stdout": {"id": "v_info_1", "format": "kv", "delimiter": "="}
      },
      {
          "id": "r_info1",
          "module": "r.info",
          "inputs": [
              {
                  "param": "map",
                  "value": "elevation2@PERMANENT"
              }
          ],
          "flags": "g",
          "stdout": {"id": "r_info_1", "format": "kv", "delimiter": "="}
      },
      {
          "id": "sleep_1",
          "exe": "sleep",
          "params": ["1"]
      },
      {
          "id": "r_mapcalc",
          "module": "r.mapcalc",
          "inputs": [
              {
                  "param": "expression",
                  "value": "baum=5"
              }
          ]
      },
      {
          "id": "r_colors_out_sld",
          "module": "r.colors.out_sld",
          "inputs": [
              {
                  "param": "map",
                  "value": "elevation2@PERMANENT"
              }
          ],
          "outputs":  [
             {
                 "param": "output",
                 "value": "$file::r_info2",
                 "export": {"type": "file", "format": "TXT"}
             }
          ]
      },
      {
          "id": "importer_2",
          "module": "importer",
          "inputs": [
              {
                  "import_descr": {
                      "source": "https://raw.githubusercontent.com/mmacata/pagestest/gh-pages/bonn.geojson",
                      "type": "vector"
                  },
                  "param": "map",
                  "value": "polygon2"
              }
          ]
      },
      {
          "id": "v_info3",
          "module": "v.info",
          "inputs": [
              {
                  "param": "map",
                  "value": "polygon2"
              }
          ],
          "flags": "g",
          "stdout": {"id": "v_info_3", "format": "kv", "delimiter": "="}
      },
      {
        "id": "exporter_1",
        "module": "exporter",
        "comment": "Export indices as COG",
        "outputs": [
          {
            "export": {
              "type": "raster",
              "format": "COG"
            },
            "param": "map",
            "value": "baum"
          },
          {
            "export": {
              "type": "raster",
              "format": "COG"
            },
            "param": "map",
            "value": "elevation@PERMANENT"
          }
        ]
      }
    ],
    "version": "1"
}
```

`pc_noerror.json`: fixed process chain

```json
{
    "list": [
      {
          "id": "importer_1",
          "module": "importer",
          "inputs": [
              {
                  "import_descr": {
                      "source": "https://raw.githubusercontent.com/mmacata/pagestest/gh-pages/pointInBonn.geojson",
                      "type": "vector"
                  },
                  "param": "map",
                  "value": "point"
              }
          ]
      },
      {
          "id": "v_info1",
          "module": "v.info",
          "inputs": [
              {
                  "param": "map",
                  "value": "point"
              }
          ],
          "flags": "g",
          "stdout": {"id": "v_info_1", "format": "kv", "delimiter": "="}
      },
      {
          "id": "r_info1",
          "module": "r.info",
          "inputs": [
              {
                  "param": "map",
                  "value": "elevation@PERMANENT"
              }
          ],
          "flags": "g",
          "stdout": {"id": "r_info_1", "format": "kv", "delimiter": "="}
      },
      {
          "id": "sleep_1",
          "exe": "sleep",
          "params": ["1"]
      },
      {
          "id": "r_mapcalc",
          "module": "r.mapcalc",
          "inputs": [
              {
                  "param": "expression",
                  "value": "baum=5"
              }
          ]
      },
      {
          "id": "r_colors_out_sld",
          "module": "r.colors.out_sld",
          "inputs": [
              {
                  "param": "map",
                  "value": "elevation@PERMANENT"
              }
          ],
          "outputs":  [
             {
                 "param": "output",
                 "value": "$file::r_info2",
                 "export": {"type": "file", "format": "TXT"}
             }
          ]
      },
      {
          "id": "importer_2",
          "module": "importer",
          "inputs": [
              {
                  "import_descr": {
                      "source": "https://raw.githubusercontent.com/mmacata/pagestest/gh-pages/bonn.geojson",
                      "type": "vector"
                  },
                  "param": "map",
                  "value": "polygon2"
              }
          ]
      },
      {
          "id": "v_info3",
          "module": "v.info",
          "inputs": [
              {
                  "param": "map",
                  "value": "polygon2"
              }
          ],
          "flags": "g",
          "stdout": {"id": "v_info_3", "format": "kv", "delimiter": "="}
      },
      {
        "id": "exporter_1",
        "module": "exporter",
        "comment": "Export indices as COG",
        "outputs": [
          {
            "export": {
              "type": "raster",
              "format": "COG"
            },
            "param": "map",
            "value": "baum"
          },
          {
            "export": {
              "type": "raster",
              "format": "COG"
            },
            "param": "map",
            "value": "elevation@PERMANENT"
          }
        ]
      }
    ],
    "version": "1"
}
```

```bash
# processing (which ends with error)
JSON=pc_error.json
actiniapost $AUTH $JSON $URL/$ENDPOINT

# job resumption
JSONPUT=pc_noerror.json
actiniaput $AUTH $JSONPUT $STATUS_URL_POST
```

### Job resumption without new process chain

If the process is not aborted due to an error in the process chain, the job
can be resumed without sending a new process chain.
Here an example process chain where a folder `/test` is requested which does not exist inside actinia.
The process can be resumpt after the folder is created inside actinia.

`pc_error_not_in_pc.json`: Process chain with not existing folder `/test`

```json
{
    "list": [
      {
          "id": "r_mapcalc",
          "module": "r.mapcalc",
          "inputs": [
              {
                  "param": "expression",
                  "value": "baum=5"
              }
          ]
      },
      {
        "id": "ls1",
        "exe": "ls",
        "params": ["/test"]
      },
      {
          "id": "r_info1",
          "module": "r.info",
          "inputs": [
              {
                  "param": "map",
                  "value": "baum"
              }
          ],
          "flags": "g",
          "stdout": {"id": "r_info_1", "format": "kv", "delimiter": "="}
      }
    ],
    "version": "1"
}
```

```bash
# processing (which ends with error)
JSON=pc_error_not_in_pc.json
actiniapost $AUTH $JSON $URL/$ENDPOINT

# manually create /test folder inside actinia

# job resumption
curl -X PUT -H 'Content-Type: application/json' -H 'accept: application/json' -u $AUTH $STATUS_URL_POST
curl -L -u $AUTH $STATUS_URL_POST | jq
```

### Cleaning up resources which are not restarted

If a job is not restarted and the processing is not finished successfully the
interim results will not be automatically cleaned. For this you can delete the
resource storage:

```bash
# get resource storage information
actiniaget $AUTH $URL/resource_storage

# delete resource storage files older than 5 days
actiniadelete $AUTH $URL/resource_storage?olderthan=5
actiniaget $AUTH

# delete all files in the user resource storage
actiniadelete $AUTH $URL/resource_storage
```

### Using templates via the actinia-module-plugin

`pc_template_error.json`: process chain with using template index_NDVI

```json
{
    "list": [
        {
            "id": "index_NDVI_1",
            "module": "index_NDVI",
            "inputs": [
                {
                    "param": "red",
                    "value": "lsat5_1987_10@landsat"
                },
                {
                    "param": "nir",
                    "value": "lsat5_1987_20@landsat"
                }
            ],
            "outputs": [
                {
                    "param": "output",
                    "value": "ndvi",
                    "export": {"type": "file", "format": "COG"}
                }
            ]
        },
        {
            "id": "r_info1",
            "module": "r.info",
            "inputs": [
                {
                    "param": "map",
                    "value": "ndvi10"
                }
            ],
            "flags": "g",
            "stdout": {"id": "r_info_1", "format": "kv", "delimiter": "="}
        }
    ],
    "version": "1"
}
```

`pc_template_forput.json`: complete process chain without template (can be found in actinia response) :

```json
{
    "list": [
        {
            "comment": "NDVI = ( NIR - RED ) / ( NIR + RED )",
            "id": "r.mapcalc_ndvi",
            "inputs": [{
                "param": "expression",
                "value": "ndvi = float( lsat5_1987_20@landsat - lsat5_1987_10@landsat ) / float( lsat5_1987_20@landsat + lsat5_1987_10@landsat )"
            }],
            "module": "r.mapcalc"
        },
        {
            "id": "r.colors_ndvi",
            "inputs": [{
                    "param": "map",
                    "value": "ndvi"
                },
                {
                    "param": "color",
                    "value": "ndvi"
                }
            ],
            "module": "r.colors"
        },
        {
            "flags": "g",
            "id": "r_info1",
            "inputs": [{
                "param": "map",
                "value": "ndvi"
            }],
            "module": "r.info",
            "stdout": {
                "delimiter": "=",
                "format": "kv",
                "id": "r_info_1"
            }
        }
    ],
    "version": "1"
}
```

```bash
# processing (which ends with error)
JSON=pc_template_error.json
actiniapost $AUTH $JSON $URL/locations/nc_spm_08/processing_export

# job resumption (with complete process chain)
JSONPUT=pc_template_forput.json
actiniaput $AUTH $JSONPUT $STATUS_URL_POST
```
