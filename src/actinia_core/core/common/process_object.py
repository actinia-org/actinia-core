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
Redis server interface for API logging
"""

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = (
    "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class Process(object):
    """This class specifies a process object that will be executed as part of a
    process chain
    """

    def __init__(
        self,
        exec_type,
        executable,
        executable_params,
        stdin_source=None,
        param_stdin_sources=None,
        skip_permission_check=False,
        id=None,
    ):
        """

        Args:
            exec_type (str): The executable type, can be "grass" or "exec"
            executable (str): The name and path of the executable, eg:
                              g.version
            or /bin/cp executable_params (list): A list of parameters (strings)
            for the executable
            stdin_source (str): The get_stdout or get_stderr method of a
                                Process
            param_stdin_sources (dict): The get_stdout or get_stderr methods of
                                        a process parameter
            skip_permission_check(boolean): Skip permission check for the
                                            module or executable, this is
                                            meaningful for internal process
                                            chain use. Hence the user can use
                                            internal process chains that
                                            contain module he has no
                                            permissions to use.
            id (str): The unique id of the process
        """

        self.exec_type = exec_type
        self.executable = executable
        if isinstance(self.executable, bytes):
            self.executable = self.executable.decode()

        self.executable_params = executable_params
        self.stdin_source = stdin_source
        self.param_stdin_sources = param_stdin_sources
        self.stdout = None
        self.stderr = None
        self.skip_permission_check = skip_permission_check
        self.id = id

    def set_stdouts(self, stdout, stderr):
        """Set the content of stdout and stderr of this process

        Set this after the process has finished.

        Args:
            stdout: The stdout string of this process
            stderr: The stderr string of this process
        """
        self.stdout = stdout
        self.stderr = stderr

    def get_stdout(self):
        return self.stdout

    def get_stderr(self):
        return self.stderr

    def __str__(self):
        return (
            self.exec_type
            + " "
            + self.executable
            + " "
            + str(self.executable_params)
        )
