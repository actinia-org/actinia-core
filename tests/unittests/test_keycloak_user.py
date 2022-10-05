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
Tests: Version unittest case
"""
import os
import pytest

from actinia_core.core.common.config import global_config
from actinia_core.core.common.keycloak_user import (
    ActiniaKeycloakUser,
    create_user_from_tokeninfo,
    read_keycloak_config,
)

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2022, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


add_versions = {
    "test_key_a": "test_val_a",
    "test_key_b": "test_val_b",
    "test_key_c": "test_val_c",
}
global_config.KEYCLOAK_CONFIG_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "keycloak.json"
)
global_config.KEYCLOAK_GROUP_PREFIX = "/actinia-user/"
read_keycloak_config(global_config.KEYCLOAK_CONFIG_PATH)


@pytest.mark.unittest
def test_keycloak_superadmin():
    token_info = {
        'exp': 1664974952,
        'iat': 1664974652,
        'jti': 'efa087ce-6853-49b5-9033-3d344994d779',
        'iss': 'http://keycloak:8080/auth/realms/actinia-realm',
        'aud': ['actinia-client', 'account'],
        'sub': '1ddd2171-3ad5-4a8a-b37e-a46b3d98a0b1',
        'typ': 'Bearer',
        'azp': 'actinia-client',
        'session_state': 'ebeca9f2-653d-4ddd-a9a5-bf563b3eae7a',
        'acr': '1',
        'allowed-origins': ['http://actinia_core:8088'],
        'realm_access': {'roles': [
            'offline_access',
            'default-roles-actinia-realm',
            'uma_authorization']},
        'resource_access': {
            'actinia-client': {'roles': ['superadmin']},
            'account': {'roles': [
                'manage-account', 'manage-account-links', 'view-profile']}
        },
        'scope': 'email profile',
        'sid': 'ebeca9f2-653d-4ddd-a9a5-bf563b3eae7a',
        'process_num_limit': 1000,
        'accessible_modules': 'None',
        'email_verified': False,
        'group_members': ['actinia-admin,actinia-superadmin,actinia-user'],
        'accessible_datasets': 'None',
        'cell_limit': 100000000000,
        'name': 'actinia-superadmin actinia-superadmin',
        'groups': ['/actinia-user/actinia_test_group_2'],
        'preferred_username': 'actinia-superadmin',
        'given_name': 'actinia-superadmin',
        'family_name': 'actinia-superadmin',
        'process_time_limit': 31536000
    }

    user = create_user_from_tokeninfo(token_info)

    assert isinstance(user, ActiniaKeycloakUser), "User has wrong type"
    assert user.check_group_members("actinia-admin"), "'actinia-admin' not " \
        "in group members"
    assert user.check_group_members("actinia-admin2") is False, \
        "'actinia-admin2' in group members"
    assert user.get_role() == "superadmin", "Role is wrong"
    assert user.get_group() == "actinia_test_group_2", "Group is wrong"
    assert "accessible_modules" in user.get_credentials()["permissions"], \
        "accessible_modules not in user credentials"
    assert len(user.get_accessible_datasets()) == 3, \
        "Accessible datasets are wrong"
    assert len(user.get_accessible_modules()) == 193, \
        "Accessible modules are wrong"
    assert user.get_cell_limit() == token_info["cell_limit"], \
        "Cell limit is wrong"
    assert user.get_process_num_limit() == token_info["process_num_limit"], \
        "Process number limit is wrong"
    assert user.get_process_time_limit() == token_info["process_time_limit"], \
        "Process time limit is wrong"
    assert user.has_guest_role() is False, "Role is wrong"
    assert user.has_user_role() is False, "Role is wrong"
    assert user.has_admin_role() is False, "Role is wrong"
    assert user.has_superadmin_role() is True, "Role is wrong"
