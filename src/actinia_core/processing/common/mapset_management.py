# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2022 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Mapset management resources

* List all mapsets
* Create mapset, Delete mapset, Get info about a mapset
* Lock mapset, unlock mapset, get mapset lock status
"""

from actinia_processing_lib.utils import try_import

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2022, Sören Gebbert & mundialis GmbH & Co. KG"
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
