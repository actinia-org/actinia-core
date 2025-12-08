#!flask/bin/python
# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2023 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Dummy server to response HTTP code 200 to a POST call from an actinia webhook
"""
import argparse
import psutil
from flask import Flask, make_response, jsonify, request, json
from multiprocessing import Process
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from pprint import pprint

__license__ = "GPL-3.0-or-later"
__author__ = "Soeren Gebbert, Anika Weinmann, Carmen Tawalika"
__copyright__ = "Copyright 2016-2023, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"


flask_app = Flask(__name__)


@flask_app.route("/webhook/finished", methods=["GET", "POST"])
def finished():
    port = request.server[1]
    try:
        pprint(json.loads(request.get_json()))
    except BadRequest:
        pass
    except UnsupportedMediaType:
        pass
    except TypeError:
        pass
    sp = Process(target=shutdown_server, args=(port,))
    sp.start()
    return make_response(jsonify("Server shutting down..."), 200)


@flask_app.route("/webhook/update", methods=["GET", "POST"])
def update():
    try:
        pprint(json.loads(request.get_json()))
    except BadRequest:
        pass
    except UnsupportedMediaType:
        pass
    except TypeError:
        pass
    return make_response(jsonify("OK"), 200)


def shutdown_server(port):
    for proc in psutil.process_iter():
        try:
            if (
                proc.name() == "webhook-server-"
                and proc.as_dict()["connections"]
                and proc.as_dict()["connections"][0].laddr.port == port
            ):
                proc.kill()
        except KeyError:
            if (
                proc.name() == "webhook-server-"
                and proc.as_dict()["net_connections"]
                and proc.as_dict()["net_connections"][0].laddr.port == port
            ):
                proc.kill()


@flask_app.route("/shutdown", methods=["GET"])
def shutdown():
    port = request.server[1]
    sp = Process(target=shutdown_server, args=(port,))
    sp.start()
    return make_response(jsonify("Server shutting down..."), 200)


def main():
    parser = argparse.ArgumentParser(
        description="Start a webhook server that exposes GET/POST endpoints "
        "which returns HTTP code 200 if called. The endpoints are: "
        " - /webhook/finished for finished callbacks "
        " - /webhook/update for status update callbacks"
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
