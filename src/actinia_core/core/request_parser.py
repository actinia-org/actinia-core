# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2018 Sören Gebbert and mundialis GmbH & Co. KG
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
Request parser
"""

from flask_restful import reqparse

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


# Create a temporal module where, order, column parser
where_parser = reqparse.RequestParser()
where_parser.add_argument(
    "where", type=str, location="args", help="A SQL where option"
)
where_parser.add_argument(
    "order", type=str, location="args", help="The order of the listing"
)
where_parser.add_argument(
    "columns", type=str, location="args", help="The columns to be listed"
)


def extract_where_parameters(args):
    """Parse the request parameters for modules that have where, order and
    column options from parsed arguments that were created with the
    where_parser.

    Args:
        args (dict): The argument dictionary with where option

    Returns:
         list:
         A list of where and/or t_where parameter
    """
    options = []
    if "where" in args and args["where"] is not None:
        options.append("where=%s" % args["where"])
    if "order" in args and args["order"] is not None:
        options.append("order=%s" % args["order"])
    if "columns" in args and args["columns"] is not None:
        options.append("columns=%s" % args["columns"])

    return options


# Create a g.list/g.remove pattern parser
glist_parser = reqparse.RequestParser()
glist_parser.add_argument(
    "pattern",
    type=str,
    help="A pattern string must be provided",
    location="args",
)


def extract_glist_parameters(args):
    """Parse the request parameters for g.list/g.remove from parsed arguments
    that were created with the glist_parser.

    Args:
        args (dict): The argument dictionary with g.list/g.remove pattern
                     option

    Returns:
         list:
         A dict of g.list parameter
    """
    options = {}

    if "pattern" in args and args["pattern"] is not None:
        options["pattern"] = args["pattern"]

    return options


# Create a grass EPSG code parser
start_script_parser = reqparse.RequestParser()
start_script_parser.add_argument(
    "epsg",
    required=True,
    location="args",
    type=int,
    help="A EPSG code as integer must be provided",
)


def extract_start_script_parameters(args):
    """Parse the request parameters for the GRASS start script from parsed
    arguments that were created with the start_script_parser.

    Args:
        args (dict): The argument dictionary with grass start script options

    Returns:
         list:
         A list of grass start script parameters
    """
    options = []
    if "epsg" in args:
        options.append("-c")
        options.append("EPSG:%i" % args["epsg"])

    return options


# Create a t.create option parser
t_create_parser = reqparse.RequestParser()
t_create_parser.add_argument(
    "temporaltype",
    type=str,
    location="args",
    help="The temporal type of the space time dataset,"
    "options: absolute,relative, default: absolute",
)
t_create_parser.add_argument(
    "title",
    required=True,
    type=str,
    location="args",
    help="Title of the new space time raster dataset",
)
t_create_parser.add_argument(
    "description",
    required=True,
    type=str,
    location="args",
    help="Description of the new space time dataset",
)


def extract_t_create_parameters(args):
    """Parse the request parameters for t.create

    Args:
        args (dict): The argument dictionary with where option

    Returns:
         list:
         A list of t.create parameter
    """
    options = []
    if "temporaltype" in args and args["temporaltype"] is not None:
        options.append("temporaltype=%s" % args["temporaltype"])
    if "title" in args and args["title"] is not None:
        options.append("title=%s" % args["title"])
    if "description" in args and args["description"] is not None:
        options.append("description=%s" % args["description"])
    options.append("semantictype=mean")

    return options


# Create a t.register option parser
t_register_parser = reqparse.RequestParser()
t_register_parser.add_argument(
    "start",
    type=str,
    location="args",
    help="Valid start date and time of the first map. "
    'Format absolute time: "yyyy-mm-dd HH:MM:SS '
    '+HHMM", relative time is of type integer',
)
t_register_parser.add_argument(
    "end",
    type=str,
    location="args",
    help="Valid end date and time of all maps. "
    'Format absolute time: "yyyy-mm-dd HH:MM:SS0'
    ' +HHMM", relative time is of type integer',
)
t_register_parser.add_argument(
    "unit",
    type=str,
    location="args",
    help="Time stamp unit. Unit must be set in case of "
    "relative time stamps. options: "
    "years,months,days,hours,minutes,seconds",
)
t_register_parser.add_argument(
    "increment",
    type=str,
    location="args",
    help="Time increment, works only in conjunction with "
    "start option. Time increment between maps for "
    "valid time interval creation (format absolute: "
    "NNN seconds, minutes, hours, days, weeks, "
    "months, years; format relative is integer: 5)",
)


def extract_t_register_parameters(args):
    """Parse the request parameters for t.register

    Args:
        args (dict): The argument dictionary with where option

    Returns:
         list:
         A list of t.register parameter
    """
    options = []
    if "start" in args and args["start"] is not None:
        options.append("start=%s" % args["start"])
    if "end" in args and args["end"] is not None:
        options.append("end=%s" % args["end"])
    if "unit" in args and args["unit"] is not None:
        options.append("unit=%s" % args["unit"])
    if "increment" in args and args["increment"] is not None:
        options.append("increment=%s" % args["increment"])

    return options
