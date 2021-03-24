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


import time
from exception.ToolException import FailException
from utils.tools import is_ipv4
from utils.tools import is_ipv6
from utils.tools import is_mac
from utils.client import RestfulClient
from utils.common import Constant
from utils.model import BaseModule
from utils.tools import init_args


class SetLoginRuleIp(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["start_time", "end_time", "ip_end", "ip_start",
                         "rule", "mac_address", "operator"]

    @property
    def dict(self):

        return {}

    def run(self, args):

        init_args(args, self.args_lst)
        url, payload = self.construct_request_parameters(args)
        client = RestfulClient(args)
        try:
            resp = client.send_request("post", url, payload)
            if (isinstance(resp, dict) and
                    resp.get(Constant.COMPLETE_CODE) == Constant.SUCCESS_0):
                suc_info = "Success: set ip login rule succeed"
                self.suc_list.append(suc_info)
            else:
                err_info = "Failure: set ip login rule failed"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def construct_request_parameters(self, args):

        payload = dict()
        url = ("/api/settings/firewall-ip-mac-rule-forbid"
               if args.rule == "Block" else
               "/api/settings/firewall-ip-mac-rule-allow")
        if ((args.ip_start and args.ip_start == "0.0.0.0")
                or (args.ip_end and args.ip_end == "0.0.0.0") or
                ((args.ip_start and (not (is_ipv4(args.ip_start) or
                                          is_ipv6(args.ip_start)))) or
                 (args.ip_end and (not (is_ipv4(args.ip_end) or
                                        is_ipv6(args.ip_end)))))):
            err_info = ("Argument: invalid choice(the ipv4/ipv6 "
                        "format is incorrect).")
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        if args.ip_start and args.ip_end:
            if ((is_ipv4(args.ip_start) and
                 (not is_ipv4(args.ip_end) and
                  is_ipv6(args.ip_end))) or
                    (is_ipv6(args.ip_start) and
                     not is_ipv6(args.ip_end) and
                     is_ipv4(args.ip_end))):
                err_info = "Argument: invalid choice: different IP protocols"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        payload["operation"] = 1 if args.operator == 'Add' else 3
        payload["ip_address_from"] = args.ip_start
        payload["ip_address_to"] = (args.ip_end if args.ip_end else "")
        if args.mac_address:
            if is_mac(args.mac_address):
                payload["mac_address"] = args.mac_address
            else:
                err_info = "Argument: invalid choice (mac address is invalid)"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        else:
            payload["mac_address"] = ""
        if not (args.start_time or args.end_time):
            payload["timeout_status"] = 0
            payload["date_from_yy"] = 0
            payload["date_from_mm"] = 0
            payload["date_from_dd"] = 0
            payload["time_from_hh"] = 0
            payload["time_from_mm"] = 0
            payload["date_to_yy"] = 0
            payload["date_to_mm"] = 0
            payload["date_to_dd"] = 0
            payload["time_to_hh"] = 0
            payload["time_to_mm"] = 0
            payload["timeout_status"] = 0
        elif args.start_time and args.end_time:
            try:
                st = time.strptime(args.start_time, "%Y-%m-%dT%H:%M")
                et = time.strptime(args.end_time, "%Y-%m-%dT%H:%M")
            except (ValueError, Exception) as err:
                self.err_list.append(str(err))
                raise FailException(*self.err_list)
            st_stamp = int(time.mktime(st))
            et_stamp = int(time.mktime(et))
            if st_stamp >= et_stamp:
                err_info = "Argument: end time must be greater than start time"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            payload["timeout_status"] = st.tm_year
            payload["date_from_yy"] = st.tm_year
            payload["date_from_mm"] = st.tm_mon
            payload["date_from_dd"] = st.tm_mday
            payload["time_from_hh"] = st.tm_hour
            payload["time_from_mm"] = st.tm_min
            payload["date_to_yy"] = et.tm_year
            payload["date_to_mm"] = et.tm_mon
            payload["date_to_dd"] = et.tm_mday
            payload["time_to_hh"] = et.tm_hour
            payload["time_to_mm"] = et.tm_min
            payload['timeout_status'] = 1
        else:
            err_info = "Argument: start time and end time must appear in pairs"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return url, payload
