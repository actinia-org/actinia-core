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
Resource logger and management interface
"""
import pickle
from .redis_resources import RedisResourceInterface
from .redis_fluentd_logger_base import RedisFluentLoggerBase

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-present, Sören Gebbert and mundialis GmbH & Co. KG"
)


class ResourceLogger(RedisFluentLoggerBase):
    """Write, update, receive and delete entries in the resource database"""

    def __init__(
        self,
        host,
        port,
        password=None,
        config=None,
        user_id=None,
        fluent_sender=None,
    ):
        RedisFluentLoggerBase.__init__(
            self, config=config, user_id=user_id, fluent_sender=fluent_sender
        )
        # Connect to a redis database
        self.db = RedisResourceInterface()
        redis_args = (host, port)
        if password is not None:
            redis_args = (*redis_args, password)
        self.db.connect(*redis_args)
        del redis_args

    @staticmethod
    def _generate_db_resource_id(user_id, resource_id, iteration=None):
        """Generate DB resource id

        Args:
            user_id (str): The user id
            resource_id (str): The resource id
            iteration (int): The iteration of the job

        Returns:
            str: The generated DB resource id

        """
        if iteration == 1:
            iteration = None
        if iteration is None:
            return "%s/%s" % (user_id, resource_id)
        else:
            return "%s/%s/%d" % (user_id, resource_id, iteration)

    @staticmethod
    def _get_iteration_from_db_resource_id(db_resource_id):
        resoucre_id_split = db_resource_id.split("/")
        if len(resoucre_id_split) == 3:
            return int(resoucre_id_split[2])
        else:
            return 1

    def commit(
        self, user_id, resource_id, iteration, document, expiration=8640000
    ):
        """Commit a resource entry to the database, create a new one if it
        does not exists, update existing resource entries

        Args:
            user_id (str): The user id
            resource_id (str): The resource id
            iteration (int): The iteration of the job
            document (str): The pickled document to store in the database
            expiration (int): Number of seconds of expiration time, default
                              8640000s hence 100 days

        Returns:
            bool:
            True for success, False otherwise

        """

        db_resource_id = self._generate_db_resource_id(
            user_id, resource_id, iteration
        )
        redis_return = bool(self.db.set(db_resource_id, document, expiration))
        _, data = pickle.loads(document)
        data["logger"] = "resources_logger"
        self.send_to_logger("RESOURCE_LOG", data)
        return redis_return

    def commit_termination(
        self, user_id, resource_id, iteration=None, expiration=3600
    ):
        """Commit a resource entry to the database that requires the
        termination of the resource, create a new one if it does not exists,
        update existing resource entries

        Args:
            user_id (str): The user id
            resource_id (str): The resource id
            iteration (int): The iteration of the job
            expiration (int): Number of seconds of expiration time, default
                              3600 hence 1 hour

        Returns:
            bool:
            True for success, False otherwise

        """
        db_resource_id = self._generate_db_resource_id(
            user_id, resource_id, iteration
        )
        return bool(self.db.set_termination(db_resource_id, expiration))

    def get(self, user_id, resource_id, iteration=None):
        """Get resource entry

        Args:
            user_id (str): The user id
            resource_id (str): The resource id
            iteration (int): The iteration of the job

        Returns:
            str:
            The resource document or None

        """
        db_resource_id = self._generate_db_resource_id(
            user_id, resource_id, iteration
        )
        return self.db.get(db_resource_id)

    def get_latest_iteration(self, user_id, resource_id=None):
        """Get resource entry with latest iteration

        Args:
            user_id (str): The user id
            resource_id (str): The resource id

        Returns:
            int:
            The latest iteration of the resource
            str:
            The resource document or None

        """
        db_resource_id_pattern = "%s*" % self._generate_db_resource_id(
            user_id, resource_id, None
        )
        db_keys = self.db.get_keys_from_pattern(db_resource_id_pattern)
        if len(db_keys) == 1:
            db_resource_id = db_keys[0]
        else:
            db_resource_id = max(db_keys)
        iteration = self._get_iteration_from_db_resource_id(db_resource_id)
        if iteration == 1:
            iteration = None
        return iteration, self.db.get(db_resource_id)

    def get_all_iteration(self, user_id, resource_id):
        """Get resource entry of all iterations

        Args:
            user_id (str): The user id
            resource_id (str): The resource id

        Returns:
            str:
            The resource document or None

        """
        db_resource_id = self._generate_db_resource_id(
            user_id, resource_id, None
        )
        db_resource_id_pattern = "%s*" % db_resource_id
        db_keys = self.db.get_keys_from_pattern(db_resource_id_pattern)
        db_keys.sort()
        resp_dict = dict()
        for db_key in db_keys:
            iteration = self._get_iteration_from_db_resource_id(db_key)
            if iteration != 1:
                db_resource_id_iter = self._generate_db_resource_id(
                    user_id, resource_id, iteration
                )
            else:
                db_resource_id_iter = db_resource_id
            resp_dict[str(iteration)] = pickle.loads(
                self.db.get(db_resource_id_iter)
            )[1]
        return pickle.dumps([200, resp_dict])

    def get_user_resources(self, user_id):
        """Get a user specific list of resource entries

        Args:
            user_id (str): The user id

        Returns:
            list:
            A list of resource document

        """
        resource_list_pickled = self.db.get_list(user_id + "*")
        resource_list = []

        if resource_list_pickled:
            for entry in resource_list_pickled:
                _, data = pickle.loads(entry)
                resource_list.append(data)

        return resource_list

    def get_all_resources(self):
        """Get all resource entries

        Returns:
            list:
            A list resource document

        """

        resource_list_pickled = self.db.get_list("*")
        resource_list = []

        if resource_list_pickled:
            for entry in resource_list_pickled:
                _, data = pickle.loads(entry)
                resource_list.append(data)

        return resource_list

    def get_termination(self, user_id, resource_id, iteration=None):
        """Get resource entry that requires the termination of the resource

        Args:
            user_id (str): The user id
            resource_id (str): The resource id
            iteration (int): The iteration of the job

        Returns:
            bool:
            True is resource should be terminated or False if otherwise

        """
        db_resource_id = self._generate_db_resource_id(
            user_id, resource_id, iteration
        )
        return self.db.get_termination(db_resource_id)

    def delete(self, user_id, resource_id, iteration=None):
        """Delete resource entry

        Args:
            user_id (str): The user id
            resource_id (str): The resource id
            iteration (int): The iteration of the job

        Returns:
            bool:
            True for success, False otherwise

        """
        db_resource_id = self._generate_db_resource_id(
            user_id, resource_id, iteration
        )
        return bool(self.db.delete(db_resource_id))

    def delete_termination(self, user_id, resource_id, iteration=None):
        """Delete resource termination entry

        Args:
            user_id (str): The user id
            resource_id (str): The resource id
            iteration (int): The iteration of the job

        Returns:
            bool:
            True for success, False otherwise

        """
        db_resource_id = self._generate_db_resource_id(
            user_id, resource_id, iteration
        )
        return bool(self.db.delete_termination(db_resource_id))
