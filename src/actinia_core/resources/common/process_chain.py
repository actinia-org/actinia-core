# -*- coding: utf-8 -*-

import os
from flask_restful_swagger_2 import Schema
from copy import deepcopy
from .process_object import Process
from .exceptions import AsyncProcessError
from .geodata_download_importer import GeoDataDownloadImportSupport
from .config import global_config
from .sentinel_processing_library import Sentinel2Processing
from .landsat_processing_library import LandsatProcessing
from .google_satellite_bigquery_interface import GoogleSatelliteBigQueryInterface

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016, Sören Gebbert"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


SUPPORTED_EXPORT_FORMATS= ['GTiff', "GML", "GeoJSON", "ESRI_Shapefile", "CSV"]

class IOParameterBase(Schema):
    """This is the input parameter of a GRASS GIS module definition
    """
    type = 'object'
    properties = {
        'param': {
            'type': 'string',
            'description': 'The name of a GRASS GIS module parameter'
        },
        'value': {
            'type': 'string',
            'description': 'The value of the GRASS GIS module parameter. '
                           'Raster, vector and STDS inputs must contain the '
                           'mapset name in their id: slope@PERMANENT if '
                           'they are not located in the working mapset. '
                           'Do not contain the mapset name in map names that are '
                           'processed in an ephemeral database, since the mapset names are '
                           'randomly generated on demand. '
                           'Outputs must not contain mapset names.'
                           'Files that are used in the process chain to exchange data '
                           'can be specified using the $file::id identifier. '
                           'The \"id\" will be replaced with a temporary file name, that'
                           'is available in the whole process chain at runtime. The \"id\" '
                           'is the identifier that can be used by different modules in a process '
                           'chain to access the same temporary file.'
        },
    }
    description = 'Input/output parameter definition of a GRASS GIS module that should be executed ' \
                  'in the Actinia Core environment.'
    required = ["param", "value"]
    example = {"param": "file", "value": "$file::ascii_points"}


class InputParameter(IOParameterBase):
    """This is the import definition of a input parameter of a GRASS GIS module definition
    """
    properties = deepcopy(IOParameterBase.properties)
    properties["import_descr"] = {
        'type': 'object',
        'description': 'Definition of sources to be imported as raster or vector map layer.',
        'properties': {
            'type': {
                'type': 'string',
                'description': 'The type of the input that should be downloaded and imported. '
                               'In case of raster or vector types a download URL must be provided '
                               'as source using http, https or ftp protocols. In case of '
                               ' sentinel2 scenes the scene name and the band must be provided. '
                               'The Landsat approach is different. <br><br>'
                               'In case a Landsat scene is requested, all '
                               'bands will be download, in the target location imported and an atmospheric correction '
                               'is applied. The atmospheric correction must be specified. The resulting raster map '
                               'layers have a specific name scheme, that is independent from the provided map name '
                               'in the process description. The name scheme is always: '
                               '<p>\<landsat scene id\>_\<atcor\>.\<band\></p>'
                               'For example, if the scene <p>LT52170762005240COA00</p> was requested, '
                               'the resulting name for'
                               'the DOS1 atmospheric corrected band 1 would be: <p>LT52170762005240COA00_dos1.1</p>.'
                               'For the DOS1 atmospheric corrected band 2 it '
                               'would be: <p>LT52170762005240COA00_dos1.2</p> '
                               'and so on. '
                               'All other process steps must use these raster map layer names to refer to the '
                               'imported Landsat bands. '
                               'Use the file option to download any kind of files that should'
                               'be processed by a grass gis module. ',
                'enum': ['raster', 'vector', 'landsat', 'sentinel2', 'file']
            },
            'sentinel_band': {
                'type': 'string',
                'description': 'The band of the sentinel2 scene that should be imported',
                'enum': ["B01", "B02", "B03", "B04", "B05", "B06", "B07",
                         "B08", "B8A", "B09" "B10", "B11", "B12"]
            },
            'landsat_atcor': {
                'type': 'string',
                'description': 'The atmospheric correction that should be applied to the landsat scene',
                'enum': ["uncorrected", "dos1", "dos2", "dos2b", "dos3", "dos4"]
            },
            'source': {
                'type': 'string',
                'description': 'The input source that may be a landsat scene name, '
                               'a sentinel2 scene name, or an URL that points '
                               'to a online accessable raster or vector file. '
                               'A HTTP, HTTPS or FTP connection must be '
                               'specified in case of raster or vector types. '
                               'In this case the source string must contain the protocol that '
                               'will used for connection: http:// or https:// or ftp://',
            },
            'basic_auth': {
                'type': 'string',
                'description': 'User name and password for basic HTTP, HTTPS and FTP '
                               'authentication of the source connection. The user name '
                               'and password must be separated by a colon: username:password'
            }
        },
        'description': 'Input/output parameter definition of a GRASS GIS module '
                       'that should be executed in the Actinia Core environment.',
        'required': ["source", "type"],
        'example': {"source": "https://storage.googleapis.com/Actinia Core-geodata/geology_30m.zip",
                    "type": "raster", 'basic_auth': 'username:password'}
    }

    required = deepcopy(IOParameterBase.required)
    description = deepcopy(IOParameterBase.description)
    example = {"param": "file", "value": "$file::ascii_points"}


