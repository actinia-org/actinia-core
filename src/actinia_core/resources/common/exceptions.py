# -*- coding: utf-8 -*-
"""
Actinia Core Exceptions that should be used in case an error occures that is related to the Actinia Core
functionality
"""

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class AsyncProcessError(Exception):
    """Raise this exception in case the asynchronous processing faces an error
    """
    def __init__(self, message):
        message = "%s:  %s"%(str(self.__class__.__name__), message)
        Exception.__init__(self, message)


class AsyncProcessTermination(Exception):
    """Raise this exception in case the termination requests was executed successfully
    """
    def __init__(self, message):
        message = "%s:  %s"%(str(self.__class__.__name__), message)
        Exception.__init__(self, message)


class AsyncProcessTimeLimit(Exception):
    """Raise this exception in case the process time limit was reached
    """
    def __init__(self, message):
        message = "%s:  %s"%(str(self.__class__.__name__), message)
        Exception.__init__(self, message)


class GoogleCloudAPIError(Exception):
    """Raise this exception in case something went wrong in
    when accessing the google API
    """
    def __init__(self, message):
        message = "%s:  %s"%(str(self.__class__.__name__), message)
        Exception.__init__(self, message)
