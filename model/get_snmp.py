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

STATUS_DICT = {
    1: "Enabled",
    0: "Disabled"
}
VERSION_DICT = {
    0: "v1",
    1: "v2c",
    2: "v3"
}


class TrapServer:

    def __init__(self):
        self.enabled = None
        self.enabled_str = None
        self.member_id = None
        self.trap_server_address = None
        self.trap_server_port = None

    @property
    def dict(self):

        return {
            "Enabled": self.enabled,
            "EnabledStr": self.enabled_str,
            "MemberId": self.member_id,
            "TrapServerAddress": self.trap_server_address,
            "TrapServerPort": self.trap_server_port
        }

    def pack_server_resource(self, server):

        self.enabled = server.get("Enabled", None)
        self.enabled_str = "Enabled" if self.enabled is True else "Disabled"
        self.member_id = server.get('MemberId', None)
        self.trap_server_address = server.get('TrapServerAddress', None)
        self.trap_server_port = server.get('TrapServerPort', None)


class GetSnmp(BaseModule):

    def __init__(self):
        super().__init__()

        self.description = None
        self.id = None
        self.long_password_enabled = None
        self.name = None
        self.read_only_community = None
        self.read_write_community = None
        self.alarm_severity = None
        self.warning_level = None
        self.community_name = None
        self.service_enabled = None
        self.service_enabled_str = None
        self.trap_mode = None
        self.trap_server_identity = None
        self.trap_v3_user = None
        self.trap_version = None

        self.snmp_v1_enabled = None
        self.snmp_v2c_enabled = None
        self.snmp_v3_auth_protocol = None
        self.snmp_v3_enabled = None
        self.snmp_v3_priv_protocol = None

        self.trap_servers = []

    @property
    def dict(self):

        return {
            "Description": self.description,
            "Id": self.id,
            "LongPasswordEnabled": self.long_password_enabled,
            "Name": self.name,
            "ReadOnlyCommunity": self.read_only_community,
            "ReadWriteCommunity": self.read_write_community,
            "AlarmSeverity": self.alarm_severity,
            "WarningLevel": self.warning_level,
            "CommunityName": self.community_name,
            "ServiceEnabled": self.service_enabled,
            "ServiceEnabledStr": self.service_enabled_str,
            "TrapMode": self.trap_mode,
            "TrapServerIdentity": self.trap_server_identity,
            "TrapV3User": self.trap_v3_user,
            "TrapVersion": self.trap_version,
            "TrapVersionUpper": self.trap_version_upper,
            "SnmpV1Enabled": self.snmp_v1_enabled,
            "SnmpV2CEnabled": self.snmp_v2c_enabled,
            "SnmpV3AuthProtocol": self.snmp_v3_auth_protocol,
            "SnmpV3Enabled": self.snmp_v3_enabled,
            "SnmpV3PrivProtocol": self.snmp_v3_priv_protocol,
            "TrapServers": self.trap_servers
        }

    @GetVersion()
    def run(self, args):

        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                url = "/api/settings/pef/snmp"
                resp = client.send_request("GET", url)
                if isinstance(resp, dict):
                    self._pack_b01_snmp_resource(resp)
                else:
                    err = "Failure: failed to get snmp information"
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
            if (isinstance(resp, dict) and
                    Constant.SUCCESS_200 == resp.get("status_code", None)):
                self._pack_snmp_resource(resp["resource"])
            else:
                err = "Failure: failed to get snmp information"
                self.err_list.append(err)
                raise FailException(*self.err_list)

        return self.suc_list

    def _pack_snmp_resource(self, resp):

        self.description = resp.get("Description", None)
        self.id = resp.get("Id", None)
        self.long_password_enabled = resp.get("LongPasswordEnabled", None)
        self.name = resp.get("Name", None)
        self.read_only_community = resp.get("ReadOnlyCommunity", None)
        self.read_write_community = resp.get("ReadWriteCommunity", None)

        snmp_trap = resp.get("SnmpTrapNotification", None)
        if snmp_trap:
            self.alarm_severity = snmp_trap.get("AlarmSeverity", None)
            if self.alarm_severity is not None:
                self.warning_level = (
                    "All" if "All" == self.alarm_severity else (
                        "Critical" if "Critical" == self.alarm_severity else
                        (
                            "WarningAndCritical" if "Warning+Critical" ==
                                                    self.alarm_severity else
                            self.alarm_severity
                        )
                    )
                )
            self.community_name = snmp_trap.get("CommunityName", None)
            self.service_enabled = snmp_trap.get("ServiceEnabled", None)
            self.service_enabled_str = (
                "Enabled" if self.service_enabled is True else "Disabled"
            )
            self.trap_mode = snmp_trap.get("TrapMode", None)
            self.trap_server_identity = snmp_trap.get("TrapServerIdentity",
                                                      None)
            self.trap_v3_user = snmp_trap.get("TrapV3User", None)
            self.trap_version = snmp_trap.get("TrapVersion", None)
            self.trap_version_upper = self.trap_version.upper()

            trap_servers = snmp_trap.get("TrapServer", None)
            if isinstance(trap_servers, list):
                for server in trap_servers:
                    trap_server = TrapServer()
                    trap_server.pack_server_resource(server)
                    self.trap_servers.append(trap_server)

        self.snmp_v1_enabled = resp.get("SnmpV1Enabled", None)
        self.snmp_v2c_enabled = resp.get("SnmpV2CEnabled", None)
        self.snmp_v3_auth_protocol = resp.get("SnmpV3AuthProtocol", None)
        self.snmp_v3_enabled = resp.get("SnmpV3Enabled", None)
        self.snmp_v3_priv_protocol = resp.get("SnmpV3PrivProtocol", None)

    def _pack_b01_snmp_resource(self, resp):

        self.service_enabled_str = STATUS_DICT.get(resp.get("snmptrap_enable"),
                                                   None)
        self.trap_version_upper = VERSION_DICT.get(
            resp.get("snmptrap_version"), None)
        self.community_name = resp.get("trap_community", None)
        self.warning_level = resp.get("snmptrap_warning_level", None)
        trap_server = TrapServer()
        trap_server.enabled_str = STATUS_DICT.get(resp.get("snmptrap_enable"),
                                                  None)
        trap_server.trap_server_address = resp.get("snmptrap_destination_1",
                                                   None)
        trap_server.member_id = "1"
        trap_server.trap_server_port = resp.get("snmptrap_port", None)
        self.trap_servers.append(trap_server)
        trap_server = TrapServer()
        trap_server.enabled_str = STATUS_DICT.get(resp.get("snmptrap_enable"),
                                                  None)
        trap_server.trap_server_address = resp.get("snmptrap_destination_2",
                                                   None)
        trap_server.member_id = "2"
        trap_server.trap_server_port = resp.get("snmptrap_port", None)
        self.trap_servers.append(trap_server)
        trap_server = TrapServer()
        trap_server.enabled_str = STATUS_DICT.get(resp.get("snmptrap_enable"),
                                                  None)
        trap_server.trap_server_address = resp.get("snmptrap_destination_3",
                                                   None)
        trap_server.member_id = "3"
        trap_server.trap_server_port = resp.get("snmptrap_port", None)
        self.trap_servers.append(trap_server)
