#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2024 Soeren Gebbert and mundialis GmbH & Co. KG
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
Purpose: Command line program to manage actinia user
         entries in the Redis database
"""

from actinia_core.core.common.config import Configuration
from actinia_core.core.common.user import ActiniaUser
from actinia_core.core.redis_user import redis_user_interface
import argparse
import pprint
import sys

__license__ = "GPLv3"
__author__ = "Soeren Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def verify_password(username_or_token, password):
    """Verify the user name and password.

    Instead of a user name an authentication token
    can be provided.

    Args:
        username_or_token (str): The username or an authentication token
        password (str): The optional user password, not required in case
        of token

    Returns:
        bool: True if authorized or False if not

    """
    # first try to authenticate by token
    user = ActiniaUser.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = ActiniaUser(user_id=username_or_token)
        if not user.exists() or not user.verify_password(password):
            return False
    return True


def set_user_credentials(user, args, method):
    """Set the user credentials

    Args:
        user (actinia.core.user.ActiniaUser()): The user object
        args: The command line arguments
        method (str): "create", "update", "update_add",
                      "update_rm", "update_rm_project"

    """

    if args.role:
        user.set_role(args.role)
    if args.cell_limit:
        user.set_cell_limit(args.cell_limit)
    if args.process_num_limit:
        user.set_process_num_limit(args.process_num_limit)
    if args.process_time_limit:
        user.set_process_time_limit(args.process_time_limit)
    if args.password:
        user.hash_password(args.password)

    if args.datasets:
        datasets = {}
        lm_list = args.datasets.split(",")

        for lm in lm_list:
            if "/" not in lm:
                sys.stderr.write("Wrong project mapset format for datasets\n")
                return

            if "/" in lm:
                project, mapset = lm.split("/")
            else:
                project = lm
                mapset = None

            if project not in datasets:
                datasets[project] = []

            datasets[project].append(mapset)

        if method == "update" or method == "create":
            user.set_accessible_datasets(datasets)
        if method == "update_add":
            for dataset in datasets:
                user.add_accessible_dataset(dataset, datasets[dataset])
        if method == "update_rm":
            for dataset in datasets:
                user.remove_mapsets_from_project(dataset, datasets[dataset])
        if method == "update_rm_project":
            for dataset in datasets:
                user.remove_project(dataset)

    if args.modules:
        modules = args.modules.split(",")
        if method == "update" or method == "create":
            user.set_accessible_modules(modules)
        if method == "update_add":
            user.add_accessible_modules(modules)
        if method == "update_rm":
            user.remove_accessible_modules(modules)


def main():
    """User management"""
    parser = argparse.ArgumentParser(
        description="Manage actinia users in the Redis database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "action",
        type=str,
        default="create",
        choices=[
            "create",
            "delete",
            "show",
            "list",
            "update",
            "update_add",
            "update_rm",
            "update_rm_project",
            "pwcheck",
        ],
        help="The action that should be performed:"
        " * create: Create a user"
        " * show:   Show the user credentials"
        " * list:   List all users"
        " * update: Update a user with the provided parameters"
        " * update_add: Update a user with the provided parameters"
        " and add datasets or/and modules"
        " * update_rm: Update a user with the provided parameters"
        " and remove mapsets or/and modules"
        " * update_rm_project: Update a user with the provided parameters"
        " and remove projects or/and modules"
        " * pwcheck: Check the password of the user",
    )
    parser.add_argument(
        "-s",
        "--server",
        type=str,
        required=False,
        help="The host name of the redis server,"
        " default is the value from the actinia config file",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        required=False,
        help="The port of the redis server,"
        " default is the value from the actinia config file",
    )
    parser.add_argument(
        "-a",
        "--redis_password",
        type=str,
        required=False,
        help="The password of the redis server,"
        " default is the value from the actinia config file or None",
    )
    parser.add_argument(
        "-u",
        "--user_id",
        type=str,
        required=False,
        help="The user name",
    )
    parser.add_argument(
        "-g",
        "--user_group",
        type=str,
        required=False,
        help="The name of the user group this user is associated with",
    )
    parser.add_argument(
        "-w",
        "--password",
        type=str,
        required=False,
        help="The password",
    )
    parser.add_argument(
        "-r",
        "--role",
        type=str,
        required=False,
        choices=["superadmin", "admin", "user", "guest"],
        help="The user role",
    )
    parser.add_argument(
        "-c",
        "--cell_limit",
        type=int,
        required=False,
        help="The maximum number of cells a user can process",
    )
    parser.add_argument(
        "-n",
        "--process_num_limit",
        type=int,
        required=False,
        help="The maximum number of processes the user can execute"
        " in a single process chain",
    )
    parser.add_argument(
        "-t",
        "--process_time_limit",
        type=int,
        required=False,
        help="The maximum number seconds a single process is allowed to run",
    )
    parser.add_argument(
        "-d",
        "--datasets",
        type=str,
        required=False,
        help="The datasets the user is allowed to access."
        " Format: project/mapset,project/mapset",
    )
    parser.add_argument(
        "-m",
        "--modules",
        type=str,
        required=False,
        help="A list of modules the user is allowed to access."
        " Format: module,module,module",
    )

    args = parser.parse_args()

    conf = Configuration()
    try:
        conf.read()
    except Exception:
        pass

    server = conf.REDIS_SERVER_URL
    port = conf.REDIS_SERVER_PORT
    if conf.REDIS_SERVER_PW:
        redis_password = conf.REDIS_SERVER_PW
    else:
        redis_password = None

    if args.server:
        server = args.server
    if args.port:
        port = args.port
    if args.redis_password:
        redis_password = args.redis_password
    redis_user_interface.connect(
        host=server,
        port=port,
        password=redis_password,
    )

    # CREATE ############################
    if args.action == "create":
        if args.user_id is None:
            sys.stderr.write("You need to provide a user id\n")
            return

        if args.user_group is None:
            sys.stderr.write("You need to provide a user group\n")
            return

        if args.password is None:
            sys.stderr.write("You need to provide a password\n")
            return

        if args.role is None:
            sys.stderr.write("You need to provide a user role\n")
            return

        user = ActiniaUser(user_id=args.user_id, user_group=args.user_group)

        if user.exists() == 1:
            sys.stderr.write(
                "Unable to create the user <%s> the user exists\n"
                % args.user_id
            )
            return

        # Set the credentials
        set_user_credentials(user, args, args.action)

        if user.commit() is True:
            sys.stderr.write(
                "Created user <%s> in group <%s>\n"
                % (args.user_id, args.user_group)
            )
            sys.stdout.write(str(user))
            return
        else:
            sys.stderr.write("Unable to create the user <%s>\n" % args.user_id)
            return
    # UPDATE ############################
    elif (
        args.action == "update"
        or args.action == "update_add"
        or args.action == "update_rm"
        or args.action == "update_rm_project"
    ):
        if args.user_id is None:
            sys.stderr.write("You need to provide a user id\n")
            return

        user = ActiniaUser(user_id=args.user_id)

        if user.exists() == 0:
            sys.stderr.write(
                "Unable to update the user <%s> the user doesn't exist\n"
                % args.user_id
            )
            return

        user.read_from_db()

        # Set the credentials
        set_user_credentials(user, args, args.action)

        if user.update() is True:
            sys.stderr.write("Updated user <%s>\n" % args.user_id)
            sys.stdout.write(str(user))
            return
        else:
            sys.stderr.write("Unable to update the user <%s>\n" % args.user_id)
            return

    # DELETE ############################
    elif args.action == "delete":
        user = ActiniaUser(args.user_id)

        if user.exists() == 1:
            if user.delete() is True:
                sys.stderr.write("User <%s> deleted\n" % args.user_id)
                return
            else:
                sys.stderr.write("Unable to delete user <%s>\n" % args.user_id)
                return
        else:
            sys.stderr.write("User <%s> does not exist\n" % args.user_id)

    # SHOW ##############################
    elif args.action == "show":
        user = ActiniaUser(args.user_id)

        if user.exists() == 1:
            sys.stdout.write(str(user))
        else:
            sys.stderr.write("User <%s> does not exist\n" % args.user_id)

    # LIST ##############################
    elif args.action == "list":
        user = ActiniaUser(args.user_id)
        pprint.pprint(user.list_all_users())

    # PWCHECK ###########################
    elif args.action == "pwcheck":
        if args.user_id is None:
            sys.stderr.write("You need to provide a user id\n")
            return

        if args.password is None:
            sys.stderr.write("You need to provide a password\n")
            return

        if verify_password(args.user_id, args.password) is False:
            sys.stderr.write("Wrong username or password\n")
        else:
            sys.stderr.write("Password and user name are correct\n")


if __name__ == "__main__":
    main()
