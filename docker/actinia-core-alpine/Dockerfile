FROM mundialis/actinia:alpine-dependencies-2023-06-03 as build-base
FROM osgeo/grass-gis:releasebranch_8_3-alpine as grass

FROM build-base as build

LABEL authors="Carmen Tawalika,Anika Bettge,Markus Neteler,Sören Gebbert"
LABEL maintainer="tawalika@mundialis.de,weinmann@mundialis.de,neteler@mundialis.de"

COPY . /src/actinia_core
WORKDIR /src/actinia_core
RUN pip3 install build && python3 -m build --outdir /build .
RUN if [[ -f /build/UNKNOWN* ]];then echo "ERROR - Check actinia-core build";exit 1;fi


FROM mundialis/actinia:alpine-dependencies-2023-06-03 as actinia_installation

ENV LC_ALL "en_US.UTF-8"
ENV GDAL_CACHEMAX=2000
ENV GRASS_COMPRESSOR=ZSTD
ENV GRASS_SKIP_MAPSET_OWNER_CHECK 1
ENV GISBASE ""
ENV ACTINIA_API_VERSION 3.4.0

USER root

# GRASS GIS SETUP
COPY --from=grass /usr/local/bin/grass /usr/local/bin/grass
COPY --from=grass /usr/local/grass* /usr/local/grass/
RUN pip3 install --upgrade pip six grass-session --ignore-installed six
RUN ln -s /usr/local/grass `grass --config path`
RUN grass --tmp-location EPSG:4326 --exec g.version -rge && \
    pdal --version && \
    python3 --version

# install GRASS GIS addon d.rast.multi, because it is needed for STRDS render
# endpoint
RUN grass --tmp-location EPSG:4326 --exec g.extension -s \
  extension=d.rast.multi url=https://github.com/mundialis/d_rast_multi

# actinia-core and actinia libs BUILD
WORKDIR /build
ARG WHEEL_NAME=actinia_api-${ACTINIA_API_VERSION}-py3-none-any.whl
RUN curl -L --output /build/${WHEEL_NAME} \
    https://github.com/actinia-org/actinia-api/releases/download/${ACTINIA_API_VERSION}/${WHEEL_NAME}

# Install actinia-core and libs
COPY --from=build /build/*.whl /build/
RUN pip3 install /build/*

# Duplicate install actinia_core requirements. They are already included
# in alpine-build / alpine-runtime images, but check for updates here.
COPY requirements.txt /src/requirements.txt
RUN pip3 install -r /src/requirements.txt

# Copy actinia config file and start scripts + set needed envs
COPY docker/actinia-core-alpine/actinia.cfg /etc/default/actinia
COPY docker/actinia-core-alpine/start.sh /src/start.sh

# Create the data directories
RUN mkdir -p /actinia_core/grassdb && \
    mkdir -p /actinia_core/resources && \
    mkdir -p /actinia_core/workspace/tmp && \
    mkdir -p /actinia_core/workspace/temp_db && \
    mkdir -p /actinia_core/workspace/actinia && \
    mkdir -p /actinia_core/workspace/download_cache && \
    mkdir -p /actinia_core/userdata && \
    ln -s /actinia_core /root/actinia


FROM actinia_installation as actinia

VOLUME /grassdb
WORKDIR /src/actinia_core

ENTRYPOINT ["/bin/sh"]
CMD ["/src/start.sh"]

EXPOSE 8088
