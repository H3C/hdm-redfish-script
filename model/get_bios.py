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


import os
import json
from exception.ToolException import FailException
from utils.client import RedfishClient
from utils.common import Constant
from utils.model import BaseModule
from utils.tools import init_args


class GetBios(BaseModule):

    def __init__(self):

        super().__init__()
        self.bios = None
        self.args_lst = ["attribute", "file_uri"]

    @property
    def dict(self):

        return self.bios

    def run(self, args):

        init_args(args, self.args_lst)
        if args.file_uri is not None:
            try:
                with open(args.file_uri, 'w'):
                    pass
            except IOError as err:
                self.err_list.append(str(err))
                raise FailException(*self.err_list)
            else:
                os.remove(args.file_uri)
        client = RedfishClient(args)
        systems_id = client.get_systems_id()
        url = "/redfish/v1/Systems/%s/Bios" % systems_id
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and resp.get("status_code", None) ==
                Constant.SUCCESS_200):
            if args.attribute is not None:
                bios_cfg = self.resolve_response(resp, args.attribute)
            else:
                bios_cfg = self.resolve_response(resp)
            if args.file_uri is not None:
                try:
                    with open(args.file_uri, 'w') as file_output:
                        file_output.write(
                            json.dumps(
                                bios_cfg,
                                indent=4,
                                separators=(
                                    ',',
                                    ': ')))
                except (IOError, Exception) as err:
                    self.err_list.append(str(err))
                    raise FailException(*self.err_list)
                else:
                    suc_info = "Success: get BIOS information successfully"
                    self.suc_list.append(suc_info)
                    self.bios = {}
            else:
                self.bios = bios_cfg
        else:
            err = "Failure: failed to get BIOS information"
            self.err_list.append(err)
            raise FailException(*self.err_list)
        return self.suc_list

    def resolve_response(self, resp, attr=None):

        detail = dict()
        if resp["resource"].get("Attributes", None) is not None:
            info = resp["resource"]["Attributes"]
            if info and isinstance(info, dict):
                if attr is None:
                    for key, value in info.items():
                        try:
                            detail[key] = value
                        except (KeyError, ValueError, Exception):
                            pass
                elif attr in info:
                    try:
                        detail[attr] = info.get(attr, None)
                    except (KeyError, ValueError, Exception):
                        pass
                else:
                    err_message = ("Failure: this attribute does not exist: "
                                   "%s" % attr)
                    self.err_list.append(err_message)
                    raise FailException(*self.err_list)
        else:
            err = "Failure: failed to get BIOS information"
            self.err_list.append(err)
            raise FailException(*self.err_list)
        return detail
