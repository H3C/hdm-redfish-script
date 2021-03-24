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


class DelLdapUser(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["role_id"]

    def run(self, args):

        init_args(args, self.args_lst)
        client = RestfulClient(args)
        try:
            url = "/api/settings/ldap-users/%s" % str(args.role_id)
            resp = client.send_request("DELETE", url)
        finally:
            if client.cookie:
                client.delete_session()

        if (isinstance(resp, dict) and
                Constant.SUCCESS_0 == resp.get("cc", None)):
            suc = "Success: delete ldap user successfully"
            self.suc_list.append(suc)
        else:
            self.err_list.append("Failure: failed to delete ldap user")
            raise FailException(*self.err_list)
        return self.suc_list
