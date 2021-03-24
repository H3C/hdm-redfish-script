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


class NVMe:

    def __init__(self):

        self.slot_id = None
        self.vendor_name = None
        self.product_name = None
        self.pd_status = None
        self.percent_life = None
        self.serial_number = None
        self.model_number = None
        self.capacity = None
        self.firmware_version = None
        self.port_type = None

    @property
    def dict(self):

        return {
            "SlotID": self.slot_id,
            "VendorName": self.vendor_name,
            "ProductName": self.product_name,
            "PDStatus": self.pd_status,
            "PercentLife": self.percent_life,
            "SerialNumber": self.serial_number,
            "ModelNumber": self.model_number,
            "Capacity": self.capacity,
            "FirmwareVersion": self.firmware_version,
            "PortType": self.port_type
        }


class GetNVMeSSD(BaseModule):

    def __init__(self):

        super().__init__()
        self.nvme_device = []

    @property
    def dict(self):

        return {
            "NVMeDevice": self.nvme_device
        }

    def run(self, args):

        client = RestfulClient(args)
        try:
            url = "/api/system/nvmeinfo"
            resp = client.send_request("get", url)
            if (isinstance(resp, dict) and resp.get(Constant.COMPLETE_CODE)
                    == Constant.SUCCESS_0):
                nvme_list = resolve_response(resp)
                if nvme_list:
                    self.nvme_device = nvme_list
                else:
                    suc_info = "Success: NVMe resource is empty"
                    self.suc_list.append(suc_info)
            else:
                err_info = "Failure: failed to get NVMe ssd information"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list


def resolve_response(resp):

    nvme_list = list()
    ssd_list = resp.get("nvme_info", None)
    if ssd_list and isinstance(ssd_list, list):
        for ssd in ssd_list:
            nvme = NVMe()
            detail = dict()
            detail["slot_id"] = ssd.get("slot_id", None)
            detail["vendor_name"] = ssd.get("vendor_name", None)
            detail["product_name"] = ssd.get("product_name", None)
            detail["pd_status"] = ssd.get("pd_status", None)
            detail["percent_life"] = ssd.get("percent_life", None)
            detail["serial_number"] = ssd.get("serial_number", None)
            detail["model_number"] = ssd.get("model_number", None)
            detail["capacity"] = ssd.get("capacity", None)
            detail["firmware_version"] = ssd.get("firmware_version", None)
            detail["port_type"] = ssd.get("port_type", None)
            nvme.__dict__.update(detail)
            nvme_list.append(nvme)
    return nvme_list
