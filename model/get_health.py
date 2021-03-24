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


class GetHealth(BaseModule):

    def __init__(self):
        super().__init__()
        self.health = None
        self.processor = None
        self.memory = None
        self.disk = None
        self.nic = None
        self.power = None
        self.fans = None

        self.temperature = None
        self.volatge = None
        self.current = None

        self.board = None
        self.nvme = None
        self.pcie = None
        self.raid = None

        self.second_psu_fault = None

    @property
    def dict(self):

        return self.__dict__

    def run(self, args):

        client = RestfulClient(args)
        try:
            url = "/api/health_info"
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and
                    Constant.SUCCESS_0 == resp.get("cc", None)):
                self._pack_resource(resp)
            else:
                err_info = "Failure: failed to get system health status"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()

        return self.suc_list

    def _pack_resource(self, resp):

        status_dict = {
            "0": "OK",
            "1": "Caution",
            "2": "Warning",
            "3": "Critical"
        }

        nic_status_dict = {
            "0": "OK",
            "1": "Absent",
            "2": "Critical",
            "3": "Present"
        }

        self.health = status_dict.get(str(resp.get("health", None)), None)
        self.processor = status_dict.get(
            str(resp.get("processor", None)), None)
        self.memory = status_dict.get(str(resp.get("memory", None)), None)
        self.disk = status_dict.get(str(resp.get("disk", None)), None)
        self.nic = nic_status_dict.get(str(resp.get("nic", None)), None)
        self.power = status_dict.get(str(resp.get("power", None)), None)
        self.fans = status_dict.get(str(resp.get("fans", None)), None)

        self.temperature = status_dict.get(str(resp.get("temperature", None)),
                                           None)
        self.voltage = status_dict.get(str(resp.get("volatge", None)), None)
        self.current = status_dict.get(str(resp.get("current", None)), None)

        self.board = status_dict.get(str(resp.get("board", None)), None)
        self.nvme = resp.get("nvme", None)
        self.pcie = status_dict.get(str(resp.get("pcie", None)), None)
        self.raid = status_dict.get(str(resp.get("raid", None)), None)
        self.second_psu_fault = status_dict.get(
            str(resp.get("second_psu_fault", None)), None)
