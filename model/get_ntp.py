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


class GetNtp(BaseModule):

    def __init__(self):
        super().__init__()

        self.service_enabled = None
        self.time_zone = None
        self.tertiary_ntp_server = None
        self.preferred_ntp_server = None
        self.alternate_ntp_server = None
        self.ntp_address_origin = None

    @property
    def dict(self):

        return {
            "ServiceEnabled": self.service_enabled,
            "TimeZone": self.time_zone,
            "TertiaryNtpServer": self.tertiary_ntp_server,
            "PreferredNtpServer": self.preferred_ntp_server,
            "AlternateNtpServer": self.alternate_ntp_server,
            "NtpAddressOrigin": self.ntp_address_origin
        }

    def run(self, args):

        client = RedfishClient(args)
        systems_id = client.get_systems_id()
        url = "/redfish/v1/Managers/%s/NtpService" % systems_id
        resp = client.send_request("get", url)
        if isinstance(
                resp,
                dict) and resp.get(
                "status_code",
                None) in Constant.SUC_CODE:
            resp = resp["resource"]
            self.service_enabled = resp.get("ServiceEnabled", None)
            if (isinstance(resp.get("Oem", None), dict) and
                    isinstance(resp["Oem"].get("Public", None), dict)):
                self.time_zone = resp["Oem"]["Public"].get("TimeZone", None)
                self.tertiary_ntp_server = (
                    resp["Oem"]["Public"].get("TertiaryNtpServer", None))
            self.preferred_ntp_server = resp.get("PreferredNtpServer", None)
            self.alternate_ntp_server = resp.get("AlternateNtpServer", None)
            self.ntp_address_origin = resp.get("NtpAddressOrigin", None)
        else:
            self.err_list.append("Failure: failed to get ntp")
            raise FailException(*self.err_list)

        return self.suc_list
