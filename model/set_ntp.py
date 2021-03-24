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


from subprocess import getstatusoutput
from exception.ToolException import FailException
from utils.client import RedfishClient
from utils.common import Constant
from utils.tools import is_ipv4
from utils.tools import is_domain
from utils.tools import is_ipv6
from utils.model import BaseModule
from utils.tools import init_args


class SetNtp(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = [
            "alternate_ntp_server",
            "preferred_ntp_server",
            "service_enabled",
            "tertiary_ntp_server",
            "time_zone",
            "interval"
        ]
        self.service_enabled = None
        self.preferred_ntp_server = None
        self.alternate_ntp_server = None
        self.tertiary_ntp_server = None
        self.time_zone = None
        self.command = None

    def run(self, args):

        init_args(args, self.args_lst)
        self._parse_args(args)

        if self.command is not None:
            ret, output = getstatusoutput(self.command)
            output = output.strip()
            if Constant.SUCCESS_0 != ret:
                self.err_list.append(output)
                err = "Failure: failed to set ntp time synchronization interval"
                self.err_list.append(err)
                raise FailException(*self.err_list)
            else:
                if "a2 63 00" == output:
                    suc = ("Success: set ntp time "
                           "synchronization interval successful")
                    self.suc_list.append(suc)
                    return self.suc_list
                else:
                    err = ("Failure: failed to set "
                           "ntp time synchronization interval")
                    self.err_list.append(err)
                    raise FailException(*self.err_list)

        payload = self._construct_param()
        if payload:
            client = RedfishClient(args)
            systems_id = client.get_systems_id()
            url = "/redfish/v1/Managers/%s/NtpService" % systems_id
            resp = client.send_request('PATCH', url, payload)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                self.suc_list.append("Success: set ntp server information "
                                     "successful")
            else:
                self.err_list.append("Failure: failed to set ntp server "
                                     "information")
                raise FailException(*self.err_list)

        return self.suc_list

    def _parse_args(self, args):

        if (args.service_enabled is None
                and args.preferred_ntp_server is None
                and args.alternate_ntp_server is None
                and args.interval is None
                and args.time_zone is None
                and args.tertiary_ntp_server is None):
            self.err_list.append("Argument :at least one "
                                 "parameter must be specified")
            raise FailException(*self.err_list)

        self.service_enabled = (("Enable" == args.service_enabled) if
                                args.service_enabled is not None else None)

        if args.preferred_ntp_server is not None:
            if not self.is_parameter_legal(args.preferred_ntp_server):
                err = ("Argument: invalid choice: %s "
                       "(primary NTP server address is incorrect)" %
                       args.preferred_ntp_server)
                self.err_list.append(err)
                raise FailException(*self.err_list)
            self.preferred_ntp_server = args.preferred_ntp_server
        if args.alternate_ntp_server is not None:
            if not self.is_parameter_legal(args.alternate_ntp_server):
                err = ("Argument: invalid choice: %s "
                       "(Secondary NTP server address is incorrect)"
                       % args.alternate_ntp_server)
                self.err_list.append(err)
                raise FailException(*self.err_list)
            self.alternate_ntp_server = args.alternate_ntp_server

        if args.tertiary_ntp_server is not None:
            if not self.is_parameter_legal(args.tertiary_ntp_server):
                err = ("Argument: invalid choice: %s"
                       " (Tertiary NTP server address is incorrect)"
                       % args.tertiary_ntp_server)
                self.err_list.append(err)
                raise FailException(*self.err_list)
            self.tertiary_ntp_server = args.tertiary_ntp_server

        self.time_zone = args.time_zone

    @staticmethod
    def hex_str(num):

        str_num = "%.8x" % num
        str_list = list()
        i = 0
        while i < 4:
            str_list.append(str_num[-2:])
            str_num = str_num[:-2]
            i = i + 1
        str_hex = "0x" + " 0x".join(str_list)
        return str_hex

    @staticmethod
    def is_parameter_legal(domain):

        return is_ipv4(domain) or is_ipv6(domain) or is_domain(domain)

    def _construct_param(self):

        payload = dict()
        if self.service_enabled is not None:
            payload["ServiceEnabled"] = self.service_enabled
        if self.preferred_ntp_server is not None:
            payload["PreferredNtpServer"] = self.preferred_ntp_server
        if self.alternate_ntp_server is not None:
            payload["AlternateNtpServer"] = self.alternate_ntp_server
        if self.time_zone is not None:
            payload["Oem"] = {"Public": {"TimeZone": self.time_zone}}
        if self.tertiary_ntp_server is not None:
            if payload.get("Oem", None) is None:
                payload["Oem"] = {"Public": {}}
            payload["Oem"]["Public"]["TertiaryNtpServer"] = (
                self.tertiary_ntp_server)

        return payload
