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

power_meter_state_dict = {
    1: "Enable",
    0: "Disabled"
}
power_meter_shutdown_dict = {
    1: "HardPowerOff",
    0: "NoAction"
}


class GetPowerLimit(BaseModule):

    def __init__(self):
        super().__init__()
        self.power_limit_enable = None
        self.power_limit_enable_str = None
        self.limit_in_watts = None
        self.limit_exception = None

    @property
    def dict(self):

        return {
            "PowerLimitEnable": self.power_limit_enable,
            "PowerLimitEnableStr": self.power_limit_enable_str,
            "LimitInWatts": self.limit_in_watts,
            "LimitException": self.limit_exception
        }

    @GetVersion()
    def run(self, args):

        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                url = "/api/power/capping"
                resp = client.send_request("GET", url)
                if (isinstance(resp, dict)) and resp.get("cc") ==\
                        Constant.SUCCESS_0:
                    self.limit_in_watts = resp.get("power_meter_set", None)
                    self.limit_exception = power_meter_shutdown_dict.get(
                        resp.get("power_meter_shutdown"), None)
                    self.power_limit_enable_str = power_meter_state_dict.get(
                        resp.get("power_meter_enable"), None)
                else:
                    err_info = "Failure: failed to get power limit"
                    self.err_list.append(err_info)
                    raise FailException(*self.err_list)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            systems_id = client.get_systems_id()
            url = "/redfish/v1/Chassis/%s/Power" % systems_id
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                self._pack_resource(resp["resource"])
            else:
                err_info = "Failure: failed to get power capping information"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        return self.suc_list

    def _pack_resource(self, resp):
        try:
            power_limit = resp["PowerControl"][0].get("PowerLimit", {})
            if power_limit.get("PowerLimitEnable", None) is None:
                self.power_limit_enable = (
                    resp["PowerControl"][0]["Status"].get("State") == "Enabled")
            else:
                self.power_limit_enable = power_limit.get("PowerLimitEnable")
            self.power_limit_enable_str = (
                "Enabled" if self.power_limit_enable is True else "Disabled"
                if self.power_limit_enable is False else None)
            self.limit_in_watts = power_limit.get("LimitInWatts", None)
            self.limit_exception = power_limit.get('LimitException', None)
        except (TypeError, KeyError, AttributeError, Exception):

            err_info = ("Failure: this type of device does not support "
                        "power capping settings")
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
