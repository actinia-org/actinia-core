# -*- coding: utf-8 -*-
"""
Actinia Core REST API call logging
"""
from datetime import datetime
import pickle
from functools import wraps
from flask import g, abort, request
import platform
import sys
from .redis_api_log import redis_api_log_interface
from .redis_fluentd_logger_base import RedisFluentLoggerBase

try:
    from fluent import sender
    from fluent import event

    has_fluent = True
except:
    has_fluent = False

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


def log_api_call(f):
    """This decorator function logs API calls

    It stores the request information, user and host id in a
    database list identified by the user name

    Args:
        f (func): The function to wrap

    Returns:
        func:
        The function

    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            abort(401)

        logger = ApiLogger()
        user_id = g.user.get_id()

        logger.add_entry(user_id=user_id, http_request=request)

        return f(*args, **kwargs)

    return decorated_function


class ApiLogger(RedisFluentLoggerBase):
    db = redis_api_log_interface

    def __init__(self, config=None, user_id=None, fluent_sender=None):
        RedisFluentLoggerBase.__init__(self, config=config, user_id=user_id, fluent_sender=fluent_sender)

    def add_entry(self, user_id, http_request):
        """Add an API call entry to the database

        Args:
            user_id (str): The user id of the API log
            http_request: The http request object


            example = {
                "endpoint": "asyncephemeralresource",
                "method": "POST",
                "path": "/locations/nc_spm_08/processing_async",
                "request_url": "http://localhost/locations/nc_spm_08/processing_async"
              }


        Returns:
            int:
            The index of the new entry in the api log list

        """
        api_info = {"endpoint": http_request.endpoint,
                    "method": http_request.method,
                    "path": http_request.path,
                    "request_url": http_request.url}

        entry = {"time_stamp": datetime.now(),
                 "node": platform.node(),
                 "api_info": api_info,
                 "request_str": str(http_request),
                 "user_id": user_id,
                 "status": "api_call"}

        # Serialize the entry
        pentry = pickle.dumps(entry)

        redis_return = bool(self.db.add(user_id, pentry))

        try:
            # Convert time stamp
            entry["time_stamp"] = str(entry["time_stamp"])
            self.send_to_fluent("API_LOG", entry)
        except Exception as e:
            sys.stderr.write("ApiLogger ERROR: Unable to connect to fluentd "
                             "server host %s port %i error: %s" % (self.host,
                                                                   self.port,
                                                                   str(e)))
            raise
        finally:
            return redis_return

    def list(self, user_id, start, end):
        """
        Return a list of api log entries

        Args:
            user_id (str): The user id of the API log
            start (int): Integer start index
            end (int): Integer end index

        Returns:
            list:
            A list of log entries

        Example:

            [{"time_stamp":"...",
             "node":"...",
             "request":"..."},
             {..},]

        """

        l = self.db.list(user_id, start, end)

        # We need to deserialize the log entries
        result_list = []

        for pentry in l:
            entry = pickle.loads(pentry)
            result_list.append(entry)

        return result_list

    def trim(self, user_id, start, end):
        """Remove all api log entries that are outside the specified indices

        Args:
            user_id (str): The user_id to trim the log entries
            start (int): The start index
            end (int): The end index

        Returns:
            bool:
            True in any case

        """
        return bool(self.db.trim(user_id, start, end))

    def delete(self, user_id):
        """Delete the user_id specific api log list

        Args:
            user_id (str): The user_id to delete the log entries

        Returns:
            bool:
            True in case of success, False otherwise

        """

        return bool(self.db.delete(user_id))

    def size(self, user_id):
        """Return the size of the user_id specific log list
        Args:
            user_id (str): The user_id

        Returns:
            int:
            The size of the user specific log list

        """

        return self.db.size(user_id)
