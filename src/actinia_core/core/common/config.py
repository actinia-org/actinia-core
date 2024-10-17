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
Global configuration
"""

import ast
import configparser
import csv
import os
from json import load as json_load

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

if os.environ.get("DEFAULT_CONFIG_PATH"):
    DEFAULT_CONFIG_PATH = os.environ["DEFAULT_CONFIG_PATH"]
else:
    DEFAULT_CONFIG_PATH = "/etc/default/actinia"
if not os.path.isfile(DEFAULT_CONFIG_PATH):
    open(DEFAULT_CONFIG_PATH, "a").close()

allow_list = [
    "d.legend",
    "d.rast",
    "d.rast.multi",
    "d.vect",
    "exporter",
    "g.findfile",
    "g.gisenv",
    "g.list",
    "g.mapset",
    "g.proj",
    "g.region",
    "g.remove",
    "g.rename",
    "g.version",
    "i.atcorr",
    "i.cluster",
    "i.colors.enhance",
    "i.gensig",
    "i.group",
    "i.landsat.toar",
    "i.maxlik",
    "i.pansharpen",
    "i.segment",
    "i.tasscap",
    "i.vi",
    "importer",
    "r.blend",
    "r.buffer",
    "r.buffer.lowmem",
    "r.carve",
    "r.category",
    "r.circle",
    "r.clump",
    "r.coin",
    "r.colors",
    "r.colors.out",
    "r.composite",
    "r.compress",
    "r.contour",
    "r.cost",
    "r.covar",
    "r.cross",
    "r.describe",
    "r.distance",
    "r.drain",
    "r.fill.dir",
    "r.fillnulls",
    "r.flow",
    "r.grow",
    "r.grow.distance",
    "r.gwflow",
    "r.his",
    "r.horizon",
    "r.info",
    "r.kappa",
    "r.lake",
    "r.latlong",
    "r.li.cwed",
    "r.li.dominance",
    "r.li.edgedensity",
    "r.li.mpa",
    "r.li.mps",
    "r.li.padcv",
    "r.li.padrange",
    "r.li.padsd",
    "r.li.patchdensity",
    "r.li.patchnum",
    "r.li.pielou",
    "r.li.renyi",
    "r.li.richness",
    "r.li.shannon",
    "r.li.shape",
    "r.li.simpson",
    "r.mapcalc",
    "r.mask",
    "r.mfilter",
    "r.mode",
    "r.neighbors",
    "r.null",
    "r.out.png",
    "r.param.scale",
    "r.patch",
    "r.plane",
    "r.profile",
    "r.proj",
    "r.quant",
    "r.quantile",
    "r.random",
    "r.random.cells",
    "r.random.surface",
    "r.reclass",
    "r.reclass.area",
    "r.recode",
    "r.region",
    "r.regression.line",
    "r.regression.multi",
    "r.regression.series",
    "r.relief",
    "r.report",
    "r.resamp.bspline",
    "r.resamp.filter",
    "r.resamp.interp",
    "r.resamp.rst",
    "r.resamp.stats",
    "r.resample",
    "r.rescale",
    "r.rescale.eq",
    "r.rgb",
    "r.ros",
    "r.series",
    "r.series.accumulate",
    "r.series.interp",
    "r.shade",
    "r.sim.sediment",
    "r.sim.water",
    "r.slope.aspect",
    "r.solute.transport",
    "r.spread",
    "r.spreadpath",
    "r.statistics",
    "r.stats",
    "r.stats.quantile",
    "r.stats.zonal",
    "r.stream.extract",
    "r.sun",
    "r.sunhours",
    "r.sunmask",
    "r.support",
    "r.support.stats",
    "r.surf.area",
    "r.surf.contour",
    "r.surf.fractal",
    "r.surf.gauss",
    "r.surf.idw",
    "r.surf.random",
    "r.terraflow",
    "r.texture",
    "r.thin",
    "r.tile",
    "r.tileset",
    "r.timestamp",
    "r.to.rast3",
    "r.to.rast3elev",
    "r.to.vect",
    "r.topidx",
    "r.topmodel",
    "r.transect",
    "r.univar",
    "r.uslek",
    "r.usler",
    "r.viewshed",
    "r.vol.dem",
    "r.volume",
    "r.walk",
    "r.water.outlet",
    "r.watershed",
    "r.what",
    "r.what.color",
    "t.create",
    "t.info",
    "t.list",
    "t.rast.accdetect",
    "t.rast.accumulate",
    "t.rast.aggr_func",
    "t.rast.aggregate",
    "t.rast.aggregate.ds",
    "t.rast.algebra",
    "t.rast.colors",
    "t.rast.extract",
    "t.rast.gapfill",
    "t.rast.list",
    "t.rast.mapcalc",
    "t.rast.sample",
    "t.rast.series",
    "t.rast.univar",
    "t.rast.what",
    "t.register",
    "t.remove",
    "t.unregister",
    "v.buffer",
    "v.clean",
    "v.db.select",
    "v.db.univar",
    "v.db.update",
    "v.dissolve",
    "v.in.ascii",
    "v.overlay",
    "v.patch",
    "v.random",
    "v.rast.stats",
    "v.select",
    "v.what.rast",
    "v.what.strds",
]
# GRASS ADDON: maybe not installed:
# * r.regression.series
# * r.vol.dem
# * d.rast.multi (https://github.com/mundialis/d_rast_multi)
# * t.rast.aggr_func (https://github.com/mundialis/openeo-addons/tree/master/
#           t.rast.udf)
# * t.rast.sample (https://github.com/mundialis/t.rast.sample)


class Configuration(object):
    def __init__(self):
        """
        The constructor creates default parameter that can be overwritten with
        a read() call
        """

        home = os.getenv("HOME")

        """GRASS"""
        # The GRASS global database
        # The GRASS database in which the user projects
        # are stored. This is the base path, der user group
        # will be added on runtime
        self.GRASS_DATABASE = "%s/actinia/grassdb" % home
        # The default GRASS project in the global database that
        # is used for project generation
        self.GRASS_USER_DATABASE = "%s/actinia/userdata" % home
        # The directory to store temporary GRASS databases
        self.GRASS_DEFAULT_PROJECT = "nc_spm_08"
        # Directory to store exported resources
        self.GRASS_TMP_DATABASE = "%s/actinia/workspace/temp_db" % home
        self.GRASS_RESOURCE_DIR = "%s/actinia/resources" % home
        # The size quota of the resource storage in Gigibit
        self.GRASS_RESOURCE_QUOTA = 100
        # Installation directory of GRASS
        self.GRASS_GIS_BASE = "/usr/local/grass/"
        self.GRASS_GIS_START_SCRIPT = "/usr/local/bin/grass"
        self.GRASS_ADDON_PATH = "%s/.grass8/addons/" % home
        self.GRASS_MODULES_XML_PATH = os.path.join(
            self.GRASS_GIS_BASE, "gui", "wxpython", "xml", "module_items.xml"
        )
        # The path to the activation script of the python2 venv (old)
        self.GRASS_VENV = (
            "%s/src/actinia/grass_venv/bin/activate_this.py" % home
        )
        # ADDITIONAL_ALLOWED_MODULES: modules to extend MODULE_ALLOW_LIST
        # e.g. ['i.cutlines', 'r.learn.ml2']
        self.ADDITIONAL_ALLOWED_MODULES = []

        """
        LIMITS
        DEFAULT LIMITS when a user is created
        """
        # Maximum number of cells that are allowed to process
        self.MAX_CELL_LIMIT = 1000 * 1000 * 1000
        # Maximum number of seconds an async process is allowed to run
        self.PROCESS_TIME_LIMT = 600
        # Maximum number of processes in a process chain
        self.PROCESS_NUM_LIMIT = 1000
        # The number of queues that process jobs
        self.NUMBER_OF_WORKERS = 3

        """
        API SETTINGS
        """
        # CHECK_CREDENTIALS: If set False all credential checks are disabled
        self.CHECK_CREDENTIALS = True
        # CHECK_LIMITS: If set False all limit checks are disabled
        self.CHECK_LIMITS = True
        # LOG_API_CALL: If set False the API calls are not logged
        self.LOG_API_CALL = True
        # LOGIN_REQUIRED: If set False, login is not required
        self.LOGIN_REQUIRED = True
        # FORCE_HTTPS_URLS: Force the use of https in response urls that
        # point to actinia services like status URL or data storage
        self.FORCE_HTTPS_URLS = False
        # PLUGINS: e.g. ["actinia_satellite_plugin","actinia_statistic_plugin"]
        self.PLUGINS = []
        # ENDPOINTS_CONFIG: configuration csv file for endpoints
        self.ENDPOINTS_CONFIG = None
        # AUTHENTICATION: If set False no authentication is needed
        self.AUTHENTICATION = True

        """
        KEYCLOAK: has only to be set if keycloak server is configured with
        actinia client and actinia attributes for the users
        """
        # Json file generated by keycloak with configuration,
        # e.g. /etc/default/keycloak.json
        self.KEYCLOAK_CONFIG_PATH = None
        # e.g. /actinia-user/
        self.KEYCLOAK_GROUP_PREFIX = None
        # Prefix to distinguish parameters inside keycloak from parameters
        # used by other applications, e.g. actinia
        self.KEYCLOAK_ATTR_PREFIX = None
        # KEYCLOAK parameter read from json configured in KEYCLOAK_CONFIG_PATH
        self.KEYCLOAK_URL = None
        self.KEYCLOAK_CLIENT_ID = None
        self.KEYCLOAK_REALM = None
        self.KEYCLOAK_CLIENT_SECRET_KEY = None

        """
        REDIS
        """
        # The hostname of the redis server
        self.REDIS_SERVER_URL = "127.0.0.1"
        # The port of the redis server
        self.REDIS_SERVER_PORT = 6379
        # The password of the redis server
        self.REDIS_SERVER_PW = None
        # Default expire time is 10 days for resource logs, that are used for
        # calculating the price of resource usage
        self.REDIS_RESOURCE_EXPIRE_TIME = 864000
        # The hostname of the redis work queue server
        self.REDIS_QUEUE_SERVER_URL = "127.0.0.1"
        # The port of the redis work queue server
        self.REDIS_QUEUE_SERVER_PORT = 6379
        # The password of the redis work queue server
        self.REDIS_QUEUE_SERVER_PASSWORD = None
        # This is the time the rq:job will be stored in the redis
        self.REDIS_QUEUE_JOB_TTL = None
        # The base name of the redis worker queue, it will be extended by a
        # numerical suffix that represents the worker id/number database to
        # re-queue it, usually this is not necessary
        self.WORKER_QUEUE_PREFIX = "job_queue"
        # The base name of the redis worker queue logfile, it will be extended
        # by a numerical suffix that represents the worker id/number
        self.WORKER_LOGFILE = "%s/actinia/workspace/tmp/worker.log" % home

        """
        QUEUE
        """
        # The number of queues that process jobs
        self.NUMBER_OF_WORKERS = 3
        # The hostname of the redis work queue server
        self.REDIS_QUEUE_SERVER_URL = "127.0.0.1"
        # The port of the redis work queue server
        self.REDIS_QUEUE_SERVER_PORT = 6379
        # The password of the redis work queue server
        self.REDIS_QUEUE_SERVER_PASSWORD = None
        # This is the time the rq:job will be stored in redis
        self.REDIS_QUEUE_JOB_TTL = None
        # The prefix for the name of the redis worker queue.
        # It will be extended by a numerical suffix that represents
        # the worker id/number database to re-queue it, usually this is not
        # necessary. If QUEUE_TYPE = per_job, it is extended by the
        # resource_id of the job, if QUEUE_TYPE = per_user, it is extended
        # by the user_id
        self.WORKER_QUEUE_PREFIX = "job_queue"
        # Type of queue.
        # "local":  Single queue for all jobs, processed by same actinia
        #           instance via multiprocessing.
        # "redis":  Number of queues is equal to number of workers as set
        #           in config NUMBER_OF_WORKERS, processed by different
        #           actinia instances (actinia worker).
        # "per_job": Separate queue for each job, config for NUMBER_OF_WORKERS
        #           is ignored. Processed by different actinia instance
        #           (actinia worker). Resource_id will be added to above
        #           WORKER_QUEUE_PREFIX.
        # "per_user": Separate queue for each user, config for NUMBER_OF_WORKERS
        #           is ignored. Processed by different actinia instance
        #           (actinia worker). User_id will be added to above
        #           WORKER_QUEUE_PREFIX.
        # future ideas
        # - redis separate queue per process type
        # - redis separate queue per resource consumption
        self.QUEUE_TYPE = "local"
        # Separate configuration for queue_type for synchronous requests which
        # might not want to be queued.
        self.QUEUE_TYPE_OVERWRITE = "local"

        """
        MISC
        """
        # The directory to store temporary files
        self.TMP_WORKDIR = "%s/actinia/workspace/tmp" % home
        self.SECRET_KEY = (
            "This is a very secret key that is used to sign tokens"
        )
        # The directory to cache downloaded data
        self.DOWNLOAD_CACHE = "/tmp/download_cache"
        # The quota of the download cache in Gigabit
        self.DOWNLOAD_CACHE_QUOTA = 100
        # If True the interim results (temporary mapset) are saved
        self.SAVE_INTERIM_RESULTS = False
        self.SAVE_INTERIM_RESULTS_ENDPOINTS_CFG = None
        self.INTERIM_SAVING_ENDPOINTS = {
            "AsyncEphemeralResource".lower(): "AsyncEphemeralResource",
            "AsyncEphemeralExportResource".lower(): "AsyncEphemeralExportResource",
            "AsyncPersistentResource".lower(): "AsyncPersistentResource",
        }
        self.INCLUDE_ADDITIONAL_MAPSET_PATTERN = None

        """
        LOGGING
        """
        # Logging: 1 Error, 2 Warning, 3 Info, 4 Debug
        self.LOG_LEVEL = 1
        # The logging interface to use: "stdout" or "fluentd" (file will
        # always be used)
        self.LOG_INTERFACE = "stdout"
        # The logformat to use for stdout: "colored" or "json"
        self.LOG_STDOUT_FORMAT = "colored"
        # The logformat to use in file: "colored" or "json"
        self.LOG_FILE_FORMAT = "colored"
        # The logformat for the stderr logger: "plain" or "default", default
        # will use STDOUT / FILE format
        self.LOG_STDERR_FORMAT = "plain"
        # The Fluentd host used for fluent logging
        self.LOG_FLUENT_HOST = "127.0.0.1"
        # The Fluentd host used for fluent logging
        self.LOG_FLUENT_PORT = 24224

        """
        MANAGEMENT
        """
        # If authentication is not required, a default user is used
        self.DEFAULT_USER = "user"
        # If authentication is not required, a default group is used
        self.DEFAULT_USER_GROUP = "group"

        # Not in config file
        self.MODULE_ALLOW_LIST = (
            allow_list  # The default allow list of GRASS modules
        )

        # AWS S3 ADMIN CREDENTIALS
        self.S3_AWS_ACCESS_KEY_ID = ""
        self.S3_AWS_SECRET_ACCESS_KEY = ""
        self.S3_AWS_DEFAULT_REGION = ""
        # The AWS S3 bucket to store user resources
        self.S3_AWS_RESOURCE_BUCKET = ""

        # GOOGLE CLOUD STORAGE (GCS) CREDENTIALS
        # This file stores the Google Cloud Storage credentials
        self.GOOGLE_APPLICATION_CREDENTIALS = "/etc/GCS_credentials.json"
        # The google project
        self.GOOGLE_CLOUD_PROJECT = ""
        # The Google Cloud Storage bucket to store user resources
        self.GCS_RESOURCE_BUCKET = ""

        """
        WEBHOOK
        """
        # Webhook finished retry
        self.WEBHOOK_RETRIES = 6
        self.WEBHOOK_SLEEP = 10

    def __str__(self):
        string = ""
        for entry in dir(self):
            if "__" not in entry and entry in self.__dict__:
                string += "%s=%s\n" % (entry, str(self.__dict__[entry]))

        return string

    def read_keycloak_config(self, key_cloak_config_path=None):
        """Read keycloak configuration json"""
        if key_cloak_config_path is None:
            key_cloak_config_path = self.KEYCLOAK_CONFIG_PATH
        if os.path.isfile(key_cloak_config_path):
            with open(key_cloak_config_path) as f:
                keycloak_cfg = json_load(f)
                self.KEYCLOAK_URL = keycloak_cfg["auth-server-url"]
                self.KEYCLOAK_REALM = keycloak_cfg["realm"]
                self.KEYCLOAK_CLIENT_ID = keycloak_cfg["resource"]
                self.KEYCLOAK_CLIENT_SECRET_KEY = keycloak_cfg["credentials"][
                    "secret"
                ]
        else:
            raise Exception(
                "KEYCLOAK_CONFIG_PATH is not a valid keycloak configuration "
                "for actinia"
            )

    def write(self, path=DEFAULT_CONFIG_PATH):
        """Save the configuration into a file

        Args:
            path (str): The path to the configuration file

        Raises:
            IOError: If unable to write config file

        """
        config = configparser.ConfigParser()

        config.add_section("GRASS")

        config.set("GRASS", "GRASS_DATABASE", self.GRASS_DATABASE)
        config.set("GRASS", "GRASS_USER_DATABASE", self.GRASS_USER_DATABASE)
        config.set(
            "GRASS", "GRASS_DEFAULT_PROJECT", self.GRASS_DEFAULT_PROJECT
        )
        config.set("GRASS", "GRASS_TMP_DATABASE", self.GRASS_TMP_DATABASE)
        config.set("GRASS", "GRASS_RESOURCE_DIR", self.GRASS_RESOURCE_DIR)
        config.set(
            "GRASS", "GRASS_RESOURCE_QUOTA", str(self.GRASS_RESOURCE_QUOTA)
        )
        config.set("GRASS", "GRASS_GIS_BASE", self.GRASS_GIS_BASE)
        config.set(
            "GRASS", "GRASS_GIS_START_SCRIPT", self.GRASS_GIS_START_SCRIPT
        )
        config.set("GRASS", "GRASS_ADDON_PATH", self.GRASS_ADDON_PATH)
        config.set(
            "GRASS", "GRASS_MODULES_XML_PATH", self.GRASS_MODULES_XML_PATH
        )
        config.set("GRASS", "GRASS_VENV", self.GRASS_VENV)

        config.add_section("LIMITS")
        config.set("LIMITS", "MAX_CELL_LIMIT", str(self.MAX_CELL_LIMIT))
        config.set("LIMITS", "PROCESS_TIME_LIMT", str(self.PROCESS_TIME_LIMT))
        config.set("LIMITS", "PROCESS_NUM_LIMIT", str(self.PROCESS_NUM_LIMIT))

        config.add_section("API")
        config.set("API", "CHECK_CREDENTIALS", str(self.CHECK_CREDENTIALS))
        config.set("API", "CHECK_LIMITS", str(self.CHECK_LIMITS))
        config.set("API", "LOG_API_CALL", str(self.LOG_API_CALL))
        config.set("API", "LOGIN_REQUIRED", str(self.LOGIN_REQUIRED))
        config.set("API", "FORCE_HTTPS_URLS", str(self.FORCE_HTTPS_URLS))
        config.set("API", "PLUGINS", str(self.PLUGINS))
        config.set("API", "ENDPOINTS_CONFIG", str(self.ENDPOINTS_CONFIG))
        config.set("API", "AUTHENTICATION", str(self.AUTHENTICATION))

        config.add_section("KEYCLOAK")
        config.set(
            "KEYCLOAK",
            "KEYCLOAK_CONFIG_PATH",
            str(self.KEYCLOAK_CONFIG_PATH),
        )
        config.set(
            "KEYCLOAK",
            "KEYCLOAK_GROUP_PREFIX",
            str(self.KEYCLOAK_GROUP_PREFIX),
        )
        config.set(
            "KEYCLOAK",
            "KEYCLOAK_ATTR_PREFIX",
            str(self.KEYCLOAK_ATTR_PREFIX),
        )
        config.set(
            "KEYCLOAK",
            "KEYCLOAK_URL",
            str(self.KEYCLOAK_URL),
        )
        config.set(
            "KEYCLOAK",
            "KEYCLOAK_CLIENT_ID",
            str(self.KEYCLOAK_CLIENT_ID),
        )
        config.set(
            "KEYCLOAK",
            "KEYCLOAK_REALM",
            str(self.KEYCLOAK_REALM),
        )
        config.set(
            "KEYCLOAK",
            "KEYCLOAK_CLIENT_SECRET_KEY",
            str(self.KEYCLOAK_CLIENT_SECRET_KEY),
        )

        config.add_section("REDIS")
        config.set("REDIS", "REDIS_SERVER_URL", self.REDIS_SERVER_URL)
        config.set("REDIS", "REDIS_SERVER_PORT", str(self.REDIS_SERVER_PORT))
        config.set("REDIS", "REDIS_SERVER_PW", str(self.REDIS_SERVER_PW))
        config.set(
            "REDIS",
            "REDIS_RESOURCE_EXPIRE_TIME",
            str(self.REDIS_RESOURCE_EXPIRE_TIME),
        )
        config.set("REDIS", "WORKER_LOGFILE", str(self.WORKER_LOGFILE))

        config.add_section("QUEUE")
        config.set("QUEUE", "NUMBER_OF_WORKERS", str(self.NUMBER_OF_WORKERS))
        config.set(
            "QUEUE", "REDIS_QUEUE_SERVER_URL", self.REDIS_QUEUE_SERVER_URL
        )
        config.set(
            "QUEUE",
            "REDIS_QUEUE_SERVER_PORT",
            str(self.REDIS_QUEUE_SERVER_PORT),
        )
        config.set(
            "QUEUE",
            "REDIS_QUEUE_SERVER_PASSWORD",
            str(self.REDIS_QUEUE_SERVER_PASSWORD),
        )
        config.set(
            "QUEUE", "REDIS_QUEUE_JOB_TTL", str(self.REDIS_QUEUE_JOB_TTL)
        )
        config.set(
            "QUEUE", "WORKER_QUEUE_PREFIX", str(self.WORKER_QUEUE_PREFIX)
        )
        config.set("QUEUE", "QUEUE_TYPE", self.QUEUE_TYPE)
        config.set("QUEUE", "QUEUE_TYPE_OVERWRITE", self.QUEUE_TYPE_OVERWRITE)

        config.add_section("MISC")
        config.set("MISC", "DOWNLOAD_CACHE", self.DOWNLOAD_CACHE)
        config.set(
            "MISC", "DOWNLOAD_CACHE_QUOTA", str(self.DOWNLOAD_CACHE_QUOTA)
        )
        config.set("MISC", "TMP_WORKDIR", self.TMP_WORKDIR)
        config.set("MISC", "SECRET_KEY", self.SECRET_KEY)
        config.set(
            "MISC", "SAVE_INTERIM_RESULTS", str(self.SAVE_INTERIM_RESULTS)
        )
        if self.SAVE_INTERIM_RESULTS_ENDPOINTS_CFG:
            config.set(
                "MISC",
                "SAVE_INTERIM_RESULTS_ENDPOINTS_CFG",
                self.SAVE_INTERIM_RESULTS_ENDPOINTS_CFG,
            )
        config.set(
            "MISC",
            "INTERIM_SAVING_ENDPOINTS",
            str(self.INTERIM_SAVING_ENDPOINTS),
        )
        config.set(
            "MISC",
            "INCLUDE_ADDITIONAL_MAPSET_PATTERN",
            str(self.INCLUDE_ADDITIONAL_MAPSET_PATTERN),
        )

        config.add_section("LOGGING")
        config.set("LOGGING", "LOG_INTERFACE", self.LOG_INTERFACE)
        config.set("LOGGING", "LOG_STDOUT_FORMAT", self.LOG_STDOUT_FORMAT)
        config.set("LOGGING", "LOG_FILE_FORMAT", self.LOG_FILE_FORMAT)
        config.set("LOGGING", "LOG_STDERR_FORMAT", self.LOG_STDERR_FORMAT)
        config.set("LOGGING", "LOG_FLUENT_HOST", str(self.LOG_FLUENT_HOST))
        config.set("LOGGING", "LOG_FLUENT_PORT", str(self.LOG_FLUENT_PORT))
        config.set("LOGGING", "LOG_LEVEL", str(self.LOG_LEVEL))

        config.add_section("MANAGEMENT")
        config.set("MANAGEMENT", "DEFAULT_USER", str(self.DEFAULT_USER))
        config.set(
            "MANAGEMENT", "DEFAULT_USER_GROUP", str(self.DEFAULT_USER_GROUP)
        )

        config.add_section("AWS_S3")
        config.set("AWS_S3", "S3_AWS_ACCESS_KEY_ID", self.S3_AWS_ACCESS_KEY_ID)
        config.set(
            "AWS_S3", "S3_AWS_SECRET_ACCESS_KEY", self.S3_AWS_SECRET_ACCESS_KEY
        )
        config.set(
            "AWS_S3", "S3_AWS_DEFAULT_REGION", self.S3_AWS_DEFAULT_REGION
        )
        config.set(
            "AWS_S3", "S3_AWS_RESOURCE_BUCKET", self.S3_AWS_RESOURCE_BUCKET
        )

        config.add_section("GCS")
        config.set(
            "GCS",
            "GOOGLE_APPLICATION_CREDENTIALS",
            self.GOOGLE_APPLICATION_CREDENTIALS,
        )
        config.set("GCS", "GCS_RESOURCE_BUCKET", self.GCS_RESOURCE_BUCKET)
        config.set("GCS", "GOOGLE_CLOUD_PROJECT", self.GOOGLE_CLOUD_PROJECT)

        config.add_section("WEBHOOK")
        config.set("WEBHOOK", "WEBHOOK_RETRIES", str(self.WEBHOOK_RETRIES))
        config.set("WEBHOOK", "WEBHOOK_SLEEP", str(self.WEBHOOK_SLEEP))

        with open(path, "w") as configfile:
            config.write(configfile)

    def read(self, path=DEFAULT_CONFIG_PATH):
        """Read the configuration from a file

        Args:
            path (str): The path to the configuration file

        Raises:
            IOError: If unable to read config file

        """
        config = configparser.ConfigParser()
        with open(path, "r") as configfile:
            config.read_file(configfile)

            if config.has_section("GRASS"):
                if config.has_option("GRASS", "GRASS_DATABASE"):
                    self.GRASS_DATABASE = config.get("GRASS", "GRASS_DATABASE")
                if config.has_option("GRASS", "GRASS_USER_DATABASE"):
                    self.GRASS_USER_DATABASE = config.get(
                        "GRASS", "GRASS_USER_DATABASE"
                    )
                # Deprecated location
                if config.has_option("GRASS", "GRASS_DEFAULT_LOCATION"):
                    self.GRASS_DEFAULT_PROJECT = config.get(
                        "GRASS", "GRASS_DEFAULT_LOCATION"
                    )
                elif config.has_option("GRASS", "GRASS_DEFAULT_PROJECT"):
                    self.GRASS_DEFAULT_PROJECT = config.get(
                        "GRASS", "GRASS_DEFAULT_PROJECT"
                    )
                if config.has_option("GRASS", "GRASS_TMP_DATABASE"):
                    self.GRASS_TMP_DATABASE = config.get(
                        "GRASS", "GRASS_TMP_DATABASE"
                    )
                if config.has_option("GRASS", "GRASS_RESOURCE_DIR"):
                    self.GRASS_RESOURCE_DIR = config.get(
                        "GRASS", "GRASS_RESOURCE_DIR"
                    )
                if config.has_option("GRASS", "GRASS_RESOURCE_QUOTA"):
                    self.GRASS_RESOURCE_QUOTA = config.getint(
                        "GRASS", "GRASS_RESOURCE_QUOTA"
                    )
                if config.has_option("GRASS", "GRASS_GIS_BASE"):
                    self.GRASS_GIS_BASE = config.get("GRASS", "GRASS_GIS_BASE")
                if config.has_option("GRASS", "GRASS_GIS_START_SCRIPT"):
                    self.GRASS_GIS_START_SCRIPT = config.get(
                        "GRASS", "GRASS_GIS_START_SCRIPT"
                    )
                if config.has_option("GRASS", "GRASS_ADDON_PATH"):
                    self.GRASS_ADDON_PATH = config.get(
                        "GRASS", "GRASS_ADDON_PATH"
                    )
                if config.has_option("GRASS", "GRASS_MODULES_XML_PATH"):
                    self.GRASS_MODULES_XML_PATH = config.get(
                        "GRASS", "GRASS_MODULES_XML_PATH"
                    )
                if config.has_option("GRASS", "GRASS_VENV"):
                    self.GRASS_VENV = config.get("GRASS", "GRASS_VENV")
                if config.has_option(
                    "MANAGEMENT", "ADDITIONAL_ALLOWED_MODULES"
                ):
                    self.ADDITIONAL_ALLOWED_MODULES = ast.literal_eval(
                        config.get("MANAGEMENT", "ADDITIONAL_ALLOWED_MODULES")
                    )
                    self.MODULE_ALLOW_LIST.extend(
                        self.ADDITIONAL_ALLOWED_MODULES
                    )
                    self.MODULE_ALLOW_LIST = list(set(self.MODULE_ALLOW_LIST))

            if config.has_section("LIMITS"):
                if config.has_option("LIMITS", "MAX_CELL_LIMIT"):
                    self.MAX_CELL_LIMIT = config.getint(
                        "LIMITS", "MAX_CELL_LIMIT"
                    )
                if config.has_option("LIMITS", "PROCESS_TIME_LIMT"):
                    self.PROCESS_TIME_LIMT = config.getint(
                        "LIMITS", "PROCESS_TIME_LIMT"
                    )
                if config.has_option("LIMITS", "PROCESS_NUM_LIMIT"):
                    self.PROCESS_NUM_LIMIT = config.getint(
                        "LIMITS", "PROCESS_NUM_LIMIT"
                    )

            if config.has_section("API"):
                if config.has_option("API", "CHECK_CREDENTIALS"):
                    self.CHECK_CREDENTIALS = config.getboolean(
                        "API", "CHECK_CREDENTIALS"
                    )
                if config.has_option("API", "CHECK_LIMITS"):
                    self.CHECK_LIMITS = config.getboolean(
                        "API", "CHECK_LIMITS"
                    )
                if config.has_option("API", "LOG_API_CALL"):
                    self.LOG_API_CALL = config.getboolean(
                        "API", "LOG_API_CALL"
                    )
                if config.has_option("API", "LOGIN_REQUIRED"):
                    self.LOGIN_REQUIRED = config.getboolean(
                        "API", "LOGIN_REQUIRED"
                    )
                if config.has_option("API", "FORCE_HTTPS_URLS"):
                    self.FORCE_HTTPS_URLS = config.getboolean(
                        "API", "FORCE_HTTPS_URLS"
                    )
                if config.has_option("API", "PLUGINS"):
                    self.PLUGINS = ast.literal_eval(
                        config.get("API", "PLUGINS")
                    )
                if config.has_option("API", "ENDPOINTS_CONFIG"):
                    self.ENDPOINTS_CONFIG = config.get(
                        "API", "ENDPOINTS_CONFIG"
                    )
                if config.has_option("API", "AUTHENTICATION"):
                    self.AUTHENTICATION = config.getboolean(
                        "API", "AUTHENTICATION"
                    )

            if config.has_section("KEYCLOAK"):
                if config.has_option("KEYCLOAK", "CONFIG_PATH"):
                    keycloak_cfg_path = config.get("KEYCLOAK", "CONFIG_PATH")
                    if os.path.isfile(keycloak_cfg_path):
                        self.KEYCLOAK_CONFIG_PATH = keycloak_cfg_path
                        self.read_keycloak_config()
                    else:
                        print(
                            "Keycloak is configured, but configfile is not "
                            "an existing file! Using Redis for user "
                            "management."
                        )
                if config.has_option("KEYCLOAK", "GROUP_PREFIX"):
                    self.KEYCLOAK_GROUP_PREFIX = config.get(
                        "KEYCLOAK", "GROUP_PREFIX"
                    )
                if config.has_option("KEYCLOAK", "ATTR_PREFIX"):
                    self.KEYCLOAK_ATTR_PREFIX = config.get(
                        "KEYCLOAK", "ATTR_PREFIX"
                    )

            if config.has_section("REDIS"):
                if config.has_option("REDIS", "REDIS_SERVER_URL"):
                    self.REDIS_SERVER_URL = config.get(
                        "REDIS", "REDIS_SERVER_URL"
                    )
                if config.has_option("REDIS", "REDIS_SERVER_PORT"):
                    self.REDIS_SERVER_PORT = config.getint(
                        "REDIS", "REDIS_SERVER_PORT"
                    )
                if config.has_option("REDIS", "REDIS_SERVER_PW"):
                    self.REDIS_SERVER_PW = config.get(
                        "REDIS", "REDIS_SERVER_PW"
                    )
                if config.has_option("REDIS", "REDIS_RESOURCE_EXPIRE_TIME"):
                    self.REDIS_RESOURCE_EXPIRE_TIME = config.getint(
                        "REDIS", "REDIS_RESOURCE_EXPIRE_TIME"
                    )
                if config.has_option("REDIS", "WORKER_LOGFILE"):
                    self.WORKER_LOGFILE = config.get("REDIS", "WORKER_LOGFILE")

            if config.has_section("QUEUE"):
                if config.has_option("QUEUE", "NUMBER_OF_WORKERS"):
                    self.NUMBER_OF_WORKERS = config.getint(
                        "QUEUE", "NUMBER_OF_WORKERS"
                    )
                if config.has_option("QUEUE", "REDIS_QUEUE_SERVER_URL"):
                    self.REDIS_QUEUE_SERVER_URL = config.get(
                        "QUEUE", "REDIS_QUEUE_SERVER_URL"
                    )
                if config.has_option("QUEUE", "REDIS_QUEUE_SERVER_PORT"):
                    self.REDIS_QUEUE_SERVER_PORT = config.get(
                        "QUEUE", "REDIS_QUEUE_SERVER_PORT"
                    )
                if config.has_option("QUEUE", "REDIS_QUEUE_SERVER_PASSWORD"):
                    self.REDIS_QUEUE_SERVER_PASSWORD = config.get(
                        "QUEUE", "REDIS_QUEUE_SERVER_PASSWORD"
                    )
                if config.has_option("QUEUE", "REDIS_QUEUE_JOB_TTL"):
                    self.REDIS_QUEUE_JOB_TTL = config.get(
                        "QUEUE", "REDIS_QUEUE_JOB_TTL"
                    )
                if config.has_option("QUEUE", "WORKER_QUEUE_PREFIX"):
                    self.WORKER_QUEUE_PREFIX = config.get(
                        "QUEUE", "WORKER_QUEUE_PREFIX"
                    )
                if config.has_option("QUEUE", "QUEUE_TYPE"):
                    self.QUEUE_TYPE = config.get("QUEUE", "QUEUE_TYPE")
                if config.has_option("QUEUE", "QUEUE_TYPE_OVERWRITE"):
                    self.QUEUE_TYPE_OVERWRITE = config.get(
                        "QUEUE", "QUEUE_TYPE_OVERWRITE"
                    )

            if config.has_section("MISC"):
                if config.has_option("MISC", "DOWNLOAD_CACHE"):
                    self.DOWNLOAD_CACHE = config.get("MISC", "DOWNLOAD_CACHE")
                if config.has_option("MISC", "DOWNLOAD_CACHE_QUOTA"):
                    self.DOWNLOAD_CACHE_QUOTA = config.getint(
                        "MISC", "DOWNLOAD_CACHE_QUOTA"
                    )
                if config.has_option("MISC", "TMP_WORKDIR"):
                    self.TMP_WORKDIR = config.get("MISC", "TMP_WORKDIR")
                if config.has_option("MISC", "SECRET_KEY"):
                    self.SECRET_KEY = config.get("MISC", "SECRET_KEY")
                if config.has_option("MISC", "LOG_LEVEL"):
                    self.LOG_LEVEL = config.getint("MISC", "LOG_LEVEL")
                if config.has_option("MISC", "SAVE_INTERIM_RESULTS"):
                    save_interim = config.get("MISC", "SAVE_INTERIM_RESULTS")
                    if save_interim == "True":
                        self.SAVE_INTERIM_RESULTS = True
                    elif save_interim == "False":
                        self.SAVE_INTERIM_RESULTS = False
                    else:
                        self.SAVE_INTERIM_RESULTS = save_interim
                if config.has_option(
                    "MISC", "SAVE_INTERIM_RESULTS_ENDPOINTS_CFG"
                ):
                    cfg = config.get(
                        "MISC", "SAVE_INTERIM_RESULTS_ENDPOINTS_CFG"
                    )
                    if os.path.isfile(cfg):
                        self.SAVE_INTERIM_RESULTS_ENDPOINTS_CFG = cfg
                        with open(cfg, mode="r") as inp:
                            reader = csv.reader(inp, delimiter=";")
                            endpoints_dict = {
                                row[0].lower(): row[1]
                                for row in reader
                                if len(row) == 2
                            }
                            self.INTERIM_SAVING_ENDPOINTS.update(
                                endpoints_dict
                            )
                if config.has_option(
                    "MISC", "INCLUDE_ADDITIONAL_MAPSET_PATTERN"
                ):
                    self.INCLUDE_ADDITIONAL_MAPSET_PATTERN = config.get(
                        "MISC", "INCLUDE_ADDITIONAL_MAPSET_PATTERN"
                    )

            if config.has_section("LOGGING"):
                if config.has_option("LOGGING", "LOG_INTERFACE"):
                    self.LOG_INTERFACE = config.get("LOGGING", "LOG_INTERFACE")
                if config.has_option("LOGGING", "LOG_STDOUT_FORMAT"):
                    self.LOG_STDOUT_FORMAT = config.get(
                        "LOGGING", "LOG_STDOUT_FORMAT"
                    )
                if config.has_option("LOGGING", "LOG_FILE_FORMAT"):
                    self.LOG_FILE_FORMAT = config.get(
                        "LOGGING", "LOG_FILE_FORMAT"
                    )
                if config.has_option("LOGGING", "LOG_STDERR_FORMAT"):
                    self.LOG_STDERR_FORMAT = config.get(
                        "LOGGING", "LOG_STDERR_FORMAT"
                    )
                if config.has_option("LOGGING", "LOG_FLUENT_HOST"):
                    self.LOG_FLUENT_HOST = config.get(
                        "LOGGING", "LOG_FLUENT_HOST"
                    )
                if config.has_option("LOGGING", "LOG_FLUENT_PORT"):
                    self.LOG_FLUENT_PORT = config.getint(
                        "LOGGING", "LOG_FLUENT_PORT"
                    )
                if config.has_option("LOGGING", "LOG_LEVEL"):
                    self.LOG_LEVEL = config.getint("LOGGING", "LOG_LEVEL")

            if config.has_section("MANAGEMENT"):
                if config.has_option("MANAGEMENT", "DEFAULT_USER"):
                    self.DEFAULT_USER = config.get(
                        "MANAGEMENT", "DEFAULT_USER"
                    )
                if config.has_option("MANAGEMENT", "DEFAULT_USER_GROUP"):
                    self.DEFAULT_USER_GROUP = config.get(
                        "MANAGEMENT", "DEFAULT_USER_GROUP"
                    )

            if config.has_section("GCS"):
                if config.has_option("GCS", "GOOGLE_APPLICATION_CREDENTIALS"):
                    self.GOOGLE_APPLICATION_CREDENTIALS = config.get(
                        "GCS", "GOOGLE_APPLICATION_CREDENTIALS"
                    )
                if config.has_option("GCS", "GCS_RESOURCE_BUCKET"):
                    self.GCS_RESOURCE_BUCKET = config.get(
                        "GCS", "GCS_RESOURCE_BUCKET"
                    )
                if config.has_option("GCS", "GOOGLE_CLOUD_PROJECT"):
                    self.GOOGLE_CLOUD_PROJECT = config.get(
                        "GCS", "GOOGLE_CLOUD_PROJECT"
                    )

            if config.has_section("AWS_S3"):
                if config.has_option("AWS_S3", "S3_AWS_ACCESS_KEY_ID"):
                    self.S3_AWS_ACCESS_KEY_ID = config.get(
                        "AWS_S3", "S3_AWS_ACCESS_KEY_ID"
                    )
                if config.has_option("AWS_S3", "S3_AWS_SECRET_ACCESS_KEY"):
                    self.S3_AWS_SECRET_ACCESS_KEY = config.get(
                        "AWS_S3", "S3_AWS_SECRET_ACCESS_KEY"
                    )
                if config.has_option("AWS_S3", "S3_AWS_DEFAULT_REGION"):
                    self.S3_AWS_DEFAULT_REGION = config.get(
                        "AWS_S3", "S3_AWS_DEFAULT_REGION"
                    )
                if config.has_option("AWS_S3", "S3_AWS_RESOURCE_BUCKET"):
                    self.S3_AWS_RESOURCE_BUCKET = config.get(
                        "AWS_S3", "S3_AWS_RESOURCE_BUCKET"
                    )

            if config.has_section("WEBHOOK"):
                if config.has_option("WEBHOOK", "WEBHOOK_RETRIES"):
                    self.WEBHOOK_RETRIES = config.get(
                        "WEBHOOK", "WEBHOOK_RETRIES"
                    )
                if config.has_option("WEBHOOK", "WEBHOOK_SLEEP"):
                    self.WEBHOOK_SLEEP = config.get("WEBHOOK", "WEBHOOK_SLEEP")

        def print_warning(cfg_section, cfg_key, file_val=None, env_val=None):
            if env_val is None:
                env_val = os.environ[cfg_key]
            if config.has_option(cfg_section, cfg_key):
                if file_val is None:
                    file_val = config.get(cfg_section, cfg_key)
                print(
                    "Config for %s from config file with value '%s' will be"
                    " overwritten by environment variable with value '%s'."
                    % (cfg_key, file_val, env_val)
                )

        # Overwrite values with environment variables if exist:
        if os.environ.get("REDIS_SERVER_URL"):
            print_warning("REDIS", "REDIS_SERVER_URL")
            self.REDIS_SERVER_URL = os.environ["REDIS_SERVER_URL"]

        if os.environ.get("REDIS_SERVER_PORT"):
            print_warning("REDIS", "REDIS_SERVER_PORT")
            self.REDIS_SERVER_PORT = os.environ["REDIS_SERVER_PORT"]

        if os.environ.get("REDIS_SERVER_PW"):
            print_warning("REDIS", "REDIS_SERVER_PW", "XXX", "XXX")
            self.REDIS_SERVER_PW = os.environ["REDIS_SERVER_PW"]

        if os.environ.get("REDIS_QUEUE_SERVER_URL"):
            print_warning("QUEUE", "REDIS_QUEUE_SERVER_URL")
            self.REDIS_QUEUE_SERVER_URL = os.environ["REDIS_QUEUE_SERVER_URL"]

        if os.environ.get("REDIS_QUEUE_SERVER_PORT"):
            print_warning("QUEUE", "REDIS_QUEUE_SERVER_PORT")
            self.REDIS_QUEUE_SERVER_PORT = os.environ[
                "REDIS_QUEUE_SERVER_PORT"
            ]

        if os.environ.get("REDIS_QUEUE_SERVER_PW"):
            print_warning("QUEUE", "REDIS_QUEUE_SERVER_PASSWORD", "XXX", "XXX")
            self.REDIS_QUEUE_SERVER_PASSWORD = os.environ[
                "REDIS_QUEUE_SERVER_PW"
            ]


global_config = Configuration()
