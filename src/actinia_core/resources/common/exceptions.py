# -*- coding: utf-8 -*-
"""
Actinia Core Exceptions that should be used in case an error occures that is related to the Actinia Core
functionality
"""
from actinia_core.resources.common.response_models import create_response_from_model

__license__ = "GPLv3"
__author__     = "Sören Gebbert"
__copyright__  = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__      = "soerengebbert@googlemail.com"


class InvalidUsage(Exception):
    """Invalid usage exception that must be raised if the user request or its data is invalid

    """
    status_code = 400

    def __init__(self, message, user_id, resource_id, status_url, orig_time, orig_datetime, status_code=None):
        """Constructor of the invalid usage exception

        Args:
            message: The error message that should be shown to the user
            status_code: The HTTP status code
        """
        Exception.__init__(self)
        self.message = message
        self.user_id = user_id
        self.resource_id = resource_id
        self.status_url = status_url
        self.orig_time = orig_time
        self.orig_datetime = orig_datetime
        if status_code is not None:
            self.status_code = status_code

    def to_json(self):
        return create_response_from_model(status="error",
                                          http_code=self.status_code,
                                          message=self.message,
                                          user_id=self.user_id,
                                          resource_id=self.resource_id,
                                          status_url=self.status_url,
                                          orig_time=self.orig_time,
                                          orig_datetime=self.orig_datetime,
                                          resp_type="json")

    def to_pickle(self):
        return create_response_from_model(status="error",
                                          http_code=self.status_code,
                                          message=self.message,
                                          user_id=self.user_id,
                                          resource_id=self.resource_id,
                                          status_url=self.status_url,
                                          orig_time=self.orig_time,
                                          orig_datetime=self.orig_datetime,
                                          resp_type="pickle")


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
