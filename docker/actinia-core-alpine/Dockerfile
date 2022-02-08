FROM mundialis/grass-py3-pdal:releasebranch_8_0-alpine as grass
FROM mundialis/actinia-core:alpine-build-pkgs_v9 as build

LABEL authors="Carmen Tawalika,Anika Bettge,Markus Neteler,Sören Gebbert"
LABEL maintainer="tawalika@mundialis.de,bettge@mundialis.de,neteler@mundialis.de,soerengebbert@gmail.com"

COPY . /src/actinia_core

WORKDIR /src/actinia_core
# setuptools uses this command or similar to determine app version
# in CI environments it might not work as expected
# RUN git describe --dirty --tags --long --first-parent
RUN git checkout .
RUN python3 setup.py sdist bdist_wheel -d /build


FROM mundialis/actinia-core:alpine-runtime-pkgs_v7 as actinia_installation

ENV LC_ALL "en_US.UTF-8"
ENV GDAL_CACHEMAX=2000
ENV GRASS_COMPRESSOR=ZSTD
ENV GRASS_SKIP_MAPSET_OWNER_CHECK 1
ENV GISBASE ""
ENV ACTINIA_API_VERSION 3.0.1

USER root

# GRASS GIS SETUP
COPY --from=grass /usr/local/bin/grass /usr/local/bin/grass
COPY --from=grass /usr/local/grass* /usr/local/grass/
RUN pip3 install --upgrade pip six grass-session --ignore-installed six
RUN ln -s /usr/local/grass /usr/local/grass7
RUN ln -s /usr/local/grass `grass --config path`
RUN grass --tmp-location EPSG:4326 --exec g.version -rge && \
    pdal --version && \
    python3 --version

# GRASS GIS addons BUILD
COPY docker/grass_addons_list.csv /src/grass_addons_list.csv
RUN while IFS=, read -r ADDON SERVER; do unset URL; test -z $SERVER || URL="url=$SERVER"; grass --tmp-location EPSG:4326 --exec g.extension -s extension=$ADDON $URL;done < /src/grass_addons_list.csv

# actinia-core and actinia libs BUILD
WORKDIR /build
ARG WHEEL_NAME=actinia_api-${ACTINIA_API_VERSION}-py3-none-any.whl
RUN echo ${WHEEL_NAME}
RUN curl -L --output /build/${WHEEL_NAME} \
    https://github.com/mundialis/actinia-api/releases/download/${ACTINIA_API_VERSION}/${WHEEL_NAME}

# Install actinia-core and plugins
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
