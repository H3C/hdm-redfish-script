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


class User:

    def __init__(self):
        self.id = None
        self.user_name = None
        self.role_id = None
        self.privilege = []
        self.locked = None
        self.enabled = None
        self.extended_privilege = None

    @property
    def dict(self):

        return {
            "Id": self.id,
            "UserName": self.user_name,
            "RoleId": self.role_id,
            "Privilege": self.privilege,
            "Locked": self.locked,
            "Enabled": self.enabled,
            "extended_privilege": self.extended_privilege
        }

    def pack_user_resource(self, resp):

        self.id = resp.get("Id", None)
        self.user_name = resp.get("UserName", None)
        self.role_id = resp.get("RoleId", None)
        self.locked = resp.get("Locked", None)
        self.enabled = "Enabled" if resp.get("Enabled") else "Disabled"

        if isinstance(resp.get("Oem", None), dict):
            pri_dict = {
                "KvmEnable": "KVM",
                "VmediaEnable": "VMM",
                "SOL": "SOL",
                "IPMIEnable": "IPMI",
                "WebEnable": "WEB"
            }
            public = resp["Oem"].get("Public", None)
            if isinstance(public, dict):
                self.extended_privilege = public
                for key, value in pri_dict.items():
                    if (public.get(key, None) is True or
                            public.get(key, None) == "true"):
                        self.privilege.append(value)
            public = resp["Oem"].get("H3C", None)
            if isinstance(public, dict):
                self.extended_privilege = public
                for key, value in pri_dict.items():
                    if (public.get(key, None) is True or
                            public.get(key, None) == "true"):
                        self.privilege.append(value)

    def pack_b01_user_resource(self, resp):

        self.id = resp.get("id", None)
        self.user_name = resp.get("name", None)
        role_display_dict = {
            "administrator": "Administrator",
            "none": "None",
            "operator": "Operator",
            "user": "User"
        }
        self.role_id = role_display_dict.get(resp.get("network_privilege"),
                                             None)
        user_access_dict = {
            1: "true",
            0: "false"
        }
        self.enabled = user_access_dict.get(resp.get("access"), None)
        if resp.get("kvm") == 1:
            self.privilege.append("KVM")
        if resp.get("vmedia") == 1:
            self.privilege.append("VMM")


class GetUser(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["name"]
        self.users = []

    @property
    def dict(self):

        return {
            "Users": self.users
        }

    @GetVersion()
    def run(self, args):

        init_args(args, self.args_lst)
        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                url = "/api/settings/users"
                resp = client.send_request("GET", url)
                user_list = []
                if isinstance(resp, list):
                    for info in resp:
                        user = User()
                        user.pack_b01_user_resource(info)
                        self.users.append(user)
                        if args.name == info.get("name"):
                            user_list.append(info)
                else:
                    self.err_list.append("Failure: get user information error")
                    raise FailException(*self.err_list)

                if args.name is not None:
                    self.users = user_list
                if not self.users:
                    self.err_list.append("Failure: the user does not exist")
                    raise FailException(*self.err_list)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            url = "/redfish/v1/AccountService/Accounts"
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                try:
                    members = sorted(resp["resource"]["Members"],
                                     key=lambda x: int(x['@odata.id'].
                                                       split(r"/")[5]))
                except (KeyError, Exception) as err:
                    self.err_list.append(str(err))
                    raise FailException(*self.err_list)
                for member in members:
                    user_url = member.get('@odata.id', None)
                    user_resp = client.send_request("GET", user_url)
                    if (isinstance(user_resp, dict) and
                            user_resp.get("status_code",
                                          None) in Constant.SUC_CODE):
                        if args.name is None:
                            user = User()
                            user.pack_user_resource(user_resp["resource"])
                            self.users.append(user)
                        elif args.name == user_resp["resource"].get("UserName",
                                                                    None):
                            user = User()
                            user.pack_user_resource(user_resp["resource"])
                            self.users.append(user)
                            break
                    else:
                        self.err_list.append("Failure: get user information"
                                             " error")
                        raise FailException(*self.err_list)
            if not self.users:
                self.err_list.append("Failure: the user does not exist")
                raise FailException(*self.err_list)
        return self.suc_list
