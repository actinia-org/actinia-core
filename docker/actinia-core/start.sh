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
export GISBASE="/usr/local/grass77/"
grass -text -e -c 'EPSG:25832' /actinia_core/grassdb/utm32n
grass -text -e -c 'EPSG:4326' /actinia_core/grassdb/latlong
export GISBASE=""

actinia-user create -u actinia-gdi -w actinia-gdi -r superadmin -g superadmin -c 100000000000 -n 1000 -t 31536000
actinia-user update -u actinia-gdi -w actinia-gdi
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start actinia-user: $status"
  exit $status
fi

gunicorn -b 0.0.0.0:8088 -w 1 actinia_core.main:flask_app
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start actinia_core/main.py: $status"
  exit $status
fi
