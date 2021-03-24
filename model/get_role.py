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
from utils.common import Constant
from utils.model import BaseModule
from utils.tools import init_args
from utils.predo import AllowCommand


class Role:

    def __init__(self):
        self.id = None
        self.is_predefined = None
        self.assigned_privileges = None
        self.oem_privileges = None

    @property
    def dict(self):

        return {
            "Id": self.id,
            "IsPredefined": self.is_predefined,
            "AssignedPrivileges": self.assigned_privileges,
            "OemPrivileges": self.oem_privileges
        }

    def pack_role_resource(self, info):

        self.id = info.get("Id", None)
        self.is_predefined = info.get("IsPredefined", None)

        assigned_privileges = info.get("AssignedPrivileges", None)
        if assigned_privileges and isinstance(assigned_privileges, list):
            assigned_privileges = ", ".join(assigned_privileges)
        self.assigned_privileges = assigned_privileges
        oem_privileges = info.get("OemPrivileges")
        if oem_privileges and isinstance(oem_privileges, list):
            oem_privileges = ", ".join(oem_privileges)
        self.oem_privileges = oem_privileges


class GetRole(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["role"]

        self.roles = []

    @property
    def dict(self):

        return {
            "Roles": self.roles
        }

    @AllowCommand()
    def run(self, args):

        init_args(args, self.args_lst)
        url = "/redfish/v1/AccountService/Roles"
        client = RedfishClient(args)
        resp = client.send_request("GET", url)
        if (not isinstance(resp, dict) or
                Constant.SUCCESS_200 != resp.get("status_code", None)):
            self.err_list.append("Failure: get role information failed")
            raise FailException(*self.err_list)

        role_url_list = list()
        if args.role is None:
            members = resp["resource"].get("Members", None)
            if members and isinstance(members, list):
                for member in members:
                    role_url_list.append(member.get("@odata.id", None))
        else:
            url = "%s/%s" % (url, args.role)
            role_url_list.append(url)
        role_list = list()
        for role_url in role_url_list:
            role_resp = client.send_request("GET", role_url)
            if (isinstance(role_resp, dict) and Constant.SUCCESS_200 ==
                    role_resp.get("status_code", None)):
                role = Role()
                role.pack_role_resource(role_resp["resource"])
                role_list.append(role)
            else:
                self.err_list.append("Failure: get role information failed")
                raise FailException(*self.err_list)
        self.roles = role_list

        return self.suc_list
