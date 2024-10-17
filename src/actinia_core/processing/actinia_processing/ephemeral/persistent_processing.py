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
Asynchronous computation in specific temporary generated and then copied
or original mapsets
"""
import os
import shutil
import subprocess

from actinia_core.processing.actinia_processing.ephemeral_processing import (
    EphemeralProcessing,
)
from actinia_core.core.common.exceptions import AsyncProcessError
from actinia_core.core.mapset_merge_utils import change_mapsetname

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Guido Riembauer, Anika Weinmann, Lina Krisztian"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class PersistentProcessing(EphemeralProcessing):
    """Processing of grass modules in a temporary or original mapset.

    This class is designed to run GRASS modules that are specified in a
    process chain in a temporary mapset that later on is copied into the
    original project or merged into an existing mapset.

    Locking concept:

        - Check if the target mapset exists
        - Lock the target mapset
        - Create a temporary mapset lock (name is generated in constructor)
        - Create the temporary mapset in the local storage
        - Process

    If target mapset exists:

        - Move the temporary mapset after processing to the user group database
        - Merge the temporary mapset into the target mapset
        - Delete the temporary mapset
        - Unlock the two mapsets after processing is finished, terminated or
          raised an error

    If target mapset does not exists:

        - After processing finished successfully, copy the
          temporary mapset to the original user group specific project using
          the target mapset name
        - Unlock the two mapsets after processing is finished, terminated or
          raised an error

    """

    def __init__(self, rdc):
        """Constructor

        Args:
            rdc (ResourceDataContainer): The data container that contains all
                                         required variables for processing

        """

        EphemeralProcessing.__init__(self, rdc)
        self.target_mapset_name = self.mapset_name
        self.target_mapset_exists = False  # By default the target mapset
        # does not exists
        # Set True if this process was successful in setting the lock
        self.target_mapset_lock_set = False
        self.orig_mapset_path = None

        # We have two mapset lock ids. The target mapset and the temporary
        # mapset
        self.target_mapset_lock_id = self._generate_mapset_lock_id(
            self.user_group, self.project_name, self.target_mapset_name
        )

        self.temp_mapset_lock_id = self._generate_mapset_lock_id(
            self.user_group, self.project_name, self.temp_mapset_name
        )
        self.temp_mapset_lock_set = False

    def _generate_mapset_lock_id(self, user_group, project_name, mapset_name):
        """Generate a unique id to lock a mapset in the redis database

        Projects are user group specific. Hence different user groups may have
        projects with the same names and with equal mapset names.

        In the same user group, a project/mapset must be locked to grant
        exclusive access rights.

        Args:
            user_group: The user group used for locking
            project_name: The project name in which the mapset is located
                           for locking
            mapset_name: The mapset name that should be locked

        Returns:
            The lock id

        """
        return "%s/%s/%s" % (user_group, project_name, mapset_name)

    def _lock_temp_mapset(self):
        """Lock the temporary mapset

        This method sets in case of success: self.tmp_mapset_lock_set = True
        """
        # Lock the temporary mapset for the time that the user can allocate at
        # maximum
        ret = self.lock_interface.lock(
            resource_id=self.temp_mapset_lock_id,
            expiration=self.process_time_limit * self.process_num_limit,
        )

        if ret == 0:
            raise AsyncProcessError(
                "Unable to lock temporary mapset <%s>, "
                "resource is already locked" % self.target_mapset_name
            )
        self.message_logger.info(
            "Mapset <%s> locked" % self.target_mapset_name
        )

        # if we manage to come here, the lock was correctly set
        self.temp_mapset_lock_set = True

    def _check_mapset(self, mapset):
        """Check if the target mapset exists

        This method will check if the target mapset exists in the global and
        user group projects.
        If the mapset is in the global database, then an AsyncProcessError
        will be raised, since global project/mapsets can not be modified.

        This method sets in case of success:

            self.target_mapset_lock_set = True
            self.tmp_mapset_lock_set = True

        Raises:
            AsyncProcessError

        """
        mapset_exists = False

        # Check if the global project is accessible and that the target mapset
        # does not exist
        if self.is_global_database is True:
            # Break if the target mapset exists in the global database
            if (
                os.path.exists(self.global_project_path)
                and os.path.isdir(self.global_project_path)
                and os.access(
                    self.global_project_path, os.R_OK | os.X_OK | os.W_OK
                )
                is True
            ):
                self.orig_mapset_path = os.path.join(
                    self.global_project_path, mapset
                )

                if os.path.exists(self.orig_mapset_path) is True:
                    if (
                        os.access(
                            self.orig_mapset_path, os.R_OK | os.X_OK | os.W_OK
                        )
                        is True
                    ):
                        raise AsyncProcessError(
                            "Mapset <%s> exists in the global "
                            "dataset and can not be modified." % mapset
                        )
            else:
                raise AsyncProcessError(
                    "Unable to access global project <%s>" % self.project_name
                )

        # Always check if the target mapset already exists and set the flag
        # accordingly
        if (
            os.path.exists(self.user_project_path)
            and os.path.isdir(self.user_project_path)
            and os.access(self.user_project_path, os.R_OK | os.X_OK | os.W_OK)
            is True
        ):
            self.orig_mapset_path = os.path.join(
                self.user_project_path, mapset
            )

            if os.path.exists(self.orig_mapset_path) is True:
                if (
                    os.access(
                        self.orig_mapset_path, os.R_OK | os.X_OK | os.W_OK
                    )
                    is True
                ):
                    mapset_exists = True
                    # Add the existing mapset to the required ones for mapset
                    # search path settings
                    self.required_mapsets.append(mapset)
                else:
                    raise AsyncProcessError(
                        "Unable to access mapset <%s> "
                        "path %s" % (mapset, self.orig_mapset_path)
                    )
            else:
                mapset_exists = False
        else:
            raise AsyncProcessError(
                "Unable to access user project <%s>" % self.project_name
            )

        return mapset_exists

    def _check_target_mapset_exists(self):
        """Check if the target mapset exists

        This method will check if the target mapset exists in the global and
        user project.
        If the mapset is in the global database, then an AsyncProcessError will
        be raised, since global mapsets can not be modified.

        This method sets in case of success:

            self.target_mapset_exists = True/False

        Raises:
            AsyncProcessError
        """
        self.target_mapset_exists = self._check_mapset(self.target_mapset_name)

    def _check_lock_target_mapset(self):
        """
        Check if the target mapset exists and lock it, then lock the temporary
        mapset

        This method will check if the target mapset exists in the global and
        user project.
        If the mapset is in the global database, then an AsyncProcessError will
        be raised, since global mapsets can not be modified.

        This method sets in case of success:

            self.target_mapset_lock_set = True
            self.tmp_mapset_lock_set = True

        Raises:
            AsyncProcessError

        """
        self._check_target_mapset_exists()
        self._lock_target_mapset()

    def _lock_target_mapset(self):
        """Lock the target mapset

        Raises:
            AsyncProcessError

        """

        # Lock the mapset for the time that the user can allocate at maximum
        ret = self.lock_interface.lock(
            resource_id=self.target_mapset_lock_id,
            expiration=self.process_time_limit * self.process_num_limit,
        )

        if ret == 0:
            raise AsyncProcessError(
                "Unable to lock project/mapset <%s/%s>, "
                "resource is already locked"
                % (self.project_name, self.target_mapset_name)
            )
        self.message_logger.info(
            "project/mapset <%s/%s> locked"
            % (self.project_name, self.target_mapset_name)
        )

        # if we manage to come here, the lock was correctly set
        self.target_mapset_lock_set = True

    def _merge_mapset_into_target(self, source_mapset, target_mapset):
        """Link the source mapset content into the target mapset

        Attention: Not all directories and files in the mapset are copied.
            See list directories.
        """
        self.message_logger.info(
            "Copy source mapset <%s> content "
            "into the target mapset <%s>" % (source_mapset, target_mapset)
        )

        # Raster, vector, group and space time data set directories/files
        directories = [
            "cell",
            "misc",
            "fcell",
            "cats",
            "cellhd",
            "cell_misc",
            "colr",
            "colr2",
            "hist",
            "vector",
            "group",
            "tgis",
            "VAR",
        ]

        for directory in directories:
            source_path = os.path.join(
                self.user_project_path, source_mapset, directory
            )
            target_path = os.path.join(self.user_project_path, target_mapset)

            change_mapsetname(
                source_path,
                directory,
                source_mapset,
                target_mapset,
                target_path,
            )

            if os.path.exists(source_path) is True:
                # Hardlink the sources into the target
                stdout = subprocess.PIPE
                stderr = subprocess.PIPE

                p = subprocess.Popen(
                    [
                        "/bin/cp",
                        "-flr",
                        "%s" % source_path,
                        "%s/." % target_path,
                    ],
                    stdout=stdout,
                    stderr=stderr,
                )
                (stdout_buff, stderr_buff) = p.communicate()
                if p.returncode != 0:
                    raise AsyncProcessError(
                        "Unable to merge mapsets. Error in linking:"
                        " stdout: %s stderr: %s" % (stdout_buff, stderr_buff)
                    )

    def _copy_merge_tmp_mapset_to_target_mapset(self):
        """Copy the temporary mapset into the original project

        In case the mapset does not exists, then use the target mapset name,
        otherwise use the temporary mapset name for copying which is later on
        merged into the target mapset and then removed
        """

        # Extent the mapset lock for an hour, since copying can take long
        if self.target_mapset_lock_set is True:
            ret = self.lock_interface.extend(
                resource_id=self.target_mapset_lock_id, expiration=3600
            )
            if ret == 0:
                raise AsyncProcessError(
                    "Unable to extend lock for mapset "
                    "<%s>" % self.target_mapset_name
                )

        if self.temp_mapset_lock_set is True:
            ret = self.lock_interface.extend(
                resource_id=self.temp_mapset_lock_id, expiration=3600
            )
            if ret == 0:
                raise AsyncProcessError(
                    "Unable to extend lock for "
                    "temporary mapset <%s>" % self.temp_mapset_name
                )

        self.message_logger.info(
            "Copy temporary mapset from %s to %s"
            % (
                self.temp_mapset_path,
                os.path.join(self.user_project_path, self.target_mapset_name),
            )
        )

        source_path = self.temp_mapset_path

        # In case the mapset does not exists, then use the target mapset name,
        # otherwise use the temporary mapset name for copying which is later
        # on merged into the target mapset and then removed
        if self.target_mapset_exists is True:
            target_path = self.user_project_path + "/."
            message = (
                "Copy temporary mapset <%s> to target project "
                "<%s>" % (self.temp_mapset_name, self.project_name)
            )
        else:
            target_path = os.path.join(
                self.user_project_path, self.target_mapset_name
            )
            message = (
                "Copy temporary mapset <%s> to target project "
                "<%s>" % (self.target_mapset_name, self.project_name)
            )

        self._send_resource_update(message)

        try:
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
            p = subprocess.Popen(
                ["/bin/cp", "-fr", "%s" % source_path, "%s" % target_path],
                stdout=stdout,
                stderr=stderr,
            )
            (stdout_buff, stderr_buff) = p.communicate()
            if p.returncode != 0:
                raise AsyncProcessError(
                    "Unable to copy temporary mapset to "
                    "original project. Copy error "
                    "stdout: %s stderr: %s returncode: %i"
                    % (stdout_buff, stderr_buff, p.returncode)
                )
        except Exception as e:
            raise AsyncProcessError(
                "Unable to copy temporary mapset to "
                "original project. Exception %s" % str(e)
            )

        # Merge the temp mapset into the target mapset in case the target
        # already exists
        if self.target_mapset_exists is True:
            self._merge_mapset_into_target(
                self.temp_mapset_name, self.target_mapset_name
            )
            shutil.rmtree(
                os.path.join(self.user_project_path, self.temp_mapset_name)
            )
            # remove interim results
            if self.interim_result.saving_interim_results is True:
                interim_dir = os.path.join(
                    self.interim_result.user_resource_interim_storage_path,
                    self.resource_id,
                )
                self.message_logger.info(
                    "Remove interim results %s" % interim_dir
                )
                if os.path.isdir(interim_dir):
                    shutil.rmtree(interim_dir)

    def _execute_process_list(self, process_list):
        """Extend the mapset lock and execute the provided process list

        Args:
            process_list: The process list to execute

        Raises:
            This method will raise an AsyncProcessError or
            AsyncProcessTermination
        """
        for process in process_list:
            # Extent the lock for each process by max processing time * 2
            if self.target_mapset_lock_set is True:
                ret = self.lock_interface.extend(
                    resource_id=self.target_mapset_lock_id,
                    expiration=self.process_time_limit * 2,
                )
                if ret == 0:
                    raise AsyncProcessError(
                        "Unable to extend lock for mapset <%s>"
                        % self.target_mapset_name
                    )

            if self.temp_mapset_lock_set is True:
                # Extent the lock for each process by max processing time * 2
                ret = self.lock_interface.extend(
                    resource_id=self.temp_mapset_lock_id,
                    expiration=self.process_time_limit * 2,
                )
                if ret == 0:
                    raise AsyncProcessError(
                        "Unable to extend lock for "
                        "temporary mapset <%s>" % self.temp_mapset_name
                    )

            if process.exec_type == "grass":
                self._run_module(process)
            elif process.exec_type == "exec":
                self._run_process(process)
            elif process.exec_type == "python":
                eval(process.executable)

    def _execute(self, skip_permission_check=False):
        """Overwrite this function in subclasses

        - Call self._setup()
        - Analyse the process chain
        - Check the target mapset and lock it for the maximum time
          a user can consume -> process_num_limit*process_time_limit
        - Initialize and create the temporal database and mapset
          or use the original mapset
        - Run the modules and extend the lock each run
        - Copy the mapset if it has not already exist
        - Cleanup and unlock the mapset

        """

        # Setup the user credentials and logger
        self._setup()
        # check if this is a job resumption
        if self.rdc.iteration is not None:
            # Create the process chain
            (
                pc_step,
                old_process_chain_list,
            ) = self._get_previous_iteration_process_chain()
            self.interim_result.set_old_pc_step(pc_step)
            process_list = self._validate_process_chain(
                process_chain=self.request_data,
                old_process_chain=old_process_chain_list,
                pc_step=pc_step,
            )
            # check iterim results
            (
                interim_result_mapset,
                interim_result_file_path,
            ) = self.interim_result.check_interim_result_mapset(
                pc_step, self.rdc.iteration - 1
            )
        else:
            # Create the process chain
            process_list = self._validate_process_chain()
            interim_result_mapset = None
            interim_result_file_path = None

        # Check and lock the target and temp mapsets
        self._check_lock_target_mapset()

        if self.target_mapset_exists is False:
            # Create the temp database and link the
            # required mapsets into it
            self._create_temp_database(self.required_mapsets)

            # Initialize the GRASS environment and switch into PERMANENT
            # mapset, which is always linked
            self._create_grass_environment(
                grass_data_base=self.temp_grass_data_base,
                mapset_name="PERMANENT",
            )

            # Create the temporary mapset with the same name as the target
            # mapset and switch into it
            self._create_temporary_mapset(
                temp_mapset_name=self.target_mapset_name,
                interim_result_mapset=interim_result_mapset,
                interim_result_file_path=interim_result_file_path,
            )
            self.temp_mapset_name = self.target_mapset_name
        else:
            # Init GRASS environment and create the temporary mapset
            self._create_temporary_grass_environment(
                source_mapset_name=self.target_mapset_name
            )
            self._lock_temp_mapset()

        # Execute the process list
        self._execute_process_list(process_list)
        # Copy local mapset to original project, merge mapsets
        # if necessary
        self._copy_merge_tmp_mapset_to_target_mapset()
        # Parse the module sdtout outputs and create the results
        self._parse_module_outputs()

    def _final_cleanup(self):
        """
        Final cleanup called in the run function at the very end of processing
        """
        # Clean up and remove the temporary gisdbase
        self._cleanup()
        # Unlock the mapsets
        if self.target_mapset_lock_set is True:
            self.lock_interface.unlock(self.target_mapset_lock_id)
        if self.temp_mapset_lock_set is True:
            self.lock_interface.unlock(self.temp_mapset_lock_id)
