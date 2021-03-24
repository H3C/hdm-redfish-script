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


import os
from exception.ToolException import FailException
from utils.model import BaseModule
from utils.client import RestfulClient
from utils.common import Constant
from utils.tools import init_args
from utils.predo import AllowCommand


class ImportSshKey(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["file_uri", "u_name"]

    @AllowCommand()
    def run(self, args):

        init_args(args, self.args_lst)
        if args.u_name is None:
            args.u_name = args.username
        config_file = args.file_uri

        if not os.path.isfile(config_file):
            err_info = ("Failure: import SSH key failed, reason: "
                        "file does not exist")
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        try:
            with open(config_file, "rb") as config_file_data:
                file_read = config_file_data.read()
        except (TypeError, ValueError, KeyError, IOError, Exception) as err:
            self.err_list.append(str(err))
            raise FailException(*self.err_list)
        else:
            _, file_name = os.path.split(config_file)
            fields = {
                "upload_ssh_key": (file_name, file_read,
                                   "application/octet-stream")
            }
        client = RestfulClient(args)
        try:

            url = "/api/settings/users"
            resp = client.send_request("get", url)
            if isinstance(resp, list):
                for info in resp:
                    if info.get("name") == args.u_name:
                        user_id = info.get("id")

                        url = "/api/settings/user/ssh-key-upload/%s" % user_id
                        import_resp = client.upload_request("POST", url,
                                                            fields=fields)
                        if (isinstance(import_resp, dict) and import_resp.get(
                                Constant.COMPLETE_CODE)
                                == Constant.SUCCESS_0):
                            url = "/api/settings/users/%s" % user_id
                            tmp_resp = client.send_request("get", url)
                            if isinstance(tmp_resp, list) and tmp_resp:
                                data = build_payload(tmp_resp[0])
                            else:
                                err = ("Failure: failed to get user "
                                       "configuration information: %s" %
                                       args.u_name)
                                self.err_list.append(err)
                                raise FailException(*self.err_list)
                            config_resp = client.send_request("put", url, data)
                            if (isinstance(config_resp, dict) and
                                    config_resp.get(Constant.COMPLETE_CODE)
                                    == Constant.SUCCESS_0):
                                suc_info = ("Success: import SSH "
                                            "key successfully")
                                self.suc_list.append(suc_info)
                            else:
                                err_info = "Failure: SSH enabled failed"
                                self.err_list.append(err_info)
                                raise FailException(*self.err_list)
                        else:
                            err_info = "Failure: SSH key import failed"
                            self.err_list.append(err_info)
                            raise FailException(*self.err_list)
                        break
                else:
                    err = "Failure: the user does not exist: %s" % args.u_name
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
            else:
                err = "Failure: filed to get user list"
                self.err_list.append(err)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list


def build_payload(detail):

    res = dict()
    res["id"] = detail.get("id")
    res["name"] = detail.get("name")
    res["email_id"] = ""
    res["user_operation"] = 1
    res["web"] = detail.get("web")
    res["ipmi"] = detail.get("ipmi")
    res["network_privilege"] = detail.get("network_privilege")
    res["snmp"] = detail.get("snmp")
    res["access"] = detail.get("access")
    res["confirm_password"] = ""
    res["password"] = ""
    res["password_size"] = ""
    res["snmp_access"] = detail.get("snmp_access")
    res["snmp_authentication_protocol"] = detail.get(
        "snmp_authentication_protocol")
    res["snmp_privacy_protocol"] = detail.get("snmp_privacy_protocol")
    return res
