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

MODE_DICT = {
    0: "Normal mode",
    1: "Bonding mode",
    2: "Active/standby mode"
}


class GetNetMode(BaseModule):

    def __init__(self):

        super().__init__()
        self.net_mode = None

    @property
    def dict(self):

        return {
            "NetPortMode": self.net_mode
        }

    def run(self, args):

        client = RestfulClient(args)
        url = "/api/settings/network_portmode"
        try:
            resp = client.send_request("get", url)
            if (isinstance(resp, dict) and
                    resp.get(Constant.COMPLETE_CODE,
                             None) == Constant.SUCCESS_0):
                self.net_mode = MODE_DICT.get(resp.get("port_mode"))
            else:
                err_info = ("Failure: failed to get network port mode "
                            "information")
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list
