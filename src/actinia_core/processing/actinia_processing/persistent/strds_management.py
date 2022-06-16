# -*- coding: utf-8 -*-
#######
# actinia-core - an open source REST API for scalable, distributed, high
# performance processing of geographical data that uses GRASS GIS for
# computational tasks. For details, see https://actinia.mundialis.de/
#
# Copyright (c) 2016-2022 Sören Gebbert and mundialis GmbH & Co. KG
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
STRDS map layer management

TODO: Integrate into the ephemeral process chain approach
"""
import os
import sqlite3

from actinia_api.swagger2.actinia_core.schemas.strds_management import \
     STRDSInfoModel, STRDSInfoResponseModel

from actinia_core.processing.actinia_processing.ephemeral.persistent_processing \
     import PersistentProcessing
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.models.response_models import \
    StringListProcessingResultResponseModel
from actinia_core.core.common.process_object import Process


__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika"
__copyright__ = "Copyright 2016-2022, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "mundialis"


class PersistentSTRDSLister(PersistentProcessing):

    def __init__(self, *args):

        PersistentProcessing.__init__(self, *args)
        self.response_model_class = StringListProcessingResultResponseModel

    def _execute(self):

        self._setup()

        pc = {
            "version": 1,
            "list": [{
                "module": "t.list",
                "id": f"list_strds_{self.unique_id}",
                "inputs": [
                    {"param": "type", "value": "strds"},
                    {"param": "column", "value": "name"}
                ]
            }]
        }

        # Make sure that only the current mapset is used for strds listing
        has_where = False

        if self.rdc.user_data:
            for option, val in self.rdc.user_data.items():
                if val is not None:
                    if "where" in option:
                        select = f"{val} AND mapset = \'{self.mapset_name}\'"
                        pc["list"][0]["inputs"].append(
                            {"param": "where", "value": select})
                        has_where = True
                    else:
                        pc["list"][0]["inputs"].append(
                            {"param": option, "value": val})

        if has_where is False:
            select = f"mapset=\'{self.mapset_name}\'"
            pc["list"][0]["inputs"].append({"param": "where", "value": select})

        process_list = self._validate_process_chain(skip_permission_check=True,
                                                    process_chain=pc)
        self._create_temp_database()
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.mapset_name)

        self._execute_process_list(process_list)

        mapset_lists = []
        mapsets = self.module_output_log[0]["stdout"].split()

        for mapset in mapsets:
            mapset_lists.append(mapset.strip())

        self.module_results = mapset_lists


class PersistentSTRDSInfo(PersistentProcessing):
    """Gather the STRDS information
    """

    def __init__(self, *args):

        PersistentProcessing.__init__(self, *args)
        self.response_model_class = STRDSInfoResponseModel

    def _execute(self):

        self._setup()

        pc = {"1": {"module": "t.info",
                    "inputs": {"type": "strds",
                               "input": self.map_name},
                    "flags": "g"}}

        process_list = self._validate_process_chain(skip_permission_check=True,
                                                    process_chain=pc)
        self._create_temp_database()
        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.mapset_name)

        self._execute_process_list(process_list)

        kv_list = self.module_output_log[0]["stdout"].split("\n")

        strds = {}

        for string in kv_list:
            if "=" in string:
                k, v = string.split("=", 1)
                strds[k] = v

        self.module_results = STRDSInfoModel(**strds)
        self.finish_message = \
            "Information gathering for STRDS <%s> successful" % self.map_name


class PersistentSTRDSDeleter(PersistentProcessing):
    """Delete a STRDS
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _merge_tgis_dbs(self, tgis_db_path_1, tgis_db_path_2):
        """Merge two tgis sqlite.db files

        Args:
            tgis_db_path_1(str): path of a tgis sqlite.db file in which the
                                 other should be merged
            tgis_db_path_2(str): path of a tgis sqlite.db file which should be
                                 merged in tgis_db_path_1
        """
        import pdb; pdb.set_trace()
        con = sqlite3.connect(tgis_db_path_1)
        con.execute(f"ATTACH '{tgis_db_path_2}' as dba")
        con.execute("BEGIN")

        table_names1 = [row[1] for row in con.execute(
            "SELECT * FROM sqlite_master where type='table'")]
        table_names2 = [row[1] for row in con.execute(
            "SELECT * FROM dba.sqlite_master where type='table'")]

        # merge databases
        for table in table_names2:
            if table == 'tgis_metadata':
                con.execute(f"DROP TABLE {table}")
                con.execute(f"CREATE TABLE {table} AS "
                            f"SELECT * FROM dba.{table}")
                continue
            # for example raster_register_xxx tables are not in both dbs
            if table not in table_names1:
                con.execute(f"CREATE TABLE {table} AS "
                            f"SELECT * FROM dba.{table}")
                continue
            combine = f"INSERT OR IGNORE INTO {table} SELECT * FROM dba.{table}"
            con.execute(combine)
        con.commit()
        con.execute("detach database dba")
        if con:
            con.close()

    def _execute(self):
        self._setup()
        self.required_mapsets.append(self.target_mapset_name)

        args = self.rdc.user_data
        flags = "f"
        if args and "recursive" in args and args["recursive"] is True:
            flags = "rf"

        pc = {
            "version": 1,
            "list": [{
                "id": f"remove_strds_{self.unique_id}",
                "module": "t.remove",
                "inputs": [
                    {"param": "type", "value": "strds"},
                    {"param": "inputs", "value": self.map_name}
                ],
                "flags": flags}]
        }

        process_list = self._validate_process_chain(skip_permission_check=True,
                                                    process_chain=pc)

        self._check_lock_target_mapset()

        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)
        # Init GRASS environment and create the temporary mapset
        self._create_temporary_grass_environment(
            source_mapset_name=self.target_mapset_name)
        self._lock_temp_mapset()

        self._execute_process_list(process_list)
        self.temp_mapset_path = os.path.join(self.temp_location_path, self.temp_mapset_name)
        self._copy_merge_tmp_mapset_to_target_mapset()
        self.finish_message = "STRDS <%s> successfully deleted" % self.map_name
