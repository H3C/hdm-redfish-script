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

MODE_DICT = {
    "Optimal": 0,
    "Increased": 1,
    "Maximum": 2,
    "Custom": 3
}


class SetFan(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["mode", "gear"]

    def run(self, args):

        init_args(args, self.args_lst)
        url = "/api/config/fan"
        payload = self.check_args(args)
        client = RestfulClient(args)
        try:
            resp = client.send_request('POST', url, payload)
            if (isinstance(resp, dict) and resp.get("cc", None) ==
                    Constant.SUCCESS_0):
                suc_info = "Success: fan speed control successfully"
                self.suc_list.append(suc_info)
            else:
                err_info = "Failure: fan speed control failed"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def check_args(self, args):

        mode = MODE_DICT[args.mode]
        fan_mode = None

        if args.mode != "Custom":
            if args.gear is not None:
                err_info = ("Argument: gear parameters are not available in "
                            "non-custom mode")
                self.err_list.append(err_info)
            else:
                fan_mode = 1 if mode == 0 else (4 if mode == 1 else 20)
        else:
            if args.gear is None:
                err_info = ("Argument: in the custom mode, "
                            "the gear parameter cannot be empty")
                self.err_list.append(err_info)
            elif args.gear > 20 or args.gear < 1:
                err_info = 'Argument: invalid choice: %s ' \
                           '(choose from 1 to 20)' % args.gear
                self.err_list.append(err_info)
            else:
                fan_mode = args.gear
        if self.err_list:
            raise FailException(*self.err_list)
        config_dict = {
            "fan_mode": fan_mode,
            "mode": mode
        }
        return config_dict
