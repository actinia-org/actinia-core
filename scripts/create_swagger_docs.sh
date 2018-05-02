#!/bin/bash

# First run the actinia server and wait it for running
make install
actinia_server &
sleep 3

# Then download the json file

wget http://localhost:5000/api/v0/swagger.json -O /tmp/actinia.json

# Then run spectacle to generate the HTML documentation

docker run -v /tmp:/tmp -t sourcey/spectacle spectacle /tmp/actinia.json -t /tmp

# Start firefox

firefox /tmp/index.html
