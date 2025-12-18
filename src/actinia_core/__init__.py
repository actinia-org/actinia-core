# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2023 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

import importlib.metadata

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = importlib.metadata.version(dist_name)
except Exception:
    __version__ = "unknown"
