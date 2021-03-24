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


class SetActiveDirectory(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = [
            "enable",
            "user_domain_name",
            "secret_username",
            "secret_password",
            "domain_controller1",
            "domain_controller2",
            "domain_controller3"
        ]

    def run(self, args):

        init_args(args, self.args_lst)
        payload = self._construct_param(args)
        client = RestfulClient(args)
        try:
            url = "/api/settings/active_directory_settings"
            resp = client.send_request("PUT", url, payload)
            if isinstance(resp, dict) and Constant.SUCCESS_0 == resp.get(
                    "cc", None):
                self.suc_list.append("Success: set ad successfully")
            else:
                self.err_list.append("Failure: failed to set ad")
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()

        return self.suc_list

    def _construct_param(self, args):

        payload = {
            "enable": 0,
            "secret_username": "",
            "secret_password": "",
            "user_domain_name": "",
            "domain_controller1": "",
            "domain_controller2": "",
            "domain_controller3": ""
        }

        if args.enable == "Enable":
            payload["enable"] = 1
        else:

            if (args.user_domain_name or args.secret_username or
                    args.secret_password or args.domain_controller1 or
                    args.domain_controller2 or args.domain_controller3):
                err_info = ("Failure: parameters are not available when "
                            "AD authentication is disabled")
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            return payload
        if args.secret_password is not None:
            payload["secret_password"] = args.secret_password

        if args.user_domain_name is not None:
            if not is_domain(args.user_domain_name):
                err = ("Failure: invalid user domain name: %s"
                       % args.user_domain_name)
                self.err_list.append(err)
                raise FailException(*self.err_list)
            payload["user_domain_name"] = args.user_domain_name
        else:
            err = "Argument: user domain name needed"
            self.err_list.append(err)
            raise FailException(*self.err_list)

        if args.domain_controller1 is not None:
            if not is_parameter_legal(args.domain_controller1):
                err = ("Failure: invalid domain controller1 server address: %s"
                       % args.domain_controller1)
                self.err_list.append(err)
                raise FailException(*self.err_list)
            payload["domain_controller1"] = args.domain_controller1
        else:
            err = "Argument: domain controller1 needed"
            self.err_list.append(err)
            raise FailException(*self.err_list)

        if args.secret_username is not None:
            if len(args.secret_username) > 64:
                self.err_list.append(
                    "Failure: invalid secret username!(Less than 64 bytes)")
                raise FailException(*self.err_list)
            payload["secret_username"] = args.secret_username

        if args.domain_controller2 is not None:
            if not is_parameter_legal(args.domain_controller2):
                err = ("Failure: invalid domain controller2 server address: %s"
                       % args.domain_controller2)
                self.err_list.append(err)
                raise FailException(*self.err_list)
            payload["domain_controller2"] = args.domain_controller2

        if args.domain_controller3 is not None:
            if not is_parameter_legal(args.domain_controller3):
                err = ("Failure: invalid domain controller3 server address: %s"
                       % args.domain_controller3)
                self.err_list.append(err)
                raise FailException(*self.err_list)
            payload["domain_controller3"] = args.domain_controller3
        return payload


def is_parameter_legal(str_):

    return is_ipv4(str_) or is_ipv6(str_) or is_domain(str_)
