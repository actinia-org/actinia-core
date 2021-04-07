FROM mundialis/actinia-core:0.99.24 as actinia_test

LABEL authors="Carmen Tawalika,Anika Weinmann,Markus Neteler,Sören Gebbert"
LABEL maintainer="tawalika@mundialis.de,weinmann@mundialis.de,neteler@mundialis.de,soerengebbert@gmail.com"

COPY . /src/actinia_core
WORKDIR /src/actinia_core

# uninstall actinia core from FROM-image
RUN pip3 uninstall actinia-core -y
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0

# Duplicate install actinia_core requirements. They are already wheels in
# /build folder, keep to check match of required packages
COPY requirements.txt /src/requirements.txt
RUN pip3 install -r /src/requirements.txt

# needed files for test
COPY tests_with_redis.sh tests_with_redis.sh
COPY Makefile Makefile
RUN chmod a+x tests_with_redis.sh

# set config for test
COPY docker/actinia-core-alpine/actinia.cfg /etc/default/actinia
COPY docker/actinia-core-tests/actinia-test.cfg /etc/default/actinia_test
ENV ACTINIA_CUSTOM_TEST_CFG /etc/default/actinia_test
# TODO do not set DEFAULT_CONFIG_PATH if this is fixed
ENV DEFAULT_CONFIG_PATH /etc/default/actinia_test

# copy tests inside docker
COPY tests tests

# install things only for tests
RUN apk add redis
RUN pip3 install iniconfig colorlog

# add data for tests
RUN wget https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_micro.zip && \
  unzip nc_spm_08_micro.zip && \
  rm -f nc_spm_08_micro.zip && \
  mv nc_spm_08_micro /actinia_core/grassdb/nc_spm_08
RUN grass -text -e -c 'EPSG:4326' /actinia_core/grassdb/latlong_wgs84
RUN wget https://grass.osgeo.org/sampledata/north_carolina/nc_spm_mapset_modis2015_2016_lst.zip && \
  unzip nc_spm_mapset_modis2015_2016_lst.zip && \
  rm -f nc_spm_mapset_modis2015_2016_lst.zip && \
  mv  modis_lst /actinia_core/grassdb/nc_spm_08/modis_lst
RUN chown -R 1001:1001 /actinia_core/grassdb/nc_spm_08/modis_lst && chmod -R g+w /actinia_core/grassdb/nc_spm_08/modis_lst

# TODO: Postgres for tests
# useing tests/data/poly.gpkg

RUN make test
