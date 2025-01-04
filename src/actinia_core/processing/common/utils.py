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
Utils for processing
"""

import importlib
from actinia_core.core.common.config import global_config

__license__ = "GPLv3"
__author__ = "Carmen Tawalika"
__copyright__ = (
    "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def try_import(actinia_module, actinia_class):
    """Tries to import module, if module not found, throw exception
    if local queue is used.
    This is used to import processing classes. When job receiver
    cannot import it and redis queue is used, this is not a problem.
    When job receiver cannot import it and local queue is used, processing
    wouldn't work and the exception is thrown.
    Job executor needs to have it installed either way.

    Args:
        actinia_module (string): processing module to use

    Raises:
        e: ImportError or subclass

    Returns:
        module: python module used for processing
    """
    try:
        imported_module = importlib.import_module(actinia_module, package=None)
        imported_class = getattr(imported_module, actinia_class)
        return imported_class
    except ImportError as e:
        # ModuleNotFoundError is a subclass and caught here as well.
        if global_config.QUEUE_TYPE == "local":
            e.msg += (
                " - No actinia_processing found but required "
                + "for local queue!"
            )
            raise e
