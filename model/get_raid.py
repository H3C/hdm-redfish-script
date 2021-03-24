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
from utils.client import RedfishClient, RestfulClient
from utils.common import Constant
from utils.model import BaseModule
from utils import globalvar
from utils.predo import GetVersion


class Controller:

    def __init__(self):
        self.member_id = None
        self.manufacturer = None
        self.model = None
        self.supported_device_protocols = None
        self.sas_address = None
        self.firmware_version = None
        self.maintain_pd_fail_history = None
        self.copy_back_state = None
        self.jbod_state = None
        self.min_stripe_size_bytes = None
        self.max_stripe_size_bytes = None
        self.memory_size_mib = None
        self.supported_raid_levels = None
        self.ddrecc_count = None
        self.temperature_celsius = None
        self.package_version = None

    @property
    def dict(self):

        return {
            "MemberId": self.member_id,
            "Manufacturer": self.manufacturer,
            "Model": self.model,
            "SupportedDeviceProtocols": self.supported_device_protocols,
            "SASAddress": self.sas_address,
            "FirmwareVersion": self.firmware_version,
            "MaintainPDFailHistory": self.maintain_pd_fail_history,
            "CopyBackState": self.copy_back_state,
            "JBODState": self.jbod_state,
            "MinStripeSizeBytes": self.min_stripe_size_bytes,
            "MaxStripeSizeBytes": self.max_stripe_size_bytes,
            "MemorySizeMiB": self.memory_size_mib,
            "SupportedRAIDLevels": self.supported_raid_levels,
            "DDRECCCount": self.ddrecc_count,
            "TemperatureCelsius": self.temperature_celsius,
            "PackageVersion": self.package_version
        }

    def pack_ctrl(self, controller):

        self.member_id = controller.get("MemberId", None)
        self.manufacturer = controller.get("Manufacturer", None)
        self.model = controller.get("Name", None)
        self.supported_device_protocols = (
            controller.get("SupportedDeviceProtocols", None))
        self.firmware_version = controller.get("FirmwareVersion", None)
        self.maintain_pd_fail_history = controller.get("MaintainPDFailHistory")
        self.copy_back_state = controller.get("CopyBackState", None)
        if (controller.get("Oem", None) and
                isinstance(controller["Oem"].get("Public", None), dict)):
            oem_info = controller["Oem"]["Public"]
            self.jbod_state = oem_info.get("JBODState", None)
            self.package_version = oem_info.get("PackageVersion", None)
            self.min_stripe_size_bytes = oem_info.get("MinStripeSizeBytes",
                                                      None)
            self.max_stripe_size_bytes = oem_info.get("MaxStripeSizeBytes",
                                                      None)

            if self.maintain_pd_fail_history is None:
                self.maintain_pd_fail_history = oem_info.get(
                    "MaintainPDFailHistory", None)
            if self.copy_back_state is None:
                self.copy_back_state = oem_info.get("CopyBackState", None)
            if oem_info.get("DDRECCCount", None) is not None:
                self.ddrecc_count = oem_info.get("DDRECCCount")
            else:
                self.ddrecc_count = controller.get("DDRECCCount", None)

            self.memory_size_mib = oem_info.get("MemorySizeMiB", None)
            if oem_info.get("SupportedRAIDLevels", None) is not None:
                self.supported_raid_levels = (
                    ", ".join(oem_info["SupportedRAIDLevels"]))
            self.sas_address = oem_info.get("SASAddress", None)
        self.temperature_celsius = controller.get("TemperatureCelsius", None)


class Raid:

    def __init__(self):
        self.name = None
        self.location = "mainboard"
        self.manufacturer = None
        self.serial_number = None
        self.state = None
        self.health = None
        self.controller = []

    @property
    def dict(self):

        return {
            "Name": self.name,
            "Location": self.location,
            "Manufacturer": self.manufacturer,
            "SerialNumber": self.serial_number,
            "State": self.state,
            "Health": self.health,
            "Controller": self.controller
        }

    def pack_raid_resource(self, resp):

        self.name = resp.get("Name", None)
        raid_ctrls = resp.get("StorageControllers", None)
        if isinstance(raid_ctrls, list):
            for controller in raid_ctrls:
                ctrl = Controller()
                ctrl.pack_ctrl(controller)
                self.controller.append(ctrl)
                self.serial_number = controller.get("SerialNumber", None)
                self.manufacturer = controller.get("Manufacturer", None)
                if controller.get("Status", None):
                    self.state = controller["Status"].get("State", None)
                    self.health = controller["Status"].get("Health", None)


class GetRaid(BaseModule):

    def __init__(self):
        super().__init__()
        self.overall_health = None
        self.maximum = None
        self.raids = []

    @property
    def dict(self):

        return {
            "OverallHealth": self.overall_health,
            "Maximum": None,
            "Raids": self.raids
        }

    @GetVersion()
    def run(self, args):

        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                self._get_b01_raid(client)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            self._get_raid(client)
        if self.suc_list:
            return self.suc_list
        client = RestfulClient(args)
        try:

            self._get_health_info(client)
        finally:
            if client.cookie:
                client.delete_session()
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
        if (isinstance(resp, dict) and
                Constant.SUCCESS_0 == resp.get("cc", None)):
            raid_health = status_dict.get(str(resp.get("disk", None)), None)
            self.overall_health = raid_health
        else:
            self.err_list.append("Failure: failed to get overall health "
                                 "status information")
            raise FailException(*self.err_list)

    def _get_raid(self, client):

        systems_id = client.get_systems_id()
        url = "/redfish/v1/Systems/%s/Storages" % systems_id
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and
                resp.get("status_code", None) in Constant.SUC_CODE):
            raid_members = resp["resource"].get("Members", None)
            if not raid_members:
                self.suc_list.append("Success: raid card resource is empty")
                return
            for member in raid_members:
                url = member.get("@odata.id", None)
                resp = client.send_request("GET", url)
                if (isinstance(resp, dict) and
                        resp.get("status_code", None) in Constant.SUC_CODE):
                    raid = Raid()
                    raid.pack_raid_resource(resp["resource"])
                    self.raids.append(raid)
                else:
                    self.err_list.append("Failure: failed to get raid card "
                                         "details")
                    raise FailException(*self.err_list)
        else:
            self.err_list.append("Failure: failed to get raid card"
                                 " collection information")
            raise FailException(*self.err_list)

    def _get_b01_raid(self, client):

        try:
            url = "/api/settings/storageinfo"
            resp1 = client.send_request("GET", url)
            if isinstance(resp1, dict) and \
                    Constant.SUCCESS_0 == resp1.get("cc"):
                raid_members = resp1.get("adapter")
                if not raid_members:
                    self.suc_list.append(
                        "Success: raid card resource is empty")
                    return
                raid = Raid()
                ctrl = Controller()
                name = raid_members.get("type")
                raid.name = name
                raid.serial_number = raid_members.get("serial")
                url = "/api/system/pcie"
                resp2 = client.send_request("GET", url)
                if isinstance(resp2, dict) and Constant.SUCCESS_0 == \
                        resp1.get("cc"):
                    pcie_members = resp2.get("pcie_info", None)
                    for member in pcie_members:
                        if member.get("produce_name") == name:
                            raid.location = member.get("slot", None)
                            ctrl.member_id = member.get("device_id", None)
                            ctrl.model = name
                            ctrl.memory_size_mib = \
                                raid_members.get("ddr_size", None)
                            raid.controller.append(ctrl)

                self.raids.append(raid)
            else:
                self.err_list.append("Failure: failed to get raid card"
                                     " collection information")
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