#


#         self._setup()
#         self.required_mapsets.append("PERMANENT")
#         self.required_mapsets.append(self.target_mapset_name)
#
#         # self._check_lock_target_mapset()
#
#         args = self.rdc.user_data
#         flags = "f"
#         if args and "recursive" in args and args["recursive"] is True:
#             flags = "rf"
#         #
#         # import pdb; pdb.set_trace()
#         # self.ginit.run_module(
#         #     self.grass_base_dir, [
#         #         os.path.join(self.user_location_path, self.target_mapset_name),
#         #         "--exec",
#         #         "t.remove",
#         #         flags,
#         #         f"inputs={self.map_name}",
#         #         "type=strds"]
#         # )
# #
#         # parameter = [
#         #     self.grass_base_dir,
#         #     os.path.join(self.user_location_path, self.target_mapset_name),
#         #     "--exec",
#         #     "t.remove",
#         #     flags,
#         #     f"inputs={self.map_name}",
#         #     "type=strds"
#         # ]
#         #
#         # p = Process(
#         #     exec_type="exec",
#         #     executable="t.remove",
#         #     id=f"remove_strds_{self.unique_id}",
#         #     executable_params=[flags, f"inputs={self.map_name} type=strds"])
#         #
#         # errorid, stdout_buff, stderr_buff = self._run_executable(p)
#
# # grass  /actinia_core/userdata/superadmin/nc_spm_08/test_strds4/ --exec t.remove -f type=strds inpu
# # ts=modis3@test_strds4
#
#         # flags = "-f"
#         # if args and "recursive" in args and args["recursive"] is True:
#         #     flags = "-rf"
#
#         # self._check_lock_target_mapset()
#         # self._create_grass_environment(
#         #     grass_data_base=os.path.split(self.user_location_path)[0],
#         #     mapset_name=self.target_mapset_name)
#         #
#         # p = Process(
#         #     exec_type="grass",
#         #     executable="t.remove",
#         #     id=f"remove_strds_{self.unique_id}",
#         #     executable_params=[flags, f"inputs={self.map_name} type=strds"])
#         # import pdb; pdb.set_trace()
#         # self._run_module(p)
#
#         pc = {
#             "version": 1,
#             "list": [{
#                 "id": f"remove_strds_{self.unique_id}",
#                 "module": "t.remove",
#                 "inputs": [
#                     {"param": "type", "value": "strds"},
#                     {"param": "inputs", "value": self.map_name}
#                 ],
#                 "flags": flags}]
#         }
#         process_list = self._validate_process_chain(skip_permission_check=True,
#                                                     process_chain=pc)
#
#         self._create_temp_database()
#         self._check_lock_target_mapset()
#
#         self._create_grass_environment(
#             grass_data_base=os.path.split(self.user_location_path)[0],
#             mapset_name=self.target_mapset_name)
#
#         # import pdb; pdb.set_trace()
#         self._execute_process_list(process_list)
#         self.finish_message = "STRDS <%s> successfully deleted" % self.map_name


class PersistentSTRDSCreator(PersistentProcessing):
    """Create a STRDS
    """

    def __init__(self, *args):
        PersistentProcessing.__init__(self, *args)

    def _execute(self):

        self._setup()
        self.required_mapsets.append(self.target_mapset_name)

        pc_1 = {"version": 1}
        pc_1["list"] = [{
            "id": f"list_strds_{self.unique_id}",
            "module": "t.list",
            "inputs": [
                {
                    "param": "type",
                    "value": "strds"
                },
                {
                    "param": "where",
                    "value": f"id = \'{self.map_name}@"
                             f"{self.target_mapset_name}\'"
                },
            ]
        }]
        # Check the first process chain
        pc_1 = self._validate_process_chain(skip_permission_check=True,
                                            process_chain=pc_1)

        pc_2 = {
            "version": 1,
            "list": [{
                "id": f"create_strds_{self.unique_id}",
                "module": "t.create",
                "inputs": [{"param": "type", "value": "strds"}],
                "outputs": [{"param": "output", "value": self.map_name}]
            }]
        }
        if self.request_data:
            for key, val in self.request_data.items():
                pc_2["list"][0]["inputs"].append({"param": key, "value": val})

        pc_2 = self._validate_process_chain(skip_permission_check=True,
                                            process_chain=pc_2)
        self._create_temp_database()
        self._check_lock_target_mapset()

        self._create_grass_environment(grass_data_base=self.temp_grass_data_base,
                                       mapset_name=self.target_mapset_name)

        self._execute_process_list(pc_1)

        # check if STRDS exists
        raster_list = self.module_output_log[0]["stdout"].split("\n")

        if len(raster_list[0]) > 0:
            raise AsyncProcessError("STRDS <%s> exists." % self.map_name)

        self._execute_process_list(pc_2)

        self.finish_message = "STRDS <%s> successfully created" % self.map_name
