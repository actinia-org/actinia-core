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
Resource storage management

TODO: Tests required
"""

from actinia_core.processing.common.utils import try_import

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis"


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
