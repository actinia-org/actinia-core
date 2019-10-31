#!/bin/bash

# TODO: read paths from config
mkdir -p /actinia_core/grassdb
mkdir -p /actinia_core/userdata
mkdir -p /actinia_core/workspace/temp_db
mkdir -p /actinia_core/workspace/tmp
mkdir -p /actinia_core/resources

# Create default location in mounted (!) directory
grass -text -e -c 'EPSG:25832' /actinia_core/grassdb/utm32n
grass -text -e -c 'EPSG:4326' /actinia_core/grassdb/latlong_wgs84
# TODO: use this location for tests and integrate sample data, see README
# created here, because set in sample config as default location
grass -text -e -c 'EPSG:3358' /actinia_core/grassdb/nc_spm_08

# optimized gunicorn settings (http://docs.gunicorn.org/en/stable/design.html) # recommended num of workers is (2 x $num_cores) + 1, here minimum is assumed.
# If deployed with 8 replicas, each will run with 3 workers.
gunicorn -b 0.0.0.0:8088 -w 3 --access-logfile=- -k gthread actinia_core.main:flask_app
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start actinia_core/main.py: $status"
  exit $status
fi
