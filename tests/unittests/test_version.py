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

from actinia_core.version import (
    find_running_since_info,
    find_additional_version_info,
    parse_additional_version_info,
    valid_additional_version_info_key,
)

__license__ = "GPLv3"
__author__ = "Anika Weinmann"
__copyright__ = "Copyright 2021, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


add_versions = {
    "test_key_a": "test_val_a",
    "test_key_b": "test_val_b",
    "test_key_c": "test_val_c",
}


@pytest.mark.unittest
@pytest.mark.parametrize(
    "key,status",
    [
        ("test_key_a", True),
        ("number1", False),
        ("a!", False),
        ("a-", False),
        ("", False),
        ("a" * 26, False),
    ],
)
def test_valid_additional_version_info_key(key, status):
    test = valid_additional_version_info_key(key)
    if status is True:
        assert test, f"Key <{key}> is wrong"
    else:
        assert not test, f"Key <{key}> is not wrong"


@pytest.mark.unittest
@pytest.mark.parametrize("use_env,val", [(False, "n/a"), (True, "test")])
def test_find_running_since_info(use_env, val):
    if use_env is True:
        os.environ["ACTINIA_RUNNING_SINCE"] = val
    test = find_running_since_info()
    assert test == val, f"Running since info is not '{val}'"


@pytest.mark.unittest
@pytest.mark.parametrize(
    "env_value,expected",
    [
        ("", {}),
        (
            [f"{key}:{val}" for key, val in add_versions.items()][0],
            {
                list(add_versions.keys())[0]: add_versions[
                    list(add_versions.keys())[0]
                ]
            },
        ),
        (
            "|".join([f"{key}:{val}" for key, val in add_versions.items()]),
            add_versions,
        ),
    ],
)
def test_parse_additional_version_info(env_value, expected):
    test = parse_additional_version_info(env_value)
    assert test == expected, "Find additional version is not right"


@pytest.mark.unittest
@pytest.mark.parametrize(
    "env_value,expected",
    [
        ("", {}),
        (
            [f"{key}:{val}" for key, val in add_versions.items()][0],
            {
                list(add_versions.keys())[0]: add_versions[
                    list(add_versions.keys())[0]
                ]
            },
        ),
        (
            "|".join([f"{key}:{val}" for key, val in add_versions.items()]),
            add_versions,
        ),
        (
            f'{"|".join([f"{k}:{v}" for k, v in add_versions.items()])}|'
            "key_1:test",
            add_versions,
        ),
    ],
)
def test_find_additional_version_info(env_value, expected):
    if env_value != "":
        os.environ["ACTINIA_ADDITIONAL_VERSION_INFO"] = env_value
    else:
        if "ACTINIA_ADDITIONAL_VERSION_INFO" in os.environ:
            del os.environ["ACTINIA_ADDITIONAL_VERSION_INFO"]
    test = find_additional_version_info()
    assert test == expected, "Additional version is not right"
