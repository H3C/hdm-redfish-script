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


from json import dumps
from exception.ToolException import FailException
from utils.client import RedfishClient
from utils.client import RestfulClient
from utils.common import Constant
from utils.tools import is_ipv4
from utils.tools import is_ipv6
from utils.tools import is_domain
from utils.model import BaseModule
from utils import globalvar
from utils.predo import GetVersion


class SetSnmp(BaseModule):

    def __init__(self):
        super().__init__()
        self.snmp_v1_enabled = None
        self.snmp_v2c_enabled = None
        self.long_password_enabled = None
        self.read_only_community = None
        self.read_write_community = None
        self.service_enabled = None
        self.trap_mode = None
        self.trap_version = None
        self.trap_v3_user = None
        self.community_name = None
        self.alarm_severity = None
        self.trap_servers = None

    @GetVersion()
    def run(self, args):

        cmd_type = self._parse_parameters(args)
        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                url = "/api/settings/pef/snmp"
                resp = client.send_request("GET", url)
                if isinstance(resp, dict):
                    payload = self.construct_b01_request_parameters(resp)

                    if payload["snmptrap_version"] == 2:
                        url = "/api/settings/users"
                        resp = client.send_request("GET", url)
                        if isinstance(resp, list):
                            user_id = None
                            for info in resp:
                                if str(payload["snmp_v3_user"]) == \
                                        str(info.get("id")) and \
                                        info.get("name") != "" \
                                        and info.get("snmp") == 1:
                                    user_id = info.get("id")
                                    break
                            if user_id is None:
                                err = ("Failure: failed to get %s, the v3 user"
                                       "id does not exist" % cmd_type)
                                self.err_list.append(err)
                                raise FailException(*self.err_list)
                    url = "/api/settings/pef/snmp"
                    resp = client.send_request("PUT", url, payload)
                    if isinstance(resp, dict) and\
                            Constant.SUCCESS_0 == resp.get("cc"):
                        suc = "Success: set %s successfully" % cmd_type
                        self.suc_list.append(suc)
                        return self.suc_list
                    else:
                        err = "Failure: failed to set %s failed" % cmd_type
                        self.err_list.append(err)
                        raise FailException(*self.err_list)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            systems_id = client.get_systems_id()
            url = "/redfish/v1/Managers/%s/SnmpService" % systems_id
            resp = client.send_request("get", url)
            if (resp is None or Constant.SUCCESS_200 != resp.get("status_code",
                                                                 None)):
                err = ("Failure: failed to get %s! Check the connection please"
                       % cmd_type)
                self.err_list.append(err)
                raise FailException(*self.err_list)
            payload = self.construct_request_parameters(resp)
            url = "/redfish/v1/Managers/%s/SnmpService" % systems_id
            resp = client.send_request('PATCH', url, payload)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                suc = "Success: set %s successfully" % cmd_type
                self.suc_list.append(suc)
                return self.suc_list
            elif ((isinstance(resp, dict) and
                   isinstance(resp.get("resource", None), dict) and
                   isinstance(resp["resource"].get("error", None), dict))):
                err = dumps(resp["resource"]["error"],
                            indent=4, separators=(",", ": "))
                self.err_list.append(err)
                raise FailException(*self.err_list)
            else:
                err = "Failure: failed to set %s failed" % cmd_type
                self.err_list.append(err)
                raise FailException(*self.err_list)

    def construct_request_parameters(self, resp):

        payload = dict()
        if self.snmp_v1_enabled is not None:
            payload["SnmpV1Enabled"] = self.snmp_v1_enabled
        if self.snmp_v2c_enabled is not None:
            payload["SnmpV2CEnabled"] = self.snmp_v2c_enabled
        if self.long_password_enabled is not None:
            payload["LongPasswordEnabled"] = self.long_password_enabled
        if self.read_only_community is not None:
            payload["ReadOnlyCommunity"] = self.read_only_community
        if self.read_write_community is not None:
            payload["ReadWriteCommunity"] = self.read_write_community
        if self.community_name is not None:
            payload["CommunityName"] = self.community_name
        if self.service_enabled is not None:
            payload["ServiceEnabled"] = self.service_enabled
        if self.trap_version is not None:
            payload["TrapVersion"] = self.trap_version
        if self.trap_v3_user is not None:
            payload["TrapV3User"] = self.trap_v3_user

        alarm_severity = {
            "All": "All",
            "Critical": "Critical",
            "MinorAndMajorAndCritical": "Minor+Major+Critical",
            "WarningAndCritical": "Warning+Critical",
            "MajorAndCritical": "Major+Critical"
        }
        if globalvar.HDM_VERSION < "2.10.00":
            if self.alarm_severity == "MajorAndCritical":
                err = ("Argument: invalid choice: %s, the current HDM version "
                       "does not support" % self.alarm_severity)
                self.err_list.append(err)
                raise FailException(*self.err_list)
        if self.alarm_severity is not None:
            payload["AlarmSeverity"] = alarm_severity.get(self.alarm_severity)
        if self.trap_mode is not None:
            payload["TrapMode"] = self.trap_mode

        if self.trap_servers:
            payload["TrapServer"] = self.trap_servers

        if (self.community_name is not None and
                (payload.get("TrapVersion") == "v3" or (payload.get(
                    "TrapVersion") is None and resp["resource"][
                    "SnmpTrapNotification"].get(
                    "TrapVersion") == "v3"))):
            err_info = ("Argument: the trap community name parameter "
                        "is not available in v3 mode")
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return payload

    def package_trap_server(self, trap_str):

        trap_server_list = list()
        try:
            if trap_str[0] != "[" or trap_str[-1] != "]":
                return None
            trap_str = trap_str[1:-1]
            server_list = trap_str.split("_")
            for number in server_list:
                s_dict = dict()
                member_id, enable, port, address, = number.split("-")
                if member_id not in {"1", "2", "3", "4"}:
                    err = ("Argument: invalid choice: %s "
                           "(choose from 1, 2, 3, 4)" % member_id)
                    self.err_list.append(err)
                    raise FailException(*self.err_list)

                if enable not in {"0", "1"}:
                    err = ("Argument: invalid choice: %s "
                           "(choose from 0, 1)" % enable)
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
                s_dict["MemberId"] = member_id
                s_dict["Enabled"] = (int(enable) == 1)
                try:
                    s_dict["TrapServerPort"] = int(port)
                except ValueError:
                    err = ("Argument: invalid choice: %s "
                           "(choose from 1 to 65535)" % port)
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
                if (s_dict["TrapServerPort"] < 1 or s_dict["TrapServerPort"]
                        > 65535):
                    err = ("Argument: invalid choice: %s "
                           "(choose from 1 to 65535)" % port)
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
                if (is_ipv4(address) or
                        is_ipv6(address) or
                        is_domain(address)):
                    s_dict["TrapServerAddress"] = address
                else:
                    err = ("Argument: invalid choice: %s "
                           "(the server address is invalid)" % address)
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
                trap_server_list.append(s_dict)
        except (OSError, TypeError, ValueError, KeyError, SyntaxError, IOError):
            return None
        return trap_server_list

    def _parse_snmp(self, args):

        self.snmp_v1_enabled = (("Enable" == args.snmp_v1_enabled)
                                if args.snmp_v1_enabled is not None else None)
        self.snmp_v2c_enabled = (("Enable" == args.snmp_v2c_enabled)
                                 if args.snmp_v2c_enabled is not None else None)
        self.long_password_enabled = (("Enable" ==
                                       args.long_password_enabled)
                                      if args.long_password_enabled is not None
                                      else None)
        self.read_only_community = args.read_only_community
        self.read_write_community = args.read_write_community
        self.community_name = args.community_name
        self.service_enabled = (("Enable" == args.service_enabled)
                                if args.service_enabled is not None else None)
        self.trap_version = args.trap_version
        self.trap_v3_user = args.trap_v3_user
        self.alarm_severity = args.alarm_severity
        self.trap_mode = args.trap_mode
        if args.trap_servers:
            self.trap_servers = self.package_trap_server(args.trap_servers)
            if not self.trap_servers:
                err = ("Argument: invalid choice: %s "
                       "(invalid format or ip is illegal, "
                       "exp: [1-1-163-192.168.10.121_2-1-163-192.168.10.122])"
                       % args.trap_servers)
                self.err_list.append(err)
                raise FailException(*self.err_list)

    def _parse_trap_com(self, args):

        self.community_name = (args.community_name if
                               args.community_name is not None else None)
        self.service_enabled = (("Enabled" == args.service_enabled)
                                if args.service_enabled is not None else None)
        self.trap_version = ({"1": "v1", "2": "v2c", "3": "v3"}.
                             get(args.trap_version, None)
                             if args.trap_version is not None else None)
        self.trap_v3_user = (args.trap_v3_user if
                             args.trap_v3_user is not None else None)
        self.alarm_severity = (args.alarm_severity if
                               args.alarm_severity is not None else None)

    def _parse_trap_server(self, args):

        self.trap_servers = list()
        s_dict = dict()
        s_dict["MemberId"] = args.member_id
        s_dict["Enabled"] = (("Enabled" == args.server_enabled)
                             if args.server_enabled is not None else None)
        s_dict["TrapServerPort"] = None
        if args.server_port is not None:
            if args.server_port < 1 or args.server_port > 65535:
                err = ("Argument: invalid choice: %s "
                       "(choose from 1 to 65535)" % args.server_port)
                self.err_list.append(err)
                raise FailException(*self.err_list)
            else:
                s_dict["TrapServerPort"] = args.server_port

        if args.server_address:
            if (is_ipv4(args.server_address) or
                    is_ipv6(args.server_address) or
                    is_domain(args.server_address)):
                s_dict["TrapServerAddress"] = args.server_address
            else:
                err = ("Argument: invalid choice: %s "
                       "(the server address is invalid)" %
                       args.server_address)
                self.err_list.append(err)
                raise FailException(*self.err_list)
        self.trap_servers.append(s_dict)

    def _parse_parameters(self, args):

        cmd_type = "snmp"

        if "snmp_v1_enabled" in args:

            cmd_type = "snmp"
            flag_snmp = (
                args.snmp_v1_enabled is not None or
                args.snmp_v2c_enabled is not None or
                args.long_password_enabled is not None or
                args.read_only_community is not None or
                args.read_write_community is not None
            )
            flag_trap = (
                args.service_enabled is not None or
                args.trap_mode is not None or
                args.trap_version is not None or
                args.trap_v3_user is not None or
                args.community_name is not None or
                args.alarm_severity is not None
            )
            flag_server = args.trap_servers
            flag_snmp = flag_snmp or flag_trap or flag_server
            if not flag_snmp:
                err = "Argument: at least one parameter must be specified"
                self.err_list.append(err)
                raise FailException(*self.err_list)
            self._parse_snmp(args)
        elif "service_enabled" in args:

            cmd_type = "SNMP trap common"
            flag_trap = (
                args.service_enabled is not None or
                args.trap_version is not None or
                args.community_name is not None or
                args.alarm_severity is not None or
                args.trap_v3_user is not None
            )
            if not flag_trap:
                err = "Argument: need at least one parameter"
                self.err_list.append(err)
                raise FailException(*self.err_list)
            self._parse_trap_com(args)
        elif "member_id" in args:

            cmd_type = "SNMP trap destination"
            flag_server = (
                args.server_enabled is not None or
                args.server_port is not None or
                args.server_address is not None
            )
            if not flag_server:
                err = "Argument: need at least one parameter"
                self.err_list.append(err)
                raise FailException(*self.err_list)
            self._parse_trap_server(args)
        return cmd_type

    def construct_b01_request_parameters(self, resp):

        payload = dict()
        if resp:
            if self.service_enabled is not None:
                if self.service_enabled:
                    payload["snmptrap_enable"] = 1
                else:
                    payload["snmptrap_enable"] = 0
            else:
                payload["snmptrap_enable"] = resp.get("snmptrap_enable")
            if self.trap_version is not None:
                payload["snmptrap_version"] = \
                    {"v1": 0, "v2c": 1, "v3": 2}.get(self.trap_version, None)
            else:
                payload["snmptrap_version"] = resp.get("snmptrap_version")
            if self.community_name is not None:
                payload["trap_community"] = self.community_name
            else:
                payload["trap_community"] = resp.get("trap_community")
            if self.trap_v3_user is not None:
                payload["snmp_v3_user"] = self.trap_v3_user
            else:
                payload["snmp_v3_user"] = resp.get("snmp_v3_user")
            if self.read_only_community is not None:
                payload["read_community"] = self.read_only_community
            else:
                payload["read_community"] = resp.get("read_community")
            payload["snmptrap_destination_1"] = \
                resp.get("snmptrap_destination_1")
            payload["snmptrap_destination_2"] = \
                resp.get("snmptrap_destination_2")
            payload["snmptrap_destination_3"] = \
                resp.get("snmptrap_destination_3")

            payload["snmptrap_port"] = resp.get("snmptrap_port")
            servers = self.trap_servers
            if servers is not None:
                for server in servers:
                    if server.get("MemberId") == str(1) and \
                            server.get("TrapServerAddress") is not None:
                        payload["snmptrap_destination_1"] = \
                            server.get("TrapServerAddress")
                    if server.get("MemberId") == str(2) and \
                            server.get("TrapServerAddress") is not None:
                        payload["snmptrap_destination_2"] = \
                            server.get("TrapServerAddress")
                    if server.get("MemberId") == str(3) and \
                            server.get("TrapServerAddress") is not None:
                        payload["snmptrap_destination_3"] = \
                            server.get("TrapServerAddress")
                if server.get("TrapServerPort") is not None:
                    payload["snmptrap_port"] = server.get("TrapServerPort")
                if server.get("Enabled") is not None:
                    if server.get("Enabled"):
                        payload["snmptrap_enable"] = 1
                    else:
                        payload["snmptrap_enable"] = 0

            payload["system_contact"] = resp.get("system_contact")
            payload["system_location"] = resp.get("system_location")
        return payload
