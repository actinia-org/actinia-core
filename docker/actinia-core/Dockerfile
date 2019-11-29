FROM mundialis/grass-py3-pdal:stable-ubuntu

# based on GRASS GIS releasebranch_7_8 (grass78)

LABEL authors="Carmen Tawalika,Anika Bettge,Markus Neteler,Sören Gebbert"
LABEL maintainer="tawalika@mundialis.de,bettge@mundialis.de,neteler@mundialis.de,soerengebbert@gmail.com"

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
    python3 \
    python3-dateutil \
    python3-dev \
    python3-magic \
    python3-pip \
    python3-ply \
    redis-server \
    redis-tools \
    subversion \
    unzip \
    vim \
    wget \
    zip \
    && apt-get autoremove -y \
    && apt-get clean -y

# wrongly linked against gdal 2.2.2; using pygdal 2.2.3.3 in requirements
#    python3-gdal \

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
# show installed version
RUN grass --tmp-location EPSG:4326 --exec g.version -rge

# Install GRASS GIS addons
WORKDIR /src
# Install the d.rast.multi module to render several maps at once
RUN git clone https://huhabla@bitbucket.org/huhabla/d_rast_multi.git d.rast.multi

COPY docker/actinia-core/grass_addons_list.csv /src/grass_addons_list.csv
RUN while IFS=, read -r ADDON SERVER; do unset URL; test -z $SERVER || URL="url=$SERVER"; grass --tmp-location EPSG:4326 --exec g.extension -s extension=$ADDON $URL;done < /src/grass_addons_list.csv

# install SNAPPY
# SNAP wants the current folder '.' included in LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH ".:$LD_LIBRARY_PATH"
RUN apt-get install default-jdk maven -y
ENV JAVA_HOME "/usr/lib/jvm/java-11-openjdk-amd64"
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
COPY docker/actinia-core/snap /src/snap
RUN bash /src/snap/install.sh
RUN update-alternatives --remove python /usr/bin/python3

# Install actinia-core
COPY . /src/actinia_core

# set link to match actinia default config (needed for tests)
RUN ln -s /actinia_core /root/actinia

WORKDIR /src/actinia_core
# necessary to be even with git for clean version
RUN git checkout .
# update build tools
RUN python3 -m pip install --user --upgrade setuptools wheel
# create build
RUN python3 setup.py sdist bdist_wheel

## install (Cython must be installed before requirements.txt)
#RUN pip3 install Cython cython-setuptools setuptools_cython
RUN pip3 install -r requirements.txt && python3 setup.py install
## TODO: fix tests
#\
#    && python3 setup.py test

# Install actinia-core plugins
RUN git config --global http.sslVerify false
RUN git clone https://github.com/mundialis/actinia_statistic_plugin.git /src/actinia_statistic_plugin
WORKDIR /src/actinia_statistic_plugin
RUN pip3 install -r requirements.txt && python3 setup.py install
## TODO: fix tests
#\
#    && python3 setup.py test

# Reduce the image size
RUN apt-get autoremove -y
RUN apt-get clean -y
RUN rm -rf /src/snap

# Data directory
WORKDIR /grassdb
VOLUME /grassdb

# Copy actinia config file and start scripts
COPY docker/actinia-core/actinia.cfg /etc/default/actinia
COPY docker/actinia-core/start.sh /src/start.sh
COPY docker/actinia-core/start-dev.sh /src/start-dev.sh

# Set actinia config file for testing
ENV ACTINIA_CUSTOM_TEST_CFG /etc/default/actinia

ENTRYPOINT ["/bin/bash"]
CMD ["/src/start.sh"]

ENV GISBASE ""

EXPOSE 8088
EXPOSE 9191
