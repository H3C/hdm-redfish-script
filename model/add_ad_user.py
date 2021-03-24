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
from utils.model import BaseModule
from utils.tools import init_args
from utils.predo import GetVersion
from utils import globalvar


class AddAdUser(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = [
            "role_id",
            "role_group_name",
            "role_group_domain",
            "role_group_privilege",
            "role_group_health_privilege",
            "role_group_network_privilege",
            "role_group_user_privilege",
            "role_group_basic_privilege",
            "role_group_remotectrl_privilege",
            "role_group_kvm_privilege",
            "role_group_vmedia_privilege",
            "role_group_power_privilege",
            "role_group_firmware_privilege"
        ]

    @GetVersion()
    def run(self, args):

        init_args(args, self.args_lst)
        client = RestfulClient(args)
        try:
            ad_config_url = "/api/settings/active_directory_settings"
            resp = client.send_request("GET", ad_config_url)
            if isinstance(resp, dict) or Constant.SUCCESS_0 == resp.get(
                    "cc", None):
                if 0 == resp.get("enable", None):
                    self.err_list.append(
                        "Failure: ad disable, can not add ad user")
                    raise FailException(*self.err_list)
            else:
                self.err_list.append("Failure: failed to add ad user")
                raise FailException(*self.err_list)
            payload = self._construct_param(args)
            add_url = "/api/settings/active_directory_users"
            resp = client.send_request("POST", add_url, payload)
            if (isinstance(resp, dict) and Constant.SUCCESS_0 == resp.get(
                    "cc", None) or resp.get("role_group_name", None)):
                self.suc_list.append("Success: add ad user successfully")
            else:
                self.err_list.append("Failure: Failed to add ad user")
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def _construct_param(self, args):

        privilege_b03 = {
            "Administrator": "administrator",
            "Operator": "operator",
            "User": "user"
        }

        privilege_b05 = {
            "CustomRole1": "custom 1",
            "CustomRole2": "custom 2",
            "CustomRole3": "custom 3",
            "CustomRole4": "custom 4",
            "CustomRole5": "custom 5",
        }

        payload = dict()
        payload["role_id"] = args.role_id
        payload["role_group_name"] = args.role_group_name
        payload["role_group_domain"] = args.role_group_domain
        if globalvar.HDM_VERSION < "2.0.04":
            if args.role_group_privilege in privilege_b03.keys():
                payload["role_group_privilege"] = (
                    privilege_b03.get(args.role_group_privilege))
            else:
                err = ("Argument: invalid choice: %s, please choose from [%s]"
                       % (args.role_group_privilege, ", ".join(
                           privilege_b03.keys())))
                self.err_list.append(err)
                raise FailException(*self.err_list)
        elif globalvar.HDM_VERSION < "2.06":
            if args.role_group_privilege in privilege_b03.keys():
                payload["role_group_privilege"] = (
                    privilege_b03.get(args.role_group_privilege))
            elif args.role_group_privilege in privilege_b05.keys():
                payload["role_group_privilege"] = (
                    privilege_b05.get(args.role_group_privilege))
            else:
                err = ("Argument: invalid choice: %s, please choose from [%s]"
                       % (args.role_group_privilege, ", ".join(
                           dict(privilege_b03, **privilege_b05).keys())))
                self.err_list.append(err)
                raise FailException(*self.err_list)
        else:
            if args.role_group_privilege in privilege_b03.keys():
                payload["role_group_privilege"] = (
                    privilege_b03.get(args.role_group_privilege))
            else:
                payload["role_group_privilege"] = args.role_group_privilege
        payload["role_group_kvm_privilege"] = (
            0 if args.role_group_kvm_privilege == 0 else 1)
        payload["role_group_vmedia_privilege"] = (
            0 if args.role_group_vmedia_privilege == 0 else 1)
        payload["role_group_network_privilege"] = (
            0 if args.role_group_network_privilege == 0 else 1)
        payload["role_group_user_privilege"] = (
            0 if args.role_group_user_privilege == 0 else 1)
        payload["role_group_basic_privilege"] = (
            0 if args.role_group_basic_privilege == 0 else 1)
        payload["role_group_power_privilege"] = (
            0 if args.role_group_power_privilege == 0 else 1)
        payload["role_group_firmware_privilege"] = (
            0 if args.role_group_firmware_privilege == 0 else 1)
        payload["role_group_health_privilege"] = (
            0 if args.role_group_health_privilege == 0 else 1)
        payload["role_group_remotectrl_privilege"] = (
            0 if args.role_group_remotectrl_privilege == 0 else 1)

        return payload
