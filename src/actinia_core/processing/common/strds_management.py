# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2022 Sören Gebbert and mundialis GmbH & Co. KG
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
STRDS map layer management

TODO: Integrate into the ephemeral process chain approach
"""

from actinia_core.processing.common.utils import try_import

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


PersistentSTRDSLister = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".strds_management"
    ),
    "PersistentSTRDSLister",
)

PersistentSTRDSInfo = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".strds_management"
    ),
    "PersistentSTRDSInfo",
)

PersistentSTRDSDeleter = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".strds_management"
    ),
    "PersistentSTRDSDeleter",
)

PersistentSTRDSCreator = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".strds_management"
    ),
    "PersistentSTRDSCreator",
)


def list_raster_mapsets(*args):
    processing = PersistentSTRDSLister(*args)
    processing.run()


def strds_info(*args):
    processing = PersistentSTRDSInfo(*args)
    processing.run()


def strds_delete(*args):
    processing = PersistentSTRDSDeleter(*args)
    processing.run()


def strds_create(*args):
    processing = PersistentSTRDSCreator(*args)
    processing.run()