class OutputParameter(IOParameterBase):
    """This is the output parameter of a GRASS GIS module definition
    """
    type = 'object'
    properties = deepcopy(IOParameterBase.properties)
    properties["export"] = {
        'type': 'object',
        'properties': {
            'format': {
                'type': 'string',
                'description': 'The format of the output file in case of raster or vector layer export. '
                               'Raster layer export support only GeoTiff format, all other formats are '
                               'vector layer export formats. ',
                'enum': SUPPORTED_EXPORT_FORMATS
            },
            'type': {
                'type': 'string',
                'description': 'The type of the output',
                'enum': ['raster', 'vector']
            },
        },
        'description': 'Input/output parameter definition of a GRASS GIS module '
                       'that should be executed in the Actinia Core environment.',
        'required': ["format", "type"],
        'example': {"format": "GTiff", "type": "raster"}
    }

    required = deepcopy(IOParameterBase.required)
    description = deepcopy(IOParameterBase.description)
    example = {'param': 'slope',
               'value': 'elev_10m_slope',
               'export': {'type': 'raster',
                          'format': 'GTiff'}}


class GrassModule(Schema):
    """The definition of a GRASS GIS module and its inputs, outputs and flags
    """
    type = 'object'
    properties = {
        "id": {'type': 'string',
               'description': 'A unique id to identify the module call in the process chain '
                              'to reference its stdout and stderr output as stdin in '
                              'other modules.'
               },
        'module': {'type': 'string',
                   'description': 'The name of the GRASS GIS module that should be executed '
                                  'as part of the process chain. '
                                  'Use as module names "importer" or "exportert" to import or export '
                                  'geographical data without calling a GRASS GIS module'
                   },
        'inputs': {'type': 'array',
                   'items': InputParameter,
                   'description': 'A list of input parameters of a GRASS GIS module.'
                   },
        'outputs': {'type': 'array',
                    'items': OutputParameter,
                    'description': 'A list of input parameters of a GRASS GIS module.'
                    },
        'flags': {'type': 'string',
                  'description': 'The flags that should be set for the GRASS GIS module.'},
        'stdin': {'type': 'string',
                  'description': 'Use the output of a GRASS GIS module or executable in of the process '
                                 'chain as input for this module. Refer to the module/executable output '
                                 'as id::stderr or id@stdout, the \"id\" is the unique identifier '
                                 'of a GRASS GIS module.'},
        'overwrite': {'type': 'boolean',
                      'description': 'Set True to overwrite existing data.'},
        'verbose': {'type': 'boolean',
                    'description': 'Set True to activate verbosity output of the module.'},
        'superquiet': {'type': 'boolean',
                       'description': 'Set True to silence the output of the module.'}
    }
    required = ['id', 'module']
    description = 'The definition of a GRASS GIS module and its inputs, outputs and flags. This ' \
                  'module will be run in a location/mapset environment and is part of a process chain. ' \
                  'The stdout and stderr output of modules that were run before this module in the process ' \
                  'chain can be used as stdin for this module.'
    example = {'id': 'r.slope.aspect_run_1',
               'module': 'r.slope.aspect',
               'inputs': [
                   {'param': 'elevation',
                    'value': 'elevation@PERMANENT'},
                   {'param': 'format',
                    'value': 'degrees'},
                   {'param': 'precision',
                    'value': 'DCELL'}
               ],
               'outputs': [
                   {'param': 'slope',
                    'value': 'elevation_slope',
                    'export': {'type': 'raster',
                               'format': 'GeoTIFF'}},
                   {'param': 'aspect',
                    'value': 'elevation_aspect',
                    'export': {'type': 'raster',
                               'format': 'GeoTIFF'}}
               ],
               'flags': 'a',
               'overwrite': False,
               'verbose': False}


class Executable(Schema):
    """The definition of a Linux executable and its parameters
    """
    type = 'object'
    properties = {
        "id": {'type': 'string',
               'description': 'A unique id to identify the executable in the process chain '
                              'to reference its stdout and stderr output as stdin in '
                              'other modules.'
               },
        'exe': {'type': 'string',
                'description': 'The name of the Linux executable that should be executed '
                               'as part of the process chain.'
                },
        'params': {'type': 'array',
                   'items': {'type': 'string'},
                   'description': 'A list of input parameters of a GRASS GIS module.'
                   },
        'stdin': {'type': 'string',
                  'description': 'Use the output of a GRASS GIS module or executable in of the process '
                                 'chain as input for this module. Refer to the module/executable output '
                                 'as id::stderr or id@stdout, the \"id\" is the unique identifier '
                                 'of a GRASS GIS module.'}
    }
    required = ['id', 'exe']
    description = 'The definition of a Linux executable and its parameters. ' \
                  'The stdout and stderr output of modules/executable ' \
                  'that were run before this module in the process ' \
                  'chain can be used as stdin for this module.'
    example = {'id': 'cat_1',
               'exe': '/bin/cat',
               'params': []}


