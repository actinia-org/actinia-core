# Tests

Build docker (bisher muss `RUN make test noch auskommentiert sein`)
```
docker build  --file docker/actinia-core-alpine/Dockerfile  --tag actinia-core:g78-stable-alpine .
```

run tests inside docker
```
docker run -it --mount type=bind,source="$(pwd)"/tests_running,target=/src/actinia_core/tests  --mount type=bind,source="$(pwd)"/grassdb/nc_spm_08_micro,target=/actinia_core/grassdb/nc_spm_08 actinia-core:g78-stable-alpine /bin/sh

make test
```

## Problems
1. `actinia-test.cfg`: `COPY docker/actinia-core-alpine/actinia-test.cfg /etc/default/actinia_test` funktioniert nicht!
2. Redis autorization is set by `from actinia_core.resources.common import redis_interface`:
  * so this does set the password:
    ```
    import os
    from actinia_core.resources.common import redis_interface # PROBLEM!!!!
    from actinia_core.resources.common.config import global_config

    custom_actinia_cfg = str(os.environ["ACTINIA_CUSTOM_TEST_CFG"])
    global_config.read(custom_actinia_cfg)
    global_config.REDIS_SERVER_PW
    ```
  * and this works fine:
    ```
    import os
    from actinia_core.resources.common.config import global_config

    custom_actinia_cfg = str(os.environ["ACTINIA_CUSTOM_TEST_CFG"])
    global_config.read(custom_actinia_cfg)
    global_config.REDIS_SERVER_PW
    ```

## Nicht funktionierende Tests
* test_login.py: test_create_get_delete_user
* test_async_raster_export.py: test_export_region
* test_resource_logging.py: test_list, test_logging
* test_async_process_validation.py: test_async_processing_new (Webhook)
* test_process_queue.py: is not listed in the tests
*
