FROM mundialis/actinia-core:0.99.26 as actinia_test

LABEL authors="Carmen Tawalika,Anika Weinmann"
LABEL maintainer="tawalika@mundialis.de,weinmann@mundialis.de"

ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0
ENV ACTINIA_CUSTOM_TEST_CFG /etc/default/actinia_test
# TODO do not set DEFAULT_CONFIG_PATH if this is fixed
ENV DEFAULT_CONFIG_PATH /etc/default/actinia_test

# install things only for tests
RUN apk add redis
RUN pip3 install iniconfig colorlog

# uninstall actinia core from FROM-image
RUN pip3 uninstall actinia-core -y

# add data for tests
RUN wget --quiet https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_micro.zip && \
  unzip nc_spm_08_micro.zip && \
  rm -f nc_spm_08_micro.zip && \
  mv nc_spm_08_micro /actinia_core/grassdb/nc_spm_08
RUN grass -text -e -c 'EPSG:4326' /actinia_core/grassdb/latlong_wgs84
RUN wget --quiet https://grass.osgeo.org/sampledata/north_carolina/nc_spm_mapset_modis2015_2016_lst.zip && \
  unzip nc_spm_mapset_modis2015_2016_lst.zip && \
  rm -f nc_spm_mapset_modis2015_2016_lst.zip && \
  mv  modis_lst /actinia_core/grassdb/nc_spm_08/modis_lst
RUN chown -R 1001:1001 /actinia_core/grassdb/nc_spm_08/modis_lst && chmod -R g+w /actinia_core/grassdb/nc_spm_08/modis_lst

# copy needed files and configs for test
COPY docker/actinia-core-alpine/actinia.cfg /etc/default/actinia
COPY docker/actinia-core-tests/actinia-test.cfg /etc/default/actinia_test
COPY Makefile Makefile
COPY tests_with_redis.sh tests_with_redis.sh
RUN chmod a+x tests_with_redis.sh

COPY requirements.txt /src/requirements.txt
RUN pip3 install -r /src/requirements.txt

# TODO: Postgres for tests
# using tests/data/poly.gpkg

COPY . /src/actinia_core
WORKDIR /src/actinia_core

RUN make install

RUN make test
