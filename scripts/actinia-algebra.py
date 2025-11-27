#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2019 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

import argparse
import requests
import simplejson
import time
import pprint
import copy
import uuid
from multiprocessing import Process, Queue

__author__ = "Soeren Gebbert"
__copyright__ = "Copyright 2016, Soeren Gebbert"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"


# spatio-temporal raster algebra threads
ST_ALGEBRA = {
    1: {
        "module": "t.rast.algebra",
        "inputs": {"expression": "", "basename": "test"},
        "flags": "ds",
        "overwrite": True,
        "verbose": False,
    }
}

# spatio-temporal raster algebra threads
R_MAPCALC = {
    "module": "r.mapcalc",
    "inputs": {"expression": ""},
    "overwrite": True,
    "verbose": False,
}

G_REGION = {
    "module": "g.region",
    "inputs": {"raster": ""},
    "flags": "p",
    "verbose": False,
}

# actinia-algebra.py -s http://104.199.28.149:80 latlong_wgs84 S2A_NDVI_1 "ndvi = (S2A_B08@S2A - S2A_B04@S2A)/(S2A_B08@S2A + S2A_B04@S2A)" ndvi -n 121  # noqa: E731

# Example with ECAD dataset
# actinia-algebra.py ECAD algebra_test 'A = temperature_mean_1950_2013_monthly_celsius@PERMANENT * 1' test precipitation_monthly_mm_0 -n 3  # noqa: E731


