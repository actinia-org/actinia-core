FROM mundialis/grass-py3-pdal:stable-alpine as grass
FROM mundialis/esa-snap:s1tbx-8.0.1 as snap
FROM mundialis/actinia-core:alpine-build-pkgs_v7 as build

LABEL authors="Carmen Tawalika,Anika Bettge,Markus Neteler,Sören Gebbert"
LABEL maintainer="tawalika@mundialis.de,bettge@mundialis.de,neteler@mundialis.de,soerengebbert@gmail.com"

COPY . /src/actinia_core

WORKDIR /src/actinia_core
#RUN git describe --dirty --tags --long --first-parent
#RUN git checkout .
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0
RUN python3 setup.py sdist bdist_wheel -d /build
# RUN pip3 wheel -r requirements.txt -w /build
# RUN python3 -m pep517.build --out-dir /build .


FROM mundialis/actinia-core:alpine-runtime-pkgs_v7 as actinia_installation

ENV LC_ALL "en_US.UTF-8"
ENV GDAL_CACHEMAX=2000
ENV GRASS_COMPRESSOR=ZSTD
ENV GRASS_SKIP_MAPSET_OWNER_CHECK 1

USER root

# ESA SNAP SETUP
ENV LD_LIBRARY_PATH ".:$LD_LIBRARY_PATH"
COPY --from=snap /root/.snap /root/.snap
COPY --from=snap /usr/local/snap /usr/local/snap
RUN (cd /root/.snap/snap-python/snappy && python3 setup.py install)
RUN /usr/bin/python3 -c 'from snappy import ProductIO'
RUN /usr/bin/python3 /root/.snap/about.py

# GRASS GIS SETUP
COPY --from=grass /usr/local/bin/grass /usr/local/bin/grass
COPY --from=grass /usr/local/grass* /usr/local/grass/
RUN pip3 install --upgrade pip six grass-session
RUN ln -s /usr/local/grass /usr/local/grass7
RUN ln -s /usr/local/grass `grass --config path`
RUN grass --tmp-location EPSG:4326 --exec g.version -rge && \
    pdal --version && \
    python3 --version

# GRASS GIS addons BUILD
# git clone various openEO plugins (local checkout due to non-standard repo structure)
RUN git clone https://github.com/mundialis/openeo-addons.git /src/openeo-addons
COPY docker/grass_addons_list.csv /src/grass_addons_list.csv

RUN while IFS=, read -r ADDON SERVER; do unset URL; test -z $SERVER || URL="url=$SERVER"; grass --tmp-location EPSG:4326 --exec g.extension -s extension=$ADDON $URL;done < /src/grass_addons_list.csv

# Install actinia-core
COPY --from=build /build/*.whl /build/
# the problem with getting broken 20.0.1 seems to be overcome, the outcommenting
# RUN apk add curl && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py pip==20.0.2 && rm get-pip.py
RUN pip3 install /build/*

# Duplicate install actinia_core requirements. They are already wheels in
# /build folder, keep to check match of required packages
COPY requirements.txt /src/requirements.txt
RUN pip3 install -r /src/requirements.txt

# Copy actinia config file and start scripts + set needed envs
COPY docker/actinia-core-alpine/actinia.cfg /etc/default/actinia
COPY docker/actinia-core-alpine/start.sh /src/start.sh
COPY docker/actinia-core-alpine/start-dev.sh /src/start-dev.sh
ENV GISBASE ""

# Create the database directories
RUN mkdir -p /actinia_core/grassdb && \
    mkdir -p /actinia_core/resources && \
    mkdir -p /actinia_core/workspace/tmp && \
    mkdir -p /actinia_core/workspace/temp_db && \
    mkdir -p /actinia_core/workspace/actinia && \
    mkdir -p /actinia_core/workspace/download_cache && \
    mkdir -p /actinia_core/userdata && \
    ln -s /actinia_core /root/actinia

# tests
FROM actinia_installation as actinia_test

WORKDIR /src/actinia_core
COPY --from=build /src/actinia_core /src/actinia_core

COPY tests_with_redis.sh tests_with_redis.sh
COPY Makefile Makefile
RUN chmod a+x tests_with_redis.sh

# set config for test
COPY docker/actinia-core-alpine/actinia.cfg /etc/default/actinia
COPY docker/actinia-core-tests/actinia-test.cfg /etc/default/actinia_test
ENV ACTINIA_CUSTOM_TEST_CFG /etc/default/actinia_test
# TODO do not set DEFAULT_CONFIG_PATH if this is fixed
ENV DEFAULT_CONFIG_PATH /etc/default/actinia_test

# TODO remove if all tests are running
RUN rm -rf tests
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
