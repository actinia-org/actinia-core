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
Resource storage management

TODO: Tests required
"""

from actinia_processing_lib.utils import try_import

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2022, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


ResourceStorageSize = try_import(
    (
        "actinia_core.processing.actinia_processing.ephemeral"
        + ".resource_storage_management"
    ),
    "ResourceStorageSize",
)

ResourceStorageDelete = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".resource_storage_management"
    ),
    "ResourceStorageDelete",
)


def start_resource_storage_size(*args):
    processing = ResourceStorageSize(*args)
    processing.run()


def start_resource_storage_remove(*args):
    processing = ResourceStorageDelete(*args)
    processing.run()
