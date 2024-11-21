FROM mundialis/actinia-core:grass8.4 AS actinia_test

LABEL authors="Carmen Tawalika,Anika Weinmann"
LABEL maintainer="tawalika@mundialis.de,weinmann@mundialis.de"

ENV DEFAULT_CONFIG_PATH=/etc/default/actinia_test
# Path must be equal to actinia config "GRASS_DATABASE"
ARG GRASS_DATABASE=/tmp/actinia_core/grassdb

# add data for tests
WORKDIR ${GRASS_DATABASE}
RUN wget --quiet https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_micro.zip && \
  unzip nc_spm_08_micro.zip && \
  rm -f nc_spm_08_micro.zip && \
  mv nc_spm_08_micro nc_spm_08
RUN grass -e -c 'EPSG:4326' latlong_wgs84
RUN wget --quiet https://grass.osgeo.org/sampledata/north_carolina/nc_spm_mapset_modis2015_2016_lst_grass8.zip && \
  unzip nc_spm_mapset_modis2015_2016_lst_grass8.zip && \
  rm -f nc_spm_mapset_modis2015_2016_lst_grass8.zip && \
  mv  modis_lst nc_spm_08/modis_lst
RUN chown -R 1001:1001 nc_spm_08/modis_lst && chmod -R g+w nc_spm_08/modis_lst

# install GRASS addons required for tests
# TODO use --tmp-project if actinia-core uses GRASS 8.4
RUN grass --tmp-location EPSG:4326 --exec g.extension -s extension=r.colors.out_sld

# install things only for tests
# DL3013 # Pin versions in pip
# DL3018: Pin versions in apk add
# hadolint ignore=DL3013,DL3018
RUN apk add --no-cache redis &&  \
    pip install --no-cache-dir pytest pytest-cov iniconfig

# uninstall actinia-core and directories from FROM-image
RUN pip uninstall actinia-core -y && \
    rmdir /actinia_core/grassdb &&  \
    rmdir /actinia_core/userdata &&  \
    rmdir /actinia_core/resources &&  \
    rmdir /actinia_core/workspace/actinia &&  \
    rmdir /actinia_core/workspace/download_cache &&  \
    rmdir /actinia_core/workspace/temp_db &&  \
    rmdir /actinia_core/workspace/tmp &&  \
    rmdir /actinia_core/workspace &&  \
    rmdir /actinia_core &&  \
    rm /etc/default/actinia

# copy needed files and configs for test
# COPY docker/actinia-core-alpine/actinia.cfg /etc/default/actinia
COPY docker/actinia-core-tests/actinia-test.cfg /etc/default/actinia_test
COPY docker/actinia-core-tests/actinia-test-noauth.cfg /etc/default/actinia_test_noauth
COPY docker/actinia-core-tests/actinia-test-worker-usedby-api.cfg /etc/default/actinia_test_worker_usedby_api
COPY docker/actinia-core-tests/actinia-test-worker-usedby-worker.cfg /etc/default/actinia_test_worker_usedby_worker

# TODO: Postgres for tests
# using tests/data/poly.gpkg

COPY . /src/actinia_core
WORKDIR /src/actinia_core

RUN make install

# RUN make test