def main():

    parser = argparse.ArgumentParser(
        description="Run temporal algebra expression "
        "parallel on a actinia Service",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "project",
        type=str,
        help="The name of the project to be used for processing",
    )

    parser.add_argument(
        "mapset",
        type=str,
        help="The name of the mapset to be used for processing. "
        "The mapset will be created if it does not exist.",
    )

    parser.add_argument(
        "expression",
        type=str,
        help="The spatio-temporal raster algebra expression",
    )

    parser.add_argument(
        "basename",
        type=str,
        help="The base name of the new created raster "
        "layer that will be extended by a numerical prefix",
    )

    parser.add_argument(
        "-s",
        "--server",
        type=str,
        default="http://127.0.0.1:80",
        required=False,
        help="The hostname:port of the actinia server",
    )

    parser.add_argument(
        "-u",
        "--user_id",
        default="superadmin",
        type=str,
        required=False,
        help="The user name",
    )

    parser.add_argument(
        "-p",
        "--password",
        default="abcdefgh",
        type=str,
        required=False,
        help="The user password",
    )

    parser.add_argument(
        "-n",
        "--nodes",
        default=1,
        type=int,
        required=False,
        help="The number of nodes used to perform parallel processing",
    )

    parser.add_argument(
        "-w",
        "--rasterwindow",
        type=str,
        required=False,
        help="The name of a raster layer used for computational region "
        "settings",
    )

    parser.add_argument(
        "-r",
        "--res",
        type=float,
        required=False,
        help="The spatial resolution of the computational region, "
        "only used in conjunction with the rasterwindow option",
    )

    parser.add_argument(
        "-d",
        "--dryrun",
        default=False,
        type=bool,
        required=False,
        help="Set this flag True to enable the processing. Otherwise "
        "only a dry run is performed.",
    )

    args = parser.parse_args()
    auth = (args.user_id, args.password)

    if args.nodes > 96:
        raise Exception("Too many modes requests")

    # Store the generated mapsets
    mapset_list = []
    time_list = {}

    try:
        ################################################################
        # 1. Start the t.rast.algebra threads first
        q = Queue()

        start = time.time()

        pc = ST_ALGEBRA
        pc[1]["inputs"]["expression"] = "%s" % args.expression
        pc[1]["inputs"]["basename"] = "%s" % args.basename

        url = args.server + "/projects/" + args.project + "/processing_async"
        param = [url, auth, q, 1, pc]
        p = Process(target=start_async_processing, args=param)
        p.start()
        r = q.get()
        p.join()

        if hasattr(r, "status_code") is True and r.status_code != 200:
            raise Exception(
                "Unable to fetch the execution instructions."
                + " Error code: "
                + str(r.status_code)
                + " message: "
                + str(r.text)
            )
        elif hasattr(r, "status_code") is False:
            raise Exception(r)

        end = time.time()
        time_list["t.rast.algebra time in seconds"] = end - start

        data = simplejson.loads(r.text)
        if args.dryrun is True:
            pprint.pprint(data)
            return

        ################################################################
        # 2. Run r.mapcalc requests parallel in new mapsets
        start = time.time()

        # Evaluate the stdout to extract the Python dictionary
        stdout = data["process_log"][0]["stdout"]
        stdout = "{" + stdout.split("{", 1)[1]
        threads_list = eval(stdout)

        pprint.pprint(threads_list)

        # Prepare parallel processing
        mapcalc_list = []

        num_proceses = len(threads_list["processes"])

        if num_proceses == 0:
            print("Nothing to do")
            return

        # Adjust the number of nodes to use
        num_nodes = args.nodes
        if args.nodes > num_proceses:
            num_nodes = num_proceses

        num_threads_per_node = int(num_proceses / num_nodes)
        num_threads_mod = int(num_proceses % num_nodes)

        print(num_proceses, num_nodes, num_threads_per_node, num_threads_mod)

        count = 0
        for num in range(num_nodes):
            n = num_threads_per_node
            # Add the non distributed processes to the nodes
            # until they are empty
            if num_threads_mod > 0:
                n += 1
                num_threads_mod -= 1

            print("Serial r.mapcalc runs", n, "at node", num)
            count = mapcal_request(
                args,
                count,
                auth,
                threads_list,
                mapset_list,
                mapcalc_list,
                q,
                n,
            )
        # Wait for the results
        count = 0
        error_count = 0
        for p in mapcalc_list:
            r = q.get()
            p.join()
            if r.status_code != 200:
                print(
                    "Error code: "
                    + str(r.status_code)
                    + " message: "
                    + str(r.text)
                )
                error_count += 1
            count += 1

        if error_count > 0:
            raise Exception("Unable to compute distributed r.mapcalc jobs")

        end = time.time()

        time_list["r.mapcalc run time in seconds"] = end - start

        ################################################################
        # 3. Create new mapset
        start = time.time()

        url = (
            args.server
            + "/projects/"
            + args.project
            + "/mapsets/"
            + args.mapset
        )
        print("Create mapset", url)
        r = requests.post(url, auth=auth)
        if r.status_code != 200:
            print("Mapset already exists, will not be created")
            print(
                "Error code: "
                + str(r.status_code)
                + " message: "
                + str(r.text)
            )
        else:
            print(str(r.status_code) + " message: " + str(r.text))

        end = time.time()

        time_list["mapset creation in seconds"] = end - start

        ################################################################
        # 4. Merge source mapsets in target mapsets
        start = time.time()

        url = (
            args.server
            + "/projects/"
            + args.project
            + "/mapsets/"
            + args.mapset
            + "/merging_async"
        )
        print(
            "Merge mapsets %s into <%s> using URL %s"
            % (str(mapset_list), args.mapset, url)
        )
        param = [url, auth, q, count + 1, mapset_list]
        p = Process(target=start_async_processing, args=param)
        p.start()
        r = q.get()
        p.join()
        if r.status_code != 200:
            raise Exception(
                "Unable to merge mapsets  %s into <%s> using"
                % (str(mapset_list), args.mapset)
                + " Error code: "
                + str(r.status_code)
                + " message: "
                + str(r.text)
            )

        end = time.time()

        time_list["mapset mergin in seconds"] = end - start

        ################################################################
        # 5. Register the maps in a new space time dataset
        # TODO
        # Create the new strds
        start = time.time()

        url = (
            args.server
            + "/projects/"
            + args.project
            + "/mapsets/"
            + args.mapset
            + "/strds/"
            + threads_list["STDS"]["name"]
            + "?temporaltype=%s&title=title&description=description"
            % threads_list["STDS"]["temporal_type"]
        )
        r = requests.post(url, auth=auth)
        if r.status_code != 200:
            raise Exception(
                "Error code: "
                + str(r.status_code)
                + " message: "
                + str(r.text)
            )
        else:
            print("Message: " + str(r.text))

        url = (
            args.server
            + "/projects/"
            + args.project
            + "/mapsets/"
            + args.mapset
            + "/strds/"
            + threads_list["STDS"]["name"]
            + "/raster_layers"
        )
        r = requests.put(
            url, auth=auth, data=simplejson.dumps(threads_list["register"])
        )
        if r.status_code != 200:
            raise Exception(
                "Error code: "
                + str(r.status_code)
                + " message: "
                + str(r.text)
            )
        else:
            print("Message: " + str(r.text))
        # pprint.pprint(threads_list["register"])

        end = time.time()

        time_list["strds creation in seconds"] = end - start

        ################################################################
        # 6. List all maps from the STRDS
        start = time.time()

        url = (
            args.server
            + "/projects/"
            + args.project
            + "/mapsets/"
            + args.mapset
            + "/strds/"
            + threads_list["STDS"]["name"]
            + "/raster_layers"
        )
        r = requests.get(url, auth=auth)
        if r.status_code != 200:
            raise Exception(
                "Error code: "
                + str(r.status_code)
                + " message: "
                + str(r.text)
            )
        else:
            print("Message: " + str(r.text))

        data = simplejson.loads(r.text)
        pprint.pprint(data)

        end = time.time()

        time_list["strds raster listing in seconds"] = end - start

    except Exception as e:
        print(str(e))
        raise
    finally:
        ################################################################
        # 6. Remove the temporary mapsets
        start = time.time()

        if mapset_list:
            for mapset_name in mapset_list:
                print("Remove temporary mapset", mapset_name)
                url = (
                    args.server
                    + "/projects/"
                    + args.project
                    + "/mapsets/"
                    + mapset_name
                )
                r = requests.delete(url, auth=auth)
                if r.status_code != 200:
                    print(
                        "Error code: "
                        + str(r.status_code)
                        + " message: "
                        + str(r.text)
                    )
                else:
                    print("Message: " + str(r.text))

        end = time.time()

        time_list["temporary mapset deletion in seconds"] = end - start

        pprint.pprint(time_list)


