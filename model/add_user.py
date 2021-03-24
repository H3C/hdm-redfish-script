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
from utils.tools import init_args
from utils.predo import GetVersion
from utils import globalvar


class AddUser(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = [
            "enabled",
            "new_user_name",
            "new_pwd",
            "role_id",
            "vmedia_enable",
            "kvm_enable",
            "privilege",
            "ipmi_enable",
            "web_enable",
            "snmp_v3_enable",
            "snmp_v3_access_permission",
            "snmp_v3_auth_protocol",
            "snmp_v3_priv_protocol"
        ]
        self.enabled = None
        self.password = None
        self.user_name = None
        self.role_id = None
        self.kvm_enable = None
        self.vmedia_enable = None
        self.ipmi_enable = None
        self.web_enable = None
        self.snmp_v3_enable = None
        self.snmp_v3_access_permission = None
        self.snmp_v3_auth_protocol = None
        self.snmp_v3_priv_protocol = None

    @GetVersion()
    def run(self, args):

        init_args(args, self.args_lst)
        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:

            client = RestfulClient(args)
            try:
                url = "/api/settings/users"
                resp = client.send_request("GET", url)
                user_id = None
                if isinstance(resp, list):
                    for info in resp:

                        if info.get("name") == "":
                            user_id = info.get("id")
                            break
                if user_id is not None:
                    self._parse_b01_args(args)
                    payload = self._construct_b01_param()
                    payload["id"] = user_id
                    url = "/api/settings/users/" + str(user_id)
                    resp = client.send_request("PUT", url, payload)
                    if isinstance(resp, dict) and\
                            resp.get("cc") == Constant.SUCCESS_0:
                        suc = "Success: add user successfully"
                        self.suc_list.append(suc)
                    else:
                        err = "Failure: failed to add user"
                        self.err_list.append(err)
                        raise FailException(*self.err_list)
                else:
                    err = "Failure: the number of user is up to the limit!"
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            self._parse_args(args)
            payload = self._construct_param()
            url = "/redfish/v1/AccountService/Accounts"
            client = RedfishClient(args)
            resp = client.send_request("POST", url, payload)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                suc = "Success: add user successfully"
                self.suc_list.append(suc)
            else:
                err = "Failure: failed to add user"
                self.err_list.append(err)
                raise FailException(*self.err_list)

        return self.suc_list

    def _parse_args(self, args):

        self.enabled = (
            ("Enable" == args.enabled) if args.enabled is not None else True)
        self.user_name = args.new_user_name
        self.password = args.new_pwd
        role_id_dict = {"Administrator": "Administrator",
                        "Operator": "Operator",
                        "User": "User",
                        "None": "None",
                        "Commonuser": "User",
                        "OEM": "None",
                        "CustomRole1": "CustomRole1",
                        "CustomRole2": "CustomRole2",
                        "CustomRole3": "CustomRole3",
                        "CustomRole4": "CustomRole4",
                        "CustomRole5": "CustomRole5"
                        }
        tmp_dict = {
            "CustomRole1": "Custom 1",
            "CustomRole2": "Custom 2",
            "CustomRole3": "Custom 3",
            "CustomRole4": "Custom 4",
            "CustomRole5": "Custom 5"
        }
        self.role_id = role_id_dict.get(args.role_id)
        key_lst = tmp_dict.keys()
        if globalvar.HDM_VERSION < "2.0.04":
            if args.role_id in key_lst:
                err = ("Argument: %s, the current HDM version does not "
                       "support this parameter value" % args.role_id)
                self.err_list.append(err)
                raise FailException(*self.err_list)

        elif globalvar.HDM_VERSION < "2.06":
            if args.role_id in key_lst:
                self.role_id = tmp_dict.get(args.role_id)
        self.kvm_enable = False
        self.vmedia_enable = False
        if args.privilege is not None:
            priv_set = set(filter(None, args.privilege.split(r',')))
            if not priv_set.issubset({"KVM", "VMM", "SOL", "None"}):
                err = ("Argument: the privilege parameter is invalid, "
                       "must be selected in {KVM,VMM,SOL,None}")
                self.err_list.append(err)
                raise FailException(*self.err_list)
            self.kvm_enable = "KVM" in priv_set
            self.vmedia_enable = "VMM" in priv_set
        else:
            self.vmedia_enable = ("Enable" == args.vmedia_enable if
                                  args.vmedia_enable is not None else None)
            self.kvm_enable = ("Enable" == args.kvm_enable if
                               args.kvm_enable is not None else None)
        self.ipmi_enable = (
            ("Enable" == args.ipmi_enable) if args.ipmi_enable is not None else
            True)
        self.web_enable = (
            ("Enable" == args.web_enable) if args.web_enable is not None else
            True)
        self.snmp_v3_enable = ("Enable" == args.snmp_v3_enable)
        self.snmp_v3_access_permission = args.snmp_v3_access_permission
        self.snmp_v3_auth_protocol = args.snmp_v3_auth_protocol
        self.snmp_v3_priv_protocol = args.snmp_v3_priv_protocol

        if self.enabled is not True:
            if (self.snmp_v3_enable or self.snmp_v3_access_permission or
                    self.snmp_v3_auth_protocol or self.snmp_v3_priv_protocol):
                err = "Argument: invalid snmp mode, please check parameter"
                self.err_list.append(err)
                raise FailException(*self.err_list)

        if self.snmp_v3_enable:
            if len(self.password) < 8:
                err = "Argument: invalid snmp mode, please check parameter"
                self.err_list.append(err)
                raise FailException(*self.err_list)

        if self.web_enable is False or self.ipmi_enable is False:
            if "User" != self.role_id:
                err = ("Argument: invalid role! Web and IPMI "
                       "can be disable only if the role is user")
                self.err_list.append(err)
                raise FailException(*self.err_list)

    def _parse_b01_args(self, args):

        self.enabled = (("Enable" == args.enabled) if args.enabled is not None
                        else True)
        self.user_name = args.new_user_name
        self.password = args.new_pwd

        role_id_dict = {"Administrator": "administrator",
                        "Operator": "operator",
                        "Commonuser": "user",
                        "OEM": "none"
                        }
        self.role_id = role_id_dict.get(args.role_id)
        self.kvm_enable = 0
        self.vmedia_enable = 0
        if args.privilege is not None:
            priv_set = set(filter(None, args.privilege.split(r',')))
            if not priv_set.issubset({"KVM", "VMM", "SOL", "None"}):
                err = ("Argument: the privilege parameter is invalid, "
                       "must be selected in {KVM,VMM,SOL,None}")
                self.err_list.append(err)
                raise FailException(*self.err_list)
            if "KVM" in priv_set:
                self.kvm_enable = 1
            if "VMM" in priv_set:
                self.vmedia_enable = 1
        if "Enable" == args.snmp_v3_enable:
            self.snmp_v3_enable = 1
        else:
            self.snmp_v3_enable = 0
        self.snmp_v3_access_permission = args.snmp_v3_access_permission
        self.snmp_v3_auth_protocol = args.snmp_v3_auth_protocol
        self.snmp_v3_priv_protocol = args.snmp_v3_priv_protocol

        if self.enabled is not True:
            if (self.snmp_v3_enable or self.snmp_v3_access_permission or
                    self.snmp_v3_auth_protocol or self.snmp_v3_priv_protocol):
                err = "Argument: invalid snmp mode, please check parameter"
                self.err_list.append(err)
                raise FailException(*self.err_list)

        if self.snmp_v3_enable:
            if len(self.password) < 8:
                err = "Argument: invalid snmp mode, please check parameter"
                self.err_list.append(err)
                raise FailException(*self.err_list)

        if self.web_enable is False or self.ipmi_enable is False:
            if "User" != self.role_id:
                err = ("Argument: invalid role! Web and IPMI "
                       "can be disable only if the role is user")
                self.err_list.append(err)
                raise FailException(*self.err_list)

    def _construct_param(self):

        payload = dict()
        payload["UserName"] = self.user_name
        payload["Password"] = self.password
        payload["RoleId"] = self.role_id
        payload["Locked"] = False
        payload["Enabled"] = self.enabled

        oem = dict()
        oem["Public"] = dict()
        oem["Public"]["KvmEnable"] = self.kvm_enable
        oem["Public"]["VmediaEnable"] = self.vmedia_enable
        oem["Public"]["IPMIEnable"] = self.ipmi_enable
        oem["Public"]["WebEnable"] = self.web_enable
        oem["Public"]["SnmpV3Enable"] = self.snmp_v3_enable
        oem["Public"]["SnmpV3AccessPermission"] = self.snmp_v3_access_permission
        oem["Public"]["SnmpV3AuthProtocol"] = self.snmp_v3_auth_protocol
        oem["Public"]["SnmpV3PrivProtocol"] = self.snmp_v3_priv_protocol
        payload['Oem'] = oem

        return payload

    def _construct_b01_param(self):

        payload = dict()
        payload["Locked"] = False
        payload["name"] = self.user_name
        payload["password"] = self.password
        payload["network_privilege"] = self.role_id
        payload["kvm"] = self.kvm_enable
        payload["vmedia"] = self.vmedia_enable
        payload["email_id"] = ""
        if self.enabled:
            payload["access"] = 1
        else:
            payload["access"] = 0
        payload["snmp"] = self.snmp_v3_enable
        payload["snmp_access"] = self.snmp_v3_access_permission
        payload["snmp_authentication_protocol"] = self.snmp_v3_auth_protocol
        payload["snmp_privacy_protocol"] = self.snmp_v3_priv_protocol
        return payload
