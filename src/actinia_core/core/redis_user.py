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
Redis server user interface
"""

from actinia_core.core.common.redis_base import RedisBaseInterface
import pickle

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class RedisUserInterface(RedisBaseInterface):
    """The Redis user database interface

    A single user is stored as Hash with several entries:
        - User id aka user name that must be unique
        - User role (superadmin, admin, user, guest)
        - User group
        - password hash
        - Permission dictionary

    In addition is the user_id saved in a hash that contains all user ids.
    """

    # We use two databases The user ID and the User name database
    # The user ID and user name databases are hashes
    user_id_hash_prefix = "USER-ID-HASH-PREFIX::"
    user_id_db = "USER-ID-DATABASE"

    def __init__(self):
        RedisBaseInterface.__init__(self)

    def get_password_hash(self, user_id):
        """Return the password hash of the user_id

        HGET User-id password_hash

        Args:
            user_id (str): The user id

        Returns:
             str:
             The password hash of the user id
        """
        return self.redis_server.hget(
            self.user_id_hash_prefix + user_id, "password_hash"
        ).decode()

    def get_role(self, user_id):
        """Return the role of the user

        HGET User-id user_role

        Args:
            user_id: The user id

        Returns:
             str:
             The api key of the user id
        """
        return self.redis_server.hget(
            self.user_id_hash_prefix + user_id, "user_role"
        ).decode()

    def get_group(self, user_id):
        """Return the group of the user

        HGET User-id user_group

        Args:
            user_id: The user id

        Returns:
             str:
             The user group
        """
        return self.redis_server.hget(
            self.user_id_hash_prefix + user_id, "user_group"
        ).decode()

    def get_credentials(self, user_id):
        """Return a dictionary that contains the user credentials

        HGETALL User-id db

        Args:
            user_id: The user id

        Returns:
            dict:
            A dictionary that contains the user credentials
        """
        creds = {}
        user_creds = self.redis_server.hgetall(
            self.user_id_hash_prefix + user_id
        )

        if user_creds:
            creds["user_id"] = user_creds[b"user_id"].decode()
            creds["password_hash"] = user_creds[b"password_hash"].decode()
            creds["user_role"] = user_creds[b"user_role"].decode()
            creds["user_group"] = user_creds[b"user_group"].decode()
            creds["permissions"] = pickle.loads(user_creds[b"permissions"])
        return creds

    def add(self, user_id, user_group, password_hash, user_role, permissions):
        """
        Add a user to the user database

        HSET User-id db -> add user-id
        HSET User-id-hash db -> add a new user with all required entries

        Args:
            user_id (str): The user id
            user_group (str): The user group
            password_hash (str): The password hash
            user_role (str): Get the role of the user ("admin", "user",
                             "guest")
            permissions (dict): A dictionary of permissions

        Returns:
            bool:
            True is success, False if user is already in the database
        """
        if (
            self.redis_server.exists(self.user_id_hash_prefix + user_id)
            is True
        ):
            return False
        pstring = pickle.dumps(permissions)

        lock = self.redis_server.lock(name="add_user_lock", timeout=1)
        lock.acquire()
        # First add the user-id to the user id database
        self.redis_server.hset(self.user_id_db, user_id, user_id)

        mapping = {
            "user_id": user_id,
            "password_hash": password_hash,
            "user_role": user_role,
            "user_group": user_group,
            "permissions": pstring,
        }
        # Make the database entry
        self.redis_server.hset(
            self.user_id_hash_prefix + user_id, mapping=mapping
        )
        lock.release()

        return True

    def update(
        self,
        user_id,
        user_group=None,
        password_hash=None,
        user_role=None,
        permissions=None,
    ):
        """Update the user credentials.

        Renaming an entry is not allowed, only existing entries with the same
        user_id can be updated.

        If a parameter is not provided (set None), the original value will be
        kept.

        HSET User-id-hash db -> set user with all required entries

        Args:
            user_id (str): The user id
            user_group (str): The user group
            password_hash (str): The password hash
            user_role (str): Get the role of the user ("admin", "user",
                             "guest")
            permissions (dict): A dictionary of permissions

        Returns:
            bool:
            True is success, False if user is not in the database

        """
        if (
            self.redis_server.exists(self.user_id_hash_prefix + user_id)
            is False
        ):
            return False

        user_creds = self.get_credentials(user_id)

        if password_hash is None:
            password_hash = user_creds["password_hash"]

        if user_role is None:
            user_role = user_creds["user_role"]

        if user_group is None:
            user_group = user_creds["user_group"]

        if permissions is None:
            permissions = user_creds["permissions"]

        pstring = pickle.dumps(permissions)

        lock = self.redis_server.lock(name="update_user_lock", timeout=1)
        lock.acquire()

        mapping = {
            "user_id": user_id,
            "password_hash": password_hash,
            "user_role": user_role,
            "user_group": user_group,
            "permissions": pstring,
        }
        # Update the database entry
        self.redis_server.hset(
            self.user_id_hash_prefix + user_id, mapping=mapping
        )

        lock.release()

        return True

    def exists(self, user_id):
        """Check if the user is in the database

        Args:
            user_id (str): The user id

        Returns:
            bool:
            True is user exists, False otherwise
        """
        return self.redis_server.exists(self.user_id_hash_prefix + user_id)

    def delete(self, user_id):
        """Remove a user id from the database

        HDEL User-id db
        DEL User-id-hash db

        Args:
            user_id (str): The user id

        Returns:
            bool:
            True is user exists, False otherwise
        """
        if self.exists(user_id) is False:
            return False

        lock = self.redis_server.lock(name="delete_user_lock", timeout=1)
        lock.acquire()
        # Delete the entry from the user id database
        self.redis_server.hdel(self.user_id_db, user_id)
        # Delete the actual user entry
        self.redis_server.delete(self.user_id_hash_prefix + user_id)
        lock.release()

        return True

    def list_all_ids(self):
        """
        List all user id's that are in the database

        HKEYS on the user id database

        Returns:
            list:
            A list of all user ids in the database
        """
        values = []
        l_entries = self.redis_server.hkeys(self.user_id_db)
        print(l_entries)
        for entry in l_entries:
            if entry:
                entry = entry.decode()
            values.append(entry)

        return values


# Create the Redis interface instance
redis_user_interface = RedisUserInterface()


def test_management(r):
    user_id = "Soeren"
    user_group = "test_1"
    password_hash = "hash"
    user_role = "admin"
    permissions = {
        "projects": {
            "NC": {"mapsets": ["PERMANWENT", "user1"]},
            "ECAD": {"mapsets": ["Temp", "Prec"]},
        },
        "modules": ["r.series", "r.slope.aspect"],
    }

    r.delete(user_id)

    r.add(
        user_id=user_id,
        user_group=user_group,
        password_hash=password_hash,
        user_role=user_role,
        permissions=permissions,
    )

    user_creds = r.get_credentials(user_id)
    # print(user_creds)

    if user_creds["user_id"] != user_id:
        raise Exception("add does not work")
    if user_creds["user_group"] != user_group:
        raise Exception("add does not work")
    if user_creds["password_hash"] != password_hash:
        raise Exception("add does not work")
    if user_creds["user_role"] != user_role:
        raise Exception("add does not work")

    if r.get_password_hash(user_id) != password_hash:
        raise Exception("get_password_hash does not work")

    if r.get_role(user_id) != user_role:
        raise Exception("get_role does not work")

    r.update(
        user_id=user_id,
        user_group=user_group,
        password_hash="hello",
        user_role=None,
        permissions=None,
    )

    user_creds = r.get_credentials(user_id)
    # print(user_creds)

    if user_creds["user_id"] != user_id:
        raise Exception("update does not work")
    if user_creds["user_group"] != user_group:
        raise Exception("add does not work")
    if user_creds["password_hash"] != "hello":
        raise Exception("update does not work")
    if user_creds["user_role"] != user_role:
        raise Exception("update does not work")

    user_group = "test_2"
    r.update(
        user_id=user_id,
        user_group=user_group,
        password_hash="yellow",
        user_role="user",
        permissions={
            "projects": {"utm32n": {"mapsets": ["PERMANWENT"]}},
            "modules": [
                "i.vi",
            ],
        },
    )

    user_creds = r.get_credentials(user_id)
    # print(user_creds)

    if user_creds["user_id"] != user_id:
        raise Exception("update does not work")
    if user_creds["user_group"] != user_group:
        raise Exception("add does not work")
    if user_creds["password_hash"] != "yellow":
        raise Exception("update does not work")
    if user_creds["user_role"] != "user":
        raise Exception("update does not work")
    if "utm32n" not in user_creds["permissions"]["projects"]:
        raise Exception("update does not work")

    user_ids = r.list_all_ids()
    if user_id not in user_ids:
        raise Exception("list_all_ids does not work")

    user_id_1 = user_id
    user_id = "Thomas"
    user_id_2 = user_id
    user_role = "guest"

    r.add(
        user_id=user_id,
        user_group=user_group,
        password_hash=password_hash,
        user_role=user_role,
        permissions=permissions,
    )

    user_creds = r.get_credentials(user_id)

    if user_creds["user_id"] != user_id:
        raise Exception("add does not work")
    if user_creds["user_group"] != user_group:
        raise Exception("add does not work")
    if user_creds["password_hash"] != password_hash:
        raise Exception("add does not work")
    if user_creds["user_role"] != user_role:
        raise Exception("user_role does not work")

    if r.get_password_hash(user_id) != password_hash:
        raise Exception("get_password_hash does not work")

    if r.get_role(user_id) != user_role:
        raise Exception("get_role does not work")

    user_ids = r.list_all_ids()
    if user_id not in user_ids:
        raise Exception("list_all_ids does not work")

    for id_ in user_ids:
        print(id_, r.get_credentials(id_))

    r.delete(user_id_1)
    r.delete(user_id_2)

    user_ids = r.list_all_ids()

    if user_ids:
        raise Exception("delete does not work")


if __name__ == "__main__":
    import os
    import signal
    import time

    pid = os.spawnl(
        os.P_NOWAIT, "/usr/bin/redis-server", "./redis.conf", "--port 7000"
    )

    time.sleep(1)

    try:
        r = RedisUserInterface()
        r.connect(host="localhost", port=7000)
        test_management(r)
        r.disconnect()
    except Exception:
        raise
    finally:
        os.kill(pid, signal.SIGTERM)
