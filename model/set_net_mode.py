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

INFO_MESSAGE = {
    0: "Success: set network port mode succeed",
    1: "Failure: failed to set network port adaptive status!",
    2: ("Failure: switching of bonding mode is not supported when vlan is "
        "enabled!"),
    3: "Failure: set network port adaptation and port adaptation conflict",
    4: "Failure: the network port adaptive mode cannot be enabled when "
    "the shared network port lan setting is disabled"
}

MODE_DICT = {
    "Normal": 0,
    "Bond": 1,
    "Adaptive": 2
}


class SetNetMode(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["port_mode"]

    def run(self, args):
        init_args(args, self.args_lst)
        client = RestfulClient(args)
        url = "/api/settings/network_portmode"
        try:
            payload = {"port_mode": MODE_DICT.get(args.port_mode)}
            resp = client.send_request("post", url, payload)
            if (isinstance(resp, dict) and resp.get(Constant.COMPLETE_CODE,
                                                    None) is not None):
                if resp.get(
                        Constant.COMPLETE_CODE,
                        None) == Constant.SUCCESS_0:
                    self.suc_list.append(INFO_MESSAGE.get(Constant.SUCCESS_0))
                else:
                    self.err_list.append(
                        INFO_MESSAGE.get(resp.get(Constant.COMPLETE_CODE)))
                    raise FailException(*self.err_list)
            else:
                err_info = "Failure: set net mode Failed"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list
