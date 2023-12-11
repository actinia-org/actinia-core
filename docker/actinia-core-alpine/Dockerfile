FROM mundialis/actinia:alpine-dependencies-2023-12-06 as build-base
FROM osgeo/grass-gis:releasebranch_8_3-alpine as grass

FROM build-base as requirements

LABEL authors="Carmen Tawalika,Anika Weinmann,Markus Neteler,Sören Gebbert"
LABEL maintainer="tawalika@mundialis.de,weinmann@mundialis.de,neteler@mundialis.de"

ENV LC_ALL "en_US.UTF-8"
ENV GDAL_CACHEMAX=2000
ENV GRASS_COMPRESSOR=ZSTD
ENV GRASS_SKIP_MAPSET_OWNER_CHECK 1
ENV GISBASE ""

# GRASS GIS SETUP
COPY --from=grass /usr/local/bin/grass /usr/local/bin/grass
COPY --from=grass /usr/local/grass* /usr/local/grass/
RUN pip install --upgrade pip six grass-session --ignore-installed six
RUN ln -s /usr/local/grass `grass --config path`
RUN grass --tmp-location EPSG:4326 --exec g.version -rge && \
    pdal --version && \
    python --version

# Install GRASS GIS addon d.rast.multi (needed for STRDS render endpoint)
RUN grass --tmp-location EPSG:4326 --exec g.extension -s \
    extension=d.rast.multi url=https://github.com/mundialis/d_rast_multi


FROM build-base as build

COPY . /src/actinia_core
WORKDIR /src/actinia_core
RUN pip install build && python -m build --outdir /build .
RUN if [[ -f /build/UNKNOWN* ]];then echo "ERROR - Check actinia-core build";exit 1;fi


FROM requirements as actinia

# actinia-core and requirements installation
WORKDIR /build
COPY --from=build /build/*.whl /build/
RUN pip install /build/*

# Copy actinia config file and start script
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

VOLUME /grassdb
WORKDIR /src/actinia_core

ENTRYPOINT ["/bin/sh"]
CMD ["/src/start.sh"]

EXPOSE 8088
