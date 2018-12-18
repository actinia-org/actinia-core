#/bin/bash

# This script contains commands that can be executed in a nc_spm_08 location
# to the the ace command and its features

# List all maps in the search path of the PERMANENT mapset of the current location in actinia server
./ace g.list rast
# The same as above with explicit location setting
./ace -o nc_spm_08 g.list rast
# List all mapsets of the current location
./ace -m
# List all mapsets of location nc_spm_08
./ace -o nc_spm_08 -m
# List all raster layers in PERMANENT mapset of location nc_spm_08
./ace -o nc_spm_08 -r PERMANENT
# List all vector layers in PERMANENT mapset of location nc_spm_08
./ace -o nc_spm_08 -v PERMANENT
# List all strds layers in PERMANENT mapset of location nc_spm_08
./ace -o nc_spm_08 -t PERMANENT

# Create some commands with import and export options
cat << EOF > /tmp/commands.sh
# Import the web resource and set the region to the imported map
g.region raster=elev+https://storage.googleapis.com/graas-geodata/elev_ned_30m.tif -ap
# Compute univariate statistics
r.univar map=elev
r.info elev
# Compute the slope of the imported map and mark it for export
r.slope.aspect elevation=elev slope=slope_elev+GTiff
r.info slope_elev
EOF

# Run the commands in an ephemeral location/mapset based on the current location
./ace -s /tmp/commands.sh

# Run the commands in an ephemeral location/mapset based in location nc_spm_08
./ace -o nc_spm_08 -s /tmp/commands.sh

#####################
# Persistent commands

# Create a new mapset in the persistent user database
./ace -o nc_spm_08 -c test_mapset
# Run the commands in the new persistent mapset
./ace -o nc_spm_08 -p test_mapset -s /tmp/commands.sh
# Show all raster maps in test_mapset
./ace -o nc_spm_08 -p test_mapset g.list type=raster mapset=test_mapset
# Show information about raster map elev and slope_elev
./ace -o nc_spm_08 -p test_mapset r.info elev@test_mapset
./ace -o nc_spm_08 -p test_mapset r.info slope_elev@test_mapset
# Show all raster maps in test_mapset
./ace -o nc_spm_08 -r test_mapset
# Delete the test_mapset
./ace -o nc_spm_08 -d test_mapset
