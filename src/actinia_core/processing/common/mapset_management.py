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
Mapset management resources

* List all mapsets
* Create mapset, Delete mapset, Get info about a mapset
* Lock mapset, unlock mapset, get mapset lock status
"""

from actinia_core.processing.common.utils import try_import

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


PersistentMapsetLister = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".mapset_management"
    ),
    "PersistentMapsetLister",
)

PersistentGetProjectionRegionInfo = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".mapset_management"
    ),
    "PersistentGetProjectionRegionInfo",
)

PersistentMapsetCreator = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".mapset_management"
    ),
    "PersistentMapsetCreator",
)

PersistentMapsetDeleter = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".mapset_management"
    ),
    "PersistentMapsetDeleter",
)

PersistentGetMapsetLock = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".mapset_management"
    ),
    "PersistentGetMapsetLock",
)

PersistentMapsetLocker = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".mapset_management"
    ),
    "PersistentMapsetLocker",
)

PersistentMapsetUnlocker = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".mapset_management"
    ),
    "PersistentMapsetUnlocker",
)


def list_raster_mapsets(*args):
    processing = PersistentMapsetLister(*args)
    processing.run()


def read_current_region(*args):
    processing = PersistentGetProjectionRegionInfo(*args)
    processing.run()


def create_mapset(*args):
    processing = PersistentMapsetCreator(*args)
    processing.run()


def delete_mapset(*args):
    processing = PersistentMapsetDeleter(*args)
    processing.run()


def get_mapset_lock(*args):
    processing = PersistentGetMapsetLock(*args)
    processing.run()


def lock_mapset(*args):
    processing = PersistentMapsetLocker(*args)
    processing.run()


def unlock_mapset(*args):
    processing = PersistentMapsetUnlocker(*args)
    processing.run()
