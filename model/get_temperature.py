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
from utils.predo import GetVersion
from utils import globalvar


class Temperature:

    def __init__(self):
        self.name = None
        self.sensor_number = None
        self.upper_threshold_fatal = None
        self.upper_threshold_critical = None
        self.upper_threshold_non_critical = None
        self.reading_celsius = None
        self.lower_threshold_non_critical = None
        self.lower_threshold_critical = None
        self.lower_threshold_fatal = None

        self.physical_context = None
        self.health = None
        self.state = None

    @property
    def dict(self):

        return {
            "Name": self.name,
            "SensorNumber": self.sensor_number,
            "UpperThresholdFatal": self.upper_threshold_fatal,
            "UpperThresholdCritical": self.upper_threshold_critical,
            "UpperThresholdNonCritical": self.upper_threshold_non_critical,
            "ReadingCelsius": self.reading_celsius,
            "LowerThresholdNonCritical": self.lower_threshold_non_critical,
            "LowerThresholdCritical": self.lower_threshold_critical,
            "LowerThresholdFatal": self.lower_threshold_fatal,
            "PhysicalContext": self.physical_context,
            "Health": self.health,
            "State": self.state
        }

    def pack_temp_resource(self, resp):

        self.name = resp.get("Name", None)
        self.sensor_number = resp.get("SensorNumber", None)
        self.upper_threshold_fatal = resp.get('UpperThresholdFatal', None)
        self.upper_threshold_critical = resp.get(
            "UpperThresholdCritical", None)
        self.upper_threshold_non_critical = (
            resp.get("UpperThresholdNonCritical", None))
        self.reading_celsius = resp.get("ReadingCelsius", None)
        self.lower_threshold_non_critical = (
            resp.get("LowerThresholdNonCritical", None))
        self.lower_threshold_critical = resp.get(
            "LowerThresholdCritical", None)
        self.lower_threshold_fatal = resp.get("LowerThresholdFatal", None)

        self.physical_context = resp.get('PhysicalContext', None)
        if isinstance(resp.get("Status", None), dict):
            self.health = resp['Status'].get('Health', None)
            self.state = resp['Status'].get('State', None)

    def pack_b01_temp_resource(self, resp):

        self.name = resp.get("name", None)
        self.sensor_number = resp.get("sensor_number", None)
        self.upper_threshold_fatal = resp.get(
            "higher_non_recoverable_threshold", None)
        self.upper_threshold_critical = resp.get("higher_critical_threshold",
                                                 None)
        self.upper_threshold_non_critical = (
            resp.get("higher_non_critical_threshold", None))
        self.reading_celsius = resp.get("reading", None)
        self.lower_threshold_non_critical = (
            resp.get("lower_non_critical_threshold", None))
        self.lower_threshold_critical = (
            resp.get("lower_critical_threshold", None))
        self.lower_threshold_fatal = resp.get(
            "lower_non_recoverable_threshold", None)


class GetTemperature(BaseModule):

    def __init__(self):
        super().__init__()

        self.temperatures = []

    @property
    def dict(self):

        return {
            "Temperatures": self.temperatures
        }

    @GetVersion()
    def run(self, args):

        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                url = "/api/sensors"
                resp = client.send_request("GET", url)
                if isinstance(resp, list):
                    data = sorted(resp, key=lambda s: s["sensor_number"])
                    for info in data:
                        if info.get("type") == "temperature":
                            temp = Temperature()
                            temp.pack_b01_temp_resource(info)
                            self.temperatures.append(temp)
                else:
                    err_info = "Failure: failed to get temperature information"
                    self.err_list.append(err_info)
                    raise FailException(*self.err_list)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            systems_id = client.get_systems_id()
            url = "/redfish/v1/Chassis/%s/Thermal" % systems_id
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                temperatures = resp["resource"].get("Temperatures", None)
                if not temperatures:
                    self.err_list.append("Failure: no data available for the "
                                         "resource")
                    raise FailException(*self.err_list)
                try:
                    temperatures = sorted(temperatures,
                                          key=lambda s: s["SensorNumber"])
                except KeyError as err:
                    self.err_list.append(str(err))
                    raise FailException(*self.err_list)
                else:
                    for info in temperatures:
                        temp = Temperature()
                        temp.pack_temp_resource(info)
                        self.temperatures.append(temp)
            else:
                self.err_list.append("Failure: failed to get temperature "
                                     "information")
                raise FailException(*self.err_list)

        return self.suc_list
