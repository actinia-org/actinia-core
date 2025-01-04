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
Process chain
"""
from flask_restful_swagger_2 import Schema
from copy import deepcopy
from actinia_api import URL_PREFIX

__license__ = "GPLv3"
__author__ = "Sören Gebbert, Carmen Tawalika, Anika Weinmann"
__copyright__ = (
    "Copyright 2016-2024, Sören Gebbert and mundialis GmbH & Co. KG"
)
__maintainer__ = "mundialis GmbH & Co. KG"
__email__ = "info@mundialis.de"

SUPPORTED_EXPORT_FORMATS = [
    "COG",
    "GTiff",
    "GPKG",
    "SQLite",
    "GML",
    "GeoJSON",
    "ESRI_Shapefile",
    "CSV",
    "TXT",
    "PostgreSQL",
]


class IOParameterBase(Schema):
    """This is the input parameter of a GRASS GIS module definition"""

    type = "object"
    properties = {
        "param": {
            "type": "string",
            "description": "The name of a GRASS GIS module parameter like "
            "*map* or *elevation*. ",
        },
        "value": {
            "type": "string",
            "description": "The value of the GRASS GIS module parameter. "
            "Raster, vector and STDS inputs must contain the "
            "mapset name in their id: *slope@PERMANENT*, if "
            "they are not located in the working mapset. "
            "Do not contain the mapset name in map names that are "
            "processed, since the mapsets are generated on demand "
            "using random names. "
            "Outputs are not allowed to contain mapset names."
            "Files that are created in the process chain to exchange "
            "data can be specified using the *$file::unique_id* "
            "identifier. The **unique_id** will be replaced with a "
            "temporary file name, that is available in the whole "
            "process chain at runtime. The **unique_id**  is the "
            "identifier that can be used by different modules in "
            "a process chain to access the same temporary file or "
            "to prepare it for export.",
        },
    }
    description = (
        "Parameter definition of a GRASS GIS module that should be executed "
        "in the actinia environment. Parameters can be of type input or "
        "output. A GRASS GIS module will be usually called like: "
        "<p>g.region raster=elevation30m@PERMANENT</p> "
        "The GRASS GIS module *g.region* parameter *raster* has the value "
        "*elevation30m@PERMANENT*. "
        "This is reflected by the *param* and *value* properties that can "
        "specify input and output "
        "parameters."
    )
    required = ["param", "value"]
    example = {"param": "file", "value": "$file::ascii_points"}


class InputParameter(IOParameterBase):
    """
    This is the import definition of a input parameter of a GRASS GIS module
    definition
    """

    properties = deepcopy(IOParameterBase.properties)
    properties["import_descr"] = {
        "type": "object",
        "description": "Definition of sources to be imported as raster or "
        "vector map layer.",
        "properties": {
            "type": {
                "type": "string",
                "description": "The type of the input that should be "
                "downloaded and imported. In case of raster or vector types "
                "a download URL must be provided as source using "
                "http, https or ftp protocols. In case of sentinel2 "
                " scenes the scene name and the band must be provided. "
                "The Landsat approach is different. <br><br>"
                "In case a Landsat scene is requested, all "
                "bands will be download, in the target project imported"
                " and an atmospheric correction is applied. The "
                "atmospheric correction must be specified. The resulting"
                " raster map layers have a specific name scheme, that "
                "is independent from the provided map name in the "
                "process description. The name scheme is always: "
                r"<p>\<landsat scene id\>_\<atcor\>.\<band\></p>"
                "For example, if the scene <p>LT52170762005240COA00</p> "
                "was requested, the resulting name for the DOS1 "
                "atmospheric corrected band 1 would be: "
                "<p>LT52170762005240COA00_dos1.1</p>."
                "For the DOS1 atmospheric corrected band 2 it "
                "would be: <p>LT52170762005240COA00_dos1.2</p> "
                "and so on. "
                "All other process steps must use these raster map layer"
                " names to refer to the imported Landsat bands. "
                "Use the file option to download any kind of files that "
                "should be processed by a grass gis module. ",
                "enum": [
                    "raster",
                    "vector",
                    "landsat",
                    "sentinel2",
                    "postgis",
                    "file",
                    "stac",
                ],
            },
            "sentinel_band": {
                "type": "string",
                "description": "The band of the sentinel2 scene that should be"
                " imported",
                "enum": [
                    "B01",
                    "B02",
                    "B03",
                    "B04",
                    "B05",
                    "B06",
                    "B07",
                    "B08",
                    "B8A",
                    "B09",
                    "B10",
                    "B11",
                    "B12",
                ],
            },
            "landsat_atcor": {
                "type": "string",
                "description": "The atmospheric correction that should be "
                "applied to the landsat scene",
                "enum": [
                    "uncorrected",
                    "dos1",
                    "dos2",
                    "dos2b",
                    "dos3",
                    "dos4",
                ],
            },
            "vector_layer": {
                "type": "string",
                "description": "The name of the layer that should be imported "
                "from the vector file or postGIS database",
            },
            "source": {
                "type": "string",
                "description": "The input source that may be a landsat scene "
                "name, a sentinel2 scene name, a postGIS database string,"
                "a stac collection ID or an URL that points "
                "to an accessible raster or vector file. "
                "A HTTP, HTTPS or FTP connection must be "
                "specified in case of raster or vector types. "
                "In this case the source string must contain the "
                "protocol that will used for connection: http:// or "
                "https:// or ftp://. PostGIS vector layer can be "
                "imported by defining a database string as source and "
                "a layer name.",
            },
            "semantic_label": {
                "type": "string",
                "description": "Refers to the common names used to"
                "call the bands of an image,"
                "for example: red, blue, nir, swir"
                "However, this property also accepts the band name"
                "such as B1, B8 etc. The semantic labeling should match"
                "the labels register in the stac collection.",
                "example": "red, blue, nir or B1, B2, B8A",
            },
            "extent": {
                "type": "string",
                "description": "Spatio-temporal constraint defined by the user"
                "throughout bbox and interval concept.",
                "enum": ["spatial", "temporal"],
                "example": {
                    "spatial": {"bbox": [[30.192, -16.369, 42.834, -0.264]]},
                    "temporal": {"interval": [["2021-09-09", "2021-09-12"]]},
                },
            },
            "filter": {
                "type": "string",
                "description": "Constrain in any other property"
                "or metadata.",
                "example": {"query": {"eo:cloud_cover": {"lt": 50}}},
            },
            "resample": {
                "type": "string",
                "description": "Resampling method to use for reprojection of "
                "raster map (default: nearest).",
                "enum": [
                    "nearest",
                    "bilinear",
                    "bicubic",
                    "lanczos",
                    "bilinear_f",
                    "bicubic_f",
                    "lanczos_f",
                ],
            },
            "resolution": {
                "type": "string",
                "description": "Resolution of output raster map. Estimated, "
                "user-specified or current region resolution "
                "(default: estimated).",
                "enum": ["estimated", "value", "region"],
            },
            "resolution_value": {
                "type": "string",
                "description": "Resolution of output raster map (use with "
                'option "resolution": "value") in units of the target '
                "coordinate reference system, not in map units. Must "
                "be convertible to float.",
                "example": {
                    "import_descr": {
                        "source": "https://example.tiff",
                        "type": "raster",
                        "resample": "bilinear_f",
                        "resolution": "value",
                        "resolution_value": "100",
                    }
                },
            },
            "basic_auth": {
                "type": "string",
                "description": "User name and password for basic HTTP, HTTPS "
                "and FTP authentication of the source connection. The user "
                "name and password must be separated by a colon: "
                "username:password",
            },
        },
    }

    required = deepcopy(IOParameterBase.required)
    description = deepcopy(IOParameterBase.description)
    example = {
        "import_descr": {
            "source": "LT52170762005240COA00",
            "type": "landsat",
            "landsat_atcor": "dos1",
        },
        "param": "map",
        "value": "ignored",
    }


class OutputParameter(IOParameterBase):
    """This is the output parameter of a GRASS GIS module definition"""

    type = "object"
    properties = deepcopy(IOParameterBase.properties)
    properties["export"] = {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "description": "The format of the output file in case of "
                "raster, strds, vector layer or text file export. Raster layer"
                " export supports only GTiff and COG format, STRDS layer "
                "export supports only GTiff format and all other formats are "
                "vector layer export formats. If the *PostgeSQL* format "
                "was chosen, a postgis database string *dbstring* "
                "must be provided  so that the GRASS GIS module "
                "*v.out.ogr knows to which PostgreSQL database it "
                "should be connect. The name of the output layer can be "
                "specified as *output_layer* for PostgreSQL database "
                "exports. Some GRASS GIS modules allow the export of "
                "text files. These files can be exported and provided "
                "as downloadable link as well.",
                "enum": SUPPORTED_EXPORT_FORMATS,
            },
            "type": {
                "type": "string",
                "description": "The type of the output. In case of the *file* "
                "option only text files are supported for export. "
                "In addition the *$file::unique_id* option must "
                "be used in the value parameter to export a file "
                "that was generated by a GRASS GIS module. Exported "
                "text and vector files will always be compressed "
                "with zip.",
                "enum": ["raster", "vector", "file", "strds"],
            },
            "dbstring": {
                "type": "string",
                "description": "The database string to be used to connect to a"
                " PostgreSQL database for vector export.",
            },
            "output_layer": {
                "type": "string",
                "description": "Name for output PostgreSQL layer. If not "
                "specified, GRASS GIS vector map layer name is used.",
            },
        },
        "description": "The raster, vector or text file export parameter.",
        "required": ["format", "type"],
        "example": {
            "format": "PostgreSQL",
            "type": "vector",
            "dbstring": "PG:host=localhost dbname=postgis user=postgres",
            "output_layer": "roads",
        },
    }
    properties["metadata"] = {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "description": "Format of the metadata file. Only STAC is "
                "supported. "
                "The STAC item builder works just on raster export file."
                "These files are accessible through a STAC Catalog"
                "and each export is stored as STAC Item",
                "enum": ["STAC"],
            },
        },
        "description": "The STAC file export parameter.",
        "required": ["format", "type"],
        "example": {"format": "STAC"},
    }
    required = deepcopy(IOParameterBase.required)
    description = deepcopy(IOParameterBase.description)
    example = {
        "param": "slope",
        "value": "elev_10m_slope",
        "export": {"type": "raster", "format": "GTiff"},
    }


class StdoutParser(Schema):
    """This is the schema of the stdout output parser for GRASS GIS modules"""

    type = "object"
    properties = {
        "id": {
            "type": "string",
            "description": "The unique id that is used to identify the "
            "parsed output in the result dictionary.",
        },
        "format": {
            "type": "string",
            "description": "The stdout format to be parsed.",
            "enum": ["table", "list", "kv", "json"],
        },
        "delimiter": {
            "type": "string",
            "description": "The delimiter that should be used to parse table,"
            " list and key/value module output. Many GRASS "
            'GIS  modules use by default "|" in tables and '
            '"=" in key/value pairs. A new line "\\n" is '
            "always the delimiter between rows in the output.",
        },
    }
    required = ["id", "format", "delimiter"]
    description = (
        "Use this parameter to automatically parse the output of GRASS GIS "
        "modules and convert the output into tables, lists or key/value pairs "
        "in the result section of the response."
        "If the property type is set to *table*, *list* or *kv* then "
        "the stdout of the current command will be parsed and "
        "the result of the parse operation will be added to the "
        "result dictionary using the provided id as key. GRASS GIS modules "
        "produce regular output. Many modules have the flag *-g* to "
        "create key value pairs as stdout output. Other create a list of "
        "values or a table with/without header."
    )
    example = {"id": "stats", "format": "table", "delimiter": "|"}


class GrassModule(Schema):
    """
    The definition of a GRASS GIS module and its inputs, outputs and flags
    """

    type = "object"
    properties = {
        "id": {
            "type": "string",
            "description": "A unique id to identify the module call in the "
            "process chain to reference its stdout and stderr "
            "output as stdin in other modules.",
        },
        "module": {
            "type": "string",
            "description": "The name of the GRASS GIS module (r.univar, "
            "r.slope.aspect, v.select, ...) that should be "
            'executed. Use as module names "importer" or '
            '"exporter" to import or export raster layer, '
            "vector layer or other file based data without "
            "calling a GRASS GIS module.",
        },
        "inputs": {
            "type": "array",
            "items": InputParameter,
            "description": "A list of input parameters of a GRASS GIS module.",
        },
        "outputs": {
            "type": "array",
            "items": OutputParameter,
            "description": "A list of output parameters of a GRASS GIS "
            "module.",
        },
        "flags": {
            "type": "string",
            "description": "The flags that should be set for the GRASS GIS "
            "module.",
        },
        "stdin": {
            "type": "string",
            "description": "Use the stdout output of a GRASS GIS module or "
            "executable of the process chain as input for this "
            "module. Refer to the module/executable output "
            'as *id::stderr* or *id::stdout*, the "id" is '
            "the unique identifier of a GRASS GIS module "
            "definition.",
        },
        "stdout": StdoutParser,
        "overwrite": {
            "type": "boolean",
            "description": "Set True to overwrite existing data.",
        },
        "verbose": {
            "type": "boolean",
            "description": "Set True to activate verbosity output of the "
            "module.",
        },
        "superquiet": {
            "type": "boolean",
            "description": "Set True to silence the output of the " "module.",
        },
        "interface-description": {
            "type": "boolean",
            "description": "Set True to print interface "
            "description and exit.",
        },
    }
    required = ["id", "module"]
    description = (
        "The definition of a single GRASS GIS module and its inputs, outputs "
        "and flags. This module will be run in a project/mapset environment "
        "and is part of a process chain. The stdout and stderr output of "
        "modules that were run before this module in the process chain can be "
        "used as stdin for this module. The stdout of a module can be "
        "automatically transformed in list, table or key/value JSON "
        "representations in the HTTP response."
    )
    example = {
        "module": "r.slope.aspect",
        "id": "r_slope_aspect_1",
        "inputs": [
            {
                "import_descr": {
                    "source": "https://storage.googleapis.com/graas-geodata/"
                    "elev_ned_30m."
                    "tif",
                    "type": "raster",
                },
                "param": "raster",
                "value": "elev_ned_30m_new",
            }
        ],
        "outputs": [
            {
                "export": {"format": "GTiff", "type": "raster"},
                "param": "slope",
                "value": "elev_ned_30m_new_slope",
            }
        ],
        "flags": "a",
    }


class Executable(Schema):
    """The definition of a Linux executable and its parameters"""

    type = "object"
    properties = {
        "id": {
            "type": "string",
            "description": "A unique id to identify the executable in the "
            "process chain to reference its stdout and stderr output as "
            "stdin in other modules.",
        },
        "exe": {
            "type": "string",
            "description": "The name of the Linux executable that should be "
            "executed as part of the process chain.",
        },
        "params": {
            "type": "array",
            "items": {"type": "string"},
            "description": "A list of input parameters of a GRASS GIS module."
            "By setting module_id::stdout(::filter) the stdout of another "
            "module can be used as input for the current module. E.g. "
            "'r_univar_module_id::stdout::max' can be used to do a rescaling "
            "of a raster.",
        },
        "stdin": {
            "type": "string",
            "description": "Use the output of a GRASS GIS module or executable"
            " in of the process chain as input for this module. "
            "Refer to the module/executable output as id::stderr "
            'or id::stdout, the "id" is the unique identifier '
            "of a GRASS GIS module.",
        },
    }
    required = ["id", "exe"]
    description = (
        "The definition of a Linux executable and its parameters. "
        "The stdout and stderr output of modules/executable "
        "that were run before this module in the process "
        "chain can be used as stdin for this module."
    )
    example = {"id": "cat_1", "exe": "/bin/cat", "params": []}


class Webhooks(Schema):
    """The definition of finished and update webhooks"""

    type = "object"
    properties = {
        "update": {
            "type": "string",
            "description": "Specify a HTTP(S) GET/POST endpoint that should be"
            " called when a status update is available while the "
            "process chain is executed. The actinia JSON status "
            "response will be send as JSON content to the POST "
            "endpoint for each status update until the process "
            "finished. The GET endpoint, that must be available "
            "by the same URL as the POST endpoint, will be used "
            "to check if the webhook endpoint is available.",
        },
        "finished": {
            "type": "string",
            "description": "Specify a HTTP(S) GET/POST endpoint that should "
            "be called when the process chain was executed "
            "successful or unsuccessfully. The actinia JSON "
            "response will be send as JSON content to the POST "
            "endpoint after processing finished. The GET "
            "endpoint, that must be available by the same URL "
            "as the POST endpoint, will be used to check if "
            "the webhook endpoint is available.",
        },
    }
    required = ["finished"]
    description = (
        "Specify HTTP(S) GET/POST endpoints that should be called when the "
        "process chain was executed successful or unsuccessfully (finished) or"
        " when a status/progress update is available (update). The actinia "
        "JSON response will be send as JSON content to the POST endpoints "
        "after processing finished or the status was updated. The GET "
        "endpoints, that must be available by the same URL as the POST "
        "endpoints (update/finished), will be used to check if the webhooks "
        "endpoints are available. "
        "The finished endpoint is mandatory, the update endpoint is optional."
    )
    example = {
        "update": f"http://business-logic.company.com{URL_PREFIX}/"
        "actinia-update-webhook",
        "finished": f"http://business-logic.company.com{URL_PREFIX}/"
        "actinia-finished-webhook",
    }


class ProcessChainModel(Schema):
    """Definition of the actinia process chain that includes GRASS GIS modules
    and common Linux commands
    """

    type = "object"
    properties = {
        "version": {
            "type": "string",
            "default": "1",
            "description": "The version string of the process chain",
        },
        "list": {
            "type": "array",
            "items": GrassModule,
            "description": "A list of process definitions that should be "
            "executed in the order provided by the list.",
        },
        "webhooks": Webhooks,
    }
    required = ["version", "list"]
    example = {
        "list": [
            {
                "module": "g.region",
                "id": "g_region_1",
                "inputs": [
                    {
                        "import_descr": {
                            "source": "https://storage.googleapis.com/"
                            "graas-geodata/elev_ned_30m.tif",
                            "type": "raster",
                        },
                        "param": "raster",
                        "value": "elev_ned_30m_new",
                    }
                ],
                "flags": "p",
            },
            {
                "module": "r.slope.aspect",
                "id": "r_slope_aspect_1",
                "inputs": [
                    {"param": "elevation", "value": "elev_ned_30m_new"}
                ],
                "outputs": [
                    {
                        "export": {"format": "GTiff", "type": "raster"},
                        "param": "slope",
                        "value": "elev_ned_30m_new_slope",
                    }
                ],
                "flags": "a",
            },
            {
                "module": "r.univar",
                "id": "r_univar_1",
                "inputs": [
                    {
                        "import_descr": {
                            "source": "LT52170762005240COA00",
                            "type": "landsat",
                            "landsat_atcor": "dos1",
                        },
                        "param": "map",
                        "value": "LT52170762005240COA00_dos1.1",
                    }
                ],
                "stdout": {"id": "stats", "format": "kv", "delimiter": "="},
                "flags": "a",
            },
            {
                "module": "exporter",
                "id": "exporter_1",
                "outputs": [
                    {
                        "export": {"format": "GTiff", "type": "raster"},
                        "metadata": {
                            "format": "STAC",
                            "type": "metadata",
                            "output_layer": "stac_result",
                        },
                        "param": "map",
                        "value": "LT52170762005240COA00_dos1.1",
                    }
                ],
            },
            {
                "id": "ascii_out",
                "module": "r.out.ascii",
                "inputs": [
                    {"param": "input", "value": "elevation@PERMANENT"},
                    {"param": "precision", "value": "0"},
                ],
                "stdout": {
                    "id": "elev_1",
                    "format": "table",
                    "delimiter": " ",
                },
                "flags": "h",
            },
            {
                "id": "ascii_export",
                "module": "r.out.ascii",
                "inputs": [{"param": "input", "value": "elevation@PERMANENT"}],
                "outputs": [
                    {
                        "export": {"type": "file", "format": "TXT"},
                        "param": "output",
                        "value": "$file::out1",
                    }
                ],
            },
            {
                "id": "raster_list",
                "module": "g.list",
                "inputs": [{"param": "type", "value": "raster"}],
                "stdout": {
                    "id": "raster",
                    "format": "list",
                    "delimiter": "\n",
                },
            },
            {
                "module": "r.what",
                "id": "r_what_1",
                "verbose": True,
                "flags": "nfic",
                "inputs": [
                    {"param": "map", "value": "landuse96_28m@PERMANENT"},
                    {
                        "param": "coordinates",
                        "value": "633614.08,224125.12,632972.36,225382.87",
                    },
                    {"param": "null_value", "value": "null"},
                    {"param": "separator", "value": "pipe"},
                ],
                "stdout": {
                    "id": "sample",
                    "format": "table",
                    "delimiter": "|",
                },
            },
        ],
        "webhooks": {
            "update": f"http://business-logic.company.com{URL_PREFIX}/"
            "actinia-update-webhook",
            "finished": f"http://business-logic.company.com{URL_PREFIX}/"
            "actinia-finished-webhook",
        },
        "version": "1",
    }
