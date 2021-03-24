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
from utils.tools import init_args
from utils.model import BaseModule


class SetAssetTag(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["asset_tag"]

    def run(self, args):

        init_args(args, self.args_lst)
        client = RestfulClient(args)
        try:
            url = "/api/system/assetTag"

            payload = {"asset_tag": args.asset_tag}
            resp = client.send_request("POST", url, payload)
            if (isinstance(resp, dict) and resp.get(Constant.COMPLETE_CODE)
                    == Constant.SUCCESS_0):
                suc_info = "Success: set asset tag succeed"
                self.suc_list.append(suc_info)
            else:
                err_info = "Failure: Set asset tag failed"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list
