#!flask/bin/python
# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2018 Soeren Gebbert and mundialis GmbH & Co. KG
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#######

"""
Dummy server to response HTTP code 200 to a POST call from an actinia webhook
"""
import argparse
from pprint import pprint
from flask import Flask, make_response, jsonify, request, json

from actinia_core.core.logging_interface import log

__license__ = "GPLv3"
__author__ = "Soeren Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"


flask_app = Flask(__name__)


@flask_app.route("/webhook/finished", methods=["GET", "POST"])
def finished():
    if request.get_json():
        pprint(json.loads(request.get_json()))
    return make_response(jsonify("OK"), 200)


@flask_app.route("/webhook/update", methods=["GET", "POST"])
def update():
    if request.get_json():
        pprint(json.loads(request.get_json()))
    return make_response(jsonify("OK"), 200)


def shutdown_server():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()


@flask_app.route("/shutdown", methods=["GET"])
def shutdown():
    shutdown_server()
    return make_response(jsonify("Server shutting down..."), 200)


def main():

    parser = argparse.ArgumentParser(
        description="Start a REST webhook server that exposes a GET/POST "
        "endpoint which returns HTTP code 200 if called. The endpoints are: "
        " - /webhook/finished for finished callbacks "
        " - /webhook/update for status update callbacks"
    )

    if parser.prog == "webhook_server":
        log.warning(
            'The call "webhook_server" is deprecated and will be '
            'removed soon. Use "webhook-server" instead!'
        )

    parser.add_argument(
        "--host",
        type=str,
        required=False,
        default="0.0.0.0",
        help="The IP address that should be used for the webhook server",
    )

    parser.add_argument(
        "--port",
        type=int,
        required=False,
        default=5005,
        help="The port that should be used for the webhook server",
    )

    args = parser.parse_args()

    flask_app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
