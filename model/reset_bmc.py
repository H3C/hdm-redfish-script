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


class ResetBmc(BaseModule):

    def __init__(self):
        super().__init__()

    def run(self, args):

        restful = RestfulClient(args)

        try:
            url = "/api/maintenance/restore_hdm"
            payload = {"reset": 1}
            resp = restful.send_request("POST", url, payload)
        finally:
            if restful.cookie:
                restful.delete_session()
        if isinstance(
                resp,
                dict) or Constant.SUCCESS_0 == resp.get(
                "cc",
                None):
            self.suc_list.append("Success: reset BMC successfully")
        else:
            self.err_list.append("Failure: failed to reset BMC")
            raise FailException(*self.err_list)
        return self.suc_list
