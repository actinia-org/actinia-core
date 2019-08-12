Installation
============

A local installation requires a full GRASS GIS installation. Make sure all
requirements are fulfilled to compile GRASS GIS from the git repository.

First install Proj4 and GRASS GIS by downloading the latest git version and compile it.

1. Install the latest projection library.

    .. code-block:: bash

        cd /tmp

        wget http://download.osgeo.org/proj/proj-4.9.3.tar.gz

        tar xzvf proj-4.9.3.tar.gz

        cd proj-4.9.3/nad

        wget http://download.osgeo.org/proj/proj-datumgrid-1.8.zip

        unzip proj-datumgrid-1.8.zip

        cd ..

        ./configure
        make -j4
        sudo make install
    ..

2. Install GRASS GIS and additional modules:

    .. code-block:: bash

        cd /tmp

        wget https://grass.osgeo.org/grass78/source/snapshot/grass-7.8.git_src_snapshot_latest.tar.gz
        tar xzvf grass-7.8.git_src_snapshot_latest.tar.gz
        mv grass-7.8.git_src_snapshot_????_??_?? grass_master

        cd grass_master

        export INTEL="-std=gnu99 -fexceptions -fstack-protector -m64"
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


4. Actinia Core must be run within a virtual python3 environment:

    .. code-block:: bash

        mkdir -p $HOME/actinia/workspace/tmp

        cd /tmp

        git clone https://github.com/mundialis/actinia_core.git actinia_core
        virtualenv -p python3.5 actinia_venv
        source actinia_venv/bin/activate
        cd actinia_core
        pip install -r requirements.txt
        python setup.py install
        deactivate

    ..

5. GRASS GIS 7.8 requires a Python 3 environment for running, so we create one (not needed if only Python 3 is present on the machine).
   This environment must be specified in the actinia config file:

    .. code-block:: bash

        cd /tmp

        virtualenv -p python2.7 grass_venv
        source grass_venv/bin/activate
        cd actinia_core
        pip install -r requirements-grass-gis.txt

    ..

6. Make sure that a redis service is running and create a user with actinia-user tool


    .. code-block:: bash

        cd /tmp
        source actinia_venv/bin/activate

        # Create the superuser
        actinia-user create -u superadmin -w abcdefgh -r superadmin -g admin -c 100000000000 -n 1000 -t 6000

        # Start the actinia service with
        actinia_server --host 0.0.0.0 --port 5000

    ..

7. Check the service with curl

    .. code-block:: bash

        export PORT=5000
        export IP=http://localhost
        export AUTH='-u superadmin:abcdefgh'

        curl -u superadmin:abcdefgh -X GET http://localhost:5000/locations

    ..
