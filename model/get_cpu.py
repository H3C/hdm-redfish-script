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
from utils.common import Constant
from utils.model import BaseModule
from utils.tools import init_args
from model.get_sensor import GetSensor
from utils import globalvar
from utils.predo import GetVersion


CPU_ID_IS_START_FROM_ONE = True
MAX_NUM = False


class CPU:

    def __init__(self):

        self.id = None
        self.common_name = None
        self.name = None
        self.location = "mainboard"
        self.model = None
        self.manufacturer = None
        self.l1_cache_kib = None
        self.l2_cache_kib = None
        self.l3_cache_kib = None
        self.temperature = None
        self.frequency_mhz = None
        self.enabled_setting = None
        self.processor_type = None
        self.processor_architecture = None
        self.instruction_set = None
        self.max_speed_mhz = None
        self.total_cores = None
        self.total_threads = None
        self.socket = None
        self.ppin = None
        self.state = None
        self.health = None
        self.identification_registers = None
        self.cpu_state = None

    @property
    def dict(self):

        return {
            "Id": self.id,
            "CommonName": self.common_name,
            "Name": self.name,
            "Location": self.location,
            "Model": self.model,
            "Manufacturer": self.manufacturer,
            "L1CacheKiB": self.l1_cache_kib,
            "L2CacheKiB": self.l2_cache_kib,
            "L3CacheKiB": self.l3_cache_kib,
            "Temperature": self.temperature,
            "FrequencyMHz": self.frequency_mhz,
            "EnabledSetting": self.enabled_setting,
            "ProcessorType": self.processor_type,
            "ProcessorArchitecture": self.processor_architecture,
            "InstructionSet": self.instruction_set,
            "MaxSpeedMHz": self.max_speed_mhz,
            "TotalCores": self.total_cores,
            "TotalThreads": self.total_threads,
            "Socket": self.socket,
            "Ppin": self.ppin,
            "State": self.state,
            "Health": self.health,
            "IdentificationRegisters": self.identification_registers,
            "cpu_state": self.cpu_state
        }

    def pack_redfish_resource(self, resp):

        self.cpu_state = Constant.EXIST
        self.id = resp.get("Id", None)
        self.name = resp.get("Name", None)
        if (resp.get("Oem", None) and
                isinstance(resp["Oem"].get("Public", None), dict)):
            self.l1_cache_kib = resp["Oem"]["Public"].get("L1CacheKiB", None)
            self.l2_cache_kib = resp["Oem"]["Public"].get("L2CacheKiB", None)
            self.l3_cache_kib = resp["Oem"]["Public"].get("L2CacheKiB", None)
            self.temperature = resp["Oem"]["Public"].get("Temperature", None)
            self.frequency_mhz = resp["Oem"]["Public"].get(
                "FrequencyMHz", None)
        self.processor_type = resp.get("ProcessorType", None)
        self.processor_architecture = resp.get("ProcessorArchitecture", None)
        self.instruction_set = resp.get("InstructionSet", None)
        self.manufacturer = resp.get("Manufacturer", None)

        self.model = resp.get("Model", None)
        self.max_speed_mhz = resp.get("MaxSpeedMHz", None)
        self.total_cores = resp.get("TotalCores", None)
        self.total_threads = resp.get("TotalThreads", None)
        self.socket = resp.get("Socket", None)
        if resp.get("Status", None):
            self.health = resp["Status"].get("Health", None)
            self.state = resp["Status"].get("State", None)
        self.enabled_setting = (self.state == "Enabled")
        if resp.get("ProcessorId", None):
            self.identification_registers = (resp['ProcessorId'].get(
                "IdentificationRegisters", None))
        self.ppin = resp.get("Ppin", None)

    def pack_restful_resource(self, resp):

        status_dict = {
            0: "Disabled",
            1: "Enabled"
        }
        health_dict = {
            1: "OK",
            2: "WARNING",
            3: "CRITICAL"
        }
        self.id = resp.get("processor_index", None)
        self.l1_cache_kib = resp.get("internal_l1_cache", None)
        self.l2_cache_kib = resp.get("internal_l2_cache", None)
        self.l3_cache_kib = resp.get("internal_l3_cache", None)
        self.frequency_mhz = resp.get("FrequencyMHz", None)
        self.processor_type = "CPU"

        self.processor_architecture = "X86"

        self.instruction_set = "X86-64"

        if resp.get("processor_name", None) is not None:
            manufacturer = resp.get("processor_name").split(" ")
            self.manufacturer = manufacturer[0] + " Corporation"
        self.model = resp.get("processor_name", None)
        self.max_speed_mhz = resp.get("processor_speed", None)
        self.total_cores = resp.get("core_num", None)
        self.total_threads = resp.get("threads", None)
        self.socket = resp.get("processor_index", None)
        self.state = status_dict.get(
            resp.get("processor_install_status"), None)
        self.health = health_dict.get(resp.get("processor_status"), None)
        self.enabled_setting = (self.state == "Enabled")
        if resp.get("ProcessorId", None):
            self.identification_registers = (resp['ProcessorId'].get(
                "IdentificationRegisters", None))
        self.ppin = resp.get("Ppin", None)

    def pack_cpu_absent(self, rt_cpu):

        if isinstance(rt_cpu.get("processor_index", None), int):
            tmp_id = rt_cpu["processor_index"]
            if not CPU_ID_IS_START_FROM_ONE:
                tmp_id += 1
            self.common_name = "CPU%s" % tmp_id
        else:
            self.common_name = None
        self.state = "Absent"
        self.cpu_state = Constant.ABSENT


