
# Installation

Requirements: docker and docker-compose

To build and deploy actinia, run

```
git clone https://github.com/actinia-org/actinia-core.git
cd actinia_core
docker-compose -f docker/docker-compose.yml up
```
Now you have a running actinia instance locally! Check with
```
curl http://127.0.0.1:8088/api/v3/version
```

* Having __trouble__? See [How to fix common startup errors](#startup-errors) below.
* Want to __start developing__? Look for [Local dev-setup with docker](#local-dev-setup) below.
* For __production deployment__, see [Production deployment](#production-deployment) below.

On startup, some GRASS GIS locations are created by default but they are still empty. How to get some geodata to start processing, see in [Testing GRASS GIS inside a container](#grass-gis)  below.

<a id="startup-errors"></a>
# How to fix common startup errors
* if a redis db is running locally this will fail. Run and try again:
```
/etc/init.d/redis-server stop
```
* if you see an error like "max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]", run
```
sudo sysctl -w vm.max_map_count=262144
```
  this is only valid on runtime. To change permanently, set vm.max_map_count in /etc/sysctl.conf


<a id="local-dev-setup"></a>
# Local dev-setup with docker

If desired, you can also directly start here without installing actinia first. You only need to have cloned and checked out the actinia_core repository.

If you use [vscode](https://code.visualstudio.com/), open actinia_core as a workspace. This can be done by eg. typing `code $PATH_TO_MY_ACTINIA_CORE_CHECKOUT` in a terminal. Then press `F5` and after a few seconds, a browser window should be opened pointing to the version endpoint. For debugging tips, [read the docs](https://code.visualstudio.com/Docs/editor/debugging#_debug-actions).

__If not stated otherwise, you need to be in folder `actinia_core/docker`__

To overwrite default config and uninstall actinia-core to use local source code, build a Dockerimage with the docker-compose-dev.yml file:
```
docker-compose -f docker-compose-dev.yml build
docker-compose -f docker-compose-dev.yml run --rm --service-ports --entrypoint sh actinia
```
Be aware, that your local actinia source code is now mounted in the docker container!
Then, inside the docker container, run
```
python3 setup.py install
sh /src/start.sh
```
Now you have a running actinia instance locally.
For debugging or if you need to start the wsgi server regularly during development, you don't need to repeat all steps from inside the start.sh file. Instead, run the server with only one worker:
```
python3 setup.py install
gunicorn -b 0.0.0.0:8088 -w 1 --access-logfile=- -k gthread actinia_core.main:flask_app

```
To test your local changes, you best use the Test Dockerimage:
```
# changing directory is necessary to have the correct build context
(cd .. && docker build -f docker/actinia-core-tests/Dockerfile -t actinia-test .)
```
To dive deeper into testing + development, see the [test README](https://github.com/actinia-org/actinia-core/blob/main/tests/README.md)

To lint your local changes, run
```
(cd ../src && flake8 --config=../.flake8 --count --statistics --show-source --jobs=$(nproc) .)
```


## Local dev-setup with redis queue
- change queue type to redis in `docker/actinia-core-dev/actinia.cfg`
- start one actinia-core instance (the job receiver) as usual, eg. with vscode
- open actinia-core on the command line and run
`docker-compose -f docker/docker-compose-dev.yml run --rm --service-ports --entrypoint sh actinia-worker` to start the container for job-execution
- inside this container, reinstall actinia-core and start the redis-queue-worker
    ```
    pip3 uninstall actinia_core
    cd /src/actinia_core && pip3 install .
    actinia-worker job_queue_0 -c /etc/default/actinia
    ```

## Local dev-setup with configured endpoints
- add an endpoints configuration csv file like `docker/actinia-core-dev/endpoints.csv`
  with all desired endpoints including method:
  ```
  Class_of_the_endpoint;method1,method2
  Class_of_the_endpoint2;method1
  ```
- make sure that the file is added in the `docker/actinia-core-dev/Dockerfile` with e.g. `COPY docker/actinia-core-dev/endpoints.csv /etc/default/actinia_endpoints.csv`
- add `endpoints_config = /etc/default/actinia_endpoints.csv` to the `API` section in the `docker/actinia-core-dev/actinia.cfg` file
- then build and run actinia dev-setup as usual.

<a id="grass-gis"></a>
# Testing GRASS GIS inside a container

Inside the container, you can run GRASS GIS with:
```
# Download GRASS GIS test data and put it into a directory (nc_spm_08_grass7 works also for GRASS GIS 8)
cd /actinia_core/grassdb
wget https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_grass7.tar.gz && \
     tar xzvf nc_spm_08_grass7.tar.gz && \
     rm -f nc_spm_08_grass7.tar.gz && \
     rm -rf nc_spm_08 && \
     mv nc_spm_08_grass7 nc_spm_08
cd -

grass --version
grass /actinia_core/grassdb/nc_spm_08/PERMANENT --exec r.univar -g elevation
grass /actinia_core/grassdb/nc_spm_08/PERMANENT --exec v.random output=myrandom n=42
grass /actinia_core/grassdb/nc_spm_08/PERMANENT --exec v.info -g myrandom
```
You now have some data which you can access through actinia. To get information
via API, start actinia with gunicorn and run
```
curl -u actinia-gdi:actinia-gdi http://127.0.0.1:8088/api/v3/locations/nc_spm_08/mapsets
```
The folder where you downloaded the data into (`/actinia_core/grassdb`) is mounted into your docker container via the compose file, so all data is kept, even if your docker container restarts.

If you want to download the data not from inside the container but from your normal system, download https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_grass7.tar.gz, extract it and place it into actinia-core/docker/actinia-core-data/grassdb/

<a id="production-deployment"></a>
# Production and Cloud deployment

To run actinia_core in production systems, best with multiple actinia_core instances, find more detailed information in the dedicated [actinia-docker](https://github.com/actinia-org/actinia-docker) repository.


# Building the API documentation

To build the apidocs, run
```
bash create-docs.sh
```
