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


class Nic:

    def __init__(self):
        self.network_port = None
        self.device_type = None
        self.product_name = None
        self.embedded = None
        self.firmware_version = None
        self.mac_address = None
        self.status = None

        self.speed = None

    @property
    def dict(self):

        return self.__dict__

    def pack_nic_resource(self, resp):

        self.network_port = resp.get('network_port', None)
        self.device_type = resp.get('device_type', None)
        self.product_name = resp.get('product_name', None)
        self.embedded = resp.get('embedded', None)
        self.firmware_version = resp.get('firmware_version', None)
        self.mac_address = resp.get('mac_address', None)
        self.status = resp.get('status', None)

        self.speed = resp.get('speed', None)


class GetNic(BaseModule):

    def __init__(self):
        super().__init__()

        self.overall_health = None
        self.maximum = None
        self.nics = []

    @property
    def dict(self):

        return {
            "OverallHealth": self.overall_health,
            "Maximum": self.maximum,
            "nics": self.nics
        }

    def run(self, args):

        client = RestfulClient(args)
        try:

            self._get_health_info(client)

            url = "/api/system/nic"
            resp = client.send_request("GET", url)
        finally:
            if client.cookie:
                client.delete_session()

        if isinstance(resp, dict) and Constant.SUCCESS_0 == resp.get("cc",
                                                                     None):
            nic_info = resp.get("nic_info", None)
            if not nic_info:
                suc_info = "Success: the NIC list is empty"
                self.suc_list.append(suc_info)
            else:
                self.maximum = len(self.suc_list)
                for info in nic_info:
                    nic = Nic()
                    nic.pack_nic_resource(info)
                    self.nics.append(nic)
        else:
            self.err_list.append("Failure: failed to get nic information list")
            raise FailException(*self.err_list)
        return self.suc_list

    def _get_health_info(self, client):
        status_dict = {
            "0": "OK",
            "1": "Caution",
            "2": "Warning",
            "3": "Critical"
        }
        url = "/api/health_info"
        resp = client.send_request("GET", url)
        if isinstance(resp, dict) and Constant.SUCCESS_0 == resp.get("cc",
                                                                     None):
            psu_health = status_dict.get(str(resp.get("nic", None)), None)
            self.overall_health = psu_health
        else:
            self.err_list.append(
                "Failure: failed to get overall health status")
            raise FailException(*self.err_list)
