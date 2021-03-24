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


class DelUser(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["name"]

    def run(self, args):

        init_args(args, self.args_lst)
        client = RestfulClient(args)
        try:
            url = "/api/settings/users"
            resp = client.send_request("GET", url)
            if isinstance(resp, list):
                for user in resp:
                    if user.get("name", None) == args.name:
                        user_id = user.get("id", None)
                        url = "/api/settings/users/%s" % user_id
                        resp = client.send_request("DELETE", url)
                        if (isinstance(resp, dict) and
                                Constant.SUCCESS_0 == resp.get("cc", None)):
                            suc = "Success: delete user successfully"
                            self.suc_list.append(suc)
                        else:
                            err = "Failure: failed to delete user"
                            self.err_list.append(err)
                            raise FailException(*self.err_list)
                        break
                else:
                    err = "Failure: this user does not exist: %s" % args.name
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
            else:
                self.err_list.append("Failure: failed to get user list")
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()

        return self.suc_list
