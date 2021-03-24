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
from utils import globalvar
from utils.predo import GetVersion
from utils.predo import AllowCommand


STATUS_DICT = {
    "on": 1,
    "off": 0
}


def construct_param(args):

    detail = dict()
    if globalvar.HDM_VERSION < "2.12.00":
        url = "/api/hdd_led"
        detail["sensor_number"] = args.disk_id
        detail["sensor_name"] = "" if args.location is None else args.location
        detail["led_status"] = STATUS_DICT.get(args.led_state)
    else:
        url = "/api/hdd/led"
        detail["instance"] = args.disk_id
        detail["disk_type"] = 1 if args.location == "1" else 0
        detail["led_status"] = STATUS_DICT.get(args.led_state)
    return url, detail


class LocateDisk(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["led_state", "location", "disk_id"]

    @GetVersion()
    @AllowCommand()
    def run(self, args):

        init_args(args, self.args_lst)
        restful = RestfulClient(args)
        try:
            url, payload = construct_param(args)
            resp = restful.send_request("POST", url, payload)
            if isinstance(resp, dict) and Constant.SUCCESS_0 == resp.get(
                    "cc", None):
                self.suc_list.append(
                    "Success: set the physical disk led light successfully")
            else:
                self.err_list.append(
                    "Failure: failed to set the physical disk led light")
                raise FailException(*self.err_list)
        finally:
            if restful.cookie:
                restful.delete_session()

        return self.suc_list
