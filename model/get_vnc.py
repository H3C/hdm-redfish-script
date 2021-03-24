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
from utils.model import BaseModule
from utils.predo import AllowCommand


class GetVnc(BaseModule):

    def __init__(self):

        super().__init__()
        self.key_board_layout = None
        self.session_timeout_minutes = None
        self.ssl_encryption_enabled = None
        self.maximum_number_of_sessions = None
        self.number_of_activated_sessions = None
        self.session_mode = None

    @property
    def dict(self):

        return {
            "KeyboardLayout": self.key_board_layout,
            "SessionTimeoutMinutes": self.session_timeout_minutes,
            "SSLEncryptionEnabled": self.ssl_encryption_enabled,
            "MaximumNumberOfSessions": self.maximum_number_of_sessions,
            "NumberOfActivatedSessions": self.number_of_activated_sessions,
            "SessionMode": self.session_mode
        }

    @AllowCommand()
    def run(self, args):

        client = RestfulClient(args)
        try:
            url = "/api/settings/services"
            resp = client.send_request("GET", url)
            if resp and isinstance(resp, list):
                for service in resp:
                    if service.get("service_name", None) == "VNC":
                        self.package_service(service)
                        return self.suc_list
                err_info = "Failure: failed to get VNC service information"
                self.err_list.append(err_info)
            else:
                err_info = "Failure: failed to get service information list"
                self.err_list.append(err_info)
            if self.err_list:
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def package_service(self, service):

        self.key_board_layout = service.get("KeyboardLayout", "en")
        self.session_timeout_minutes = int(service['time_out'] / 60) \
            if "time_out" in service else None

        self.ssl_encryption_enabled = service.get("SSLEncryptionEnabled",
                                                  False)
        self.maximum_number_of_sessions = (service['maximum_sessions'] & 127) \
            if "maximum_sessions" in service else None
        self.number_of_activated_sessions = (service["active_session"] & 127) \
            if "active_session" in service else None

        self.session_mode = service.get("SessionMode", None)
