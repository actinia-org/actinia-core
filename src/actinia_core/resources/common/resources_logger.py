# -*- coding: utf-8 -*-
"""
Resource logger and management interface
"""
import sys
import pickle
from .redis_resources import RedisResourceInterface
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


class ResourceLogger(RedisFluentLoggerBase):
    """Write, update, receive and delete entries in the resource database
    """

    def __init__(self, host, port, config=None, user_id=None, fluent_sender=None):
        RedisFluentLoggerBase.__init__(self, config=config, user_id=user_id, fluent_sender=fluent_sender)
        # Connect to a redis database
        self.db = RedisResourceInterface()
        self.db.connect(host, port)

    @staticmethod
    def _generate_db_resource_id(user_id, resource_id):
        return "%s/%s" % (user_id, resource_id)

    def commit(self, user_id, resource_id, document, expiration=8640000):
        """Commit a resource entry to the database, create a new one if it does not exists,
        update existing resource entries

        Args:
            user_id (str): The user id
            resource_id (str): The resource id
            document (str): The pickled document to store in the database
            expiration (int): Number of seconds of expiration time, default 8640000s hence 100 days

        Returns:
            bool:
            True for success, False otherwise

        """

        db_resource_id = self._generate_db_resource_id(user_id, resource_id)
        redis_return = bool(self.db.set(db_resource_id, document, expiration))
        log_entry = "empty"
        data = ""
        try:
            http_code, data = pickle.loads(document)
            self.send_to_fluent("RESOURCE_LOG", data)
        except Exception as e:
            sys.stderr.write("ResourceLogger ERROR: Unable to connect to fluentd server "
                             "host %s port %i error: %s Logentry: %s\n\n Content: %s" % (self.host,
                                                                                         self.port,
                                                                                         str(e),
                                                                                         str(log_entry),
                                                                                         str(data)))
            raise
        finally:
            return redis_return

    def commit_termination(self, user_id, resource_id, expiration=3600):
        """Commit a resource entry to the database that requires the termination of the resource,
        create a new one if it does not exists, update existing resource entries

        Args:
            user_id (str): The user id
            resource_id (str): The resource id
            expiration (int): Number of seconds of expiration time, default 3600 hence 1 hour

        Returns:
            bool:
            True for success, False otherwise

        """

        db_resource_id = self._generate_db_resource_id(user_id, resource_id)
        return bool(self.db.set_termination(db_resource_id, expiration))

    def get(self, user_id, resource_id):
        """Get resource entry

        Args:
            user_id (str): The user id
            resource_id (str): The resource id

        Returns:
            str:
            The resource document or None

        """
        db_resource_id = self._generate_db_resource_id(user_id, resource_id)
        return self.db.get(db_resource_id)

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
                http_code, data = pickle.loads(entry)
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
                http_code, data = pickle.loads(entry)
                resource_list.append(data)

        return resource_list

    def get_termination(self, user_id, resource_id):
        """Get resource entry that requires the termination of the resource

        Args:
            user_id (str): The user id
            resource_id (str): The resource id

        Returns:
            bool:
            True is resource should be terminated or False if otherwise

        """
        db_resource_id = self._generate_db_resource_id(user_id, resource_id)
        return self.db.get_termination(db_resource_id)

    def delete(self, user_id, resource_id):
        """Delete resource entry

        Args:
            user_id (str): The user id
            resource_id (str): The resource id

        Returns:
            bool:
            True for success, False otherwise

        """
        db_resource_id = self._generate_db_resource_id(user_id, resource_id)
        return bool(self.db.delete(db_resource_id))

    def delete_termination(self, user_id, resource_id):
        """Delete resource termination entry

        Args:
            user_id (str): The user id
            resource_id (str): The resource id

        Returns:
            bool:
            True for success, False otherwise

        """
        db_resource_id = self._generate_db_resource_id(user_id, resource_id)
        return bool(self.db.delete_termination(db_resource_id))
