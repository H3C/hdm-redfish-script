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
from utils.client import RedfishClient
from utils.model import BaseModule
from utils.common import Constant
from utils.predo import get_hdm_firmware

STATUS_DICT = {
    "0": "OK",
    "1": "Caution",
    "2": "Warning",
    "3": "Critical"
}

PCIE_STATUS_DICT = {
    0: "OK",
    1: "Abnormal",
    2: "Absent"
}


class PCIe:

    def __init__(self):

        self.id = None
        self.common_name = None
        self.position = None
        self.slot = None
        self.vendor_id = None
        self.device_id = None
        self.sub_vendor_id = None
        self.sub_device_id = None
        self.current_speed = None
        self.current_bandwidth = None
        self.current_gen_flag = None
        self.max_speed = None
        self.pcie_gen_flag = None
        self.pcie_status = None
        self.productor_name = None
        self.pcie_sn = None
        self.pcie_partnumber = None
        self.support_bandwidth = None
        self.produce_name = None
        self.health = None
        self.slot_bus = None
        self.slot_device = None
        self.slot_function = None
        self.type = None

    @property
    def dict(self):

        return {
            "Id": self.id,
            "Location": self.position,
            "Status": self.pcie_status,
            "ProductName": self.produce_name,
            "VendorID": self.vendor_id,
            "VendorName": self.productor_name,
            "SerialNumber": self.pcie_sn,
            "ProductID": self.device_id,
            "NegotiatedSpeed": self.current_speed,
            "NegotiatedProtocol": self.current_gen_flag,
            "NegotiatedLinkWidth": self.current_bandwidth,
            "MaxSpeed": self.max_speed,
            "MaxProtocol": self.pcie_gen_flag,
            "PartNumber": self.pcie_partnumber,
            "MaxLinkWidth": self.support_bandwidth,
            "Slot": self.slot,
            "Health": self.health,
            "SlotBus": self.slot_bus,
            "SlotDevice": self.slot_device,
            "SlotFunction": self.slot_function,
            "Type": self.type
        }


class GetPCIe(BaseModule):

    def __init__(self):

        super().__init__()
        self.overall_health = None
        self.maximum = None
        self.pcie_device = []

    @property
    def dict(self):

        return {
            "OverallHealth": self.overall_health,
            "Maximum": self.maximum,
            "PCIeDevice": self.pcie_device
        }

    def run(self, args):

        client = RestfulClient(args)
        try:
            self.overall_health = self.get_overall_health(client)
            self.get_pcie_info(client)
            hdm_version = get_hdm_firmware(client)
        finally:
            if client.cookie:
                client.delete_session()

        if not hdm_version < "1.11":
            client = RedfishClient(args)
            pcie_detail = self._get_pcie_devices(client)
            if pcie_detail:
                package_pcie_info(self.pcie_device, pcie_detail)

        return self.suc_list

    def get_overall_health(self, client):

        url = "/api/health_info"
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and
                resp.get(Constant.COMPLETE_CODE, None) == Constant.SUCCESS_0):
            p_health = STATUS_DICT.get(str(resp.get("pcie", None)), None)
        else:
            err_info = "Failure: failed to get overall health status"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return p_health

    def get_pcie_info(self, client):

        url = "/api/system/pcie"
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and
                resp.get(Constant.COMPLETE_CODE, None) == Constant.SUCCESS_0):

            self.maximum = resp.get("pcie_max_num")
            if resp.get("pcie_info", None) is not None:
                if self.maximum is None:
                    self.maximum = len(resp["pcie_info"])
                for i in range(len(resp["pcie_info"])):
                    self.pcie_device.append(
                        package_pcie(resp["pcie_info"][i], i))
        else:
            err_info = "Failure: failed to get pcie information list"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)

    def _get_pcie_devices(self, client):

        systems_id = client.get_systems_id()
        pcie_detail = []

        url = "/redfish/v1/Chassis/%s/PCIeDevices" % systems_id
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and
                resp.get("status_code", None) in Constant.SUC_CODE):
            devices_members = resp["resource"].get("Members", None)
            for member in devices_members:
                url = member.get("@odata.id", None)
                resp = client.send_request("GET", url)
                if (isinstance(resp, dict) and
                        resp.get("status_code", None) in Constant.SUC_CODE):
                    pcie_type = resp["resource"]["Oem"]["Public"].get(
                        "PCIeCardType", None)
                    location = resp["resource"]["Oem"]["Public"].get(
                        "DeviceLocator", None)
                    if location is not None and isinstance(location, str):
                        location = location.replace("Card", "Slot ")
                    if resp["resource"].get("Links") is not None:
                        pcie_functions = resp["resource"]["Links"].get(
                            "PCIeFunctions", None)
                        if isinstance(pcie_functions, dict):
                            url = pcie_functions.get("@odata.id", None)
                        elif isinstance(pcie_functions, list):
                            url = pcie_functions[0].get("@odata.id", None)
                        resp = client.send_request("GET", url)
                        if (isinstance(resp, dict) and resp.get(
                                "status_code", None) in Constant.SUC_CODE):
                            oem_info = resp["resource"]["Oem"]["Public"]
                            oem_info["Type"] = pcie_type
                            oem_info["Location"] = location
                            pcie_detail.append(oem_info)
        return pcie_detail


def package_pcie_info(pcie_device, pcie_detail):

    for member1 in pcie_device:
        for member2 in pcie_detail:
            if member1.slot == int(member2.get("Slot")):
                member1.slot_bus = member2.get("BusNumber")
                member1.slot_device = member2.get("DeviceNumber")
                member1.slot_function = member2.get("FunctionNumber")
                member1.type = member2.get("Type")

                if member1.position == "":
                    member1.position = member2.get("Location")


def package_pcie(service, index):

    detail = dict()
    detail["id"] = index
    detail["slot"] = service.get('slot', None)

    if service.get("position") is not None:
        detail["position"] = service.get('position', None)
    else:
        detail["position"] = service.get('slot', None)
    detail["produce_name"] = service.get('produce_name', None)
    detail["productor_name"] = service.get('productor_name', None)

    detail["max_speed"] = service.get('max_speed', None)
    detail["vendor_id"] = service.get('vendor_id', None)
    detail["device_id"] = service.get('device_id', None)
    detail["pcie_status"] = (
        "Enabled" if service.get("pcie_status") in {0, 1} else "Absent")
    detail["health"] = PCIE_STATUS_DICT.get(service.get("pcie_status"))
    detail["current_speed"] = service.get('current_speed', None)
    detail["current_bandwidth"] = service.get('current_bandwidth', None)
    detail["current_gen_flag"] = service.get('current_gen_flag', None)
    detail["pcie_gen_flag"] = service.get('pcie_gen_flag', None)
    detail["pcie_sn"] = service.get('pcie_sn', None)
    detail["pcie_partnumber"] = service.get('pcie_partnumber', None)
    detail["support_bandwidth"] = service.get('support_bandwidth', None)
    pcie = PCIe()
    pcie.__dict__.update(detail)
    return pcie
