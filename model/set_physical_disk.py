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
from utils.predo import AllowCommand


class SetPDisk(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["controller_id", "physical_id", "status"]

    @AllowCommand()
    def run(self, args):

        init_args(args, self.args_lst)
        url = "/api/remote/physical_config"
        payload = self.construct_request_parameters(args)
        client = RestfulClient(args)
        try:
            resp = client.send_request("POST", url, payload)
        finally:
            if client.cookie:
                client.delete_session()
        if (isinstance(resp, dict) and
                Constant.SUCCESS_0 == resp.get("cc", None)):
            suc = "Success: set physical drive successfully"
            self.suc_list.append(suc)
        else:
            err = "Failure: failed to set physical drive"
            self.err_list.append(err)
            raise FailException(*self.err_list)

        return self.suc_list

    @staticmethod
    def construct_request_parameters(args):

        payload = dict()
        payload["ctrl_id"] = args.controller_id
        payload["physical_id"] = args.physical_id
        payload["config"] = (
            0 if "Enable" == args.status else (
                1 if "Disable" == args.status else 64))
        payload["status"] = ""
        payload["name"] = ""
        payload["panel"] = ""
        payload["location"] = ""

        return payload
