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
GRASS GIS environment initialization
"""

import os
import os.path
import subprocess
import tempfile
import shutil
import uuid
from .messages_logger import MessageLogger

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert, Anika Weinmann and mundialis GmbH & "
    "Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"


class GrassInitError(Exception):
    """Exception that is thrown in case of a an
    initialization error of the GRASS environment
    """

    def __init__(self, message):
        message = "%s:  %s" % (str(self.__class__.__name__), message)
        Exception.__init__(self, message)
        logger = MessageLogger()
        logger.error(message)


class ProcessLogging:
    """This class initiates the logging mechanism and is the base class for all
    other classes, which have information to be logged.
    """

    def __init__(self, config=None, user_id=None):
        self.logger = MessageLogger(config=config, user_id=user_id)

    def log_debug(self, message):
        """Write an info message into the logfile"""
        if message is not None and message != "":
            self.logger.debug(message)

    def log_info(self, message):
        """Write an info message into the logfile"""
        if message is not None and message != "":
            self.logger.info(message)

    def log_warning(self, message):
        """Write a warning message into the logfile"""
        if message is not None and message != "":
            self.logger.warning(message)

    def log_error(self, message):
        """Write an error message into the logfile"""
        if message is not None and message != "":
            self.logger.error(message)


class GrassEnvironment(ProcessLogging):
    """This class saves and sets grass environment variables"""

    def __init__(self):
        ProcessLogging.__init__(self)
        self.env = {
            "GISBASE": "",
            "GISRC": "",
            "LD_LIBRARY_PATH": "",
            "GRASS_ADDON_PATH": "",
            "GRASS_VERSION": "",
            "PYTHONPATH": "",
            "GRASS_MESSAGE_FORMAT": "plain",
            "GRASS_SKIP_MAPSET_OWNER_CHECK": "1",
            "GRASS_TGIS_RAISE_ON_ERROR": "1",
        }

    def set_grass_environment(
        self, gisrc_path, grass_gis_base, grass_addon_path
    ):
        """Set the grass environment variables

        Args:
            gisrc_path (str): Path to the GISRC file
            grass_gis_base (str): GRASS installation directory
            grass_addon_path (str): The path to GRASS addons

        """
        self.env["GIS_LOCK"] = str(os.getpid())
        self.env["GISBASE"] = grass_gis_base
        self.env["HOME"] = os.getenv("HOME", "/tmp/")
        self.env["GRASS_MESSAGE_FORMAT"] = "plain"
        self.env["GRASS_SKIP_MAPSET_OWNER_CHECK"] = "1"
        self.env["GRASS_TGIS_RAISE_ON_ERROR"] = "1"
        self.env["GISRC"] = os.path.join(gisrc_path, "gisrc")
        self.env["LD_LIBRARY_PATH"] = str(
            os.path.join(self.env["GISBASE"], "lib")
        )
        self.env["GRASS_VERSION"] = "8"
        self.env["GRASS_ADDON_PATH"] = grass_addon_path
        self.env["GRASS_ADDON_BASE"] = grass_addon_path
        if os.name != "posix":
            self.env["PATH"] = str(
                os.path.join(self.env["GISBASE"], "bin")
                + ";"
                + os.path.join(self.env["GISBASE"], "scripts")
                + ";"
                + os.path.join(self.env["GISBASE"], "lib")
                + ";"
                + os.path.join(self.env["GISBASE"], "extralib")
            )
            self.env["PYTHONPATH"] = str(
                self.env["PYTHONPATH"]
                + ";"
                + os.path.join(self.env["GISBASE"], "etc", "python")
            )
        else:
            self.env["PATH"] = str(
                os.path.join(self.env["GISBASE"], "bin")
                + ":"
                + os.path.join(self.env["GISBASE"], "scripts")
            )
            self.env["PYTHONPATH"] = str(
                self.env["PYTHONPATH"]
                + ":"
                + os.path.join(self.env["GISBASE"], "etc", "python")
            )

        self.set()
        self.get()

    def get(self):
        for key in self.env:
            try:
                self.env[key] = os.getenv(key, self.env[key])
            except Exception as e:
                raise GrassInitError(
                    "Error getting grass environmental variables. Exception: "
                    + str(e)
                )

    def set(self):
        for key in self.env:
            value = self.env[key]
            # use self.env and enviroment variable values
            if key in ["PATH", "PYTHONPATH"]:
                origValue = os.getenv(key, None)
                if origValue:
                    value += ":" + origValue
            try:
                os.putenv(key, value)
                os.environ[key] = value
                self.log_debug(key + "=" + value)
            except Exception as e:
                raise GrassInitError(
                    "Error setting grass environmental variables. Exception: "
                    + str(e)
                )


class GrassGisRC(ProcessLogging):
    """This class takes care of the correct creation of the gisrc file

    ATTENTION: Here the TGIS_DISABLE_MAPSET_CHECK variable is set True
    to allow map registering from none-current mapsets
    """

    def __init__(self, gisdbase, project_name, mapset):
        ProcessLogging.__init__(self)
        self.project_name = project_name
        self.mapset = mapset
        self.gisdbase = gisdbase
        self.__gisrc_ile = ""
        self.__tmpDir = ""

    def rewrite_file(self):
        if self.__gisrc_ile != "":
            self.__write()
        else:
            raise GrassInitError("Error re-writing the gisrc file")

    def write(self, gisrc_path):
        if os.path.isdir(gisrc_path):
            try:
                self.__gisrc_ile = os.path.join(gisrc_path, "gisrc")
                self.__write()
            except Exception:
                raise GrassInitError("Error writing the gisrc file")

    def print_gisrc(self):
        try:
            gisrc = open(self.__gisrc_ile, "r")
            self.log_debug(str(gisrc.read()))
            gisrc.close()
        except Exception:
            raise GrassInitError("Error printing the gisrc file")

    def __write(self):
        try:
            gisrc = open(self.__gisrc_ile, "w")
            # TODO with GRASS GIS 9
            gisrc.write("LOCATION_NAME: %s\n" % self.project_name)
            gisrc.write("MAPSET: %s\n" % self.mapset)
            gisrc.write("DIGITIZER: none\n")
            gisrc.write("GISDBASE: %s\n" % self.gisdbase)
            gisrc.write("OVERWRITE: 1\n")
            gisrc.write("DEBUG: 0\n")
            gisrc.write("GRASS_GUI: text")
            gisrc.write("TGIS_DISABLE_MAPSET_CHECK: 1")
            gisrc.close()
            gisrc = open(self.__gisrc_ile, "r")
            self.log_debug(gisrc.read())
            gisrc.close()
        except Exception:
            raise GrassInitError("Error writing the gisrc file")

    def get_filename(self):
        return self.__gisrc_ile


class GrassWindFile(ProcessLogging):
    """This class takes care of the correct creation of grass WIND and
    DEFAULT_WIND files using a dummy region"""

    def __init__(self, gisdbase, project, mapset):
        """

        Args:
            gisdbase (str): The GRASS database
            project (str): The project name
            mapset (str): The name of the mapset

        Raises:
            GrassInitError if unable to write wind file

        """
        ProcessLogging.__init__(self)
        """ Create the WIND and if needed the DEFAULT_WIND file """
        self.__windFile = ""
        self.__windname = "WIND"

        if mapset == "PERMANENT":
            # If PERMANENT is used as mapset, the DEFAULT_WIND file will be
            # created too
            self.__windFile = os.path.join(
                gisdbase, project, mapset, "DEFAULT_WIND"
            )
            self.__write()

        self.__windFile = os.path.join(gisdbase, project, mapset, "WIND")
        self.__write()

        try:
            wind = open(self.__windFile, "w")
            wind.write("""proj:       0\n""")
            wind.write("""zone:       0\n""")
            wind.write("""north:      100\n""")
            wind.write("""south:      0\n""")
            wind.write("""east:       100\n""")
            wind.write("""west:       0\n""")
            wind.write("""cols:       100\n""")
            wind.write("""rows:       100\n""")
            wind.write("""e-w resol:  1\n""")
            wind.write("""n-s resol:  1\n""")
            wind.close()
        except Exception:
            raise GrassInitError("Error writing the WIND file")

    def getFileName(self):
        return self.__windFile


class GrassModuleRunner(ProcessLogging):
    def __init__(self, grassbase, grass_addon_path):
        ProcessLogging.__init__(self)

        self.grassbase = grassbase
        self.grass_addon_path = grass_addon_path

    def _run_process(
        self,
        inputlist,
        raw=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    ):
        """This function runs a process and logs its stdout and stderr output.
        It either returns the subprocess or its error id, stderr and stdout

        Args:
            inputlist (list): The input list for subprocess.Popen(args)
            raw (bool): If True return the subprocess, the caller has to take
                        care of it
            stdout (file): A file object that receives stdout, default
                           subprocess.PIPE
            stderr (file): A file object that receives stderr, default
                           subprocess.PIPE

        Returns:
            subprocess:
            The subprocess or a tuple of (errorid, stdout_buff, stderr_buff)

        """
        try:
            self.log_info("Run process: " + str(inputlist))
            proc = subprocess.Popen(
                args=inputlist, stdout=stdout, stderr=stderr, stdin=stdin
            )
            self.runPID = proc.pid
            self.log_debug("Process pid: " + str(self.runPID))

            if raw is True:
                return proc

            (stdout_buff, stderr_buff) = proc.communicate()
            stdout_buff = stdout_buff.decode()
            stderr_buff = stderr_buff.decode()

            self.log_debug("Return code: " + str(proc.returncode))
            self.log_debug(stderr_buff)
        except Exception:
            raise GrassInitError(
                "Unable to execute process: " + str(inputlist)
            )

        return proc.returncode, stdout_buff, stderr_buff

    def _create_grass_module_path(self, grass_module):
        """
        Create the parameter list and start the grass module. Search for grass
        modules in different grass specific directories

        Args:
            grass_module: The name of the module

        """

        if os.name != "posix":
            grass_module = grass_module + ".exe"

        pathList = []

        # Search the module in the bin directory
        grass_module_path = os.path.join(self.grassbase, "bin", grass_module)
        pathList.append(grass_module_path)
        self.log_debug("Looking for %s" % grass_module_path)

        if os.path.isfile(grass_module_path) is not True:
            grass_module_path = os.path.join(
                self.grassbase, "scripts", grass_module
            )
            pathList.append(grass_module_path)
            self.log_debug("Looking for %s" % grass_module_path)
            # if the module was not found in the bin dir, test the script
            # directory
            if os.path.isfile(grass_module_path) is not True:
                grass_module_path = os.path.join(
                    self.grass_addon_path, "bin", grass_module
                )
                pathList.append(grass_module_path)
                self.log_debug("Looking for %s" % grass_module_path)
                # if the module was not found in the script dir, test the addon
                # path
                if os.path.isfile(grass_module_path) is not True:
                    grass_module_path = os.path.join(
                        self.grass_addon_path, "scripts", grass_module
                    )
                    pathList.append(grass_module_path)
                    self.log_debug("Looking for %s" % grass_module_path)
                    if os.path.isfile(grass_module_path) is not True:
                        raise GrassInitError(
                            "GRASS module "
                            + grass_module
                            + " not found in "
                            + str(pathList)
                        )

        self.log_debug("GRASS module path is " + grass_module_path)

        return grass_module_path

    def run_module(
        self,
        grass_module,
        args,
        raw=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    ):
        """Set all input and output options and start the module

        Raises:
            This method raises a GrassInitError Exception in case
            the GRASS module returns with an error. This happens only
            if raw=False.

        Args:
            grass_module (str): The module name, eg.: "g.region"
            args (list): The module arguments as list e.g.:
                         ["raster=slope", "-a"]
            raw (bool): If True the subprocess that run the module is returned,
                        otherwise a tuple of (errorid, stdout_buff,
                        stderr_buff) is returned
            stdout (file): A file object that receives stdout, default
                           subprocess.PIPE
            stderr (file): A file object that receives stderr, default
                           subprocess.PIPE
            stdin (file): A file object that provides stdin, default
                          subprocess.PIPE

        Returns:
            subprocess:
            Either the subprocess or a tuple of (errorid, stdout_buff,
            stderr_buff)

        """

        parameter = []
        grass_module_path = self._create_grass_module_path(grass_module)
        parameter.append(grass_module_path)
        parameter.extend(args)

        if raw is False:
            errorid, stdout_buff, stderr_buff = self._run_process(parameter)
        else:
            return self._run_process(
                parameter, raw=raw, stdout=stdout, stderr=stderr, stdin=stdin
            )

        if errorid != 0:
            log = (
                "Error while executing the grass module. "
                " \
            "
                "The following error message was logged:\n" + stderr_buff
            )
            raise GrassInitError(log)

        return errorid, stdout_buff, stderr_buff


class GrassInitializer(ProcessLogging):
    def __init__(
        self,
        grass_data_base,
        grass_base_dir,
        project_name,
        mapset_name,
        grass_addon_path="",
        config=None,
        user_id=None,
    ):
        """Initilialze the GRASS environment.

        Use an instance of this class for each independent process that should
        run GRASS modules or script to avoid conflicts. This class will create
        an environment to run GRASS GIS modules and Python scripts.

        Args:
            grass_data_base (str): GRASS GIS database root directory that
                                   contains projects
            grass_base_dir (str): The installation directory of GRASS GIS
            project_name (str): The name of the project to work in
            mapset_name (str): The name of the mapset to work in
            grass_addon_path (str): The path to GRASS GIS addons

        """

        ProcessLogging.__init__(self, config=config, user_id=user_id)

        self.gisrc_path = None
        self.grass_data_base = grass_data_base
        self.grass_base_dir = grass_base_dir
        self.project_name = project_name
        self.mapset_name = mapset_name
        self.grass_addon_path = grass_addon_path
        self.has_temp_region = False

    def initialize(self):
        """
        Initialize the GRASS environment to run GRASS commands
        """

        self.gisrc_path = tempfile.mkdtemp()

        self.mapset_path = os.path.join(
            self.grass_data_base, self.project_name, self.mapset_name
        )

        # Generate a temporary region name
        self.tmp_region_name = "tmp." + str(uuid.uuid1())

        self.genv = GrassEnvironment()
        self.genv.set_grass_environment(
            self.gisrc_path, self.grass_base_dir, self.grass_addon_path
        )

        self.gisrc = GrassGisRC(
            self.grass_data_base, self.project_name, self.mapset_name
        )
        self.gisrc.write(self.gisrc_path)

        self.runner = GrassModuleRunner(
            self.grass_base_dir, self.grass_addon_path
        )

    def run_module(
        self,
        module_name,
        parameter_list,
        raw=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
    ):
        """Run a grass module

        Args:
            module_name (str): The name of the module to run
            parameter_list (list): A list of parameter for the module
            raw (bool): If True the subprocess that run the module is returned,
                        otherwise a tuple of (errorid, stdout_buff,
                        stderr_buff) is returned
            stdout (file): A file object that receives stdout, default
                           subprocess.PIPE
            stderr (file): A file object that receives stderr, default
                           subprocess.PIPE

        Raises:
            This method raises a GrassInitError Exception in case
            the GRASS module returns with an error. This happens only
            if raw=False.

        Returns:
            subprocess:
            Either the subprocess or a tuple of (errorid, stdout_buff,
            stderr_buff)

        """
        return self.runner.run_module(
            module_name,
            parameter_list,
            raw,
            stdout=stdout,
            stderr=stderr,
            stdin=stdin,
        )

    def clean_up(self):
        """Try to remove the temporary gisrc file and the mapset lock"""
        self.delete_tmp_region()
        if self.gisrc_path is not None and os.path.isdir(self.gisrc_path):
            shutil.rmtree(self.gisrc_path)
        else:
            logger = MessageLogger()
            logger.error(
                "Unable to delete temporary grass database <%s>"
                % self.gisrc_path
            )

    def setup_tmp_region(self):
        """Setup a temporary region, so that g.region calls can be performed
        without altering the mapsets current region.

        Make sure to call delete_tmp_region() in the same process after
        processing finished, to make sure that the temporary region was removed
        and the environmental variable was unset.

        Raises:
            This method raises a GrassInitError Exception

        """
        # Safe the current region in a temporary region that can be overwritten
        errorid, _, _ = self.run_module(
            "g.region", ["save=%s" % self.tmp_region_name, "--o"]
        )

        if errorid != 0:
            raise GrassInitError("Unable to create a temporary region")

        # Put the region in the process environment
        os.environ["WIND_OVERRIDE"] = self.tmp_region_name
        self.has_temp_region = True

    def delete_tmp_region(self):
        """Remove the temporary region is exists

        This method will only try to remove a temporary
        region that were created with this object

        """
        if self.has_temp_region is True:
            try:
                if "WIND_OVERRIDE" in os.environ:
                    os.environ.pop("WIND_OVERRIDE")
                    self.run_module(
                        "g.remove",
                        [
                            "name=%s" % self.tmp_region_name,
                            "type=region",
                            "-f",
                        ],
                    )
            except Exception:
                logger = MessageLogger()
                logger.error(
                    "Unable to delete temporary region <%s>"
                    % self.tmp_region_name
                )

            self.has_temp_region = False
