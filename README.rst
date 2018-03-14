============
Actinia Core
============

Actinia Core is an open source REST API for scalable, distributed, high performance
processing of geographical data that uses GRASS GIS for computational tasks.


Description
===========

Actinia Core is an open source REST API for scalable, distributed, high performance
processing of geographical data that uses GRASS GIS for computational tasks.

It provides a REST API to process satellite images, time series of satellite images,
arbitrary raster data with geographical relations and vector data.

Installation
============

A local installation requires a full GRASS GIS installation. Make sure all
requirements are fulfilled to compile GRASS GIS from the svn repository.

First install Proj4 and GRASS GIS by downloading the latest svn version and compile it.

1. Install the latest projection library.

    .. code-block:: bash

        cd /tmp

        wget http://download.osgeo.org/proj/proj-4.9.3.tar.gz

        tar xzvf proj-4.9.3.tar.gz

        cd proj-4.9.3/

        wget http://download.osgeo.org/proj/proj-datumgrid-1.6.zip

        unzip proj-datumgrid-1.6.zip

        ./configure
        make -j4
        sudo make install
    ..

2. Install GRASS GIS and additional modules:

    .. code-block:: bash

        cd /tmp

        wget https://grass.osgeo.org/grass75/source/snapshot/grass-7.5.svn_src_snapshot_2018_03_10.tar.gz
        tar xzvf grass-7.5.svn_src_snapshot_2018_03_10.tar.gz
        mv grass-7.5.svn_src_snapshot_2018_03_10 grass_trunk

        cd grass_trunk
        svn cleanup
        svn up

        export INTEL="-march=native -std=gnu99 -fexceptions -fstack-protector -m64"
        export MYCFLAGS="-Wall -ggdb -fno-fast-math -fno-common $INTEL $MYGCC"
        export MYLDFLAGS="-Wl,--no-undefined"
        export LD_LIBRARY_PATH="/usr/local/lib"
        export LDFLAGS="$MYLDFLAGS"
        export CFLAGS="$MYCFLAGS"
        export CXXFLAGS="$MYCXXFLAGS"

        ./configure \
          --with-cxx \
          --enable-largefile \
          --with-proj=/usr/local/lib \
          --with-proj-share=/usr/local/share/proj \
          --with-gdal \
          --with-python \
          --with-geos \
          --with-sqlite \
          --with-cairo --with-cairo-ldflags=-lfontconfig \
          --with-fftw \
          --with-netcdf \
          --with-bzlib \
          --with-zstd \
          --without-postgres \
          --without-freetype \
          --without-openmp \
          --without-opengl \
          --without-nls \
          --without-mysql \
          --without-odbc \
          --without-openmp \
          --without-ffmpeg \
          --prefix=/usr/local

        make -j16
        sudo make install

        cd temporal
        git clone https://bitbucket.org/huhabla/temporal-raster-sampling.git t.rast.sample
        cd t.rast.sample
        make
        sudo make install
        cd ..

        git clone https://github.com/huhabla/t_rast_aggr_func.git t.rast.aggr_func
        cd t.rast.aggr_func
        make
        sudo make install

        cd ../../display/
        git clone https://bitbucket.org/huhabla/d_rast_multi.git d.rast.multi
        cd d.rast.multi
        make
        sudo make install

    ..

3. Download the test locations and place them into a specific directory that will
   be used by actinia as persistent database:

    .. code-block:: bash

        mkdir -p $HOME/actinia/grassdb
        cd $HOME/actinia/grassdb
        wget https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_grass7.tar.gz
        tar xzvf nc_spm_08_grass7.tar.gz
        rm -f nc_spm_08_grass7.tar.gz
        mv nc_spm_08_grass7 nc_spm_08

        wget https://storage.googleapis.com/datentransfer/ECAD.tar.gz
        tar xzvf ECAD.tar.gz
        rm -f ECAD.tar.gz

        wget https://storage.googleapis.com/datentransfer/LL.tar.gz
        tar xzvf LL.tar.gz
        rm -f LL.tar.gz
    ..


4. Actinia Core will run within a virtual python3 environment.

    .. code-block:: bash
        mkdir -p $HOME/actinia/workspace/tmp

        git clone https://github.com/mundialis/actinia_core.git actinia_core
        virtualenv -p python3.5 actinia_venv
        source actinia_venv/bin/activate
        cd actinia_core
        pip install -r requirements.txt
        python setup.py install
    ..
