Installation
============

Installation with docker
------------------------

Requirements: docker and docker-compose

To build and deploy actinia, run

```
git clone https://github.com/mundialis/actinia-core.git
cd actinia-core
docker-compose -f docker/docker-compose.yml up
```
Now you have a running actinia instance locally! Check with
```
curl http://127.0.0.1:8088/api/v3/version
```

* For how to add data to this setup, how to run actinia locally with most recent GRASS GIS or how to fix common startup errors, see more details in [docker README](https://github.com/actinia-org/actinia-core/blob/main/docker/README.md).



Local installation
------------------

A local installation requires a full GRASS GIS installation. Make sure
all requirements are fulfilled to compile GRASS GIS from the git
repository.

These installation instructions are based on a Ubuntu Linux system (other
operating systems and distributions are fine, too).


First install PROJ and GRASS GIS by downloading the latest packages
and GRASS GIS git version and compile it.

1.  Install the latest projection library

```bash
sudo apt-get update
sudo apt-get install proj-bin proj-data
```


2.  Set Python 3 environment

Note that this step changes `python` to point to `python3`, system-wide:

```bash
# recommended to give Python3 precedence over Python2 (which is end-of-life since 2019)
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 1
```


3.  Compile and install GRASS GIS and additional modules:

```bash
# or some other location of your choice, /tmp will not keep data between reboots
cd /tmp

# fetch weekly generated latest snapshot of GRASS GIS stable
wget https://grass.osgeo.org/grass80/source/snapshot/grass-8.0.git_src_snapshot_latest.tar.gz
tar xzvf grass-8.0.git_src_snapshot_latest.tar.gz
mv grass-8.0.git_src_snapshot_????_??_?? grass
rm -f grass-8.0.git_src_snapshot_latest.tar.gz

cd grass

# production related compilation flags (no debugging enabled)
export CFLAGS="-O2 -std=gnu99 -fexceptions -fstack-protector -m64"
export CXXFLAGS="-O2"
export LDFLAGS="-Wl,--no-undefined -Wl,-z,now"

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
cd actinia_core
pip install -r requirements.txt
python setup.py install
```


6.  Actinia API must be installed and run within a (virtual) Python3 environment:

```bash
mkdir -p $HOME/actinia/workspace/tmp

cd /tmp

git clone https://github.com/mundialis/actinia-api.git actinia-api
cd actinia-api
python setup.py install
```


7.  Make sure that a redis service is running and create a user with
   actinia-user tool

```bash
cd /tmp

# install and start redis server
apt-get install -y redis
redis-server &

# Create the superuser
actinia-user create -u superadmin -w abcdefgh -r superadmin -g admin -c 100000000000 -n 1000 -t 6000

# Start the actinia service with
actinia-server --host 0.0.0.0 --port 5000
```


8.  Check the service with curl

```bash
ACTINIA_VERSION="v3"
export ACTINIA_URL="http://localhost:5000/api/${ACTINIA_VERSION}"
export AUTH='-u superadmin:abcdefgh'

curl ${AUTH} -X GET ${ACTINIA_URL}/locations
```

The `curl` command call should report back:

```bash
{"locations":["nc_spm_08","ECAD","latlong_wgs84"],"status":"success"}
```

Success and welcome to actinia!
