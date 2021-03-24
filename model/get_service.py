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
from utils.tools import init_args
from utils.model import BaseModule


class Service:

    def __init__(self):

        self.name = None
        self.enabled = None
        self.non_secure_port = None
        self.secure_port = None
        self.ssl_enable = None
        self.timeout = None
        self.maximum_sessions = None

    @property
    def dict(self):

        return {
            "Name": self.name,
            "Enabled": self.enabled,
            "NonSecurePort": self.non_secure_port,
            "SecurePort": self.secure_port,
            "SSLEnable": self.ssl_enable,
            "Timeout": self.timeout,
            "MaximumSessions": self.maximum_sessions
        }


class GetService(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["service_type"]
        self.service = []

    @property
    def dict(self):

        return {
            "Service": self.service
        }

    def run(self, args):

        init_args(args, self.args_lst)
        client = RestfulClient(args)
        url = "/api/settings/services"
        try:
            resp = client.send_request("GET", url)
            if isinstance(resp, list) and resp:
                if args.service_type is not None:
                    self.service = get_service_list(resp, args.service_type)
                else:
                    self.service = get_service_list(resp)
            else:
                err_info = "Failure: failed to get service information list"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list


def get_service_list(resp, service_type=None):

    service_list = list()
    for service in resp:
        if service_type is None:
            service_list.append(package_service(service))
        else:
            if service_type == service.get("service_name", None):
                service_list.append(package_service(service))
                break
    return service_list


def package_service(service):

    detail = dict()
    detail["name"] = service.get("service_name", None)
    if service.get("state", None) is not None:
        state = ("Enable" if service["state"] == 1 else "Disable")
    else:
        state = None
    detail["enabled"] = state
    non_secure_port = service.get("non_secure_port", None)
    if non_secure_port == -1:
        non_secure_port = "N/A"
    detail["non_secure_port"] = non_secure_port

    secure_port = service.get("secure_port", None)
    detail["ssl_enable"] = ("Enabled" if secure_port != -1 else "Disabled")
    if secure_port == -1:
        secure_port = "N/A"
    detail["secure_port"] = secure_port

    time_out = service.get("time_out", None)
    if time_out == -1:
        time_out = "N/A"
    detail["timeout"] = time_out

    maximum_sessions = service.get("maximum_sessions", None)
    if maximum_sessions == 255:
        maximum_sessions = "N/A"
    elif maximum_sessions is not None:
        maximum_sessions = maximum_sessions & 127
    detail["maximum_sessions"] = maximum_sessions

    ser = Service()
    ser.__dict__.update(detail)
    return ser
