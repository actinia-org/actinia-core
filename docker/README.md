
# Installation

Requirements: docker and docker-compose

To build and deploy actinia, run

```
git clone https://github.com/mundialis/actinia_core.git
cd actinia_core
docker-compose -f docker/docker-compose.yml up
```
Now you have a running actinia instance locally! Check with
```
curl http://127.0.0.1:8088/api/v2/version
```

* Having __trouble__? See [How to fix common startup errors](#startup-errors) below.
* Want to __start developing__? Look for [Local dev-setup with docker](#local-dev-setup) below.
* For __production deployment__, see [Production deployment](#production-deployment) below.

On startup, some GRASS GIS locations are created by default but they are still empty. How to get some geodata to start processing, see in [Testing GRASS GIS inside a container](#grass-gis)  below.


# actinia version matrix

| docker image  | actinia-core                           | actinia-core-latest                      | actinia-core-dev       | actinia-core-prod           |
|---------------|----------------------------------------|------------------------------------------|------------------------|-----------------------------|
| base image    | mundialis/grass-py3-pdal:stable-ubuntu | mundialis/grass-py3-pdal:latest-ubuntu   | mundialis/actinia-core | mundialis/actinia-core:0.99 |
| [dockerhub tag](https://hub.docker.com/repository/docker/mundialis/actinia-core/tags) | mundialis/actinia:stable | mundialis/actinia:latest |    |       |
| Linux version | Ubuntu 20.04                           | Ubuntu 20.04                             |                        |                             |
| GRASS GIS     | 7.8.x                                  | 7.9.x                                    |                        |                             |
| GDAL          | 3.0.4                                  | 3.0.4                                    |                        |                             |
| PROJ          | 6.3.1                                  | 6.3.1                                    |                        |                             |
| PDAL          | 2.2.0                                  | 2.2.0                                    |                        |                             |
| Python        | 3.8.5                                  | 3.8.5                                    |                        |                             |

Latest update: 16 Dec 2020

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
To dive deeper into testing + development, see the [test README](https://github.com/mundialis/actinia_core/blob/main/tests/README.md)

To lint your local changes, run
```
(cd ../src && flake8 --config=../.flake8 --count --statistics --show-source --jobs=$(nproc) .)
```


## Local dev-setup for actinia-core plugins
To also integrate dev setup for actinia-core plugins
(eg. actinia-actinia-metadata-plugin or actinia-module-plugin), uninstall them
in actinia-core-dev/Dockerfile (see outcommented code), build and run like
described above and rebuild from your mounted source code:
```
docker-compose -f docker-compose-dev.yml build
docker-compose -f docker-compose-dev.yml run --rm --service-ports --entrypoint sh actinia

(cd /src/actinia_core && python3 setup.py install)
(cd /src/actinia-metadata-plugin && python3 setup.py install)
(cd /src/actinia-module-plugin && python3 setup.py install)

# you can also run tests here, eg.
(cd /src/actinia-module-plugin && python3 setup.py test)

gunicorn -b 0.0.0.0:8088 -w 1 --access-logfile=- -k gthread actinia_core.main:flask_app
```

To avoid cache problems, remove the packaged actinia_core (already done in Dockerfile)
```
pip3 uninstall actinia_core -y
```
If you have other problems with cache, run
```
python3 setup.py clean --all
```
To reach kibana (only setup in docker-compose-dev.yml, currently outcommented), open http://127.0.0.1:5601 in your browser.

If if elasticsearch is shutting down immediately (if used), check logs with
```
docker logs docker_elasticsearch_1
```

<a id="grass-gis"></a>
# Testing GRASS GIS inside a container

Inside the container, you can run GRASS GIS with:
```
# Download GRASS GIS test data and put it into a directory
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
curl -u actinia-gdi:actinia-gdi http://127.0.0.1:8088/api/v2/locations/nc_spm_08/mapsets
```
The folder where you downloaded the data into (`/actinia_core/grassdb`) is mounted into your docker container via the compose file, so all data is kept, even if your docker container restarts.

If you want to download the data not from inside the container but from your normal system, download https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_grass7.tar.gz, extract it and place it into actinia-core/docker/actinia-core-data/grassdb/

<a id="production-deployment"></a>
# Production deployment

To run actinia_core in production systems, you can use the docker-compose-prod.yml. Please change before the default redis password in redis_data/config/.redis and inside the actinia.cfg. To start the server, run:

```
docker-compose -f docker-compose-prod.yml build
docker-compose -f docker-compose-prod.yml up -d
```
Then actinia runs at 'http://127.0.0.1:8088' and depending on your server settings might be accessible from outside. Because of this the start.sh is overwritten to not create any user to avoid security vulnerability. You will have to use a clean redis database to avoid stored actinia credentials from previous runs. You have to create the user by yourself by using the built-in actinia-user cli. __Please change below username (-u) and password (-w)__:
```
# list help about the cli tool:
docker-compose -f docker-compose-prod.yml exec actinia \
    actinia-user --help

# create a user and grant permissions to mapsets:
docker-compose -f docker-compose-prod.yml exec actinia \
    actinia-user create -u actinia-core -w actinia-core -r user -g user -c 100000000 -n 1000 -t 6000
docker-compose -f docker-compose-prod.yml exec actinia \
    actinia-user update -u actinia-core -d nc_spm_08/PERMANENT
```
Read more about user roles here: https://actinia.mundialis.de/tutorial/actinia_concepts.html#user-user-roles-and-user-groups

# Testing the actinia server

After deployment, you should be able to access the endpoints.

Examples:

* https://actinia.mundialis.de/latest/version
* https://actinia.mundialis.de/latest/health_check
* requires authorization (actinia user):
    * https://actinia.mundialis.de/api/v2/locations

# Cloud deployment with multiple actinia_core instances

For cloud deployment, you can use the `docker-swarm.sh` script as a starting point.

Shutdown current actinia swarm:
```
docker stack rm actinia_swarm
docker swarm leave --force
```
Start new actinia swarm:
```
bash docker-swarm.sh
```
See the scripts for hints.

# Building the API documentation

To build the apidocs, run
```
bash create-docs.sh
```
