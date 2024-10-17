# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2023 mundialis GmbH & Co. KG
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
Utils needed for mapsets merge to rename the mapset inside the mapset
directory for groups, virtual rasters and tgis
"""
import fileinput
import os
import sqlite3

from actinia_core.core.common.exceptions import AsyncProcessError

__license__ = "GPLv3"
__author__ = "Anika Weinmann, Lina Krisztian"
__copyright__ = "Copyright 2023, mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


def _change_mapsetname_in_raster_vrt(
    source_path, source_mapset, target_mapset
):
    """Replaces the mapset name in the vrt files of a mapset

    Args:
        source_path(str): path of the cell_misc folder in the source mapset
        source_mapset(str): name of source mapset
        target_mapset(str): name of target mapset
    """
    for raster in os.listdir(source_path):
        vrt_file = os.path.join(source_path, raster, "vrt")
        if os.path.isfile(vrt_file):
            for line in fileinput.input(vrt_file, inplace=True):
                print(
                    line.replace(f"@{source_mapset}", f"@{target_mapset}"),
                    end="",
                )


def _change_mapsetname_in_group(group_path, source_mapset, target_mapset):
    """Replaces the mapset name in the group file

    Args:
        group_path(str): path of the group folder in the source mapset
        source_mapset(str): name of source mapset
        target_mapset(str): name of target mapset

    Raises:
        This method will raise an AsyncProcessError if a group has no REF
        file
    """
    group_dirs = os.listdir(group_path)
    for group_dir in group_dirs:
        group_file = os.path.join(group_path, group_dir, "REF")
        if os.path.isfile(group_file):
            for line in fileinput.input(group_file, inplace=True):
                print(line.replace(source_mapset, target_mapset), end="")
        else:
            raise AsyncProcessError("group %s has no REF file" % (group_dir))


def _merge_tgis_dbs(tgis_db_path_1, tgis_db_path_2):
    """Merge two tgis sqlite.db files

    Args:
        tgis_db_path_1(str): path of a tgis sqlite.db file in which the
                                other should be merged
        tgis_db_path_2(str): path of a tgis sqlite.db file which should be
                                merged in tgis_db_path_1
    """
    con = sqlite3.connect(tgis_db_path_1)
    con.execute(f"ATTACH '{tgis_db_path_2}' as dba")
    con.execute("BEGIN")

    table_names1 = [
        row[1]
        for row in con.execute(
            "SELECT * FROM sqlite_master where type='table'"
        )
    ]
    table_names2 = [
        row[1]
        for row in con.execute(
            "SELECT * FROM dba.sqlite_master where type='table'"
        )
    ]

    # merge databases
    for table in table_names2:
        if table == "tgis_metadata":
            con.execute(f"DROP TABLE {table}")
            con.execute(
                f"CREATE TABLE {table} AS " f"SELECT * FROM dba.{table}"
            )
            continue
        # for example raster_register_xxx tables are not in both dbs
        if table not in table_names1:
            con.execute(
                f"CREATE TABLE {table} AS " f"SELECT * FROM dba.{table}"
            )
            continue
        combine = f"INSERT OR IGNORE INTO {table} SELECT * FROM dba.{table}"
        con.execute(combine)
    con.commit()
    con.execute("detach database dba")
    if con:
        con.close()


def _update_views_in_tgis(tgis_db_path):
    """Update views in tgis sqlite.db

    Args:
        tgis_db_path(str): Path to the tgis sqlite.db file where the views
                            should be updated
    """
    con = sqlite3.connect(tgis_db_path)
    cur = con.cursor()

    sql_script_folder = os.path.join(os.getenv("GISBASE"), "etc", "sql")
    drop_view_sql = os.path.join(sql_script_folder, "drop_views.sql")
    with open(drop_view_sql, "r") as sql:
        sql_drop_str = sql.read()
    cur.executescript(sql_drop_str)

    view_sql_file_names = [
        "raster_views.sql",
        "raster3d_views.sql",
        "vector_views.sql",
        "strds_views.sql",
        "str3ds_views.sql",
        "stvds_views.sql",
    ]
    for view_sql_file_name in view_sql_file_names:
        view_sql_file = os.path.join(sql_script_folder, view_sql_file_name)
        with open(view_sql_file, "r") as sql:
            sql_view_str = sql.read()
        cur.executescript(sql_view_str)
    con.commit()
    if con:
        con.close()
    del cur


def _change_mapsetname_in_tgis(
    tgis_path, source_mapset, target_mapset, target_tgis_db=None
):
    """Replaces the mapset name in the tgis sqlite.db

    Args:
        tgis_path(str): path of the tgis folder in the source mapset
        source_mapset(str): name of source mapset
        target_mapset(str): name of target mapset
        target_tgis_db(str): path to existing tgis sqlite.db of target
                                mapset. None if nonexistent.
    """

    tgis_db_path = os.path.join(tgis_path, "sqlite.db")

    # tables
    con = sqlite3.connect(tgis_db_path)
    cur = con.cursor()
    table_names = [
        row[1]
        for row in cur.execute(
            "SELECT * FROM sqlite_master where type='table'"
        )
    ]
    for table_name in table_names:
        columns = [
            row[0]
            for row in cur.execute(f"SELECT * FROM {table_name}").description
        ]
        for col in columns:
            cur.execute(
                f"UPDATE {table_name} SET {col} = REPLACE({col}, "
                f"'{source_mapset}', '{target_mapset}')"
            )
    con.commit()
    if con:
        con.close()
    del cur

    # if there already exists a sqlite.db file then merge it
    if target_tgis_db is not None:
        _merge_tgis_dbs(tgis_db_path, target_tgis_db)

    # update views
    _update_views_in_tgis(tgis_db_path)


def change_mapsetname(
    source_path,
    directory,
    source_mapset,
    target_mapset,
    target_path=None,
):
    if os.path.exists(source_path) is True:
        if directory == "group":
            _change_mapsetname_in_group(
                source_path, source_mapset, target_mapset
            )
        elif directory == "tgis":
            target_tgis_db = None
            if target_path and os.path.isdir(
                os.path.join(target_path, "tgis")
            ):
                target_tgis_db = os.path.join(target_path, "tgis", "sqlite.db")
            else:
                target_path = None
            _change_mapsetname_in_tgis(
                source_path,
                source_mapset,
                target_mapset,
                target_tgis_db,
            )
        # for raster VRTs the mapset has to be changed
        elif directory == "cell_misc":
            _change_mapsetname_in_raster_vrt(
                source_path, source_mapset, target_mapset
            )
