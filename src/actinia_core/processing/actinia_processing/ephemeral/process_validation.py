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
Compute areal categorical statistics on a raster map layer based on an input
polygon.
"""

from actinia_processing_lib.ephemeral_processing import (
    EphemeralProcessing,
)

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2022, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class ProcessValidation(EphemeralProcessing):
    def __init__(self, *args):
        EphemeralProcessing.__init__(self, *args)

    def _execute(self):
        self._setup()

        process_chain = (
            self._create_temporary_grass_environment_and_process_list()
        )

        result = []
        for process in process_chain:
            result.append(str(process))

        self.finish_message = "Validation successful"

        self.module_results = result
