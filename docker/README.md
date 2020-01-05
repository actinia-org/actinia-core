# Version matrix

| docker image  | actinia-core                             | actinia-core-latest                      | actinia-core-dev       | actinia-core-prod           |
|---------------|------------------------------------------|------------------------------------------|------------------------|-----------------------------|
| base image    | mundialis/grass-py3-pdal:stable-ubuntu   | mundialis/grass-py3-pdal:latest-ubuntu19 | mundialis/actinia-core | mundialis/actinia-core:0.99 |
| Linux version | Ubuntu 18.04                             | Ubuntu 19.10                             |                        |                             |
| GRASS GIS     | 7.8.x                                    | 7.9.x                                    | ?                      | ?                           |
| GDAL          | 2.2.3.3                                  | 2.4.2                                    |                        |                             |
| PROJ          | 4.9.3                                    | 5.2.0                                    |                        |                             |
| PDAL          | 1.8.0                                    | 1.9.1                                    |                        |                             |

Latest update: 5 Jan 2020
 

# Requirements

 * docker
 * docker-compose

# Installation

To obtain the actinia_core source code, run

```
mkdir $HOME/repos/
cd $HOME/repos/

git clone https://github.com/mundialis/actinia_core.git
cd actinia_core/docker/
```

In this directory are the needed docker-compose scripts available.

# Building and deployment of actinia_core

To build and deploy actinia, run

```
docker-compose build --pull

# Note: adding -d starts the containers in the background and leaves them
#       running; without docker-compose will show the logging in the terminal:
docker-compose up

# or DEV setup
docker-compose -f docker-compose-dev.yml build
docker-compose -f docker-compose-dev.yml up
```

This will keep logging in the terminal foreground.

__See below for production deployment__.

# Notes on actinia_core development and testing GRASS GIS inside a container

For actinia_core development, run and enter the running container (in a separate terminal):
```
docker-compose run --rm --service-ports --entrypoint /bin/bash -v $HOME/repos/actinia_core/src:/src/actinia_core/src actinia-core

docker-compose -f docker-compose-dev.yml run --rm --service-ports --entrypoint /bin/bash -v $HOME/repos/actinia/actinia_core/src:/src/actinia_core/src -v $HOME/repos/actinia/actinia_core/scripts:/src/actinia_core/scripts actinia-core
```

Inside the container, you can run GRASS GIS with:
```
# Download GRASS GIS test data and put it into a directory
cd /actinia_core/grassdb
wget https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_grass7.tar.gz && \
     tar xzvf nc_spm_08_grass7.tar.gz && \
     rm -f nc_spm_08_grass7.tar.gz && \
     mv nc_spm_08_grass7 nc_spm_08
cd -

grass --version
grass /actinia_core/grassdb/nc_spm_08/PERMANENT --exec r.univar -g elevation
grass /actinia_core/grassdb/nc_spm_08/PERMANENT --exec v.random output=myrandom n=42
grass /actinia_core/grassdb/nc_spm_08/PERMANENT --exec v.info -g myrandom
```

Alternatively, run the actinia_core server with your mounted source code inside the container:

```
cd /src/actinia_core
python3 setup.py install

bash /src/start-dev.sh

# python3 -m actinia_core.main
gunicorn -b 0.0.0.0:8088 -w 1 --access-logfile=- -k gthread actinia_core.main:flask_app

```
If you have problems with cache, run
```
python3 setup.py clean --all
```

# Testing actinia with API calls

And test from outside with API calls, e.g.:

```
# on the same server
curl -u actinia-gdi:actinia-gdi 'http://127.0.0.1:8088/api/v1/locations'

# from another server (update IP to that of the actinia server), e.g.:
curl -u actinia-gdi:actinia-gdi 'http://10.133.7.128:8088/api/v1/locations'
```

# Production deployment

To run actinia_core in production systems, you can use the docker-compose-prod.yml. Please change before the default redis password in redis_data/config/.redis and inside the actinia.cfg. To start the server, run:

```
docker-compose -f docker-compose-prod.yml build
docker-compose -f docker-compose-prod.yml up -d
```
Then actinia runs at 'http://127.0.0.1:8088' and depending on your server settings might be accessible from outside. Because of this the start.sh is overwritten to not create any user to avoid security vulnarability. You will have to use a clean redis database to avoid stored actinia credentials from previous runs. You have to create the user by yourself by using the build-in actinia-user cli. __Please change below username (-u) and password (-w)__:
```
# list help about the cli tool:
docker-compose -f docker-compose-prod.yml exec actinia-core \
    actinia-user --help

# create a user and grant permissions to mapsets:
docker-compose -f docker-compose-prod.yml exec actinia-core \
    actinia-user create -u actinia-core -w actinia-core -r user -g user -c 100000000 -n 1000 -t 6000
docker-compose -f docker-compose-prod.yml exec actinia-core \
    actinia-user update -u actinia-core -d nc_spm_08/PERMANENT
```
Read more about user roles here: https://actinia.mundialis.de/tutorial/actinia_concepts.html#user-user-roles-and-user-groups

# Testing the actinia server

After deployment, you should be able to access the endpoints.

Examples:

* https://actinia.mundialis.de/latest/version
* https://actinia.mundialis.de/latest/health_check
* requires authorization (actinia user):
    * https://actinia.mundialis.de/api/v1/locations

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
