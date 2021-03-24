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
from utils.client import RestfulClient
from utils.common import Constant
from utils.tools import is_ipv4
from utils.tools import is_ipv6
from utils.tools import is_domain
from utils.model import BaseModule
from utils.tools import init_args


class SetLdap(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = [
            "bind_dn",
            "common_name_type",
            "enable",
            "encryption_type",
            "ldap_password",
            "ldap_port",
            "search_base",
            "server_address",
            "user_login_attribute"
        ]
        self.bind_dn = None
        self.common_name_type = None
        self.enable = None
        self.encryption_type = None
        self.password = None
        self.ldap_port = None
        self.search_base = None
        self.server_address = None
        self.user_login_attribute = None

    def run(self, args):

        init_args(args, self.args_lst)
        self._parse_args(args)

        client = RestfulClient(args)
        try:
            url = "/api/settings/ldap-settings"
            resp = client.send_request("GET", url)
            if not isinstance(resp, dict) or Constant.SUCCESS_0 != resp.get(
                    "cc", None):
                self.err_list.append("Failure: failed to set ldap")
                raise FailException(*self.err_list)
            self._construct_param(resp)
            resp = client.send_request("PUT", url, resp)
            if isinstance(resp, dict) and Constant.SUCCESS_0 == resp.get(
                    "cc", None):
                self.suc_list.append("Success: set ldap successfully")
            else:
                self.err_list.append("Failure: failed to set ldap")
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()

        return self.suc_list

    def _parse_args(self, args):

        self.enable = args.enable
        if "0" == args.enable:
            return
        args_dict = {
            "encryption_type": "encryption type",
            "common_name_type": "LDAP server address type",
            "server_address": "LDAP Server string",
            "ldap_port": "the port number",
            "bind_dn": "LDAP administrator user DN",
            "search_base": "search base DN",
            "user_login_attribute": "user login properties"
        }
        for key, value in args_dict.items():
            if args.__dict__.get(key, None) is None:
                self.err_list.append("Argument: %s needed" % value)
                raise FailException(*self.err_list)
            self.__dict__[key] = args.__dict__.get(key, None)
        if ((self.common_name_type == "ip" and
             not (is_ipv4(self.server_address) or
                  is_ipv6(self.server_address))) or
                (self.common_name_type == "fqdn" and
                 not is_domain(self.server_address))):
            self.err_list.append("Argument: invalid server address")
            raise FailException(*self.err_list)

        if args.ldap_port < 1 or args.ldap_port > 65535:
            self.err_list.append("Argument: invalid port number(1-65535)")
            raise FailException(*self.err_list)
        if len(self.bind_dn) > 255:
            self.err_list.append(
                "Argument: invalid bind dn(Less than 255 bytes)")
            raise FailException(*self.err_list)
        if len(self.search_base) > 255:
            self.err_list.append(
                "Argument: invalid search base(Less than 255 bytes)")
            raise FailException(*self.err_list)

        if args.ldap_password is not None:
            self.password = args.ldap_password

    def _construct_param(self, payload):

        if self.bind_dn is not None:
            payload["bind_dn"] = self.bind_dn
        if self.common_name_type is not None:
            payload["common_name_type"] = self.common_name_type
        if self.enable is not None:
            payload["enable"] = self.enable
        if self.encryption_type is not None:
            payload["encryption_type"] = self.encryption_type
        if self.password is not None:
            payload["password"] = self.password
        if self.ldap_port is not None:
            payload["port"] = self.ldap_port
        if self.search_base is not None:
            payload["search_base"] = self.search_base
        if self.server_address is not None:
            payload["server_address"] = self.server_address
        if self.user_login_attribute is not None:
            payload["user_login_attribute"] = self.user_login_attribute
        payload["password"] = self.password if self.password is not None else ""
        payload.pop("cc")
