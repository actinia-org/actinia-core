# Tests



## Running tests locally

__If not stated otherwise, you need to be in folder `actinia_core`__

When writing new tests it is useful to run tests locally and isolated. In this way it is also possible to debug interactively:

1. in the `actinia_core/docker/actinia-core-tests/Dockerfile` comment out `RUN make test` (last line)

2. docker build
```
docker build -f docker/actinia-core-tests/Dockerfile -t actinia-test .
```
3. create local `tmp_tests` folder and fill it with

- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_resource_base.py`
- your new test(s)


4. start docker container and mount your local `tmp_tests` folder
```
docker run -it -v /path/to/tmp_tests:/src/actinia_core/tests actinia-test:latest -i
```

5. to run the new test(s) run
```
make test
```

When you are done, add your new test(s) to `actinia_core/tests`.


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