class ProcessChainModel(Schema):
    """Definition of the Actinia Core process chain that includes GRASS GIS modules
    and common Linux commands
    """
    type = 'object'
    properties = {
        'version': {'type': 'string',
                    'default': '1',
                    'description': 'The version string of the process chain'},
        'list': {'type': 'array',
                 'items': GrassModule,
                 'description': "A list of process definitions that should be executed "
                                "in the order provided by the list."}
    }
    required = ['version', 'list']
    example = {'list': [{'module': 'g.region',
                         'id': 'g_region_1',
                         'inputs': [{'import_descr': {'source': 'https://storage.googleapis.com/Actinia Core-geodata/elev_ned_30m.tif',
                                                      'type'  : 'raster'},
                                      'param': 'raster',
                                      'value': 'elev_ned_30m_new'}],
                         'flags': 'p',
                         'overwrite': True,
                         'verbose': True},
                        {'module': 'r.slope.aspect',
                         'id': 'r_slope_aspect_1',
                         'inputs': [{'param': 'elevation',
                                     'value': 'elev_ned_30m_new'},
                                    {'param': 'format',
                                     'value': 'degree'},
                                    {'param': 'precision',
                                     'value': 'DCELL'}],

                         'outputs': [{'export': {'format': 'GTiff',
                                                 'type': 'raster'},
                                      'param': 'slope',
                                      'value': 'elev_ned_30m_new_slope'},
                                     {'export': {'format': 'GTiff',
                                                 'type': 'raster'},
                                      'param': 'aspect',
                                      'value': 'elev_ned_30m_new_aspect'}],
                         'flags': 'a',
                         'overwrite': True,
                         'verbose': True}],
               'version': '1'}


