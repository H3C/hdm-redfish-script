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
from utils.tools import init_args
from utils.model import BaseModule


class SetService(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = [
            "service_type",
            "status",
            "non_secure_port",
            "secure_port",
            "timeout"
        ]

    def run(self, args):

        init_args(args, self.args_lst)
        flag = self.check_args(args)
        client = RestfulClient(args)
        url = "/api/settings/services"
        try:
            resp = client.send_request("GET", url)
            if resp and isinstance(resp, list):
                for service in resp:
                    if service.get("service_name", None) == args.service_type:
                        url, payload = (self.construct_request_parameters(
                            service, url, args))
                        resp = client.send_request("PUT", url, payload)
                        if (isinstance(resp, dict) and
                                ((resp.get("code") == Constant.FAILED_1306 or
                                  resp.get("cc") ==
                                  Constant.SUCCESS_0) if flag else resp.get(
                                    "cc") == Constant.SUCCESS_0)):
                            suc_info = ("Success: set BMC network protocol "
                                        "services successfully")
                            self.suc_list.append(suc_info)
                        else:
                            err_info = "Failure: service setup failed"
                            self.err_list.append(err_info)
                        break
                else:
                    err_info = "Failure: the service item was not found"
                    self.err_list.append(err_info)
            else:
                err_info = ("Failure: failed to get service configuration "
                            "information")
                self.err_list.append(err_info)
            if self.err_list:
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def check_args(self, args):

        flag = False
        if args.service_type == "Web":
            flag = True
            if args.status is not None:
                err_info = ("Argument: invalid choice: %s (may cause serious "
                            "consequences)" % args.status)
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        if args.service_type == "IPMI":
            flag = True
            if args.status is not None:
                err_info = ("Argument: invalid choice: %s (may cause serious "
                            "consequences)" % args.status)
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        return flag

    def construct_request_parameters(self, service, url, args):

        payload = service
        if args.status is not None:
            payload["state"] = (1 if args.status == "Enabled" else 0)
        if args.non_secure_port is not None:
            if (payload.get("non_secure_port", None) is None or payload.get(
                    "non_secure_port", None) == -1):
                err_info = ("Argument: invalid choice: %s (parameter not "
                            "available)" % args.non_secure_port)
                self.err_list.append(err_info)
            else:
                payload["non_secure_port"] = args.non_secure_port
        if args.secure_port is not None:
            if (payload.get("secure_port", None) is None or payload.get(
                    "secure_port", None) == -1):
                err_info = ("Argument: invalid choice: %s (parameter not "
                            "available)" % args.secure_port)
                self.err_list.append(err_info)
            else:
                payload["secure_port"] = args.secure_port
        if args.timeout is not None:
            if args.timeout < 5 or args.timeout > 30:
                err_info = ("Argument: invalid choice: %s (choose from 5 to "
                            "30)" % args.timeout)
                self.err_list.append(err_info)
            else:
                payload["time_out"] = args.timeout * 60
        url = "%s/%s" % (url, payload.get("id"))
        if self.err_list:
            raise FailException(*self.err_list)
        return url, payload
