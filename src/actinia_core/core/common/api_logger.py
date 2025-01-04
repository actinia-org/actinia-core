# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2024 Sören Gebbert and mundialis GmbH & Co. KG
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
Actinia Core REST API call logging
"""
from datetime import datetime
import pickle
from functools import wraps
from flask import g, abort, request
import platform
from actinia_core.core.redis_api_log import redis_api_log_interface
from actinia_core.core.redis_fluentd_logger_base import RedisFluentLoggerBase

try:
    from fluent import sender
    from fluent import event

    if sender and event:
        has_fluent = True
except Exception:
    has_fluent = False

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-present, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


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
        RedisFluentLoggerBase.__init__(
            self, config=config, user_id=user_id, fluent_sender=fluent_sender
        )

    def add_entry(self, user_id, http_request):
        """Add an API call entry to the database

        Args:
            user_id (str): The user id of the API log
            http_request: The http request object


            example = {
                "endpoint": "asyncephemeralresource",
                "method": "POST",
                "path": "/projects/nc_spm_08/processing_async",
                "request_url": "http://localhost/projects/nc_spm_08/"
                "processing_async"
              }


        Returns:
            int:
            The index of the new entry in the api log list

        """
        api_info = {
            # For deprecated location endpoints remove "_locations" from
            # endpoint class name
            "endpoint": http_request.endpoint.replace("_locations", ""),
            "method": http_request.method,
            "path": http_request.path,
            "request_url": http_request.url,
        }

        entry = {
            "time_stamp": datetime.now(),
            "node": platform.node(),
            "api_info": api_info,
            "request_str": str(http_request),
            "user_id": user_id,
            "status": "api_call",
            "logger": "api_logger",
        }

        # Serialize the entry
        pentry = pickle.dumps(entry)

        redis_return = bool(self.db.add(user_id, pentry))

        entry["time_stamp"] = str(entry["time_stamp"])
        self.send_to_logger("API_LOG", entry)
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

        l_entries = self.db.list(user_id, start, end)

        # We need to deserialize the log entries
        result_list = []

        for pentry in l_entries:
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
