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
from utils.model import BaseModule
from utils.client import RestfulClient
from utils.common import Constant
from utils.tools import init_args


class PowerControl(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["command_type"]

    def run(self, args):

        init_args(args, self.args_lst)
        url = "/api/chassis-status"
        client = RestfulClient(args)
        try:
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and resp.get("cc", None) ==
                    Constant.SUCCESS_0):
                payload = self.construct_request_parameters(resp, args)
                url = "/api/actions/power"
                sec_resp = client.send_request("POST", url, payload)
                if (isinstance(sec_resp, dict) and sec_resp.get("cc", None) ==
                        Constant.SUCCESS_0):
                    operator_suc = ("Success: power control request "
                                    "succeeded: %s" %
                                    args.command_type)
                    self.suc_list.append(operator_suc)
                else:
                    err_info = "Failure: system power control failed"
                    self.err_list.append(err_info)
                    raise FailException(*self.err_list)
            else:
                err_info = "Failure: failed to get current system power status"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def construct_request_parameters(self, resp, args):

        power_command = {
            "ForceOff": 0,
            "On": 1,
            "ForcePowerCycle": 2,
            "ForceReset": 3,
            "GracefulShutdown": 5
        }
        current_status = resp.get("power_status", None)
        if current_status is not None:
            if ((current_status == 1 and power_command[args.command_type] == 1)
                    or (current_status == 0 and
                        (power_command[args.command_type] in {0, 2, 3, 5}))):
                err_info = ("Failure: command is not available in "
                            "current system power state")
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        payload = {"power_command": power_command[args.command_type]}
        return payload
