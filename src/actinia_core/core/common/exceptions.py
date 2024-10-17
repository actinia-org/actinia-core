# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2018 Sören Gebbert and mundialis GmbH & Co. KG
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
Actinia Core Exceptions that should be used in case an error occurs that is
related to the Actinia Core functionality
"""

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class AsyncProcessError(Exception):
    """
    Raise this exception in case the asynchronous processing faces an error
    """

    def __init__(self, message):
        message = "%s:  %s" % (str(self.__class__.__name__), message)
        Exception.__init__(self, message)


class RsyncError(Exception):
    """Raise this exception in case the rsync of the interim result fails"""

    def __init__(self, message):
        message = "%s:  %s" % (str(self.__class__.__name__), message)
        Exception.__init__(self, message)


class AsyncProcessTermination(Exception):
    """
    Raise this exception in case the termination requests was executed
    successfully
    """

    def __init__(self, message):
        message = "%s:  %s" % (str(self.__class__.__name__), message)
        Exception.__init__(self, message)


class AsyncProcessTimeLimit(Exception):
    """Raise this exception in case the process time limit was reached"""

    def __init__(self, message):
        message = "%s:  %s" % (str(self.__class__.__name__), message)
        Exception.__init__(self, message)


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
