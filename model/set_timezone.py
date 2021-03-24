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


class SetTimezone(BaseModule):

    def __init__(self):
        super().__init__()

    @GetVersion()
    def run(self, args):

        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                url = "/api/config/ntp"
                payload = dict()
                resp = client.send_request("GET", url)
                if isinstance(resp, dict):
                    payload["auto_date"] = resp.get("auto_date")
                    payload["primary_ntp"] = resp.get("primary_ntp")
                    payload["secondary_ntp"] = resp.get("secondary_ntp")
                    payload["utc_minutes"] = resp.get("utc_minutes")

                    if payload["auto_date"] == 1:
                        err_info = ("Failure: automatically synchronize "
                                    "with NTP server, can not set timezone")
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
                    else:

                        payload["timezone"] = \
                            args.datetime_local_offset.replace("UTC", "GMT")
                        resp = client.send_request("POST", url, payload)
                        if isinstance(resp, dict) and Constant.SUCCESS_0 == \
                                resp.get("cc"):
                            self.suc_list.append(
                                "Success: set system timezone "
                                "successfully: %s" %
                                args.datetime_local_offset)
                            return self.suc_list
                        else:
                            self.err_list.append("Failure: failed to set "
                                                 "system timezone")
                            raise FailException(*self.err_list)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            systems_id = client.get_systems_id()

            url = "/redfish/v1/Managers/%s/NtpService" % systems_id
            resp = client.send_request('GET', url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                if resp["resource"].get("ServiceEnabled", None):
                    err_info = ("Failure: automatically synchronize "
                                "with NTP server, can not set timezone")
                    self.err_list.append(err_info)
                    raise FailException(*self.err_list)
            url = "/redfish/v1/Managers/%s/NtpService" % systems_id
            payload = {"Oem": {"Public": {"TimeZone":
                                          args.datetime_local_offset}}}
            resp = client.send_request("PATCH", url, payload)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                self.suc_list.append("Success: set system timezone "
                                     "successfully: %s"
                                     % args.datetime_local_offset)
            else:
                self.err_list.append("Failure: failed to set system timezone")
                raise FailException(*self.err_list)
        return self.suc_list
