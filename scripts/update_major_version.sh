#!/usr/bin/env bash

############################################################################
#
# MODULE:       update_major_version.sh
# AUTHOR(S):    Anika Weinmann
#
# PURPOSE:      This script updates the major actinia-core version in url
#
# COPYRIGHT:    (C) 2022 by mundialis GmbH & Co. KG
#
#               This program is free software under the GNU General Public
#               License (>=v3). Read the file COPYING that comes with GRASS
#               for details.
#
#############################################################################

# execution for example with.
#     bash update_major_version.sh v2 v3

OLD_VERSION=$1
NEW_VERSION=$2

# code
sed -i "s+API_VERSION = \"${OLD_VERSION}\"+API_VERSION = \"${NEW_VERSION}\"+g" ../src/actinia_core/core/common/app.py
sed -i "s+to '${OLD_VERSION}' in the URL.+to '${NEW_VERSION}' in the URL.+g" ../src/actinia_core/version.py
# shellcheck disable=SC2089
FUNC="\n\n@flask_app.route(\"/api/${OLD_VERSION}/<path:actinia_path>\")\n\
def hint_${OLD_VERSION}(actinia_path):\n\
\t\"\"\"Return a hint that this version is no longer installed. If an older\n\
\tversion is installed, this endpoint will be overwritten by a proxy.\n\n\
\tReturns: Response\n\n\t\"\"\"\n\
\turl = request.url_root.strip('/') + URL_PREFIX + '/' + actinia_path\n\
\n\treturn make_response(jsonify(LinkResponseModel(\n\
\t\t\tstatus=\"Not found\",\n\
\t\t\tmessage=(\"Are you looking for the current API version? \"\n\
\t\t\t\t\t \"Change '${OLD_VERSION}' to '${NEW_VERSION}' in the URL.\"),\n\
\t\t\tlinks=[url]), 404))"
# shellcheck disable=SC2090
echo -e ${FUNC} | sed "s+\t+    +g" >> ../src/actinia_core/version.py

# for vscode Debugging
sed -i "s+\"%s://localhost:%s/api/${OLD_VERSION}/version\"+\"%s://localhost:%s/api/${NEW_VERSION}/version\"+g" ../.vscode/launch.json

# docker
sed -i "s+/api/${OLD_VERSION}/+/api/${NEW_VERSION}/+g" ../docker/create-docs.sh
sed -i "s+/api/${OLD_VERSION}/+/api/${NEW_VERSION}/+g" ../docker/README.md

# docs
sed -i "s+ACTINIA_VERSION=\"${OLD_VERSION}\"+ACTINIA_VERSION=\"${NEW_VERSION}\"+g" ../docs/docs/installation.md
sed -i "s+api/${OLD_VERSION}/+api/${NEW_VERSION}/+g" ../docs/docs/tutorial_data_access.md
sed -i "s+/api/${OLD_VERSION}/+/api/${NEW_VERSION}/+g" ../docs/docs/tutorial_landsat_ndvi.md
sed -i "s+/api/${OLD_VERSION}/+/api/${NEW_VERSION}/+g" ../docs/docs/tutorial_process_chain.md
sed -i "s+/api/${OLD_VERSION}/+/api/${NEW_VERSION}/+g" ../docs/docs/tutorial_sentinel2_ndvi.md
sed -i "s+/api/${OLD_VERSION}/+/api/${NEW_VERSION}/+g" ../docs/docs/tutorial_strds_sampling.md

# README
sed -i "s+/api/${OLD_VERSION}/+/api/${NEW_VERSION}/+g" ../README.md

# scripts
sed -i "s+/api/${OLD_VERSION}+/api/${NEW_VERSION}+g" ../scripts/actinia-bench
sed -i "s+/api/${OLD_VERSION}/+/api/${NEW_VERSION}/+g" ../scripts/curl_commands.sh
sed -i "s+actinia_version=\"${OLD_VERSION}\"+actinia_version=\"${NEW_VERSION}\"+g" ../scripts/curl_commands.sh
sed -i "s+/api/${OLD_VERSION}/+/api/${NEW_VERSION}/+g" ../scripts/README.md

# logging README
sed -i "s+/api/${OLD_VERSION}+/api/${NEW_VERSION}+g" ../logging.md
