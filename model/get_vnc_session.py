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


class Session:
    def __init__(self):

        self.id = None
        self.session_id = None
        self.session_type = None
        self.client_ip = None
        self.user_id = None
        self.user_name = None
        self.user_privilege = None

    @property
    def dict(self):

        return {
            "Id": self.id,
            "SessionID": self.session_id,
            "SessionType": self.session_type,
            "ClientIP": self.client_ip,
            "UserID": self.user_id,
            "UserName": self.user_name,
            "UserPrivilege": self.user_privilege
        }


class GetVncSession(BaseModule):

    def __init__(self):

        super().__init__()
        self.maximum = None
        self.session_lst = list()

    @property
    def dict(self):

        return {
            "Maximum": self.maximum,
            "Session": self.session_lst
        }

    @AllowCommand()
    def run(self, args):

        client = RestfulClient(args)
        try:
            self.maximum = self.get_maximum(client)
            self.session_lst = self.get_session_list(client)
            if not self.session_lst:
                suc_info = "Success: vnc session is empty"
                self.suc_list.append(suc_info)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def get_maximum(self, client):

        maximum = None
        url = "/api/settings/services"
        resp = client.send_request("GET", url)
        if isinstance(resp, list) and resp:
            for service in resp:
                if "VNC" == service.get("service_name", None):
                    maximum_sessions = service.get("maximum_sessions", None)
                    maximum_sessions = (
                        "N/A" if maximum_sessions == 255 else (
                            maximum_sessions & 127 if
                            isinstance(maximum_sessions, int) else None))
                    maximum = maximum_sessions
        else:
            err_info = "Failure: failed to get service information list"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return maximum

    def get_session_list(self, client):

        sessions = []
        url = "/api/settings/service-sessions?service_id=2048"
        resp = client.send_request("GET", url)
        if isinstance(resp, list):
            for session in resp:
                sessions.append(package_session(session))
        else:
            err_info = "Failure: failed to get vnc session"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return sessions


def package_session(session):

    session_type_dict = {
        0: "Web HTTP",
        1: "Web HTTPS",
        2: "Telnet",
        3: "SSH",
        4: "Web",
        5: "KVM",
        6: "VMedia",
        7: "VMedia CD",
        8: "VMedia FD",
        9: "VMedia HD",
        10: "VMedia local CD",
        11: "VMedia local FD",
        12: "VMedia local HD",
        13: "SOL SSH",
        14: "Remote XDP",
        15: "VNC"
    }
    privilege_dict = {
        0: "Reserved",
        1: "Callback",
        2: "User",
        3: "Operator",
        4: "Administrator",
        5: "OEM",
        15: "Reserved"
    }

    detail = dict()
    detail["id"] = session.get("id")
    detail["session_id"] = session.get("session_id")
    detail["session_type"] = session_type_dict.get(session.get("session_type"))
    detail["client_ip"] = session.get("client_ip")
    detail["user_id"] = session.get("user_id")
    detail["user_name"] = session.get("user_name")
    detail["user_privilege"] = privilege_dict.get(
        session.get("user_privilege"))
    sens = Session()
    sens.__dict__.update(detail)
    return sens
