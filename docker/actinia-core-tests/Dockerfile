FROM mundialis/actinia-core:latest as actinia_test

LABEL authors="Carmen Tawalika,Anika Weinmann"
LABEL maintainer="tawalika@mundialis.de,weinmann@mundialis.de"

ENV ACTINIA_API_VERSION 3.4.0

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
RUN grass -e -c 'EPSG:4326' /actinia_core/grassdb/latlong_wgs84
RUN wget --quiet https://grass.osgeo.org/sampledata/north_carolina/nc_spm_mapset_modis2015_2016_lst_grass8.zip && \
  unzip nc_spm_mapset_modis2015_2016_lst_grass8.zip && \
  rm -f nc_spm_mapset_modis2015_2016_lst_grass8.zip && \
  mv  modis_lst /actinia_core/grassdb/nc_spm_08/modis_lst
RUN chown -R 1001:1001 /actinia_core/grassdb/nc_spm_08/modis_lst && chmod -R g+w /actinia_core/grassdb/nc_spm_08/modis_lst

# install actinia-api
RUN pip3 install actinia-api@https://github.com/actinia-org/actinia-api/releases/download/${ACTINIA_API_VERSION}/actinia_api-${ACTINIA_API_VERSION}-py3-none-any.whl

# install GRASS addons required for tests
RUN grass --tmp-location EPSG:4326 --exec g.extension -s extension=r.colors.out_sld
RUN grass --tmp-location EPSG:4326 --exec g.extension -s \
  extension=d.rast.multi url=https://github.com/mundialis/d_rast_multi

# copy needed files and configs for test
COPY docker/actinia-core-alpine/actinia.cfg /etc/default/actinia
COPY docker/actinia-core-tests/actinia-test.cfg /etc/default/actinia_test
COPY docker/actinia-core-tests/actinia-test-noauth.cfg /etc/default/actinia_test_noauth

RUN pip3 install pytest pytest-cov

# TODO: Postgres for tests
# using tests/data/poly.gpkg

COPY . /src/actinia_core
WORKDIR /src/actinia_core

RUN make install

# RUN make test
