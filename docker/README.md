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
docker-compose build

# Note: adding -d starts the containers in the background and leaves them
#       running; without docker-compose will show the logging in the terminal:
docker-compose up
```

This will keep logging in the terminal foreground.

# Notes on actinia_core development and testing GRASS GIS inside a container

For actinia_core development, run and enter the running container (in a separate terminal):
```
cd $HOME/repos/actinia_core/docker/
docker-compose run --rm --entrypoint /bin/bash -v $HOME/repos/actinia_core/src:/src/actinia_core/src actinia_core
```

Inside the container, you can run GRASS GIS with:
```
export GISBASE="/usr/local/grass77/"

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
gunicorn -b 0.0.0.0:8088 -w 1 actinia_core.main:flask_app

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

# Cloud deployment with multiple actinia_core instances

For cloud deployment, you can use the `deploy_swarm.sh` script as a starting point.

```
bash docker-swarm.sh
```

# Building the API documentation

To build the apidocs, run
```
bash create-docs.sh
```
