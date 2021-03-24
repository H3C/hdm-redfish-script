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
from utils.common import Constant
from utils.model import BaseModule
from utils.predo import AllowCommand


class GPU:

    def __init__(self):
        self.id = None
        self.name = None
        self.model = None
        self.location = None
        self.manufacture = None
        self.part_number = None
        self.power_consumed_watts = None
        self.serial_number = None
        self.firmware_version = None
        self.slot_num = None
        self.health = None
        self.state = None
        self.temperature_celsius = None
        self.v_id = None
        self.d_id = None
        self.sv_id = None
        self.sd_id = None
        self.total_memory_mib = None
        self.rated_speed = None
        self.operating_speed = None
        self.rated_band_width = None
        self.operating_band_width = None
        self.total_cores = None
        self.power = None
        self.ecc = None
        self.nv_link = None

    @property
    def dict(self):

        return {
            "ID": self.id,
            "Name": self.name,
            "Model": self.model,
            "Location": self.location,
            "Manufacturer": self.manufacture,
            "PartNumber": self.part_number,
            "SerialNumber": self.serial_number,
            "PowerConsumedWatts": self.power_consumed_watts,
            "SlotNum": self.slot_num,
            "Health": self.health,
            "State": self.state,
            "TemperatureCelsius": self.temperature_celsius,
            "VID": self.v_id,
            "DID": self.d_id,
            "SVID": self.sd_id,
            "SDID": self.sv_id,
            "TotalMemoryMib": self.total_memory_mib,
            "FirmwareVersion": self.firmware_version,
            "RatedSpeed": self.rated_speed,
            "OperatingSpeed": self.operating_speed,
            "RatedBandwidth": self.rated_band_width,
            "OperatingBandwidth": self.operating_band_width,
            "TotalCores": self.total_cores,
            "Power": self.power,
            "ECC": self.ecc,
            "Nvlink": self.nv_link
        }

    def pack_gpu_resource(self, resp):

        self.id = resp.get("ID")
        self.name = resp.get("Name")
        self.model = resp.get("Model")
        self.location = resp.get("Location")
        self.manufacture = resp.get("Manufacture")
        self.part_number = resp.get("PartNumber")
        self.power_consumed_watts = resp.get("PowerConsumedWatts")
        self.serial_number = resp.get("SerialNumber")
        self.slot_num = resp.get("SlotNum")
        status_dict = resp.get("Status")
        if status_dict is not None:
            self.health = status_dict.get("Health")
            self.state = status_dict.get("State")
        self.temperature_celsius = resp.get("TemperatureCelsius")
        self.v_id = resp.get("VID")
        self.d_id = resp.get("DID")
        self.sv_id = resp.get("SVID")
        self.sd_id = resp.get("SDID")
        self.total_memory_mib = resp.get("TotalMemoryMib")
        self.firmware_version = resp.get("FirmwareVersion")
        self.rated_speed = resp.get("RatedSpeed")
        self.operating_speed = resp.get("OperatingSpeed")
        self.rated_band_width = resp.get("RatedBandwidth")
        self.operating_band_width = resp.get("OperatingBandwidth")
        self.total_cores = resp.get("TotalCores")
        self.power = {
            "PowerWatts": self.power_consumed_watts,
            "PowerBrakelsSet": None,
            "SufficientExternalPower": None
        }
        self.ecc = resp.get("ECC")
        self.nv_link = resp.get("Nvlink")


class GetGPU(BaseModule):

    def __init__(self):
        super().__init__()
        self.overall_health = None
        self.maximum = None
        self.gpu = []

    @property
    def dict(self):

        return {
            "OverallHealth": self.overall_health,
            "Maximum": self.maximum,
            "GPU": self.gpu
        }

    @AllowCommand()
    def run(self, args):

        client = RedfishClient(args)
        systems_id = client.get_systems_id()
        url = "/redfish/v1/Systems/%s/GPU" % systems_id
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and
                resp.get("status_code", None) in Constant.SUC_CODE):
            self._parse_gpu_resource(resp["resource"])
            if not self.gpu:
                suc_info = "Success: GPU resource is empty"
                self.suc_list.append(suc_info)
        else:
            self.err_list.append("Failure: failed to get GPU information")
            raise FailException(*self.err_list)

        return self.suc_list

    def _parse_gpu_resource(self, resp):

        gpus = resp.get("GPU", None)
        if gpus is None:
            self.err_list.append("Failure: no data available for the resource")
            raise FailException(*self.err_list)

        for g in gpus:
            gpu = GPU()
            gpu.pack_gpu_resource(g)
            self.gpu.append(gpu)
