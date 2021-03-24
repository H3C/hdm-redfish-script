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


class DelAdUser(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["role_id"]

    def run(self, args):

        init_args(args, self.args_lst)
        client = RestfulClient(args)
        try:
            if self.check_conditions(client, args):
                url = "/api/settings/active_directory_users/%s" % args.role_id
                resp = client.send_request("DELETE", url)
                if isinstance(resp, dict) and Constant.SUCCESS_0 == resp.get(
                        "cc", None):
                    err = "Success: delete ad user successfully"
                    self.suc_list.append(err)
                else:
                    self.err_list.append("Failure: failed to delete ad user")
                    raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def check_conditions(self, client, args):

        url = "/api/settings/active_directory_settings"
        resp = client.send_request("GET", url)
        if isinstance(resp, dict) and resp.get("cc") == Constant.SUCCESS_0:
            if resp.get("enable") == 1:
                url = "/api/settings/active_directory_users"
                ad_users_resp = client.send_request("GET", url)
                if isinstance(ad_users_resp, list):
                    for user in ad_users_resp:
                        if (args.role_id == user.get("id") and
                                user.get("role_group_name")):
                            return True
                    else:
                        err_info = ("Failure: group is not enabled and "
                                    "cannot be deleted")
                        self.err_list.append(err_info)
                else:
                    err_info = ("Failure: failed to get group "
                                "collection information")
                    self.err_list.append(err_info)
            else:
                err_info = ("Failure: AD is not enabled, "
                            "the group cannot be deleted")
                self.err_list.append(err_info)
        else:
            err_info = "Failure: failed to get AD configuration information"
            self.err_list.append(err_info)
        raise FailException(*self.err_list)
