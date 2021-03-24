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
from utils.tools import init_args
from utils.predo import get_hdm_firmware

MAX_NUM = False


class Memory:

    def __init__(self):
        self.common_name = None
        self.capacity_mib = None
        self.manufacturer = None
        self.operating_speed_mhz = None
        self.serial_number = None
        self.memory_device_type = None
        self.data_width_bits = None
        self.rank_count = None
        self.part_number = None
        self.technology = None
        self.min_voltage_milli_volt = None
        self.state = None
        self.health = None
        self.position = None
        self.channel = None
        self.slot = None
        self.memory_state = None

    @property
    def dict(self):

        return {
            "CommonName": self.common_name,
            "Location": self.common_name,
            "Manufacturer": self.manufacturer,
            "CapacityMiB": self.capacity_mib,
            "OperatingSpeedMhz": self.operating_speed_mhz,
            "SerialNumber": self.serial_number,
            "MemoryDeviceType": self.memory_device_type,
            "DataWidthBits": self.data_width_bits,
            "RankCount": self.rank_count,
            "PartNumber": self.part_number,
            "Technology": self.technology,
            "MinVoltageMillivolt": self.min_voltage_milli_volt,
            "Position": self.position,
            "Channel": self.channel,
            "Slot": self.slot,
            "State": self.state,
            "Health": self.health,
            "memory_state": self.memory_state
        }


class GetMemory(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["memory_id"]
        self.overall_health = None
        self.maximum = 0
        self.total_system_memory_mib = 0
        self.total_power_watts = None
        self.memory = []

    @property
    def dict(self):

        return {
            "OverallHealth": self.overall_health,
            "Maximum": self.maximum,
            "TotalSystemMemoryGiB": self.total_system_memory_mib // 1024,
            "TotalPowerWatts": self.total_power_watts,
            "Memorys": self.memory
        }

    def run(self, args):

        init_args(args, self.args_lst)
        client = RestfulClient(args)
        try:
            hdm_version = get_hdm_firmware(client)
            self.overall_health = self._get_health_info(client)

            memory_lst = self._get_memory_detail(client)
            self.memory = self.resolve_memory_detail_info(memory_lst, args)
            if not hdm_version < "1.11":
                self.get_info_by_redfish(args)

            if not MAX_NUM:
                self.maximum = len(memory_lst)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def get_info_by_redfish(self, args):

        client = RedfishClient(args)
        systems_id = client.get_systems_id()

        global MAX_NUM
        url = "/redfish/v1/Chassis/%s" % systems_id
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_200 == resp.get("status_code", None)):
            try:
                self.maximum = (resp["resource"]["Oem"]["Public"]
                                ["DeviceMaxNum"].get("MemoryNum"))
                MAX_NUM = True
            except (KeyError, ValueError):
                self.maximum = None

        url = "/redfish/v1/Chassis/%s/Power" % systems_id
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_200 == resp.get("status_code", None)):
            try:
                self.total_power_watts = (resp["resource"]["PowerControl"][0]
                                          ["Oem"]["Public"].
                                          get("CurrentMemoryPowerWatts"))
            except (KeyError, ValueError):
                self.total_power_watts = None

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
            memory_health = status_dict.get(
                str(resp.get("memory", None)), None)
        else:
            self.err_list.append("Failure: failed to get memory health status")
            raise FailException(*self.err_list)
        return memory_health

    def resolve_memory_detail_info(self, resp, args):

        status_dict = {
            0: "Absent",
            1: "OK",
            2: "Abnormal",
            3: "Disabled"
        }
        memory_lst = []
        self.maximum = len(resp)
        for item in resp:
            memory = Memory()
            detail = dict()
            status = item.get("status")

            if status in {0, 3}:
                detail["memory_state"] = Constant.ABSENT
            else:
                detail["memory_state"] = Constant.EXIST
            detail["state"] = ("Disabled" if status == 3 else
                               ("Absent" if status == 0 else "Enabled"))
            detail["health"] = status_dict.get(status)
            memory_location = item.get("memory_location")
            slot_number = item.get("slotnumber")
            detail["slot"] = slot_number
            position = None
            common_name = None
            if isinstance(memory_location, int):
                position = "CPU%s" % (memory_location + 1)
                if slot_number is not None:
                    common_name = "%s%s" % (position, slot_number)
            detail["position"] = position
            detail["common_name"] = common_name
            size = item.get("size", 0)
            self.total_system_memory_mib += size
            detail["capacity_mib"] = size
            detail["manufacturer"] = item.get("manufacture")
            detail["operating_speed_mhz"] = item.get("max_frequency")
            detail["serial_number"] = item.get("memory_sn")
            detail["memory_device_type"] = item.get("type")
            detail["data_width_bits"] = item.get("data_width_bits")
            detail["rank_count"] = item.get("ranks")
            detail["part_number"] = (item.get("part_number").strip() if
                                     isinstance(item.get("part_number"),
                                                str) else None)
            detail["technology"] = item.get("technology")
            detail["min_voltage_milli_volt"] = (
                item.get("min_voltage_milli_volt"))
            detail["channel"] = item.get("channel_number")
            memory.__dict__.update(detail)
            memory_lst.append(memory)
        try:
            memory_lst = sorted(memory_lst,
                                key=lambda s: (s.position, int(s.slot[1:])))
        except (KeyError, IndexError, TypeError, Exception):
            pass
        if args.memory_id is not None:
            memory_lst = list(filter(lambda s: s.slot == args.memory_id,
                                     memory_lst))
            if not memory_lst:
                err_info = "Failure: resource was not found"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            for memory in memory_lst:
                if memory.state not in {"Absent", "Disabled"}:
                    break
            else:
                err_info = "Failure: resource was not found"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        return memory_lst

    def _get_memory_detail(self, client):

        memory_lst = []
        url = "/api/system/memory_detail"
        resp = client.send_request("GET", url)
        if isinstance(resp, list):
            memory_lst.extend(resp)
        else:
            err_info = "Failure: failed to get memory collection information"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return memory_lst
