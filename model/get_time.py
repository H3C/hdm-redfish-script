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
import datetime


class GetTime(BaseModule):

    def __init__(self):
        super().__init__()

        self.time = None
        self.timezone = None
        self.date_time = None

    @property
    def dict(self):

        return {
            "Time": self.time,
            "Timezone": self.timezone,
            "DateTime": self.date_time
        }

    @GetVersion()
    def run(self, args):

        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                url = "/api/config/ntp"
                resp = client.send_request("GET", url)
                if isinstance(resp, dict):
                    if resp.get("timestamp") is not None:
                        date_array = datetime.datetime.utcfromtimestamp(
                            resp.get("timestamp"))
                        style_time = date_array.strftime("%Y-%m-%d %H:%M:%S")
                        self.time = style_time
                    self.timezone = resp.get("timezone")
                else:
                    err_info = "Failure: failed to get time information!"
                    self.err_list.append(err_info)
                    raise FailException(*self.err_list)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            systems_id = client.get_systems_id()
            url = "/redfish/v1/Managers/%s" % systems_id
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                self.date_time = resp["resource"].get("DateTime", None)
                if self.date_time:
                    self.time = self.date_time[:19].replace("T", " ")
                self.timezone = resp["resource"].get("DateTimeLocalOffset",
                                                     None)
            else:
                self.err_list.append(
                    "Failure: failed to get time information!")
                raise FailException(*self.err_list)
        return self.suc_list
