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


class SetUser(BaseModule):

    def __init__(self):
        super().__init__()

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

        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                cmd_type = self._parse_b01_args(args)
                url = "/api/settings/users"
                user_id = None
                user_info = None
                resp = client.send_request("GET", url)
                if isinstance(resp, list):
                    for info in resp:
                        if self.user_name == info.get("name"):
                            user_id = info.get("id")
                            user_info = info
                            break
                if user_id is None:
                    err = "Failure: the user does not exist: %s" \
                          % self.user_name
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
                else:
                    url = "/api/settings/users/" + str(user_id)
                    payload = self._construct_b01_request_param(user_info)
                    payload["id"] = user_id
                    resp = client.send_request("PUT", url, payload)
                    if isinstance(resp, dict) and resp.get("cc") ==\
                            Constant.SUCCESS_0:
                        suc = "Success: set %s successfully" % cmd_type
                        self.suc_list.append(suc)
                    else:
                        err = "Failure: failed to set %s" % cmd_type
                        self.err_list.append(err)
                        raise FailException(*self.err_list)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            cmd_type = self._parse_args(args)
            url = "/redfish/v1/AccountService/Accounts"
            client = RedfishClient(args)
            resp = client.send_request("GET", url)
            if ((not isinstance(resp, dict)) or
                    resp.get("status_code", None) not in Constant.SUC_CODE):
                self.err_list.append("Failure: failed to get user collection")
                raise FailException(*self.err_list)
            user_list = resp["resource"].get("Members", [])
            for user in user_list:
                user_url = user.get("@odata.id", None)
                user_resp = client.send_request("GET", user_url)
                if (isinstance(user_resp, dict) and
                        user_resp.get("status_code", None)
                        in Constant.SUC_CODE):
                    if (user_resp["resource"].get("UserName", None) ==
                            self.user_name):
                        user_cache = user_resp
                        break
                else:
                    err = "Failure: failed to get user details"
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
            else:
                err = "Failure: the user does not exist: %s" % self.user_name
                self.err_list.append(err)
                raise FailException(*self.err_list)
            url, payload = self._construct_request_param(user_cache, url)
            resp = client.send_request("PATCH", url, payload)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                suc = "Success: set %s successfully" % cmd_type
                self.suc_list.append(suc)
            else:
                err = "Failure: failed to set %s" % cmd_type
                self.err_list.append(err)
                raise FailException(*self.err_list)

        return self.suc_list

    def _parse_args(self, args):

        cmd_type = None
        if "enabled" in args:
            self.enabled = ("Enable" == args.enabled) if args.enabled else None
            cmd_type = "user"
        if "new_user_name" in args:
            if args.new_user_name:
                self.user_name = args.new_user_name
            else:
                self.user_name = args.username
        if "new_pwd" in args:
            self.password = args.new_pwd
            if not cmd_type:
                cmd_type = "user password"
        role_id_dict = {"Administrator": "Administrator",
                        "Operator": "Operator",
                        "User": "User",
                        "None": "None",
                        "Commonuser": "User",
                        "OEM": "None"
                        }
        if "role_id" in args:
            self.role_id = role_id_dict.get(args.role_id)
        if "privilege" in args:
            if not (args.privilege or args.role_id):
                err = "Argument: at least one parameter must be specified"
                self.err_list.append(err)
                raise FailException(*self.err_list)
            if not cmd_type:
                cmd_type = "user permissions"
            self.kvm_enable = False
            self.vmedia_enable = False
            if args.privilege:
                priv_set = set(filter(None, args.privilege.split(r',')))
                if not priv_set.issubset({"KVM", "VMM", "SOL", "None"}):
                    err = ("Argument: the privilege parameter is invalid, "
                           "must be selected in {KVM,VMM,SOL,None}")
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
                self.kvm_enable = "KVM" in priv_set
                self.vmedia_enable = "VMM" in priv_set
        else:
            if "vmedia_enable" in args:
                self.vmedia_enable = (("Enable" == args.vmedia_enable) if
                                      args.vmedia_enable else None)
            if "kvm_enable" in args:
                self.kvm_enable = (("Enable" == args.kvm_enable) if
                                   args.kvm_enable else None)
        if "ipmi_enable" in args:
            self.ipmi_enable = (("Enable" == args.ipmi_enable) if
                                args.ipmi_enable else None)
        if "web_enable" in args:
            self.web_enable = (("Enable" == args.web_enable) if
                               args.web_enable else None)
        if "snmp_v3_enable" in args:
            self.snmp_v3_enable = (("Enable" == args.snmp_v3_enable) if
                                   args.snmp_v3_enable else None)
        if "snmp_v3_access_permission" in args:
            self.snmp_v3_access_permission = args.snmp_v3_access_permission
        if "snmp_v3_auth_protocol" in args:
            self.snmp_v3_auth_protocol = args.snmp_v3_auth_protocol
        if "snmp_v3_priv_protocol" in args:
            self.snmp_v3_priv_protocol = args.snmp_v3_priv_protocol

        if self.enabled is False:
            if (self.snmp_v3_enable or self.snmp_v3_access_permission or
                    self.snmp_v3_auth_protocol or self.snmp_v3_priv_protocol):
                err = ("Failure: the parameter is not available "
                       "while the user is inactive")
                self.err_list.append(err)
                raise FailException(*self.err_list)

        if self.snmp_v3_enable and self.password:
            if len(self.password) < 8:
                err = ("Failure: when the user SNMP extension permission is "
                       "enabled, the password length cannot be less than 8")
                self.err_list.append(err)
                raise FailException(*self.err_list)

        if self.web_enable is False or self.ipmi_enable is False:
            if self.role_id and "User" != self.role_id:
                err = ("Failure: invalid role! Web and IPMI "
                       "can be disable only if the role is user")
                self.err_list.append(err)
                raise FailException(*self.err_list)

        flag = (
            self.enabled is not None or
            self.password is not None or
            self.role_id is not None or
            self.kvm_enable is not None or
            self.vmedia_enable is not None or
            self.ipmi_enable is not None or
            self.web_enable is not None or
            self.snmp_v3_enable is not None or
            self.snmp_v3_access_permission is not None or
            self.snmp_v3_auth_protocol is not None or
            self.snmp_v3_priv_protocol is not None
        )

        if not flag:
            self.err_list.append("Failure: need at least one parameter")
            raise FailException(*self.err_list)

        return cmd_type

    def _parse_b01_args(self, args):

        cmd_type = None
        if "enabled" in args:
            self.enabled = ("Enable" == args.enabled) if args.enabled else None
            cmd_type = "user"
        if "new_user_name" in args:
            if args.new_user_name:
                self.user_name = args.new_user_name
            else:
                self.user_name = args.username
        if "new_pwd" in args:
            self.password = args.new_pwd
            if not cmd_type:
                cmd_type = "user password"
        role_id_dict = {"Administrator": "administrator",
                        "Operator": "operator",
                        "Commonuser": "user",
                        "OEM": "none"
                        }
        if "role_id" in args:
            self.role_id = role_id_dict.get(args.role_id)
        if "privilege" in args:
            if not (args.privilege or args.role_id):
                err = "Argument: at least one parameter must be specified"
                self.err_list.append(err)
                raise FailException(*self.err_list)
            if not cmd_type:
                cmd_type = "user permissions"
            self.kvm_enable = 0
            self.vmedia_enable = 0
            if args.privilege:
                priv_set = set(filter(None, args.privilege.split(r',')))
                if not priv_set.issubset({"KVM", "VMM"}):
                    err = ("Argument: the privilege parameter is invalid, "
                           "must be selected in {KVM,VMM}")
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
                if "KVM" in priv_set:
                    self.kvm_enable = 1
                if "VMM" in priv_set:
                    self.vmedia_enable = 1
        else:
            if "vmedia_enable" in args:
                self.vmedia_enable = (("Enable" == args.vmedia_enable) if
                                      args.vmedia_enable else None)
            if "kvm_enable" in args:
                self.kvm_enable = (("Enable" == args.kvm_enable) if
                                   args.kvm_enable else None)
        if "ipmi_enable" in args:
            self.ipmi_enable = (("Enable" == args.ipmi_enable) if
                                args.ipmi_enable else None)
        if "web_enable" in args:
            self.web_enable = (("Enable" == args.web_enable) if
                               args.web_enable else None)
        if "snmp_v3_enable" in args:
            self.snmp_v3_enable = (("Enable" == args.snmp_v3_enable) if
                                   args.snmp_v3_enable else None)
        if "snmp_v3_access_permission" in args:
            self.snmp_v3_access_permission = args.snmp_v3_access_permission
        if "snmp_v3_auth_protocol" in args:
            self.snmp_v3_auth_protocol = args.snmp_v3_auth_protocol
        if "snmp_v3_priv_protocol" in args:
            self.snmp_v3_priv_protocol = args.snmp_v3_priv_protocol

        if self.enabled is False:
            if (self.snmp_v3_enable or self.snmp_v3_access_permission or
                    self.snmp_v3_auth_protocol or self.snmp_v3_priv_protocol):
                err = ("Failure: the parameter is not available "
                       "while the user is inactive")
                self.err_list.append(err)
                raise FailException(*self.err_list)

        if self.snmp_v3_enable and self.password:
            if len(self.password) < 8:
                err = ("Failure: when the user SNMP extension permission is "
                       "enabled, the password length cannot be less than 8")
                self.err_list.append(err)
                raise FailException(*self.err_list)

        if self.web_enable is False or self.ipmi_enable is False:
            if self.role_id and "User" != self.role_id:
                err = ("Failure: invalid role! Web and IPMI "
                       "can be disable only if the role is user")
                self.err_list.append(err)
                raise FailException(*self.err_list)

        flag = (
            self.enabled is not None or
            self.password is not None or
            self.role_id is not None or
            self.kvm_enable is not None or
            self.vmedia_enable is not None or
            self.ipmi_enable is not None or
            self.web_enable is not None or
            self.snmp_v3_enable is not None or
            self.snmp_v3_access_permission is not None or
            self.snmp_v3_auth_protocol is not None or
            self.snmp_v3_priv_protocol is not None
        )

        if not flag:
            self.err_list.append("Failure: need at least one parameter")
            raise FailException(*self.err_list)

        return cmd_type

    def _construct_request_param(self, cache, url):

        cache = cache["resource"]
        payload = dict()
        url = "%s/%s" % (url, cache.get('Id', None))
        payload["Enabled"] = (self.enabled if self.enabled is not None else
                              cache.get('Enabled', None))
        payload["Password"] = (self.password if self.password else
                               cache.get("Password", None))
        payload["UserName"] = self.user_name
        payload["RoleId"] = (self.role_id if self.role_id else
                             cache.get("RoleId", None))
        if isinstance(cache.get("Oem", None), dict):
            if isinstance(cache["Oem"].get("Public", None), dict):
                public = cache["Oem"]["Public"]
                kvm_enable = (
                    self.kvm_enable if self.kvm_enable is not None else
                    public.get('KvmEnable', None)
                )
                vmedia_enable = (
                    self.vmedia_enable if self.vmedia_enable is not None else
                    public.get('VmediaEnable', None)
                )
                oem_dict = {
                    "Public": {
                        "KvmEnable": kvm_enable,
                        "VmediaEnable": vmedia_enable
                    }
                }
                oem_dict["Public"]["IPMIEnable"] = (
                    self.ipmi_enable if self.ipmi_enable is not None else
                    public.get("IPMIEnable", None)
                )
                oem_dict["Public"]["WebEnable"] = (
                    self.web_enable if self.web_enable is not None else
                    public.get("WebEnable", None)
                )
                oem_dict["Public"]["SnmpV3Enable"] = (
                    self.snmp_v3_enable if self.snmp_v3_enable is not None else
                    public.get("SnmpV3Enable", None)
                )
                oem_dict["Public"]["SnmpV3AccessPermission"] = (
                    self.snmp_v3_access_permission if
                    self.snmp_v3_access_permission else public.get(
                        "SnmpV3AccessPermission", None)
                )
                oem_dict["Public"]["SnmpV3AuthProtocol"] = (
                    self.snmp_v3_auth_protocol if self.snmp_v3_auth_protocol
                    else public.get("SnmpV3AuthProtocol", None)
                )
                oem_dict["Public"]["SnmpV3PrivProtocol"] = (
                    self.snmp_v3_priv_protocol if self.snmp_v3_priv_protocol
                    else public.get("SnmpV3PrivProtocol", None)
                )

                if (oem_dict["Public"]["SnmpV3Enable"] is True and
                        self.password):
                    if len(self.password) < 8:
                        err = ("Failure: when the user SNMP extension "
                               "permission is enabled, the password "
                               "length cannot be less than 8")
                        self.err_list.append(err)
                        raise FailException(*self.err_list)

                payload["Oem"] = oem_dict

        if (payload["RoleId"] != "User" and
                (self.web_enable is False or self.ipmi_enable is False)):
            err = ("Argument: invalid role, Web and IPMI "
                   "can be disable only if the role is user")
            self.err_list.append(err)
            raise FailException(*self.err_list)

        if payload["Enabled"] is False:
            if (self.snmp_v3_enable or self.snmp_v3_access_permission or
                    self.snmp_v3_auth_protocol or self.snmp_v3_priv_protocol):
                err = ("Failure: the parameter is not available "
                       "while the user is inactive")
                self.err_list.append(err)
                raise FailException(*self.err_list)

        return url, payload

    def _construct_b01_request_param(self, user_info):

        payload = dict()
        payload["Locked"] = False
        payload["name"] = self.user_name
        payload["password"] = self.password
        payload["confirm_password"] = self.password
        if self.role_id is None:
            payload["network_privilege"] = user_info.get("network_privilege")
        else:
            payload["network_privilege"] = self.role_id
        payload["kvm"] = self.kvm_enable
        payload["vmedia"] = self.vmedia_enable
        payload["access"] = user_info.get("access")
        payload["email_id"] = user_info.get("email_id")
        payload["snmp"] = user_info.get("snmp")
        payload["snmp_access"] = user_info.get("snmp_access")
        payload["snmp_authentication_protocol"] = \
            user_info.get("snmp_authentication_protocol")
        payload["snmp_privacy_protocol"] = user_info.get(
            "snmp_privacy_protocol")
        payload["ssh_key"] = user_info.get("ssh_key")
        payload["user_operation"] = 1
        return payload
