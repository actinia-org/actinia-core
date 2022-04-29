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
XML to module list
AW: I suspect that this file is no longer used
    because of F821: undefined names after missing import PyQt4
    PyQt4 is obsolete and since python3 PyQt5 is used
"""

# from PyQt4.QtCore import *
# from PyQt4.QtXml import *
# from config import global_config

__license__ = "GPLv3"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2016-2018, Sören Gebbert and mundialis GmbH & Co. KG"
__maintainer__ = "Sören Gebbert"
__email__ = "soerengebbert@googlemail.com"


class GrassModuleReader(object):
    """
    Class to parse the module_items.xml file from GRASS

    This class creates a nested module dictionary based on keywords.
    The keyword depth is 2, if the second keyword is missing, the
    keyword "unspecific" is used as default.
    """

    def __init__(self, filename):

        self.modules_keyword_dict = {}

        file = QFile(filename)
        file.open(QIODevice.ReadOnly)
        self.xml = QXmlStreamReader(file)

        while not self.xml.atEnd():
            self.xml.readNext()
            if self.xml.isStartElement():
                if self.xml.name() == "module-item":
                    name = self.xml.attributes().value("name")
                    if name:
                        self.parse_module()

    def get(self):
        """
        Return the keyword dictionary
        :return:
        """
        return self.modules_keyword_dict

    def parse_module(self):

        module = None
        keywords = None
        description = None

        while self.xml.readNextStartElement():

            if self.xml.name() == "module":
                module = self.xml.readElementText()
            elif self.xml.name() == "description":
                description = self.xml.readElementText()
            elif self.xml.name() == "keywords":
                keywords = self.xml.readElementText()

        if module and keywords and description:
            if module in global_config.MODULE_ALLOW_LIST:
                # First and second keyword must exist
                key_list = str(keywords).split(",")
                first_key = key_list[0]
                second_key = "unspecific"
                if len(key_list) > 1:
                    second_key = key_list[1]

                if first_key not in self.modules_keyword_dict:
                    self.modules_keyword_dict[first_key] = {}
                if second_key not in self.modules_keyword_dict[first_key]:
                    self.modules_keyword_dict[first_key][second_key] = {}

                module_entry = self.modules_keyword_dict[first_key][second_key]
                module_entry[str(module)] = {}
                module_entry[str(module)]["module"] = str(module)
                module_entry[str(module)]["description"] = str(description)
                module_entry[str(module)]["keywords"] = str(keywords)


def test():
    url = global_config.GRASS_MODULES_XML_PATH
    xml = GrassModuleReader(url)

    for first_key in xml.modules_keyword_dict:
        print(first_key)
        level_one = xml.modules_keyword_dict[first_key]
        for second_key in level_one:
            print("  " + second_key)
            level_two = level_one[second_key]
            for module in level_two:
                entry = level_two[module]
                print("    " + entry["module"])
                print("      " + entry["description"])


def main():

    grass_modules_xml_path = global_config.GRASS_MODULES_XML_PATH
    module_reader = GrassModuleReader(grass_modules_xml_path)

    file = open("grass_modules_list.py", "w")
    file.write("module_list=")
    file.write(str(module_reader.get()))
    file.close()


if __name__ == "__main__":
    test()
    main()
