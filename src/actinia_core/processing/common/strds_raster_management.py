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
STRDS raster map layer management

TODO: Integrate into the ephemeral process chain approach
"""

from actinia_core.processing.common.utils import try_import

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis"


PersistentRasterSTRDSLister = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".strds_raster_management"
    ),
    "PersistentRasterSTRDSLister",
)

PersistentRasterSTRDSRegisterer = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".strds_raster_management"
    ),
    "PersistentRasterSTRDSRegisterer",
)

PersistentRasterSTRDSUnregisterer = try_import(
    (
        "actinia_core.processing.actinia_processing.persistent"
        + ".strds_raster_management"
    ),
    "PersistentRasterSTRDSUnregisterer",
)


def list_raster_strds(*args):
    processing = PersistentRasterSTRDSLister(*args)
    processing.run()


def register_raster(*args):
    processing = PersistentRasterSTRDSRegisterer(*args)
    processing.run()


def unregister_raster(*args):
    processing = PersistentRasterSTRDSUnregisterer(*args)
    processing.run()
