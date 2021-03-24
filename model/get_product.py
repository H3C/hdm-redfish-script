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


from collections import OrderedDict
from exception.ToolException import FailException
from utils.client import RedfishClient
from utils.client import RestfulClient
from utils.common import Constant
from utils.model import BaseModule
from utils import globalvar
from utils.predo import GetVersion


class GetProduct(BaseModule):

    def __init__(self):
        super().__init__()
        self.board_serial_number = None
        self.power_overall = None
        self.slot_id = None
        self.model = None
        self.manufacturer = None
        self.host_name = None
        self.serial_number = None
        self.uuid = None
        self.power_state = None
        self.overall_health = None

        self.id = None
        self.name = None
        self.asset_tag = None
        self.indicator_led = None
        self.part_number = None
        self.system_type = None
        self.bios_version = None

        self.status = {}
        self.health_state = OrderedDict()
        self.independent_power_supply = False

    @property
    def dict(self):

        return {
            "board_serial_number": self.board_serial_number,
            "power_overall": self.power_overall,
            "slot_id": self.slot_id,
            "Model": self.model,
            "HostName": self.host_name,
            "Manufacturer": self.manufacturer,
            "SerialNumber": self.serial_number,
            "UUID": self.uuid,
            "PowerState": self.power_state,
            "OverallHealth": self.overall_health,
            "Id": self.id,
            "Name": self.name,
            "AssetTag": self.asset_tag,
            "IndicatorLED": self.indicator_led,
            "PartNumber": self.part_number,
            "SystemType": self.system_type,
            "BiosVersion": self.bios_version,
            "Status": self.status,
            "Healthstate": self.health_state,
            "IndependentPowerSupply": self.independent_power_supply
        }

    @GetVersion()
    def run(self, args):

        client = RestfulClient(args)
        try:

            self._get_fru(client)

            self._get_capping(client)
        finally:
            if client.cookie:
                client.delete_session()
        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            try:
                client = RestfulClient(args)

                self._get_uuid(client)

                self._get_powerstate(client)

                self._get_healthinfo(client)

                self.slot_id = 1
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            systems_id = client.get_systems_id()
            self.slot_id = systems_id
            url = "/redfish/v1/Systems/%s" % systems_id
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                self._pack_system_info(resp["resource"])
            else:
                self.err_list.append("Failure: failed to get product"
                                     "information")
                raise FailException(*self.err_list)
        return self.suc_list

    def _get_fru(self, client):

        url = "/api/fru"
        resp = client.send_request("GET", url)
        if resp is None:
            err_info = "Failure: failed to get mainboard serial number"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        else:
            try:
                self.board_serial_number = resp[0]["board"]["serial_number"]

                self.manufacturer = resp[0]["product"]["manufacturer"]
                self.model = resp[0]["product"]["product_name"]
                self.serial_number = resp[0]["product"]["serial_number"]

            except (IndexError, KeyError, Exception):
                self.board_serial_number = None

    def _get_capping(self, restful):

        url = "/api/power/capping"
        resp = restful.send_request("GET", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_0 == resp.get("cc", None)):
            self.power_overall = resp.get("power_overall", None)
        else:
            err_info = ("Failure: failed to get the total "
                        "power input of the system power")
            self.err_list.append(err_info)
            raise FailException(*self.err_list)

    def _get_uuid(self, restful):

        url = "/api/uuid"
        resp = restful.send_request("GET", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_0 == resp.get("cc", None)):
            self.uuid = resp.get("uuid", None)
        else:
            err_info = ("Failure: failed to get the total "
                        "power input of the system power")
            self.err_list.append(err_info)
            raise FailException(*self.err_list)

    def _get_powerstate(self, restful):

        status_dict = {
            0: "Off",
            1: "On"
        }
        url = "/api/chassis-status"
        resp = restful.send_request("GET", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_0 == resp.get("cc", None)):
            self.power_state = status_dict.get(resp.get("power_status"), None)
        else:
            err_info = ("Failure: failed to get the total "
                        "power input of the system power")
            self.err_list.append(err_info)
            raise FailException(*self.err_list)

    def _get_healthinfo(self, restful):

        status_dict = {
            0: "OK",
            1: "Caution",
            2: "Warning",
            3: "Critical"
        }
        url = "/api/health_info"
        resp = restful.send_request("GET", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_0 == resp.get("cc", None)):
            self.overall_health = status_dict.get(resp.get("health"), None)
        else:
            err_info = ("Failure: failed to get the total "
                        "power input of the system power")
            self.err_list.append(err_info)
            raise FailException(*self.err_list)

    def _pack_system_info(self, resp):

        self.model = resp.get("Model", None)
        self.manufacturer = resp.get("Manufacturer", None)

        if resp.get("SerialNumber", None):
            self.serial_number = resp.get("SerialNumber")
        self.host_name = resp.get("HostName", None)
        self.uuid = resp.get("UUID", None)
        self.power_state = resp.get("PowerState", None)

        if isinstance(resp.get("Healthstate", None), dict):
            health_state = resp["Healthstate"]
            self.overall_health = health_state.get("OverallHealth", None)
            self.health_state = health_state

        self.id = resp.get("Id", None)
        self.name = resp.get("Name", None)
        self.asset_tag = resp.get("AssetTag", None)
        self.indicator_led = resp.get("IndicatorLED", None)
        self.part_number = resp.get("PartNumber", None)
        self.system_type = resp.get("SystemType", None)
        self.bios_version = resp.get("BiosVersion", None)
        if isinstance(resp.get('Status', None), dict):
            self.status["Health"] = resp['Status'].get('Health', None)
            self.status["HealthRollup"] = resp['Status'].get('HealthRollup',
                                                             None)
            self.status["State"] = resp['Status'].get('State', None)
