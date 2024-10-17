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
Asynchronous merging of several mapsets into a single one
"""
from actinia_core.processing.actinia_processing.ephemeral.persistent_processing import (
    PersistentProcessing,
)
from actinia_core.core.common.exceptions import (
    AsyncProcessError,
    AsyncProcessTermination,
)

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class PersistentMapsetMerger(PersistentProcessing):
    """Processing of grass modules in a temporary or original mapset.

    This class is designed to run GRASS modules that are specified in a process
    chain in a temporary mapset that later on is copied into the original
    project.

    If the processing should be run in an existing mapset, the original mapset
    will be used for processing.
    """

    def __init__(self, rdc):
        """Constructor

        Args:
            rdc (ResourceDataContainer): The data container that contains all
                                         required variables for processing

        """

        PersistentProcessing.__init__(self, rdc)
        self.lock_ids = (
            {}
        )  # This dict holds the lock ids of all locked mapsets

    def _check_lock_mapset(self, mapset_name):
        """Check if the mapset exists and lock it

        If the mapset is a global mapset and Error will be raised.

        The duration of the lock is process_time_limit * process_num_limit
        and should be extended if needed.

        Only mapsets of the user database are locked.

        Unlock the mapset after the processing finished.
        """
        # check if the resource is accessible
        mapset_exists = self._check_mapset(mapset_name)

        if mapset_exists is False:
            raise AsyncProcessError(
                "Mapset <%s> does not exist and can not be locked."
                % mapset_name
            )

        # Finally lock the mapset for the time that the user can allocate at
        # maximum
        lock_id = "%s/%s/%s" % (
            self.user_group,
            self.project_name,
            mapset_name,
        )
        ret = self.lock_interface.lock(
            resource_id=lock_id,
            expiration=self.process_time_limit * self.process_num_limit,
        )

        if ret == 0:
            raise AsyncProcessError(
                "Unable to lock mapset <%s>, resource is already locked"
                % mapset_name
            )
        self.message_logger.info("Mapset <%s> locked" % mapset_name)

        # if we manage to come here, the lock was correctly set, hence store
        # the lock id for later unlocking
        self.lock_ids[lock_id] = mapset_name

    def _check_lock_source_mapsets(self, source_mapsets):
        """Check and lock the source mapsets from the merging list

        Args:
            source_mapsets: A list of source mapsets that should be checked
                            and locked

        Raises:
            This method will raise an AsyncProcessError

        """
        # Expect a list of mapset names
        if len(source_mapsets) == 0:
            raise AsyncProcessError("Empty source mapset list.")

        # Check and lock the mapsets
        for mapset in source_mapsets:
            self._check_lock_mapset(mapset)

    def _merge_mapsets(self):
        """Merge mapsets in a target mapset

        - Check the target mapset and lock it for the maximum time
          a user can consume -> process_num_limit*process_time_limit
        - Check and lock all source mapsets with the same scheme
        - Copy each source mapset into the target mapset
        - Extend the locks each copy run
        - Cleanup and unlock the mapsets

        """
        # Lock the target mapset
        self._check_lock_mapset(self.target_mapset_name)
        # Lock the source mapsets
        self._check_lock_source_mapsets(self.request_data)

        step = 1
        steps = len(self.request_data)

        mapsets_to_merge = []

        # Copy each mapset into the target
        for lock_id in self.lock_ids:
            # Check for termination requests
            if (
                self.resource_logger.get_termination(
                    self.user_id, self.resource_id
                )
                is True
            ):
                raise AsyncProcessTermination(
                    "Mapset merging was terminated "
                    "by user request at setp %i of %i" % (step, steps)
                )

            mapset_name = self.lock_ids[lock_id]
            mapsets_to_merge.append(mapset_name)

            for lock_id in self.lock_ids:
                # Extent the lock for each process by max processing time * 2
                ret = self.lock_interface.extend(
                    resource_id=lock_id, expiration=self.process_time_limit * 2
                )
                if ret == 0:
                    raise AsyncProcessError(
                        "Unable to extend lock for mapset <%s>" % mapset_name
                    )

            message = (
                "Step %i of %i: Copy content from source "
                "mapset <%s> into target mapset <%s>"
                % (step, steps, mapset_name, self.target_mapset_name)
            )
            self._send_resource_update(message)
            self.message_logger.info(message)

            # Copy the source mapset into the target mapset
            if mapset_name != self.target_mapset_name:
                step += 1
                self._merge_mapset_into_target(
                    mapset_name, self.target_mapset_name
                )

    def _execute(self):
        """The _execute() function that does all the magic.

        Overwrite this function in subclasses.

            - Check the target mapset and lock it for the maximum time
              a user can consume -> process_num_limit*process_time_limit
            - Check and lock all source mapsets with the same scheme
            - Copy each source mapset into the target mapset
            - Extend the locks each copy run
            - Cleanup and unlock the mapsets

        """
        # Setup the user credentials and logger
        self._setup()
        self._merge_mapsets()

    def _final_cleanup(self):
        """
        Final cleanup called in the run function at the very end of processing
        """
        # Clean up and remove the temporary gisdbase
        # Unlock mapsets
        PersistentProcessing._final_cleanup(self)
        # Unlock the mapsets
        for lock_id in self.lock_ids:
            self.lock_interface.unlock(lock_id)
