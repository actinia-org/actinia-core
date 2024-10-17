# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2021 Sören Gebbert and mundialis GmbH & Co. KG
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
Utils file with common util functions
"""

import os
from actinia_core.core.common.process_object import Process
from actinia_core.core.common.exceptions import SecurityError
from actinia_core.core.common.config import global_config

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2021, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def ensure_valid_path(path_parts, intent="r"):
    """
    The function returns a joined and normalized path or raises an error if
    it is not as expected for the passed intent.

    Args:
        - path_parts (list of strings): The parts of the path in a list
        - intent (string): for what you want the path to be ensured, can
            be "r" (read), "w" (write) or "rw" (read and write). Default
            is to check for read access.

    Returns:
        path: joined normalized path

    Raise:
        - raises a TypeError if the intent is not 'r', 'w' or 'rw'
        - raises a SecurityError if the path is not valid for the given intent
    """
    allowed_intents = ["r", "w", "rw"]
    if intent not in allowed_intents:
        raise TypeError(
            f"Intent '{intent}' not allowed, allowed are 'r', 'w' and 'rw'"
        )

    path = os.path.normpath(os.path.join(*path_parts))
    error_message = f"Path '{path}' with intent '{intent}' is insecure."

    if not path.startswith(path_parts[0]):
        raise SecurityError(f"{error_message} Too deep path traversal?")
    if intent == "r" and not path_is_in_allowed_read_paths(path):
        raise SecurityError(error_message)
    if intent == "w" and not path_is_in_allowed_write_paths(path):
        raise SecurityError(error_message)
    if intent == "rw" and not path_is_in_allowed_read_and_write_paths(path):
        raise SecurityError(error_message)

    return path


def path_is_in_allowed_read_and_write_paths(path):
    """Checks whether the passed path is a valid read and write path, uses the
    global_config variables `GRASS_USER_DATABASE` and `GRASS_RESOURCE_DIR`
    for the check.

    Args:
        path (string): a normalized path

    Returns:
        (bool) Whether the passed path is a valid write path
    """
    read_allowed = path_is_in_allowed_read_paths(path)
    both_allowed = read_allowed and path_is_in_allowed_write_paths(path)
    return both_allowed


def path_is_in_allowed_read_paths(path):
    """Checks whether the passed path is a valid read path, uses the
    global_config variables `GRASS_USER_DATABASE`, `GRASS_DATABASE` and
    `GRASS_RESOURCE_DIR` for the check.

    Args:
        path (string): a normalized path

    Returns:
        (bool) Whether the passed path is a valid write path
    """
    allowed_read_starts = [
        global_config.GRASS_USER_DATABASE,
        global_config.GRASS_DATABASE,
        global_config.GRASS_RESOURCE_DIR,
    ]
    return any(path.startswith(allowed) for allowed in allowed_read_starts)


def path_is_in_allowed_write_paths(path):
    """Checks whether the passed path is a valid write path, uses the
    global_config variables `GRASS_USER_DATABASE` and `GRASS_RESOURCE_DIR` for
    the check.

    Args:
        path (string): a normalized path

    Returns:
        (bool) Whether the passed path is a valid write path
    """
    allowed_write_starts = [
        global_config.GRASS_USER_DATABASE,
        global_config.GRASS_RESOURCE_DIR,
    ]
    return any(path.startswith(allowed) for allowed in allowed_write_starts)


def get_wget_process(source, url):
    """The function returns a wget Process for the given source and url

    Args:
        source (str): The source file name where to download the data
        url (str): The url which should be downloaded

    Returns:
        p (Process): process for wget
    """

    wget = "/usr/bin/wget"
    wget_params = list()
    wget_params.append("-t5")
    wget_params.append("-c")
    wget_params.append("-q")
    wget_params.append("-O")
    wget_params.append("%s" % source)
    wget_params.append(url)

    p = Process(
        exec_type="exec",
        executable=wget,
        executable_params=wget_params,
        id=f"importer_wget_{os.path.basename(source)}",
        skip_permission_check=True,
    )
    return p


def get_mv_process(source, dest):
    """The function returns a move Process for the given source and dest

    Args:
        source (str): The source file name
        dest (str): The destination file name

    Returns:
        p (Process): process for mv
    """

    copy = "/bin/mv"
    copy_params = list()
    copy_params.append(source)
    copy_params.append(dest)

    p = Process(
        exec_type="exec",
        executable=copy,
        executable_params=copy_params,
        id=f"importer_mv_{os.path.basename(source)}",
        skip_permission_check=True,
    )
    return p


def allowed_file(filename, allowed_extensions):
    """The function checks if the file has an allowed extension.

    Args:
        filename (str): The file name
        allowed_extensions (list): The list of allowed extensions

    Returns:
        (bool): Returns True, if file extension is allowed
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed_extensions
    )