class GetCpu(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["cpu_id"]
        self.overall_health = None
        self.maximum = None
        self.total_power_watts = None
        self.cpus = []

    @property
    def dict(self):

        return {
            "OverallHealth": self.overall_health,
            "Maximum": self.maximum,
            "TotalPowerWatts": self.total_power_watts,
            "CPUS": self.cpus
        }

    @GetVersion()
    def run(self, args):

        init_args(args, self.args_lst)
        restful = RestfulClient(args)
        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            self.cpus = self._get_b01_processor(restful, args)
        else:
            redfish = RedfishClient(args)
            redfish_cpu = self._get_processor(redfish, args)
        try:

            self._get_health_info(restful)
            restful_cpu = self._get_hardware_cpu(restful)
            if is_adapt_b01 is not True:

                if not restful_cpu:
                    return self.suc_list
                self.cpus = self._pack_cpu_resource(restful_cpu, redfish_cpu)
        finally:
            if restful.cookie:
                restful.delete_session()
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
        if isinstance(resp, dict) and Constant.SUCCESS_0 == resp.get("cc"):
            psu_health = status_dict.get(str(resp.get("processor")), None)
            self.overall_health = psu_health
        else:
            self.err_list.append("Failure: failed to get cpu health status")
            raise FailException(*self.err_list)

    def _get_processor(self, client, args):

        cpu_list = list()
        systems_id = client.get_systems_id()

        global MAX_NUM
        url = "/redfish/v1/Chassis/%s" % systems_id
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_200 == resp.get("status_code", None)):
            try:
                self.maximum = (resp["resource"]["Oem"]["Public"]
                                ["DeviceMaxNum"].get("CPUNum"))
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
                                          get("CurrentCPUPowerWatts"))
            except (KeyError, ValueError):
                self.total_power_watts = None
        url = "/redfish/v1/Systems/%s/Processors" % systems_id
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_200 == resp.get("status_code", None)):
            members = resp["resource"].get("Members", None)
            for member in members:
                url = member.get("@odata.id", None)
                resp = client.send_request("GET", url)
                if (isinstance(resp, dict) and
                        Constant.SUCCESS_200 == resp.get("status_code", None)):
                    if args.cpu_id is None:
                        cpu = CPU()
                        cpu.pack_redfish_resource(resp["resource"])
                        cpu_list.append(cpu)
                    elif args.cpu_id == resp["resource"].get("Id", None):
                        cpu = CPU()
                        cpu.pack_redfish_resource(resp["resource"])
                        cpu_list.append(cpu)
                        break
                else:
                    self.err_list.append("Failure: failed to get cpu "
                                         "information")
                    raise FailException(*self.err_list)
            try:
                cpu_list = sorted(cpu_list, key=lambda s: s.id)
            except (KeyError, ValueError, Exception) as err:
                self.err_list.append(str(err))
                raise FailException(*self.err_list)
        else:
            self.err_list.append("Failure: failed to get system CPUs "
                                 "information")
            raise FailException(*self.err_list)
        if not cpu_list:
            err_info = "Failure: resource was not found"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return cpu_list

    def _get_b01_processor(self, client, args):

        cpu_list = list()
        url = "/api/system/processor"
        resp = client.send_request("GET", url)
        i = 1
        if isinstance(resp, list):
            for info in resp:
                if isinstance(info, dict):
                    cpu = CPU()
                    cpu.name = "CPU%s" % (str(i))
                    cpu.temperature = self._get_temp(client, cpu.name)
                    cpu.pack_restful_resource(info)
                    cpu_list.append(cpu)
                    i = i + 1
                else:
                    self.err_list.append("Failure: failed to get cpu "
                                         "information")
                    raise FailException(*self.err_list)
            try:
                cpu_list = sorted(cpu_list, key=lambda s: s.id)
            except (KeyError, ValueError, Exception) as err:
                self.err_list.append(str(err))
                raise FailException(*self.err_list)
        else:
            self.err_list.append("Failure: failed to get system CPUs "
                                 "information")
            raise FailException(*self.err_list)
        if not cpu_list:
            err_info = "Failure: resource was not found"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return cpu_list

    def _get_temp(self, client, cpu_name):
        sensors = GetSensor.get_hardware_sensor(self, client)
        for sensor in sensors:
            if cpu_name in sensor.get("name"):
                return sensor.get("raw_reading")
        return None

    def _get_hardware_cpu(self, client):

        cpu_list = []
        url = "/api/system/processor"
        resp = client.send_request("GET", url)
        if isinstance(resp, list):
            if not resp:
                self.suc_list.append("Failure: CPU resource is empty")
            else:

                if not MAX_NUM:
                    self.maximum = len(resp)
                for cpu in resp:
                    if cpu.get("processor_index") == 0:
                        global CPU_ID_IS_START_FROM_ONE
                        CPU_ID_IS_START_FROM_ONE = False
                        break
                cpu_list.extend(resp)
        else:
            self.err_list.append("Failure: failed to get CPU collection")
            raise FailException(*self.err_list)
        return cpu_list

    @staticmethod
    def _pack_cpu_resource(restful_cpu, redfish_cpu):

        cpu_list = list()
        for rt_cpu in restful_cpu:
            present = 1
            if present == rt_cpu.get("processor_install_status", None):
                flag = False
                for rd_cpu in redfish_cpu:
                    tmp_id = rt_cpu.get("processor_index", None)
                    if not CPU_ID_IS_START_FROM_ONE and isinstance(
                            tmp_id, int):
                        tmp_id = tmp_id + 1
                    if rd_cpu.id == str(tmp_id):
                        cpu_list.append(rd_cpu)
                        flag = True
                        break
                if not flag:
                    cpu = CPU()
                    cpu.__dict__.update(rt_cpu)
                    cpu_list.append(cpu)
            else:
                absent_cpu = CPU()
                absent_cpu.pack_cpu_absent(rt_cpu)
                cpu_list.append(absent_cpu)
        return cpu_list
