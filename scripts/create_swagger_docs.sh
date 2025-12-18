#!/bin/bash
# only run this when actinia-core is already running

#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2018 Sören Gebbert and mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

mkdir -p build/stylesheets

echo "
#spectacle article h1.doc-title {
    color: #97BF0D;
}
#spectacle #sidebar {
    background-color: #97BF0D;
}
#spectacle #sidebar h5 {
    color: #000000;
}" \
> build/stylesheets/actinia.css

# download the json file locally
wget -O build/actinia.json "http://127.0.0.1:8088/api/v3/swagger.json"

# run spectacle to generate the api docs
docker run -v "$(pwd)"/build:/tmp -t sourcey/spectacle \
    spectacle /tmp/actinia.json -t /tmp

sed -i 's+<link rel="stylesheet" href="stylesheets/spectacle.min.css" />+<link rel="stylesheet" href="stylesheets/spectacle.min.css" />\n    <link rel="stylesheet" href="stylesheets/actinia.min.css" />+g' build/index.html

chromium-browser build/index.html &
