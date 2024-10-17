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
Raster layer resources
"""

from actinia_core.processing.common.utils import try_import

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Guido Riembauer, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


EphemeralRasterInfo = try_import(
    ("actinia_core.processing.actinia_processing.ephemeral" + ".raster_layer"),
    "EphemeralRasterInfo",
)

PersistentRasterDeleter = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".raster_layer"
    ),
    "PersistentRasterDeleter",
)

PersistentRasterCreator = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".raster_layer"
    ),
    "PersistentRasterCreator",
)


def start_info_job(*args):
    processing = EphemeralRasterInfo(*args)
    processing.run()


def start_delete_job(*args):
    processing = PersistentRasterDeleter(*args)
    processing.run()


def start_create_job(*args):
    processing = PersistentRasterCreator(*args)
    processing.run()
