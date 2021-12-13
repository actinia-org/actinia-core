Installation
============

A local installation requires a full GRASS GIS installation. Make sure
all requirements are fulfilled to compile GRASS GIS from the git
repository.

These installation instructions a based on a Ubuntu Linux system (other
operating systems and distributions are fine, too).


First install PPROJ and GRASS GIS by downloading the latest packages
and GRASS GIS git version and compile it.

1.  Install the latest projection library

```bash
 sudo apt-get update
 sudo apt-get install proj-bin proj-data
```


2.  Set Python 3 environemtn

```bash
 # recommended to give Python3 precedence over Python2 (which is end-of-life since 2019)
 sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
```


3.  Compile and install GRASS GIS and additional modules:

```bash
 cd /tmp

 wget https://grass.osgeo.org/grass78/source/snapshot/grass-7.8.git_src_snapshot_latest.tar.gz
 tar xzvf grass-7.8.git_src_snapshot_latest.tar.gz
 mv grass-7.8.git_src_snapshot_????_??_?? grass78
 rm -f grass-7.8.git_src_snapshot_latest.tar.gz

 cd grass78

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
   --with-proj-share=/usr/share/proj \
   --with-gdal \
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
   --prefix=/usr/local

 make -j8
 sudo make install

 cd temporal/
 git clone https://github.com/mundialis/t.rast.sample
 cd t.rast.sample
 make
 cd ../..
 sudo make install

 # t.rast.udf
 # see https://github.com/mundialis/openeo-addons

 cd display/
 git clone https://github.com/mundialis/d_rast_multi d.rast.multi
 cd d.rast.multi
 make
 cd ../..
 sudo make install
```


4.  Download the test datasets ("locations") and place them into a
    specific directory that will be used by actinia as a persistent database:

```bash
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
 mv LL latlong_wgs84
```


5.  Actinia Core must be installed and run within a (virtual) Python3 environment:

```bash
 mkdir -p $HOME/actinia/workspace/tmp

 cd /tmp

 git clone https://github.com/mundialis/actinia_core.git actinia_core
 # virtualenv -p python3 actinia_venv
 # source actinia_venv/bin/activate
 cd actinia_core
 pip install -r requirements.txt
 python setup.py install
 # deactivate
```


6.  Actinia API must be installed and run within a (virtual) Python3 environment:

```bash
 mkdir -p $HOME/actinia/workspace/tmp

 cd /tmp

 git clone https://github.com/mundialis/actinia-api.git actinia-api
 # virtualenv -p python3 actinia_venv
 # source actinia_venv/bin/activate
 cd actinia-api
 python setup.py install
 # deactivate
```


7.  Make sure that a redis service is running and create a user with
    actinia-user tool

```bash
 cd /tmp

 # install and start redis server
 apt-get install -y redis
 redis-server &

 # source actinia_venv/bin/activate
 # Create the superuser
 actinia-user create -u superadmin -w abcdefgh -r superadmin -g admin -c 100000000000 -n 1000 -t 6000

 # Start the actinia service with
 actinia-server --host 0.0.0.0 --port 5000
```


8.  Check the service with curl

```bash
ACTINIA_VERSION="v2"
 export ACTINIA_URL="http://localhost:5000/api/${ACTINIA_VERSION}"
 export AUTH='-u superadmin:abcdefgh'

 curl ${AUTH} -X GET ${ACTINIA_URL}/locations
```

The `curl` command call should report back:

```bash
{"locations":["nc_spm_08","ECAD","latlong_wgs84"],"status":"success"}
```

Success!
