###
# Copyright 2021 New H3C Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-


import argparse
import importlib
import os
import xml.etree.ElementTree as ET
from utils import globalvar
from exception.ToolException import ConfigException


class XmlConfig(object):

    tool_set = {"hREST"}

    def __init__(self):
        self._args = None
        self._model_class = None
        self._model_method = None
        self._view_class = None
        self._view_method = None
        self._format = None
        self._type = None
        self.path = "./config_hrest.xml"

    @property
    def args(self):
        return self._args

    @property
    def model_class(self):
        return self._model_class

    @property
    def model_method(self):
        return self._model_method

    @property
    def view_class(self):
        return self._view_class

    @property
    def view_method(self):
        return self._view_method

    @property
    def format(self):
        return self._format

    @property
    def type(self):
        return self._type

    def config_parser(self):

        try:
            xml_path = self.path
            config_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)) + xml_path)
            tree = ET.ElementTree(file=config_path)
        except FileNotFoundError as err:
            raise ConfigException(err)
        root = tree.getroot()
        type_ = root.get("type")
        if type_ not in XmlConfig.tool_set:
            err = ("Failure: Unrecognized profile type_ : "
                   "{}! Please check your configure file".format(type_))
            raise ConfigException(err)
        self._type = type_
        version = root.get("version")

        globalvar.IS_ADAPT_B01 = (
            True if root.get("is_adapt_b01") == "True" else False)
        parser = argparse.ArgumentParser(prog=type_,
                                         add_help=True)

        parser.add_argument('-V', '--version', action='version',
                            version="%s version %s" % (type_, version))

        propertys = tree.find("propertys")

        if propertys is not None:
            propertys = propertys.findall("property")
            for property_ in propertys:
                parser.add_argument(property_.get("name"),
                                    dest=property_.get("dest"),
                                    required=(property_.get("required") ==
                                              "True"),
                                    type={"str": str,
                                          "int": int,
                                          "float": float}
                                    .get(property_.get("type"), None),
                                    help=property_.get("help"))
        subparsers = parser.add_subparsers(title="sub commands",
                                           dest="sub_command",
                                           help="sub-command help",
                                           metavar="sub command")
        mappers = tree.findall("mapper")
        for elem in mappers:
            sub_parser = subparsers.add_parser(elem.get("id"),
                                               help=elem.get("help"))
            propertys = elem.find("propertys")
            if propertys is not None:
                propertys = propertys.findall("property")
                for property_ in propertys:
                    choices = property_.get("choices")
                    if choices:
                        choices = choices.split()
                        if "int" == property_.get("type"):
                            try:
                                choices = [int(i) for i in choices]
                            except ValueError:
                                err = ("Failure: Unrecognized choices: "
                                       "{%s}!" % property_.get("choices"))
                                raise ConfigException(err)
                    sub_parser.add_argument(property_.get("name"),
                                            dest=property_.get("dest"),
                                            required=(property_.get("required")
                                                      == "True"),
                                            type={"str": str,
                                                  "int": int,
                                                  "float": float}
                                            .get(property_.get("type"), None),
                                            help=property_.get("help"),
                                            choices=choices)
        self._args = parser.parse_args()

        sub_command = self._args.sub_command
        path = "mapper[@id='" + sub_command + "']"
        module_config = tree.find(path)
        self._format = module_config.find("result")
        file = module_config.get("file")
        if not file:
            raise ConfigException(
                "Failure: File is not exist. File: %s" %
                file)
        filename = file.split("/")
        class_name = module_config.get("class")
        method_name = module_config.get("method")
        module = importlib.import_module(".".join(filename))
        module_class = getattr(module, class_name)
        self._model_method = getattr(module_class, method_name)
        self._model_class = module_class

    def get_all_cmd(self):
        try:
            tree = ET.ElementTree(file=self.path)
            xml_path = tree.getroot().findall("filename")[-1].get("path")
            config_path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)) + xml_path)
            tree = ET.ElementTree(file=config_path)
        except FileNotFoundError as err:
            raise ConfigException(err)
        else:
            cmd_list = []
            mappers = tree.findall("mapper")
            for elem in mappers:
                cmd = elem.get("id")
                cmd_list.append(cmd)
        return cmd_list
