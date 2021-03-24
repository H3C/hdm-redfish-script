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
from utils.client import RedfishClient
from utils.client import RestfulClient
from utils.common import Constant
from utils.model import BaseModule
from utils import globalvar
from utils.predo import GetVersion

HEALTH_DICT = {
    4: "Critical",
    3: "OK"
}

STATUS_DICT = {
    1: "Enabled",
    0: "Disabled"
}

STANDBY_DICT = {
    0: "Active",
    1: "Passive"
}

POWER_DICT = {
    "0": "OK",
    "1": "Caution",
    "2": "Warning",
    "3": "Critical"
}


class PSU:

    def __init__(self):
        self.psu_state = None
        self.id = None
        self.common_name = None
        self.location = "Chassis"
        self.model = None
        self.manufacturer = None
        self.protocol = "PMBus"
        self.power_output_watts = None
        self.input_amperage = None
        self.active_standby = None
        self.output_voltage = None
        self.power_input_watts = None
        self.output_amperage = None
        self.part_number = None
        self.power_supply_type = None
        self.line_input_voltage = None
        self.power_capacity_watts = None
        self.firmware_version = None
        self.serial_number = None
        self.health = None
        self.state = None
        self.name = None
        self.line_input_voltage_type = None
        self.power_id = None
        self.original_serial_number = None
        self.slot_number = None

    @property
    def dict(self):

        return {
            "psu_state": self.psu_state,
            "id": self.id,
            "CommonName": self.common_name,
            "Location": self.location,
            "Model": self.model,
            "Manufacturer": self.manufacturer,
            "Protocol": self.protocol,
            "PowerOutputWatts": self.power_output_watts,
            "InputAmperage": self.input_amperage,
            "ActiveStandby": self.active_standby,
            "OutputVoltage": self.output_voltage,
            "PowerInputWatts": self.power_input_watts,
            "OutputAmperage": self.output_amperage,
            "PartNumber": self.part_number,
            "PowerSupplyType": self.power_supply_type,
            "LineInputVoltage": self.line_input_voltage,
            "PowerCapacityWatts": self.power_capacity_watts,
            "FirmwareVersion": self.firmware_version,
            "SerialNumber": self.serial_number,
            "Health": self.health,
            "State": self.state,

            "Name": self.name,
            "LineInputVoltageType": self.line_input_voltage_type,
            "PowerID": self.power_id,
            "OriginalSerialNumber": self.original_serial_number,
            "SlotNumber": self.slot_number
        }

    def get_power_id(self):

        return self.power_id

    def pack_power_supply(self, resp):

        self.psu_state = Constant.EXIST
        self.firmware_version = resp.get("FirmwareVersion", None)
        self.line_input_voltage_type = resp.get("LineInputVoltageType", None)
        self.manufacturer = resp.get("Manufacturer", None)
        self.model = resp.get("Model", None)
        self.name = resp.get("Name", None)
        self.common_name = self.name
        self.power_capacity_watts = resp.get("PowerCapacityWatts", None)
        self.power_supply_type = resp.get("PowerSupplyType", None)
        self.serial_number = resp.get("SerialNumber", None)
        self.power_id = resp['Oem']['Public'].get('PowerID', None)
        self.slot_number = resp['Oem']['Public'].get('SlotNumber', None)
        self.active_standby = resp['Oem']['Public'].get('ActiveStandby', None)
        if isinstance(resp.get("Status", None), dict):
            self.health = resp["Status"].get("Health", None)
            self.state = resp["Status"].get("State", None)

    def pack_b01_power_supply(self, resp):

        self.psu_state = Constant.EXIST
        self.firmware_version = resp.get("version", None)
        self.model = resp.get("model", None)
        self.serial_number = resp.get("serial", None)
        self.power_id = str(resp.get("id", None))
        self.common_name = "PSU%s" % resp.get("id", None)
        self.health = HEALTH_DICT.get(resp.get("input_mode"), None)
        self.state = STATUS_DICT.get(resp.get("present"), None)

    def pack_b01_power_standby(self, resp):

        self.active_standby = STANDBY_DICT.get(resp.get('power_standby'), None)

    def update_psu_persent(self, resp):

        self.id = int(resp.get("id", None))
        self.power_output_watts = resp.get("PowerOutputWatts", None)
        self.output_voltage = resp.get("OutputVoltage", None)
        self.output_amperage = resp.get("OutputAmperage", None)
        self.power_input_watts = resp.get("PowerInputWatts", None)
        self.input_amperage = resp.get("InputAmperage", None)
        self.line_input_voltage = resp.get("LineInputVoltage", None)

        self.manufacturer = resp.get("Manufacturer", None)
        self.power_capacity_watts = resp.get("PowerCapacityWatts", None)
        if resp.get("SerialNumber") != "null":
            self.original_serial_number = resp.get("SerialNumber")

    def update_psu_absent(self, resp):

        self.psu_state = Constant.ABSENT
        self.id = int(resp.get("id", None))
        self.common_name = "PSU%s" % resp.get("id", None)
        self.state = "Absent"


