FROM mundialis/grass-py3-pdal

LABEL authors="Carmen Tawalika,Anika Bettge,Markus Neteler,Sören Gebbert"
LABEL maintainer="tawalika@mundialis.de,bettge@mundialis.de,neteler@mundialis.de,soerengebbert@gmail.com"

ARG SOURCE_GIT_URL=https://github.com
ARG SOURCE_GIT_REMOTE=mundialis
ARG SOURCE_GIT_REPO=actinia_core
# can be "tags" (for tag) or "heads" (for) branch
ARG SOURCE_GIT_TYPE=heads
# can be a tag name or branch name
ARG SOURCE_GIT_REF=master

ENV GDAL_CACHEMAX=2000
ENV GRASS_COMPRESSOR=ZSTD

USER root

# Install dependencies and tools
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends --no-install-suggests \
    # gnutls-bin \
    # libgnutls28-dev \
    # ruby \
    build-essential \
    bzip2 \
    curl \
    git \
    language-pack-en-base \
    libcurl4-gnutls-dev \
    libpython3-all-dev \
    moreutils \
    subversion \
    python3 \
    python3-dateutil \
    python3-dev \
    python3-magic \
    python3-pip \
    python3-ply \
    redis-server \
    redis-tools \
    unzip \
    vim \
    wget \
    zip \
    && apt-get autoremove -y \
    && apt-get clean -y

ENV LC_ALL "en_US.UTF-8"
ENV GRASS_SKIP_MAPSET_OWNER_CHECK 1

# Create the database directories
RUN mkdir -p /actinia_core/grassdb && \
    mkdir -p /actinia_core/resources && \
    mkdir -p /actinia_core/workspace/tmp && \
    mkdir -p /actinia_core/workspace/temp_db && \
    mkdir -p /actinia_core/workspace/actinia && \
    mkdir -p /actinia_core/workspace/download_cache && \
    mkdir -p /actinia_core/userdata

# Create generic GRASS GIS binary name regardless of version number
RUN ln -sf `find /usr/local/bin -name "grass??" | sort | tail -n 1` /usr/local/bin/grass
# Create a generic link to GRASS GIS libs (simplifies actinia configuration)
RUN ln -s `grass --config path` /usr/local/grass7
RUN grass --config svn_revision build

# Install actinia-core plugins
RUN git config --global http.sslVerify false
RUN git clone https://github.com/mundialis/actinia_statistic_plugin.git /src/actinia_statistic_plugin
WORKDIR /src/actinia_statistic_plugin
RUN pip3 install -r requirements.txt && python3 setup.py install

# Install GRASS GIS addons
WORKDIR /src
# Install the d.rast.multi module to render several maps at once
RUN git clone https://huhabla@bitbucket.org/huhabla/d_rast_multi.git d.rast.multi
RUN grass --tmp-location EPSG:25832 --exec g.extension -s extension=d.rast.multi url=/src/d.rast.multi

# TODO: is there a better workaround to install addons?
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
RUN grass --tmp-location EPSG:4326 --exec g.extension -s extension=i.cutlines && \
    grass --tmp-location EPSG:25832 --exec g.extension -s extension=v.out.png && \
    grass --tmp-location -c EPSG:25832 --exec g.extension -s extension=v.centerpoint
RUN update-alternatives --remove python /usr/bin/python3

# Fixup python shebangs - TODO: will be resolved in future by grass-core
WORKDIR /root/.grass7/addons/scripts
RUN find -type f | xargs sed -zi 's,#!/usr/bin/env python\n,#!/usr/bin/env python3\n,'

# install SNAPPY
RUN apt-get install default-jdk maven -y
ENV JAVA_HOME "/usr/lib/jvm/java-11-openjdk-amd64"
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
COPY snap /src/snap
RUN sh /src/snap/install.sh
RUN update-alternatives --remove python /usr/bin/python3

# Install actinia-core
WORKDIR /src

ADD https://api.github.com/repos/$SOURCE_GIT_REMOTE/$SOURCE_GIT_REPO/git/refs/$SOURCE_GIT_TYPE/$SOURCE_GIT_REF version.json
RUN git clone -b ${SOURCE_GIT_REF} --single-branch ${SOURCE_GIT_URL}/${SOURCE_GIT_REMOTE}/${SOURCE_GIT_REPO}.git actinia_core

WORKDIR /src/actinia_core
RUN pip3 install -r requirements.txt && python3 setup.py install

# Reduce the image size
RUN apt-get autoremove -y
RUN apt-get clean -y

# Data directory
WORKDIR /grassdb
VOLUME /grassdb

# Copy actinia config file and start scripts
COPY actinia.cfg /etc/default/actinia
COPY start.sh /src/start.sh
COPY start-dev.sh /src/start-dev.sh

ENTRYPOINT ["/bin/bash"]
CMD ["/src/start.sh"]

ENV GISBASE ""

EXPOSE 8088
EXPOSE 9191