class ProcessChainConverter(object):
    """Convert the process chain description into a process list that can be executed
    """

    def __init__(self, config=None, temp_file_path=None, process_dict=None, temporary_pc_files=None,
                 required_mapsets=None, resource_export_list=None, message_logger=None,
                 send_resource_update=None):
        """Constructor to convert the process chain into a process list

        Args:
            config: The Actinia Core configuration object
            temp_file_path: The path to the temporary directory to store temporary files.
                            It is assumed that this path is available when the generated
                            commands are executed.
            message_logger: The message logger to be used
            process_dict (dict): The dictionary that describes the process chain
            temporary_pc_files (dict): A dictionary of temporary process chain files
                                       that are generated by this class
            required_mapsets (list): A list that will be filled with mapsets names
                                     that must be linked for processing
            resource_export_list (list): A list that will be filled with export definitions found in
                                         output descriptions for geodata export
            send_resource_update: The function to call for resource updates

        Returns:

        """
        if config is None:
            self.config = global_config
        else:
            self.config = config
        if temp_file_path is None:
            self.temp_file_path = "/tmp"
        else:
            self.temp_file_path = temp_file_path
        self.temp_file_count = 0

        if process_dict is None:
            self.process_dict = {}
        else:
            self.process_dict = process_dict
        if temporary_pc_files is None:
            self.temporary_pc_files = {}
        else:
            self.temporary_pc_files = temporary_pc_files
        if required_mapsets is None:
            self.required_mapsets = []
        else:
            self.required_mapsets = required_mapsets
        if resource_export_list is None:
            self.resource_export_list = []
        else:
            self.resource_export_list = resource_export_list

        self.send_resource_update = send_resource_update
        self.message_logger = message_logger
        self.import_descr_list = []


    def process_chain_to_process_list(self, process_chain):

        if not process_chain:
            raise AsyncProcessError("Process chain is empty")

        if "list" in process_chain and "version" in process_chain:
            return self._process_chain_to_process_list(process_chain)
        else:
            return self._process_chain_to_process_list_legacy(process_chain)

    def _process_chain_to_process_list(self, process_chain):
        """Transform the module chain description into an ordered list of process runs

        All input map layer from a specific mapset
        MUST be specified with the mapset they belong to: map@mapset.
        Maps from an ephemeral mapset should not contain a mapset name,
        because the mapset names are temporary and created with random names.

        Args:
            process_chain (dict): The process chain

        Return:
             list
             A list of ordered grass processes

        """
        process_list = []

        if "version" not in process_chain:
            raise AsyncProcessError("Version information is missing "
                                    "in the process chain definition")

        if "list" not in process_chain:
            raise AsyncProcessError("List of processes to be executed is missing "
                                    "in the process chain definition")

        for process_descr in process_chain["list"]:

            if "module" in process_descr:
                module = self._create_module_process(process_descr)
                if module:
                    process_list.append(module)
            elif "exe" in process_descr:
                exe = self._create_exec_process(process_descr)
                if exe:
                    process_list.append(exe)
            elif "evaluate" in process_descr:
                process_list.append(("python", process_descr["evaluate"]))
            else:
                raise AsyncProcessError("Unknown process description "
                                        "in the process chain definition")

        downimp_list = self._create_download_process_list()
        downimp_list.extend(process_list)

        return downimp_list

    def _create_download_process_list(self):

        downimp_list = []

        if self.message_logger: self.message_logger.info("Creating download process "
                                                         "list for all import definitions")

        for entry in self.import_descr_list:
            if self.message_logger: self.message_logger.info(entry)

            if "import_descr" not in entry:
                raise AsyncProcessError("import_descr specification is required in import definition")

            if "type" not in entry["import_descr"]:
                raise AsyncProcessError("Type specification is required in import definition")

            if "source" not in entry["import_descr"]:
                raise AsyncProcessError("Source specification is required in import definition")

            if entry["import_descr"]["type"] not in ["raster", "vector", "sentinel2", "landsat", "file"]:
                raise AsyncProcessError("Unkown type specification: %s"%entry["import_descr"]["type"])

            if entry["import_descr"]["type"].lower() == "raster" or \
               entry["import_descr"]["type"].lower() == "vector" or \
               entry["import_descr"]["type"].lower() == "file":

                url = entry["import_descr"]["source"]

                gdis = GeoDataDownloadImportSupport(config=self.config,
                                                    temp_file_path=self.temp_file_path,
                                                    download_cache=self.temp_file_path,
                                                    message_logger=self.message_logger,
                                                    send_resource_update=self.send_resource_update,
                                                    url_list=[url,])

                download_commands, import_file_info = gdis.get_download_process_list()
                downimp_list.extend(download_commands)

                if entry["import_descr"]["type"] == "raster":
                    import_command = gdis.get_raster_import_command(import_file_info[0][2], entry["value"])
                    downimp_list.append(import_command)
                if entry["import_descr"]["type"] == "vector":
                    import_command = gdis.get_vector_import_command(import_file_info[0][2], entry["value"])
                    downimp_list.append(import_command)
                if entry["import_descr"]["type"] == "file":
                    value = entry["value"]
                    # Search for file identifiers
                    if "$file" in value and "::" in value:
                        file_id = value.split("::")[1]
                        # Use the temporary file name as copy target
                        if file_id in self.temporary_pc_files:
                            rename_commands = gdis.get_file_rename_command(import_file_info[0][2],
                                                                           self.temporary_pc_files[file_id])
                            downimp_list.append(rename_commands)
                        else:
                            raise AsyncProcessError("A file id is required for a download file "
                                                    "to use it in the process chain.")
                    else:
                        raise AsyncProcessError("A file id is required for a download file "
                                                "to use it in the process chain.")

            elif entry["import_descr"]["type"].lower() == "sentinel2":
                # Check for band information
                if "sentinel_band" not in entry["import_descr"]:
                    raise AsyncProcessError("Band specification is required for Sentinel2 scene import")

                scene = entry["import_descr"]["source"]
                band = entry["import_descr"]["sentinel_band"]

                gqi = GoogleSatelliteBigQueryInterface(config=self.config)
                query_result = gqi.get_sentinel_urls(product_ids=[scene,],
                                                     bands=[band,])
                sp = Sentinel2Processing(config=self.config,
                                         bands=[band,],
                                         download_cache=self.temp_file_path,
                                         temp_file_path=self.temp_file_path,
                                         message_logger=self.message_logger,
                                         send_resource_update=self.send_resource_update,
                                         product_id=scene,
                                         query_result=query_result)

                download_commands, import_file_info = sp.get_sentinel2_download_process_list()
                downimp_list.extend(download_commands)
                import_commands = sp.get_sentinel2_import_process_list()
                downimp_list.extend(import_commands)

                input_file, map_name = import_file_info[band]
                p = Process(exec_type="grass", executable="g.rename",
                                 executable_params=["raster=%s,%s"%(map_name, entry["value"]),])
                downimp_list.append(p)

            elif entry["import_descr"]["type"].lower() == "landsat":
                # Check for band information
                if "landsat_atcor" not in entry["import_descr"]:
                    raise AsyncProcessError("Atmospheric detection specification is required for Landsat scene import")

                atcor = entry["import_descr"]["landsat_atcor"].lower()

                if atcor not in ["uncorrected", "dos1", "dos2", "dos2b", "dos3", "dos4"]:
                    raise AsyncProcessError("Atmospheric detection specification is wrong for "
                                            "Landsat scene import.")

                scene = entry["import_descr"]["source"]

                lp = LandsatProcessing(config=self.config,
                                       download_cache=self.temp_file_path,
                                       temp_file_path=self.temp_file_path,
                                       message_logger=self.message_logger,
                                       send_resource_update=self.send_resource_update,
                                       scene_id=scene)

                download_commands, import_file_info = lp.get_download_process_list()
                downimp_list.extend(download_commands)
                import_commands = lp.get_import_process_list()
                downimp_list.extend(import_commands)
                atcor_commands = lp.get_i_landsat_toar_process_list(atcor)
                downimp_list.extend(atcor_commands)
            else:
                raise AsyncProcessError("Unknown import type specification: %s"%entry["import_descr"]["type"])

        return downimp_list

    def generate_temp_file_path(self):
        """Generate the path of a new unique temporary file that will be removed when the processe
        finishes. The _setup() method must be called for correct file generate.

        Returns: The file path to a unique temporary file
        """

        if not self.temp_file_path:
            raise AsyncProcessError("Unable to create temporary file, "
                                    "temp_file_path is not set.")

        self.temp_file_count += 1

        return os.path.join(self.temp_file_path, "temp_file_%i" % self.temp_file_count)

    def _create_module_process(self, module_descr):
        """Analyse a grass process description dict and create a Process
        that is used to execute a GRASS GIS binary.

        Identify the required mapsets from the input definition and stores them in a list.

        Args:
            module_descr (dict): The module description

        Returns: Process:
            An object of type Process that contains the module name,
            the parameter list and stdout/stdin definitions

        """
        if self.message_logger:
            self.message_logger.info(str(module_descr))
        params = []

        if "id" not in module_descr:
            raise AsyncProcessError("The <id> is missing from the process description.")

        id = module_descr["id"]

        stdin_func = None
        if "stdin" in module_descr:
            if "::" not in module_descr["stdin"]:
                raise AsyncProcessError("The stdin option in id %s misses the ::" % str(id))

            object_id, method = module_descr["stdin"].split("::")

            if "stdout" == method is True:
                stdin_func = self.process_dict[object_id].stdout

            elif "stderr" == method is True:
                stdin_func = self.process_dict[object_id].stderr
            else:
                raise AsyncProcessError("The stdout or stderr flag in id %s is missing" % str(id))

        if "module" not in module_descr:
            raise AsyncProcessError("Missing module name in module description of id %s" % str(id))

        module_name = module_descr["module"]

        if "inputs" in module_descr:

            if isinstance(module_descr["inputs"], list) is False:
                raise AsyncProcessError("Inputs in the process chain definition "
                                        "must be of type list")

            for input in module_descr["inputs"]:

                # Add import description to the import ist
                if "import_descr" in input:
                    self.import_descr_list.append(input)

                if "value" not in input:
                    raise AsyncProcessError("<value> is missing in input description of process id: %s"%id)

                if "param" not in input:
                    raise AsyncProcessError(" <param> is missing in input description of process id: %s"%id)

                value = input["value"]
                param = input["param"]

                # Search for file identifiers and generate the temporary file path
                if "$file" in value and "::" in value:
                    file_id = value.split("::")[1]
                    # Generate the temporary file path and store it in the dict
                    if file_id not in self.temporary_pc_files:
                        self.temporary_pc_files[file_id] = self.generate_temp_file_path()

                    param = "%s=%s" % (param, self.temporary_pc_files[file_id])
                else:
                    param = "%s=%s" % (param, value)
                    # Check for mapset in input name and append it
                    # to the list of required mapsets
                    if "@" in str(value):

                        # Mapset names are after an @ symbol
                        # Mapsets in expressions can be detected by replacing the
                        # symbols like *, +, :, /, {, (,},], ... by spaces and split
                        # the string by spaces, searching in each substring for @

                        symbols = ['*', '+', '-', '/', '%', '$', '!', ':', '(', ')',
                                   '{', '}', '&', '?', '#', '=', '^', '~',
                                   '<', '>', '\\']

                        for symbol in symbols:
                            value = value.replace(symbol, " ")

                        values = value.split(" ")

                        for entry in values:
                            for subentry in entry.split(","):
                                if "@" in subentry:
                                    mapset = subentry.split("@")[1]
                                    if mapset not in self.required_mapsets:
                                        self.required_mapsets.append(mapset)

                params.append(param)

        if "outputs" in module_descr:
            for output in module_descr["outputs"]:

                if "value" not in output:
                    raise AsyncProcessError("<value> is missing in input description of process id: %s"%id)

                if "param" not in output:
                    raise AsyncProcessError(" <param> is missing in input description of process id: %s"%id)

                value = output["value"]
                param = output["param"]

                # Search for file identifiers and generate the temporary file path
                if "$file" in value and "::" in value:
                    file_id = value.split("::")[1]
                    # Generate the temporary file path and store it in the dict
                    if file_id not in self.temporary_pc_files:
                        self.temporary_pc_files[file_id] = self.generate_temp_file_path()

                    param = "%s=%s" % (param, self.temporary_pc_files[file_id])
                else:
                    param = "%s=%s" % (param, value)
                params.append(param)

                # List the resource for potential export
                if "export" in output:
                    exp = output["export"]
                    if "format" not in exp or "type" not in exp:
                        raise AsyncProcessError("Invalid export parameter in description of module <%s>" % module_name)
                    if exp["format"] not in SUPPORTED_EXPORT_FORMATS:
                        raise AsyncProcessError(
                                "Invalid export <format> parameter in description of module <%s>" % module_name)
                    if exp["type"] not in ["raster", "vector", "strds", "file", "stvds"]:
                        raise AsyncProcessError(
                                "Invalid export <type> parameter in description of module <%s>" % module_name)
                    self.resource_export_list.append(output)

        if "flags" in module_descr:
            if "flags" in module_descr:
                params.append("-" + str(module_descr["flags"]))

        if "overwrite" in module_descr and module_descr["overwrite"] is True:
            params.append("--o")

        if "superquiet" in module_descr and module_descr["superquiet"] is True:
            params.append("--qq")

        if "verbose" in module_descr and module_descr["verbose"] is True:
            params.append("--v")

        # Check for un-allowed characters in the parameter list
        for entry in params:
            if "&" in entry:
                raise AsyncProcessError("Character '&' not supported in process "
                                        "description for %s" % module_name)

        if module_name != "importer" and module_name != "exporter":
            p = Process(exec_type="grass", executable=module_name, executable_params=params,
                             stdin_source=stdin_func)

            self.process_dict[id] = p

            return p

        return None

    def _create_exec_process(self, module_descr):
        """Analyse a grass process description dict and create a Process
        that is used to execute a common Linux binary.

        Args:
            id (str): The id of this process in the process chain
            module_descr (dict): The module description

        Returns: Process:
            An object of type Process that contains the module name,
            the parameter list and stdout/stdin definitions

        """
        if self.message_logger:
            self.message_logger.info(str(module_descr))

        id = module_descr["id"]

        stdin_func = None
        if "stdin" in module_descr:
            if "::" not in module_descr["stdin"]:
                raise AsyncProcessError("The stdin option in id %s misses the ::" % str(id))

            object_id, method = module_descr["stdin"].split("::")

            if "stdout" in method:
                stdin_func = self.process_dict[object_id].get_stdout
            elif "stderr" in method:
                stdin_func = self.process_dict[object_id].get_stderr
            else:
                raise AsyncProcessError("The stdout or stderr flag in "
                                        "id %s is missing" % str(id))

        if "exe" not in module_descr:
            raise AsyncProcessError("Missing executable name in module "
                                    "description of id %s" % str(id))

        executable = module_descr["exe"]

        params = []

        if "params" in module_descr:
            for search_string in module_descr["params"]:

                # Search for file identifiers and generate the temporary file path
                if "$file" in search_string and "::" in search_string:
                    file_id = search_string.split("::")[1]
                    # Generate the temporary file path and store it in the dict
                    if file_id not in self.temporary_pc_files:
                        self.temporary_pc_files[file_id] = self.generate_temp_file_path()

                    param = "%s" % self.temporary_pc_files[file_id]
                else:
                    param = "%s" % search_string

                params.append(param)

        # Check for un-allowed characters in the parameter list
        for entry in params:
            if "&" in entry:
                raise AsyncProcessError("Character '&' not supported in process "
                                        "description for %s" % executable)

        p = Process(exec_type="exec",
                         executable=executable,
                         executable_params=params,
                         stdin_source=stdin_func)

        self.process_dict[id] = p

        return p

    def _process_chain_to_process_list_legacy(self, process_chain):
        """
        Transform a legacy module chain description into an ordered list of process runs

        All input map layer MUST be specified with the mapset they belong to: map@mapset

        Args:
            process_chain (dict): The process chain

        Return:
             list
             A list of ordered grass processes

        Process chain input format::

            {                                           # A process chain is a dict with entries for each module that should be run
               Id:{                                     # Id must be numerical and indicates the process order
                    "module":<module_name>,             # Name of the module to run
                    "stdin":<Id::stdout | Id::stderr>     # Use the output of a specific module as input for this module
                                                        # Id:stdout, Id:stderr are available
                    "inputs":{                          # Definition of all input parameters as key:value pairs
                             <parameter name>:<value>,  # e.g.: value == "raster_name@mapset_name" or "degree" or 0.0
                             <parameter name>:<value>   # e.g.: value == $file::slope_output_file to specify an output file
                                                        # that name will be automatically generated by the API.
                    },
                    "outputs":{                         # Definition of all outputs using key:value pairs
                        <parameter name>:{
                            "name":<value>,             # Output name e.g. "my_aspect_map" or a temporary file id
                                                        # definition: $file::id  eg: $file::aspect_output_file
                                                        # This file can be used in other module as input
                            "export":{                  # Export options, if present this map will be exported
                                "format":<value>        # Set the export format raster=GeoTiff (default), vector = shape (default)
                                "type":<output type>,   # Output type e.g.: raster, vector, file, stds
                            }
                        },
                        <parameter name>:{
                            "name":<value>,             # Output name e.g. "my_slope_map"
                            "export":{                  # Export options, if present this map will be exported
                                "format":<value>        # Set the export format raster=GeoTiff (default), vector = shape (default)
                                "type":<output type>,   # Output type e.g.: raster, vector, file, stds
                            }
                        }
                    },
                    "flags":<flags>,                    # All flags in a string e.g.: "ge"
                    "overwrite":<True|False>,           # Set True to overwrite existing data
                    "verbose":<True|False>              # Verbosity of the module
                },
               Id:{                                     # The id of an executable command, that is not a grass module
                    "executable":<path>,                # The name and path of the executable e.g. /bin/cp
                    "stdin":<Id::stdout | Id::stderr>     # Use the output of a specific module as input for this module
                                                        # Id::stdout, Id::stderr are available
                    "parameters":[<parameter>,]         # A list of strings that represent the parameters that may contain
                                                        # temporary file definitions: $file::id  eg: $file::aspect_output_file
               },
                ...
            }

        """
        process_list = []

        keys = process_chain.keys()
        int_keys = []
        # Convert the keys to integer to sort correctly
        for k in keys:
            int_keys.append(int(k))

        int_keys = sorted(int_keys)
        # Re-order the process chain by integer sorting index
        for index in int_keys:
            program = process_chain[str(index)]

            if "module" in program:
                process_list.append(self._create_module_process_legacy(str(index), program))
            elif "executable" in program:
                process_list.append(self._create_exec_process_legacy(str(index), program))
            elif "evaluate" in program:
                process_list.append(("python", program["evaluate"]))

        return process_list

    def _create_module_process_legacy(self, id, module_descr):
        """Analyse a grass process description dict and create a Process
        that is used to execute a GRASS GIS binary.

        Identify the required mapsets from the input definition and stores them in a list.

        Args:
            id (str): The id of this process in the process chain
            module_descr (dict): The module description

        Returns: Process:
            An object of type Process that contains the module name,
            the parameter list and stdout/stdin definitions

        """
        self.message_logger.info(str(module_descr))
        parameters = []

        stdin_func = None
        if "stdin" in module_descr:
            if "::" not in module_descr["stdin"]:
                raise AsyncProcessError("The stdin option in id %s misses the ::" % str(id))

            object_id, method = module_descr["stdin"].split("::")

            if "stdout" == method is True:
                stdin_func = self.process_dict[object_id].stdout

            elif "stderr" == method is True:
                stdin_func = self.process_dict[object_id].stderr
            else:
                raise AsyncProcessError("The stdout or stderr flag in id %s is missing" % str(id))

        if "module" not in module_descr:
            raise AsyncProcessError("Missing module name in module description of id %s" % str(id))

        module_name = module_descr["module"]
        if "inputs" in module_descr:
            for key in module_descr["inputs"]:

                search_string = str(module_descr["inputs"][key])

                # Search for file identifiers and generate the temporary file path
                if "$file" in search_string and "::" in search_string:
                    file_id = search_string.split("::")[1]
                    # Generate the temporary file path and store it in the dict
                    if file_id not in self.temporary_pc_files:
                        self.temporary_pc_files[file_id] = self.generate_temp_file_path()

                    param = "%s=%s" % (key, self.temporary_pc_files[file_id])
                else:
                    param = "%s=%s" % (key, module_descr["inputs"][key])
                    # Check for mapset in input name and append it
                    # to the list of required mapsets
                    if "@" in str(module_descr["inputs"][key]):

                        # Mapset names are after an @ symbol
                        # Mapsets in expressions can be detected by replacing the
                        # symbols like *, +, :, /, {, (,},], ... by spaces and split
                        # the string by spaces, searching in each substring for @


                        symbols = ['*', '+', '-', '/', '%', '$', '!', ':', '(', ')',
                                   '{', '}', '&', '?', '#', '=', '^', '~',
                                   '<', '>', '\\']

                        for symbol in symbols:
                            search_string = search_string.replace(symbol, " ")

                        search_strings = search_string.split(" ")

                        for entry in search_strings:
                            for subentry in entry.split(","):
                                if "@" in subentry:
                                    mapset = subentry.split("@")[1]
                                    if mapset not in self.required_mapsets:
                                        self.required_mapsets.append(mapset)

                parameters.append(param)

        if "outputs" in module_descr:
            for key in module_descr["outputs"]:
                if "name" in module_descr["outputs"][key]:

                    search_string = module_descr["outputs"][key]["name"]

                    # Search for file identifiers and generate the temporary file path
                    if "$file" in search_string and "::" in search_string:
                        file_id = search_string.split("::")[1]
                        # Generate the temporary file path and store it in the dict
                        if file_id not in self.temporary_pc_files:
                            self.temporary_pc_files[file_id] = self.generate_temp_file_path()

                        param = "%s=%s" % (key, self.temporary_pc_files[file_id])
                    else:
                        param = "%s=%s" % (key, search_string)
                    parameters.append(param)
                    # List the resource for potential export
                    if "export" in module_descr["outputs"][key]:
                        exp = module_descr["outputs"][key]["export"]
                        if "format" not in exp or "type" not in exp:
                            raise AsyncProcessError(
                                    "Invalid export parameter in description of module <%s>" % module_name)
                        if exp["format"] not in ["GTiff", "ESRI_Shapefile"]:
                            raise AsyncProcessError(
                                    "Invalid export <format> parameter in description of module <%s>" % module_name)
                        if exp["type"] not in ["raster", "vector", "strds", "file", "stvds"]:
                            raise AsyncProcessError(
                                    "Invalid export <type> parameter in description of module <%s>" % module_name)
                        self.resource_export_list.append(module_descr["outputs"][key])

        if "flags" in module_descr:
            if "flags" in module_descr:
                parameters.append("-" + str(module_descr["flags"]))

        if "overwrite" in module_descr and module_descr["overwrite"] is True:
            parameters.append("--o")

        if "superquiet" in module_descr and module_descr["superquiet"] is True:
            parameters.append("--qq")

        if "verbose" in module_descr and module_descr["verbose"] is True:
            parameters.append("--v")

        # Check for un-allowed characters in the parameter list
        for entry in parameters:
            if "&" in entry:
                raise AsyncProcessError("Character '&' not supported in process "
                                        "description for %s" % module_name)

        p = Process(exec_type="grass", executable=module_name, executable_params=parameters,
                         stdin_source=stdin_func)

        self.process_dict[id] = p

        return p

    def _create_exec_process_legacy(self, id, module_descr):
        """Analyse a grass process description dict and create a Process
        that is used to execute a common Linux binary.

        Args:
            id (str): The id of this process in the process chain
            module_descr (dict): The module description

        Returns: Process:
            An object of type Process that contains the module name,
            the parameter list and stdout/stdin definitions

        """
        self.message_logger.info(str(module_descr))
        parameters = []

        stdin_func = None
        if "stdin" in module_descr:
            if "::" not in module_descr["stdin"]:
                raise AsyncProcessError("The stdin option in id %s misses the ::" % str(id))

            object_id, method = module_descr["stdin"].split("::")

            if "stdout" in method:
                stdin_func = self.process_dict[object_id].get_stdout
            elif "stderr" in method:
                stdin_func = self.process_dict[object_id].get_stderr
            else:
                raise AsyncProcessError("The stdout or stderr flag in id %s is missing" % str(id))

        if "executable" not in module_descr:
            raise AsyncProcessError("Missing executable name in module description of id %s" % str(id))

        executable = module_descr["executable"]
        if "parameters" in module_descr:
            for search_string in module_descr["parameters"]:

                # Search for file identifiers and generate the temporary file path
                if "$file" in search_string and "::" in search_string:
                    file_id = search_string.split("::")[1]
                    # Generate the temporary file path and store it in the dict
                    if file_id not in self.temporary_pc_files:
                        self.temporary_pc_files[file_id] = self.generate_temp_file_path()

                    param = "%s" % self.temporary_pc_files[file_id]
                else:
                    param = "%s" % search_string

                parameters.append(param)

        # Check for un-allowed characters in the parameter list
        for entry in parameters:
            if "&" in entry:
                raise AsyncProcessError("Character '&' not supported in process "
                                        "description for %s" % executable)

        p = Process(exec_type="exec",
                         executable=executable,
                         executable_params=parameters,
                         stdin_source=stdin_func)

        self.process_dict[id] = p

        return p


