#!/bin/bash

# TODO: read paths from config
mkdir -p /actinia_core/grassdb
mkdir -p /actinia_core/userdata
mkdir -p /actinia_core/workspace/temp_db
mkdir -p /actinia_core/workspace/tmp
mkdir -p /actinia_core/resources

# copy pgpass from mounted (!) file
cp /mnt/pgpass/.pgpass $HOME/.pgpass
chmod 0600 $HOME/.pgpass

# copy db.login file from mounted (!) file
cp /mnt/pgpass/.grass7 $HOME/.grass7/dblogin
chmod 0600 $HOME/.grass7/dblogin

# copy db.login file to actinia-core tmp location
mkdir -p /tmp/:/root/.grass7
cp /root/.grass7/dblogin /tmp/:/root/.grass7/

# Create default location in mounted (!) directory
[ ! -d "/actinia_core/grassdb/utm32n" ] && grass -text -e -c 'EPSG:25832' /actinia_core/grassdb/utm32n
[ ! -d "/actinia_core/grassdb/latlong_wgs84" ] && grass -text -e -c 'EPSG:4326' /actinia_core/grassdb/latlong_wgs84
# TODO: use this location for tests and integrate sample data, see README
# created here, because set in sample config as default location
[ ! -d "/actinia_core/grassdb/nc_spm_08" ] && grass -text -e -c 'EPSG:3358' /actinia_core/grassdb/nc_spm_08

actinia-user create -u actinia-gdi -w actinia-gdi -r superadmin -g superadmin -c 100000000000 -n 1000 -t 31536000
actinia-user update -u actinia-gdi -w actinia-gdi
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start actinia-user: $status"
  exit $status
fi

# optimized gunicorn settings (http://docs.gunicorn.org/en/stable/design.html) # run only 1 worker for debugging reasons. This is overwritten for production
# deployment.
gunicorn -b 0.0.0.0:8088 -w 8 --access-logfile=- -k gthread actinia_core.main:flask_app
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start actinia_core/main.py: $status"
  exit $status
fi
