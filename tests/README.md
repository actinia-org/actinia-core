# Tests

## Running tests locally

```
docker build  --file docker/actinia-core-alpine/Dockerfile  --tag actinia-core:g78-stable-alpine .
```

run tests inside docker
```
docker run -it --mount type=bind,source="$(pwd)"/tests,target=/src/actinia_core/tests  --mount type=bind,source="$(pwd)"/grassdb/nc_spm_08_micro,target=/actinia_core/grassdb/nc_spm_08 actinia-core:g78-stable-alpine /bin/sh

make test
```

## Problems
Redis autorization is set by `from actinia_core.common import redis_interface`:
  * so this does set the password:
    ```
    import os
    from actinia_core.common import redis_interface # PROBLEM!!!!
    from actinia_core.common.config import global_config

    custom_actinia_cfg = str(os.environ["ACTINIA_CUSTOM_TEST_CFG"])
    global_config.read(custom_actinia_cfg)
    global_config.REDIS_SERVER_PW
    ```
  * and this works fine:
    ```
    import os
    from actinia_core.common.config import global_config

    custom_actinia_cfg = str(os.environ["ACTINIA_CUSTOM_TEST_CFG"])
    global_config.read(custom_actinia_cfg)
    global_config.REDIS_SERVER_PW
    ```

## Not working processes
* test_login.py: test_create_get_delete_user
* test_async_process_validation.py: test_async_processing_new (Webhook)
* test_asynx_process_postgis_import_export.py: all tests cause of missing PostgreSQL db