class GetPSU(BaseModule):

    def __init__(self):
        super().__init__()

        self.overall_health = None
        self.maximum = None
        self.psus = []

    @property
    def dict(self):
        return {
            "OverallHealth": self.overall_health,
            "Maximum": self.maximum,
            "PSUS": self.psus
        }

    @GetVersion()
    def run(self, args):

        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                psu = self._get_b01_power_supply(client)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            psu = self._get_power_supply(client)
        try:
            client = RestfulClient(args)

            self._get_health_info(client)
        finally:
            if client.cookie:
                client.delete_session()
        self.psus = psu
        self.maximum = len(self.psus)
        return self.suc_list

    @staticmethod
    def _reload_resp(redfish_psu, ipmi_psu):

        psu_list = list()
        for power in ipmi_psu["PSU"].values():
            flag = False
            for psu in redfish_psu:
                if psu.get_power_id() == str(power.get("id", None)):
                    psu.update_psu_persent(power)
                    psu_list.append(psu)
                    flag = True
                    break
            if not flag:
                psu = PSU()
                psu.update_psu_absent(power)
                psu_list.append(psu)
        return psu_list

    def _get_health_info(self, restful):

        url = "/api/health_info"
        resp = restful.send_request("GET", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_0 == resp.get("cc", None)):
            psu_health = POWER_DICT.get(str(resp.get("power", None)), None)
            self.overall_health = psu_health
        else:
            self.err_list.append("Failure: failed to get overall health "
                                 "status information")
            raise FailException(*self.err_list)

    def _get_power_supply(self, client):

        redfish_psu = list()
        systems_id = client.get_systems_id()
        url = "/redfish/v1/Chassis/%s/Power" % systems_id
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and
                resp.get("status_code", None) in Constant.SUC_CODE):
            if isinstance(resp["resource"].get("PowerSupplies", None), list):
                power_supplies = resp["resource"]["PowerSupplies"]
                for power in power_supplies:
                    psu = PSU()
                    psu.pack_power_supply(power)
                    redfish_psu.append(psu)
        else:
            self.err_list.append("Failure: failed to get power supply "
                                 "information")
            raise FailException(*self.err_list)

        return redfish_psu

    def _get_b01_power_supply(self, client):

        restful_psu = list()
        url1 = "/api/system/hardware_power"
        url2 = "/api/power/standby"
        try:
            resp1 = client.send_request("GET", url1)
            resp2 = client.send_request("GET", url2)
            if isinstance(resp1, list):
                for power in resp1:
                    psu = PSU()
                    psu.pack_b01_power_supply(power)
                    for standby in resp2:
                        if standby.get("power_id") == power.get("id"):
                            psu.pack_b01_power_standby(standby)
                    restful_psu.append(psu)
            else:
                self.err_list.append("Failure: failed to get power supply "
                                     "information")
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return restful_psu
