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


class DelLDisk(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["controller_id", "logical_drive_id"]

    def run(self, args):

        init_args(args, self.args_lst)
        payload = self.construct_param(args)
        client = RestfulClient(args)
        url = '/api/remote/delete_raid'
        try:
            resp = client.send_request("delete", url, payload)
            if (isinstance(resp, dict) and
                    Constant.SUCCESS_0 == resp.get("cc", None)):
                self.suc_list.append("Success: delete logical driver "
                                     "successfully")
            else:
                err = "Failure: failed to delete logical driver"
                self.err_list.append(err)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()

        return self.suc_list

    @staticmethod
    def construct_param(args):

        payload = dict()
        payload["ctrl_id"] = args.controller_id
        payload["logical_id"] = args.logical_drive_id
        payload["name"] = ""

        return payload
