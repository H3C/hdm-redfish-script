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


from exception.ToolException import FailException
from utils.client import RestfulClient
from utils.common import Constant
from utils.model import BaseModule
from utils.tools import init_args


class SetSysBoot(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["dev", "effective", "mode"]

    def run(self, args):

        init_args(args, self.args_lst)
        if args.dev is None and args.effective is None and args.mode is None:
            self.err_list.append("Argument: need at least one parameter")
            raise FailException(*self.err_list)

        restful = RestfulClient(args)
        try:
            url = "/api/config/boot"
            resp = restful.send_request("GET", url)
            if isinstance(resp, dict) and Constant.SUCCESS_0 == resp.get(
                    "cc", None):
                payload = self._construct_param(args, resp)
                resp = restful.send_request("POST", url, payload)
                if isinstance(resp, dict) or Constant.SUCCESS_0 == resp.get(
                        "cc", None):
                    self.suc_list.append(
                        "Success: set system startup item successfully")
                else:
                    self.err_list.append(
                        "Failure: failed to set system startup item")
                    raise FailException(*self.err_list)
            else:
                self.err_list.append(
                    "Failure: failed to get system startup item")
                raise FailException(*self.err_list)
        finally:
            if restful.cookie:
                restful.delete_session()

        return self.suc_list

    @staticmethod
    def _construct_param(args, resp):

        boot_device_dict = {
            "HDD": 0,
            "PXE": 1,
            "BIOSSETUP": 2,
            "CD": 4,
            "none": 7
        }
        boot_mode_dict = {
            "UEFI": 1,
            "Legacy": 0
        }
        effective_mode_dict = {
            "Once": 0,
            "Continuous": 1
        }
        detail = dict()
        detail["dev"] = (boot_device_dict[args.dev] if
                         args.dev is not None else resp.get("dev", None))
        detail["alwaysflag"] = (effective_mode_dict[args.effective] if
                                args.effective is not None else
                                resp.get("alwaysflag", None))
        detail["mode"] = (boot_mode_dict[args.mode] if
                          args.mode is not None else resp.get("mode", None))
        return detail
