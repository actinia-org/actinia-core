# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# SPDX-FileCopyrightText: (c) 2016-2025 Sören Gebbert & mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#######

"""
Actinia Core Exceptions that should be used in case an error occurs that is
related to the Actinia Core functionality
"""

__license__ = "GPL-3.0-or-later"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2025, Sören Gebbert & mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


# class AsyncProcessError(Exception):
#     """
#     Raise this exception in case the asynchronous processing faces an error
#     """

#     def __init__(self, message):
#         message = "%s:  %s" % (str(self.__class__.__name__), message)
#         Exception.__init__(self, message)


class RsyncError(Exception):
    """Raise this exception in case the rsync of the interim result fails"""

    def __init__(self, message):
        message = "%s:  %s" % (str(self.__class__.__name__), message)
        Exception.__init__(self, message)


# class AsyncProcessTermination(Exception):
#     """
#     Raise this exception in case the termination requests was executed
#     successfully
#     """

#     def __init__(self, message):
#         message = "%s:  %s" % (str(self.__class__.__name__), message)
#         Exception.__init__(self, message)


# class AsyncProcessTimeLimit(Exception):
#     """Raise this exception in case the process time limit was reached"""

#     def __init__(self, message):
#         message = "%s:  %s" % (str(self.__class__.__name__), message)
#         Exception.__init__(self, message)


class GoogleCloudAPIError(Exception):
    """Raise this exception in case something went wrong in
    when accessing the google API
    """

    def __init__(self, message):
        message = "%s:  %s" % (str(self.__class__.__name__), message)
        Exception.__init__(self, message)


class SecurityError(Exception):
    """Raise this exception in case some security problem occurs"""

    def __init__(self, message):
        message = "%s:  %s" % (str(self.__class__.__name__), message)
        Exception.__init__(self, message)