def test_process_chain():
    from pprint import pprint

    elev_in = InputParameter(param="elevation",
                             value="elev_10m",
                             import_descr={"source": "https://storage.googleapis.com/Actinia Core-geodata/elev_ned_30m.tif",
                                           "type": "raster"})
    format_in = InputParameter(param="format",
                               value="degree")
    precision_in = InputParameter(param="precision",
                                  value="DCELL")
    export = {'type': 'raster',
              'format': 'GTiff'}

    slope_out = OutputParameter(param="slope",
                                value='elev_10m_slope',
                                export=export)

    aspect_out = OutputParameter(param="aspect",
                                 value='elev_10m_aspect',
                                 export=export)

    module_1 = GrassModule(id="r_slope_aspect_1",
                         module='r.slope.aspect',
                         inputs=[elev_in, format_in, precision_in],
                         outputs=[slope_out, aspect_out],
                         flags='a',
                         overwrite=True,
                         verbose=False)

    file_in = InputParameter(param="name",
                             value="$file::polygon",
                             import_descr={"source": "https://storage.googleapis.com/Actinia Core-geodata/brazil_polygon.json",
                                           "type": "file"})

    module_2 = GrassModule(id="importer",
                         module='importer',
                         inputs=[file_in])

    exe_1 = Executable(id="cat_1",
                     exe='/bin/cat',
                     params=[],
                     stdin='r_slope_aspect_1::stderr')

    func_in_1 = InputParameter(param="pyfile",
                             value="$file::polygon")

    module_3 = GrassModule(id="udf",
                         module='t.rast.aggr_func',
                         inputs=[func_in_1])

    func_in_2 = InputParameter(param="pyfile",
                             value="$file::polygon",
                             import_descr={"source": "https://storage.googleapis.com/Actinia Core-geodata/brazil_polygon.json",
                                           "type": "file"})

    module_4 = GrassModule(id="udf",
                         module='t.rast.aggr_func',
                         inputs=[func_in_2])

    pc = ProcessChainModel(version='1', list=[module_1, module_2, exe_1, module_3, module_4])

    pprint(pc)

    pconv = ProcessChainConverter()
    pl = pconv.process_chain_to_process_list(pc)

    for proc in pl:
        pprint(str(proc))

    pprint(pconv.process_dict)
    pprint(pconv.required_mapsets)
    pprint(pconv.resource_export_list)
    pprint(pconv.import_descr_list)
    pprint(pconv.temporary_pc_files)


if __name__ == '__main__':
    test_process_chain()