def mapcal_request(
    args, count, auth, threads_list, mapset_list, mapcalc_list, q, n
):
    """Create the mapset calls and send the processing request

    Args:
        args (argparse.ArgumentParser): The command line arguments
        count (int): The r.mapcalc threads counter
        threads_list (list): The list of r.mapcalc processes
        mapset_list (list): The list of temporary mapsets
        mapcalc_list (list): The list that stores the spawned subprocesses
        q (multiprocessing.Queue): The queue that stores the responses
        n (int): The number of processes in a single request

    Returns: The updated counter

    """
    id_ = uuid.uuid4()
    id_ = str(id_).split("-")[0]

    mapset_name = args.mapset + "_%s" % id_
    mapset_list.append(mapset_name)

    url = (
        args.server
        + "/projects/"
        + args.project
        + "/mapsets/"
        + mapset_name
        + "/processing_async"
    )

    pchain = {}
    shift = 0

    # If the raster window is set, us it to set the region of the computation
    if args.rasterwindow:
        shift = 1
        region = copy.deepcopy(G_REGION)
        region["inputs"]["raster"] = args.rasterwindow
        if args.res:
            region["inputs"]["res"] = args.res
        pchain[0] = region

    for j in range(n):

        threads = threads_list["processes"][count]
        p = copy.deepcopy(R_MAPCALC)
        p["inputs"]["expression"] = threads["inputs"][0][1]
        # Use the union option to define the computational region, i
        # f the raster window is not set
        if not args.rasterwindow:
            p["inputs"]["region"] = "union"

        pchain[j + shift] = p

        count += 1

    pprint.pprint(url)
    pprint.pprint(pchain)

    param = [url, auth, q, 1, pchain]
    p = Process(target=start_async_processing, args=param)
    p.start()
    # Store the threads
    mapcalc_list.append(p)

    return count


def start_async_processing(url, auth, q, id, pc):
    """Start an asynchronous actinia threads and poll until its finished

    This function is the argument for multiprocessing.threads

    Args:
        url (str): URL to the asynchronous request
        auth (tuple): Username and password as tuple
        q (multiprocessing.Queue): The queue to store the processing time in
        id (int): The id of the request

    """

    start = time.time()

    # threads chain request
    try:
        r = requests.post(
            url,
            data=simplejson.dumps(pc),
            auth=auth,
            headers={"content-type": "application/json"},
        )
    except Exception as e:
        q.put(str(e))
        raise

    if r.status_code == 200:
        if not r.text:
            q.put(r)
            raise Exception("No JSON content in response")

        data = simplejson.loads(r.text)

        poll(data["urls"]["status"], auth, start, q, id)
    else:
        q.put(r)
        string = "Error for threads %i %i HTTP Status %s" % (
            id,
            r.status_code,
            r,
        )
        raise Exception(string)


def poll(url, auth, start, q, id):
    """Function to poll the status of the asynchronous request

    Args:
        url (str): The url to poll the status from
        auth (tuple): Username and password as tuple
        q (multiprocessing.Queue): The queue to store the processing time in
        id (int): The id of the request
        start (float): The start time

    """
    while True:
        r = requests.get(url, auth=auth)
        try:
            data = simplejson.loads(r.text)
            print(
                "### Thread",
                id,
                r.status_code,
                "HTTP Status",
                r,
                "\n",
                r.text,
                data["status"],
            )
            if (
                data["status"] == "finished"
                or data["status"] == "error"
                or data["status"] == "terminated"
            ):
                break
            time.sleep(1)
            end = time.time()
            print(
                "threads",
                id,
                r.status_code,
                "HTTP Status",
                data["status"],
                "Time needed:",
                "%.2f" % (end - start),
                "seconds",
            )
        except Exception as a:
            print(str(a))
            raise

    print(data["urls"]["status"])

    q.put(r)


if __name__ == "__main__":
    main()
