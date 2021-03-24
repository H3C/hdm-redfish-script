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


class Log:

    def __init__(self):

        self.id = None
        self.username = None
        self.interface = None
        self.log_ip_address = None
        self.log_type = None
        self.log_content = None
        self.timestamp = None
        self.hostname = None
        self.log_level = None

    @property
    def dict(self):

        return {
            "Id": self.id,
            "UserName": self.username,
            "Interface": self.interface,
            "LogIpAdd": self.log_ip_address,
            "LogType": self.log_type,
            "LogContent": self.log_content,
            "Timestamp": self.timestamp,
            "HostName": self.hostname,
            "LogLevel": self.log_level
        }


class GetHdmLog(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["count"]
        self.hdm_log = []

    @property
    def dict(self):

        return {
            "HdmLog": self.hdm_log
        }

    def run(self, args):

        init_args(args, self.args_lst)
        if args.count is not None and args.count <= 0:
            err_info = ("Argument: invalid choice: %s (the value is a "
                        "positive integer)") % args.count
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        client = RestfulClient(args)
        try:
            url = "/api/health/hdm_log"
            resp = client.send_request("get", url)
            if isinstance(resp, list):
                count = len(resp)
                if args.count and args.count < count:
                    count = args.count
                self.hdm_log = get_log_resource(resp, count)
            else:
                err_info = "Failure: get hdm log failed"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list


def get_log_resource(log_list, count):

    res_log = []
    log_list_len = len(log_list)
    index = count
    while index >= 1:
        detail = dict()
        detail["id"] = log_list_len - index + 1
        detail["username"] = log_list[-index].get("username", None)
        detail["interface"] = log_list[-index].get("interface", None)
        detail["log_ip_address"] = log_list[-index].get("logIPAdrr", None)
        detail["log_type"] = log_list[-index].get("logtype", None)
        detail["log_content"] = log_list[-index].get("logcontent", None)
        detail["timestamp"] = log_list[-index].get("timestamp", None)
        detail["hostname"] = log_list[-index].get("hostname", None)
        detail["log_level"] = log_list[-index].get("loglevel", None)
        log = Log()
        log.__dict__.update(detail)
        res_log.append(log)
        index -= 1
    return res_log
