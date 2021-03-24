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


import traceback
from config import XmlConfig
from exception.ToolException import ConfigException
from exception.ToolException import FailException
from view.view import show


class CommandControl(object):

    def __init__(self, config):
        self._args = config.args
        self._model_class = config.model_class
        self._model_method = config.model_method
        self._view_class = config.view_class
        self._view_method = config.view_method
        self._format = config.format
        self._type = config.type

    def run(self):

        object_ = self._model_class()
        try:
            suc_list = self._model_method(object_, self._args)
            show(data=object_, suc_list=suc_list, formatter=self._format)
        except FailException as err:
            show(err_list=err.args, formatter=self._format)
        except (ValueError, Exception):
            err_list = [traceback.format_exc()]
            show(err_list=err_list, formatter=self._format)


def main():
    config = XmlConfig()
    try:
        config.config_parser()
    except ConfigException as err:
        print(err)
        return
    app = CommandControl(config)
    app.run()


if __name__ == "__main__":
    main()
