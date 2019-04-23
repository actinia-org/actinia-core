To run actinia, run

```
docker-compose build
docker-compose up
```

For actinia-core development, run and enter the running container.
```
docker-compose run --rm --entrypoint /bin/bash -v $HOME/repos/actinia_core/src:/src/actinia_core/src actinia-core
```

Inside the container, you can run GRASS with:
```
export GISBASE="/usr/local/grass77/"

# Download GRASS GIS test data and put it into a directory
cd /actinia_core/grassdb
wget https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_grass7.tar.gz && \
     tar xzvf nc_spm_08_grass7.tar.gz && \
     rm -f nc_spm_08_grass7.tar.gz && \
     mv nc_spm_08_grass7 nc_spm_08
cd -

grass /actinia_core/grassdb/nc_spm_08/PERMANENT
```

Or run the actinia-core server with your mounted source code:
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

And test from outside with API calls, e.g.:
```
curl -u actinia-gdi:actinia-gdi 'http://127.0.0.1:8088/api/v1/locations'
```

For cloud deployment, you can use the deploy_swarm.sh script as a starting point.

```
bash docker-swarm.sh
```

To build the apidocs, run
```
bash create-docs.sh
```
