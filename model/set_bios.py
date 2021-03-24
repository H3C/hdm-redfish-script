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


import json
from exception.ToolException import FailException
from utils.client import RedfishClient
from utils.common import Constant
from utils.tools import init_args
from utils.predo import GetVersion


class SetBios:

    def __init__(self):

        self.err_list = []
        self.suc_list = []
        self.args_lst = ["attribute", "attr_value", "config_file"]

    @GetVersion()
    def run(self, args):

        init_args(args, self.args_lst)
        config_dict = self.check_args(args)

        client = RedfishClient(args)
        systems_id = client.get_systems_id()
        url = "/redfish/v1/Systems/%s/Bios" % systems_id
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and resp.get("status_code") in
                Constant.SUC_CODE):
            attrs = resp["resource"]["Attributes"]
            for key_, value_ in config_dict.items():
                if attrs.get(key_, None) is not None:
                    if isinstance(attrs.get(key_, None), int):
                        try:
                            config_dict[key_] = int(value_)
                        except (KeyError, ValueError) as err:
                            self.err_list.append(str(err))
                            raise FailException(*self.err_list)
                else:
                    err_message = ("Failure: the BIOS setting item does "
                                   "not exist: %s" % key_)
                    self.err_list.append(err_message)
                    raise FailException(*self.err_list)
            self.result_response(client, url, config_dict)
        else:
            err_message = ("Failure: failed to get current BIOS setup "
                           "information")
            self.err_list.append(err_message)
            raise FailException(*self.err_list)
        return self.suc_list

    def result_response(self, client, url, data):

        url = "%s/SD" % url
        payload = {"Attributes": data}
        resp = client.send_request("PATCH", url, payload, 300)
        if (isinstance(resp, dict) and resp.get("status_code") in
                Constant.SUC_CODE):
            suc_message = "Success: BIOS setup is successfully"
            self.suc_list.append(suc_message)
        else:
            err_message = "Failure: BIOS setup failed"
            self.err_list.append(err_message)
            raise FailException(*self.err_list)

    def check_args(self, args):

        config_dict = dict()
        if not (args.attr_value or args.attribute or args.config_file):
            err_info = "Argument: requires at least one parameter"
            self.err_list.append(err_info)
        elif args.config_file is not None:
            if args.attr_value or args.attribute:
                err_info = "Argument: illegal parameter combination"
                self.err_list.append(err_info)
            else:
                try:
                    with open(args.config_file, "r") as r_file:
                        config_dict = json.load(r_file)
                except (IOError, TypeError, ValueError,
                        json.decoder.JSONDecodeError, Exception) as err:
                    self.err_list.append(str(err))
        else:
            if not (args.attr_value and args.attribute):
                err_info = "Argument: illegal parameter combination"
                self.err_list.append(err_info)
            else:
                config_dict[args.attribute] = args.attr_value
        if self.err_list:
            raise FailException(*self.err_list)
        return config_dict
