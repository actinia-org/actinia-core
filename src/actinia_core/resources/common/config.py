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
Global configuration
"""

import os
import configparser
import ast

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"

if os.environ.get('DEFAULT_CONFIG_PATH'):
    DEFAULT_CONFIG_PATH = os.environ['DEFAULT_CONFIG_PATH']
else:
    DEFAULT_CONFIG_PATH = "/etc/default/actinia"

# Generate from GRASS_module_white_list.txt
white_list = [
    'r.blend', 'r.buffer', 'r.buffer.lowmem', 'r.carve', 'r.category', 'r.circle', 'r.clump', 'r.coin', 'r.colors',
    'r.composite', 'r.compress', 'r.contour', 'r.cost', 'r.covar', 'r.cross', 'r.describe', 'r.distance', 'r.drain',
    'r.fill.dir', 'r.fillnulls', 'r.flow', 'r.grow', 'r.grow.distance', 'r.gwflow', 'r.his', 'r.horizon', 'r.kappa',
    'r.lake', 'r.latlong', 'r.li.cwed', 'r.li.dominance', 'r.li.edgedensity', 'r.li.mpa', 'r.li.mps', 'r.li.padcv',
    'r.li.padrange', 'r.li.padsd', 'r.li.patchdensity', 'r.li.patchnum', 'r.li.pielou', 'r.li.renyi', 'r.li.richness',
    'r.li.shannon', 'r.li.shape', 'r.li.simpson', 'r.mapcalc', 'r.mask', 'r.mfilter', 'r.mode', 'r.neighbors', 'r.null',
    'r.param.scale', 'r.patch', 'r.plane', 'r.profile', 'r.proj', 'r.quant', 'r.quantile', 'r.random', 'r.random.cells',
    'r.random.surface', 'r.reclass', 'r.reclass.area', 'r.recode', 'r.region', 'r.regression.line',
    'r.regression.multi', 'r.regression.series', 'r.relief', 'r.report', 'r.resamp.bspline', 'r.resamp.filter',
    'r.resamp.interp', 'r.resample', 'r.resamp.rst', 'r.resamp.stats', 'r.rescale', 'r.rescale.eq', 'r.rgb', 'r.ros',
    'r.series', 'r.series.accumulate', 'r.series.interp', 'r.shade', 'r.sim.sediment', 'r.sim.water', 'r.slope.aspect',
    'r.solute.transport', 'r.spread', 'r.spreadpath', 'r.statistics', 'r.stats', 'r.stats.quantile', 'r.stats.zonal',
    'r.stream.extract', 'r.sun', 'r.sunhours', 'r.sunmask', 'r.support', 'r.support.stats', 'r.surf.area',
    'r.surf.contour', 'r.surf.fractal', 'r.surf.gauss', 'r.surf.idw', 'r.surf.random', 'r.terraflow', 'r.texture',
    'r.thin', 'r.tile', 'r.tileset', 'r.timestamp', 'r.topidx', 'r.topmodel', 'r.to.rast3', 'r.to.rast3elev',
    'r.to.vect', 'r.transect', 'r.univar', 'r.uslek', 'r.usler', 'r.viewshed', 'r.vol.dem',
    'r.volume', 'r.walk', 'r.water.outlet', 'r.watershed', 'r.what', 'r.what.color', 'r.info',
    'g.region', 'g.mapset', 'g.proj', 'g.remove', 'g.rename', 'g.version', 'g.list', 'g.findfile', 'g.gisenv', 'i.vi',
    'v.in.ascii', 't.rast.sample', 'r.out.png', 'r.colors.out', 'd.rast', 'd.vect', 'd.legend', 't.rast.aggr_func',
    'd.rast.multi', 'v.buffer', 't.rast.extract', 't.rast.mapcalc', 't.rast.series', 't.rast.colors', 't.info',
    't.rast.list', 't.rast.univar', 'importer', 'exporter']


class Configuration(object):

    def __init__(self):
        """
        The constructor creates default parameter that can be overwritten with a read() call
        """

        home = os.getenv("HOME")

        # GRASS
        self.GRASS_DATABASE = "%s/actinia/grassdb" % home  # The GRASS global database
        self.GRASS_USER_DATABASE = "%s/actinia/userdata" % home  # The GRASS database in which the user locations
        #                                                          are stored. This is the base path, der user group
        #                                                          will be added on runtime
        self.GRASS_DEFAULT_LOCATION = "nc_spm_08"  # The default GRASS location in the global database that
        #                                            is used for location generation
        self.GRASS_TMP_DATABASE = "%s/actinia/workspace/temp_db" % home  # The directory to store temporary GRASS databases
        self.GRASS_RESOURCE_DIR = "%s/actinia/resources" % home  # Directory to store exported resources
        self.GRASS_RESOURCE_QUOTA = 100  # The size quota of the resource storage in Gigibit
        self.GRASS_GIS_BASE = "/usr/local/grass78/"  # Installation directory of GRASS
        self.GRASS_GIS_START_SCRIPT = "/usr/local/bin/grass78"
        self.GRASS_ADDON_PATH = "%s/.grass7/addons/" % home
        self.GRASS_MODULES_XML_PATH = os.path.join(self.GRASS_GIS_BASE, "gui", "wxpython", "xml", "module_items.xml")
        self.GRASS_VENV = "%s/src/actinia/grass_venv/bin/activate_this.py" % home  # The path to the activation
        #                                                                          script of the python2 venv (old)

        # DEFAULT LIMITS when a user is created
        self.MAX_CELL_LIMIT = 1000 * 1000 * 1000  # Maximum number of cells that are allowed to process
        self.PROCESS_TIME_LIMT = 600   # Maximum number of seconds an async process is
        #                                allowed to run
        self.PROCESS_NUM_LIMIT = 1000  # Maximum number of processes in a process chain
        self.NUMBER_OF_WORKERS = 3     # The number of queues that process jobs

        # API SETTINGS
        self.CHECK_CREDENTIALS = True  # If set False all credential checks are disabled
        self.CHECK_LIMITS = True       # If set False all limit checks are disabled
        self.LOG_API_CALL = True       # If set False the API calls are not logged
        self.LOGIN_REQUIRED = True     # If set False, login is not required
        self.FORCE_HTTPS_URLS = False  # Force the use of https in response urls that
        #                                point to actinia services like status URL or data storage
        self.PLUGINS = [] # ["actinia_satellite_plugin", "actinia_statistic_plugin"]

        # REDIS
        self.REDIS_SERVER_URL = "127.0.0.1"       # The hostname of the redis server
        self.REDIS_SERVER_PORT = 6379             # The port of the redis server
        self.REDIS_SERVER_PW = None             # The password of the redis server
        self.REDIS_RESOURCE_EXPIRE_TIME = 864000  # Default expire time is 10 days for resource logs,
        #                                           that are used for calculating the price of resource usage
        self.REDIS_QUEUE_SERVER_URL = "127.0.0.1" # The hostname of the redis work queue server
        self.REDIS_QUEUE_SERVER_PORT = 6379   # The port of the redis work queue server
        self.REDIS_QUEUE_JOB_TTL = 0          # This is the time the rq:job will be stored in the redis
        self.WORKER_QUEUE_NAME = "job_queue"  # The base name of the redis worker queue,
        #                                       it will be extended by a numerical suffix
        #                                       that represents the worker id/number
        #                                       database to re-queue it, usually this is not necessary
        self.WORKER_LOGFILE = "%s/actinia/workspace/tmp/worker" % home  # The base name of the redis worker queue logfile,
        #                                                                 it will be extended by a numerical suffix
        #                                                                 that represents the worker id/number
        # MISC
        self.TMP_WORKDIR = "%s/actinia/workspace/tmp" % home  # The directory to store temporary files
        self.SECRET_KEY = "This is a very secret key that is used to sign tokens"
        self.DOWNLOAD_CACHE = "/tmp/download_cache"  # The directory to cache downloaded data
        self.DOWNLOAD_CACHE_QUOTA = 100  # The quota of the download cache in Gigibit

        # Logging
        self.LOG_LEVEL = 1                  # 1 Error, 2 Warning, 3 Info, 4 Debug
        self.LOG_INTERFACE = "fluentd"      # The logging interface to use: "stderr" or "fluentd"
        self.LOG_FLUENT_HOST = "127.0.0.1"  # The Fluentd host used for fluent logging
        self.LOG_FLUENT_PORT = 24224        # The Fluentd host used for fluent logging

        self.DEFAULT_USER = "user"         # If authentication is not required, a default user is used
        self.DEFAULT_USER_GROUP = "group"  # If authentication is not required, a default group is used

        # Not in config file
        self.MODULE_WHITE_LIST = white_list  # The default white list of GRASS modules

        # AWS S3 ADMIN CREDENTIALS
        self.S3_AWS_ACCESS_KEY_ID = ""
        self.S3_AWS_SECRET_ACCESS_KEY = ""
        self.S3_AWS_DEFAULT_REGION = ''
        self.S3_AWS_RESOURCE_BUCKET = ""  # The AWS S3 bucket to store user resources

        # GOOGLE CLOUD STORAGE (GCS) CREDENTIALS
        self.GOOGLE_APPLICATION_CREDENTIALS = "/etc/GCS_credentials.json"  # This file stores the Google
        #                                                                    Cloud Storage credentials
        self.GOOGLE_CLOUD_PROJECT = ""  # The google project
        self.GCS_RESOURCE_BUCKET = ""   # The Google Cloud Storage bucket to store user resources

    def __str__(self):
        string = ""
        for entry in dir(self):
            if "__" not in entry and entry in self.__dict__:
                string += "%s=%s\n" % (entry, str(self.__dict__[entry]))

        return string

    def write(self, path=DEFAULT_CONFIG_PATH):
        """Save the configuration into a file

        Args:
            path (str): The path to the configuration file

        Raises:
            IOError: If unable to write config file

        """
        config = configparser.ConfigParser()

        config.add_section('GRASS')

        config.set('GRASS', 'GRASS_DATABASE', self.GRASS_DATABASE)
        config.set('GRASS', 'GRASS_USER_DATABASE', self.GRASS_USER_DATABASE)
        config.set('GRASS', 'GRASS_DEFAULT_LOCATION', self.GRASS_DEFAULT_LOCATION)
        config.set('GRASS', 'GRASS_TMP_DATABASE', self.GRASS_TMP_DATABASE)
        config.set('GRASS', 'GRASS_RESOURCE_DIR', self.GRASS_RESOURCE_DIR)
        config.set('GRASS', 'GRASS_RESOURCE_QUOTA', str(self.GRASS_RESOURCE_QUOTA))
        config.set('GRASS', 'GRASS_GIS_BASE', self.GRASS_GIS_BASE)
        config.set('GRASS', 'GRASS_GIS_START_SCRIPT', self.GRASS_GIS_START_SCRIPT)
        config.set('GRASS', 'GRASS_ADDON_PATH', self.GRASS_ADDON_PATH)
        config.set('GRASS', 'GRASS_MODULES_XML_PATH', self.GRASS_MODULES_XML_PATH)
        config.set('GRASS', 'GRASS_VENV', self.GRASS_VENV)

        config.add_section('LIMITS')
        config.set('LIMITS', 'MAX_CELL_LIMIT', str(self.MAX_CELL_LIMIT))
        config.set('LIMITS', 'PROCESS_TIME_LIMT', str(self.PROCESS_TIME_LIMT))
        config.set('LIMITS', 'PROCESS_NUM_LIMIT', str(self.PROCESS_NUM_LIMIT))
        config.set('LIMITS', 'NUMBER_OF_WORKERS', str(self.NUMBER_OF_WORKERS))

        config.add_section('API')
        config.set('API', 'CHECK_CREDENTIALS', str(self.CHECK_CREDENTIALS))
        config.set('API', 'CHECK_LIMITS', str(self.CHECK_LIMITS))
        config.set('API', 'LOG_API_CALL', str(self.LOG_API_CALL))
        config.set('API', 'LOGIN_REQUIRED', str(self.LOGIN_REQUIRED))
        config.set('API', 'FORCE_HTTPS_URLS', str(self.FORCE_HTTPS_URLS))
        config.set('API', 'PLUGINS', str(self.PLUGINS))

        config.add_section('REDIS')
        config.set('REDIS', 'REDIS_SERVER_URL', self.REDIS_SERVER_URL)
        config.set('REDIS', 'REDIS_SERVER_PORT', str(self.REDIS_SERVER_PORT))
        config.set('REDIS', 'REDIS_SERVER_PW', str(self.REDIS_SERVER_PW))
        config.set('REDIS', 'REDIS_RESOURCE_EXPIRE_TIME', str(self.REDIS_RESOURCE_EXPIRE_TIME))
        config.set('REDIS', 'REDIS_QUEUE_SERVER_URL', self.REDIS_QUEUE_SERVER_URL)
        config.set('REDIS', 'REDIS_QUEUE_SERVER_PORT', str(self.REDIS_QUEUE_SERVER_PORT))
        config.set('REDIS', 'REDIS_QUEUE_JOB_TTL', str(self.REDIS_QUEUE_JOB_TTL))
        config.set('REDIS', 'WORKER_QUEUE_NAME', str(self.WORKER_QUEUE_NAME))
        config.set('REDIS', 'WORKER_LOGFILE', str(self.WORKER_LOGFILE))

        config.add_section('MISC')
        config.set('MISC', 'DOWNLOAD_CACHE', self.DOWNLOAD_CACHE)
        config.set('MISC', 'DOWNLOAD_CACHE_QUOTA', str(self.DOWNLOAD_CACHE_QUOTA))
        config.set('MISC', 'TMP_WORKDIR', self.TMP_WORKDIR)
        config.set('MISC', 'SECRET_KEY', self.SECRET_KEY)

        config.add_section('LOGGING')
        config.set('LOGGING', 'LOG_INTERFACE', self.LOG_INTERFACE)
        config.set('LOGGING', 'LOG_FLUENT_HOST', str(self.LOG_FLUENT_HOST))
        config.set('LOGGING', 'LOG_FLUENT_PORT', str(self.LOG_FLUENT_PORT))
        config.set('LOGGING', 'LOG_LEVEL', str(self.LOG_LEVEL))

        config.add_section('MANAGEMENT')
        config.set('MANAGEMENT', 'DEFAULT_USER', str(self.DEFAULT_USER))
        config.set('MANAGEMENT', 'DEFAULT_USER_GROUP', str(self.DEFAULT_USER_GROUP))

        config.add_section('AWS_S3')
        config.set('AWS_S3', 'S3_AWS_ACCESS_KEY_ID', self.S3_AWS_ACCESS_KEY_ID)
        config.set('AWS_S3', 'S3_AWS_SECRET_ACCESS_KEY', self.S3_AWS_SECRET_ACCESS_KEY)
        config.set('AWS_S3', 'S3_AWS_DEFAULT_REGION', self.S3_AWS_DEFAULT_REGION)
        config.set('AWS_S3', 'S3_AWS_RESOURCE_BUCKET', self.S3_AWS_RESOURCE_BUCKET)

        config.add_section('GCS')
        config.set('GCS', 'GOOGLE_APPLICATION_CREDENTIALS', self.GOOGLE_APPLICATION_CREDENTIALS)
        config.set('GCS', 'GCS_RESOURCE_BUCKET', self.GCS_RESOURCE_BUCKET)
        config.set('GCS', 'GOOGLE_CLOUD_PROJECT', self.GOOGLE_CLOUD_PROJECT)

        with open(path, 'w') as configfile:
            config.write(configfile)

    def read(self, path=DEFAULT_CONFIG_PATH):
        """Read the configuration from a file

        Args:
            path (str): The path to the configuration file

        Raises:
            IOError: If unable to read config file

        """
        config = configparser.ConfigParser()
        with open(path, 'r') as configfile:
            config.read_file(configfile)

            if config.has_section("GRASS"):
                if config.has_option("GRASS", "GRASS_DATABASE"):
                    self.GRASS_DATABASE = config.get("GRASS", "GRASS_DATABASE")
                if config.has_option("GRASS", "GRASS_USER_DATABASE"):
                    self.GRASS_USER_DATABASE = config.get("GRASS", "GRASS_USER_DATABASE")
                if config.has_option("GRASS", "GRASS_DEFAULT_LOCATION"):
                    self.GRASS_DEFAULT_LOCATION = config.get("GRASS", "GRASS_DEFAULT_LOCATION")
                if config.has_option("GRASS", "GRASS_TMP_DATABASE"):
                    self.GRASS_TMP_DATABASE = config.get("GRASS", "GRASS_TMP_DATABASE")
                if config.has_option("GRASS", "GRASS_RESOURCE_DIR"):
                    self.GRASS_RESOURCE_DIR = config.get("GRASS", "GRASS_RESOURCE_DIR")
                if config.has_option("GRASS", "GRASS_RESOURCE_QUOTA"):
                    self.GRASS_RESOURCE_QUOTA = config.getint("GRASS", "GRASS_RESOURCE_QUOTA")
                if config.has_option("GRASS", "GRASS_GIS_BASE"):
                    self.GRASS_GIS_BASE = config.get("GRASS", "GRASS_GIS_BASE")
                if config.has_option("GRASS", "GRASS_GIS_START_SCRIPT"):
                    self.GRASS_GIS_START_SCRIPT = config.get("GRASS", "GRASS_GIS_START_SCRIPT")
                if config.has_option("GRASS", "GRASS_ADDON_PATH"):
                    self.GRASS_ADDON_PATH = config.get("GRASS", "GRASS_ADDON_PATH")
                if config.has_option("GRASS", "GRASS_MODULES_XML_PATH"):
                    self.GRASS_MODULES_XML_PATH = config.get("GRASS", "GRASS_MODULES_XML_PATH")
                if config.has_option("GRASS", "GRASS_VENV"):
                    self.GRASS_VENV = config.get("GRASS", "GRASS_VENV")

            if config.has_section("LIMITS"):
                if config.has_option("LIMITS", "MAX_CELL_LIMIT"):
                    self.MAX_CELL_LIMIT = config.getint("LIMITS", "MAX_CELL_LIMIT")
                if config.has_option("LIMITS", "PROCESS_TIME_LIMT"):
                    self.PROCESS_TIME_LIMT = config.getint("LIMITS", "PROCESS_TIME_LIMT")
                if config.has_option("LIMITS", "PROCESS_NUM_LIMIT"):
                    self.PROCESS_NUM_LIMIT = config.getint("LIMITS", "PROCESS_NUM_LIMIT")
                if config.has_option("LIMITS", "NUMBER_OF_WORKERS"):
                    self.NUMBER_OF_WORKERS = config.getint("LIMITS", "NUMBER_OF_WORKERS")

            if config.has_section("API"):
                if config.has_option("API", "CHECK_CREDENTIALS"):
                    self.CHECK_CREDENTIALS = config.getboolean("API", "CHECK_CREDENTIALS")
                if config.has_option("API", "CHECK_LIMITS"):
                    self.CHECK_LIMITS = config.getboolean("API", "CHECK_LIMITS")
                if config.has_option("API", "LOG_API_CALL"):
                    self.LOG_API_CALL = config.getboolean("API", "LOG_API_CALL")
                if config.has_option("API", "LOGIN_REQUIRED"):
                    self.LOGIN_REQUIRED = config.getboolean("API", "LOGIN_REQUIRED")
                if config.has_option("API", "FORCE_HTTPS_URLS"):
                    self.FORCE_HTTPS_URLS = config.getboolean("API", "FORCE_HTTPS_URLS")
                if config.has_option("API", "PLUGINS"):
                    self.PLUGINS = ast.literal_eval(config.get("API", "PLUGINS"))

            if config.has_section("REDIS"):
                if config.has_option("REDIS", "REDIS_SERVER_URL"):
                    self.REDIS_SERVER_URL = config.get("REDIS", "REDIS_SERVER_URL")
                if config.has_option("REDIS", "REDIS_SERVER_PORT"):
                    self.REDIS_SERVER_PORT = config.getint("REDIS", "REDIS_SERVER_PORT")
                if config.has_option("REDIS", "REDIS_SERVER_PW"):
                    self.REDIS_SERVER_PW = config.get("REDIS", "REDIS_SERVER_PW")
                if config.has_option("REDIS", "REDIS_RESOURCE_EXPIRE_TIME"):
                    self.REDIS_RESOURCE_EXPIRE_TIME = config.getint("REDIS", "REDIS_RESOURCE_EXPIRE_TIME")
                if config.has_option("REDIS", "REDIS_QUEUE_SERVER_URL"):
                    self.REDIS_QUEUE_SERVER_URL = config.get("REDIS", "REDIS_QUEUE_SERVER_URL")
                if config.has_option("REDIS", "REDIS_QUEUE_SERVER_PORT"):
                    self.REDIS_QUEUE_SERVER_PORT = config.get("REDIS", "REDIS_QUEUE_SERVER_PORT")
                if config.has_option("REDIS", "REDIS_QUEUE_JOB_TTL"):
                    self.REDIS_QUEUE_JOB_TTL = config.get("REDIS", "REDIS_QUEUE_JOB_TTL")
                if config.has_option("REDIS", "WORKER_QUEUE_NAME"):
                    self.WORKER_QUEUE_NAME = config.get("REDIS", "WORKER_QUEUE_NAME")
                if config.has_option("REDIS", "WORKER_LOGFILE"):
                    self.WORKER_LOGFILE = config.get("REDIS", "WORKER_LOGFILE")

            if config.has_section("MISC"):
                if config.has_option("MISC", "DOWNLOAD_CACHE"):
                    self.DOWNLOAD_CACHE = config.get("MISC", "DOWNLOAD_CACHE")
                if config.has_option("MISC", "DOWNLOAD_CACHE_QUOTA"):
                    self.DOWNLOAD_CACHE_QUOTA = config.getint("MISC", "DOWNLOAD_CACHE_QUOTA")
                if config.has_option("MISC", "TMP_WORKDIR"):
                    self.TMP_WORKDIR = config.get("MISC", "TMP_WORKDIR")
                if config.has_option("MISC", "SECRET_KEY"):
                    self.SECRET_KEY = config.get("MISC", "SECRET_KEY")
                if config.has_option("MISC", "LOG_LEVEL"):
                    self.LOG_LEVEL = config.getint("MISC", "LOG_LEVEL")

            if config.has_section("LOGGING"):
                if config.has_option("LOGGING", "LOG_INTERFACE"):
                    self.LOG_INTERFACE = config.get("LOGGING", "LOG_INTERFACE")
                if config.has_option("LOGGING", "LOG_FLUENT_HOST"):
                    self.LOG_FLUENT_HOST = config.get("LOGGING", "LOG_FLUENT_HOST")
                if config.has_option("LOGGING", "LOG_FLUENT_PORT"):
                    self.LOG_FLUENT_PORT = config.getint("LOGGING", "LOG_FLUENT_PORT")
                if config.has_option("LOGGING", "LOG_LEVEL"):
                    self.LOG_LEVEL = config.getint("LOGGING", "LOG_LEVEL")

            if config.has_section("MANAGEMENT"):
                if config.has_option("MANAGEMENT", "DEFAULT_USER"):
                    self.DEFAULT_USER = config.get("MANAGEMENT", "DEFAULT_USER")
                if config.has_option("MANAGEMENT", "DEFAULT_USER_GROUP"):
                    self.DEFAULT_USER_GROUP = config.get("MANAGEMENT", "DEFAULT_USER_GROUP")

            if config.has_section("GCS"):
                if config.has_option("GCS", "GOOGLE_APPLICATION_CREDENTIALS"):
                    self.GOOGLE_APPLICATION_CREDENTIALS = config.get("GCS", "GOOGLE_APPLICATION_CREDENTIALS")
                if config.has_option("GCS", "GCS_RESOURCE_BUCKET"):
                    self.GCS_RESOURCE_BUCKET = config.get("GCS", "GCS_RESOURCE_BUCKET")
                if config.has_option("GCS", "GOOGLE_CLOUD_PROJECT"):
                    self.GOOGLE_CLOUD_PROJECT = config.get("GCS", "GOOGLE_CLOUD_PROJECT")

            if config.has_section("AWS_S3"):
                if config.has_option("AWS_S3", "S3_AWS_ACCESS_KEY_ID"):
                    self.S3_AWS_ACCESS_KEY_ID = config.get("AWS_S3", "S3_AWS_ACCESS_KEY_ID")
                if config.has_option("AWS_S3", "S3_AWS_SECRET_ACCESS_KEY"):
                    self.S3_AWS_SECRET_ACCESS_KEY = config.get("AWS_S3", "S3_AWS_SECRET_ACCESS_KEY")
                if config.has_option("AWS_S3", "S3_AWS_DEFAULT_REGION"):
                    self.S3_AWS_DEFAULT_REGION = config.get("AWS_S3", "S3_AWS_DEFAULT_REGION")
                if config.has_option("AWS_S3", "S3_AWS_RESOURCE_BUCKET"):
                    self.S3_AWS_RESOURCE_BUCKET = config.get("AWS_S3", "S3_AWS_RESOURCE_BUCKET")


global_config = Configuration()
