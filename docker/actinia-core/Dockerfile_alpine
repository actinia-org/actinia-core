FROM mundialis/grass-py3-pdal:stable-alpine as grass
FROM mundialis/esa-snap:latest as snap
FROM alpine:edge as preparation

LABEL authors="Carmen Tawalika,Anika Bettge,Markus Neteler,Sören Gebbert"
LABEL maintainer="tawalika@mundialis.de,bettge@mundialis.de,neteler@mundialis.de,soerengebbert@gmail.com"

ENV LC_ALL "en_US.UTF-8"
ENV GDAL_CACHEMAX=2000
ENV GRASS_COMPRESSOR=ZSTD
ENV GRASS_SKIP_MAPSET_OWNER_CHECK 1

USER root

RUN apk update && apk add gcc geos-dev git linux-headers musl-dev python3-dev
RUN pip3 install --upgrade pip pep517 wheel


FROM preparation as actinia_core_build
COPY . /src/actinia_core
WORKDIR /src/actinia_core
RUN git checkout .
COPY requirements-alpine.txt /src/requirements-alpine.txt
RUN python3 setup.py sdist bdist_wheel -d /build && \
    pip3 wheel -r requirements-alpine.txt -w /build
# RUN python3 -m pep517.build --out-dir /build . && \


FROM preparation

ENV BUILD_PACKAGES="\
    # jpeg-dev \
    # libc-dev \
    # sqlite-dev \
    # zlib-dev \
    "

ENV ALPINE_TESTING_PACKAGES="\
    pdal \
    "

# BLOCK 0 (above in build image)
ENV ACTINIA_CORE_BUILD_PACKAGES="\
    gcc \
    geos-dev \
    git \
    linux-headers \
    musl-dev \
    python3-dev \
    "

# BLOCK 1
ENV SNAPPY_RUNTIME_PACKAGES="\
    python3 \
    openjdk8 \
    "

# BLOCK 2
ENV GRASS_RUNTIME_PACKAGES="\
    gdal-dev \
    proj-dev \
    python3 \
    zstd-libs \
    "

# BLOCK 3
ENV GRASS_ADDONS_SETUP_PACKAGES="\
    build-base \
    cairo \
    fftw-dev \
    gcc \
    geos-dev \
    git \
    make \
    postgresql-dev \
    py3-numpy-dev \
    subversion \
    "

# BLOCK 4
ENV ACTINIA_PLUGIN_INSTALL_PACKAGES="\
    curl \
    jq \
    python3-dev \
    "

# BLOCK 5
ENV ACTINIA_REQUIREMENTS_INSTALL_PACKAGES="\
    cython \
    py3-gdal \
    py3-scipy \
    "

# BLOCK 6
ENV RUNTIME_PACKAGES="\
    # gdal \
    # libmagic \
    # proj-datumgrid \
    proj-util \
    vim \
    # zstd \
    "

RUN echo "Install minimalistic dependencies and tools";\
    apk update; \
    apk add --no-cache \
      --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
      $ALPINE_TESTING_PACKAGES; \
    apk add --no-cache \
        $SNAPPY_RUNTIME_PACKAGES \
        $GRASS_RUNTIME_PACKAGES \
        $GRASS_ADDONS_SETUP_PACKAGES \
        $ACTINIA_PLUGIN_INSTALL_PACKAGES \
        $ACTINIA_REQUIREMENTS_INSTALL_PACKAGES \
        $RUNTIME_PACKAGES; \
    # apk add --no-cache --virtual .build-deps $BUILD_PACKAGES; \
    echo "Install step done"

# BLOCK 1 - ESA SNAP related setup
ENV LD_LIBRARY_PATH ".:$LD_LIBRARY_PATH"
COPY --from=snap /root/.snap /root/.snap
COPY --from=snap /usr/local/snap /usr/local/snap
RUN (cd /root/.snap/snap-python/snappy && python3 setup.py install)
RUN /usr/bin/python3 -c 'from snappy import ProductIO'

# BLOCK 2 - GRASS GIS related setup
COPY --from=grass /usr/local/bin/grass /usr/local/bin/grass
COPY --from=grass /usr/local/grass* /usr/local/grass
RUN pip3 install --upgrade pip six grass-session
RUN ln -s /usr/local/grass /usr/local/grass7
RUN ln -s /usr/local/grass `grass --config path`
RUN grass --tmp-location EPSG:4326 --exec g.version -rge && \
    pdal --version && \
    python3 --version

# BLOCK 3 - Install GRASS GIS addons
RUN git clone https://github.com/mundialis/openeo-addons.git /src/openeo-addons
COPY docker/actinia-core/grass_addons_list.csv /src/grass_addons_list.csv
RUN while IFS=, read -r ADDON SERVER; do unset URL; test -z $SERVER || URL="url=$SERVER"; grass --tmp-location EPSG:4326 --exec g.extension -s extension=$ADDON $URL;done < /src/grass_addons_list.csv
# broken:
# i.cutlines,
# r.learn.ml,
# v.strds.stats,
# t.rast.sample,https://github.com/mundialis/t.rast.sample

# BLOCK 4 - Get actinia-core plugins
WORKDIR /build
# Get statistics plugin
RUN curl https://api.github.com/repos/mundialis/actinia_statistic_plugin/releases/latest > resp.json && \
    name=`cat resp.json | jq '.assets[0].name' | tr -d '"'` && \
    cat resp.json | jq '.assets[0].browser_download_url' | xargs curl -L --output /build/$name && rm resp.json
# Get satellite plugin
RUN curl https://api.github.com/repos/mundialis/actinia_satellite_plugin/releases/latest > resp.json && \
    name=`cat resp.json | jq '.assets[0].name' | tr -d '"'` && \
    cat resp.json | jq '.assets[0].browser_download_url' | xargs curl -L --output /build/$name && rm resp.json
# Get actinia-gdi plugin
RUN curl https://api.github.com/repos/mmacata/actinia-gdi/releases/latest > resp.json && \
    name=`cat resp.json | jq '.assets[0].name' | tr -d '"'` && \
    cat resp.json | jq '.assets[0].browser_download_url' | xargs curl -L --output /build/$name && rm resp.json
# Install actinia-core plugins
COPY --from=actinia_core_build /build/*.whl /build/
RUN pip3 install /build/*

# BLOCK 6 - Install actinia_core requirements
# Duplicate as they are wheels in /build folder, but requirements are necessary.
COPY requirements-alpine.txt /src/requirements-alpine.txt
RUN pip3 install -r /src/requirements-alpine.txt

# Copy actinia config file and start scripts + set needed envs
COPY docker/actinia-core/actinia.cfg /etc/default/actinia
COPY docker/actinia-core/start.sh /src/start.sh
COPY docker/actinia-core/start-dev.sh /src/start-dev.sh
ENV ACTINIA_CUSTOM_TEST_CFG /etc/default/actinia
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

VOLUME /grassdb

ENTRYPOINT ["/bin/sh"]
CMD ["/src/start.sh"]

EXPOSE 8088
EXPOSE 9191
