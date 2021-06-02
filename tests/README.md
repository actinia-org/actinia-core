# Tests



## Running tests locally

__If not stated otherwise, you need to be in folder `actinia_core`__

When writing new tests it is useful to run selected tests locally and isolated. In this way it is also possible to debug interactively:

1. In the `actinia_core/docker/actinia-core-tests/Dockerfile` comment out `RUN make test` (last line)

2. Then run `docker build`:
```
docker build -f docker/actinia-core-tests/Dockerfile -t actinia-test .
```
3. Create a local `tmp_tests` folder and fill it with the files:

- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_resource_base.py`
- your_new_test(s).py


4. Start the docker container and mount your local `tmp_tests` folder:

```
docker run -it -v /path/to/tmp_tests:/src/actinia_core/tests actinia-test:latest -i

# If you want to run all tests from actinia_core/tests instead of selected ones you can use the following command:
docker run -it actinia-test:latest -i

```

5. To execute the test(s) run:

```
make test

# If you added a debugger to your test it will stop there.
# After making changes to the test, you need to close and restart the docker container (docker run ...) before testing again.
```

When you are done, add your new test(s) to `actinia_core/tests`. You can run the entire testsuite including your new tests by rebuilding the docker image and running the container without mounting (see 4.)


## Problems
Redis autorization is set by `from actinia_core.core.common import redis_interface`:
  * so this does set the password:
    ```
    import os
    from actinia_core.core.common import redis_interface # PROBLEM!!!!
    from actinia_core.core.common.config import global_config

    custom_actinia_cfg = str(os.environ["ACTINIA_CUSTOM_TEST_CFG"])
    global_config.read(custom_actinia_cfg)
    global_config.REDIS_SERVER_PW
    ```
  * and this works fine:
    ```
    import os
    from actinia_core.core.common.config import global_config

    custom_actinia_cfg = str(os.environ["ACTINIA_CUSTOM_TEST_CFG"])
    global_config.read(custom_actinia_cfg)
    global_config.REDIS_SERVER_PW
    ```

## Not working processes
* test_login.py: test_create_get_delete_user
* test_async_process_validation.py: test_async_processing_new (Webhook)
* test_asynx_process_postgis_import_export.py: all tests cause of missing PostgreSQL db
