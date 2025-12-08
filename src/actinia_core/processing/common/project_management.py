# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2024 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Project management

TODO: Integrate into the ephemeral process chain approach
"""

from actinia_processing_lib.utils import try_import

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2016-2024, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


PersistentProjectCreator = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".project_management"
    ),
    "PersistentProjectCreator",
)

PersistentGetProjectionRegionInfo = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".mapset_management"
    ),
    "PersistentGetProjectionRegionInfo",
)


def create_project(*args):
    processing = PersistentProjectCreator(*args)
    processing.run()


def read_current_region(*args):
    processing = PersistentGetProjectionRegionInfo(*args)
    processing.run()
