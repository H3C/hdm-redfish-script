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
from utils.client import RestfulClient
from utils.common import Constant
from utils.model import BaseModule
from utils.tools import init_args


class GetScreenCapture(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["file_path"]

    def run(self, args):

        init_args(args, self.args_lst)
        config_file = args.file_path
        folder = config_file
        if not os.path.exists(folder):
            self.err_list.append("Failure: screen capture "
                                 "storage path is not available")
            raise FailException(*self.err_list)

        client = RestfulClient(args)

        try:
            url = "/api/screen/capture"
            resp = client.send_request("get", url)
            if Constant.SUCCESS_0 == resp.get("cc", None):
                pic_name = resp.get("file_name", None)
                if not pic_name:
                    self.err_list.append(
                        "Failure: failed to get screen capture")
                    raise FailException(*self.err_list)
                pic_name = str(pic_name)
                url = "/bsod/%s" % pic_name
                resp = client.get_screen_capture(url)
                file_name = os.path.join(args.file_path, pic_name)
                if resp:
                    self._save_config_file(resp, file_name)
                else:
                    self.err_list.append(
                        "Failure: failed to get screen capture")
                    raise FailException(*self.err_list)
            elif resp.get("cc", None) in {1, 2, 3, 4, 5}:
                message = {1: "WRITE_CMD_IN_PIPE_FAILED.",
                           2: "OPEN_SMC_CONF_FILE_FAILED.",
                           3: "READ_SMC_CONF_FILE_FAILED.",
                           4: "SCREEN_MANUAL_CAPTURE_NO_SIGNAL.",
                           5: "SCREEN_MANUAL_CAPTURE_FILE_NO_MATCH."}.get(
                               resp.get("cc"), None)
                self.err_list.append("Failure: %s" % message)
                raise FailException(*self.err_list)
            else:
                self.err_list.append("Failure: failed to get screen capture")
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def _save_config_file(self, resp, file_name):

        try:
            with open(file_name, "wb") as conf_data:
                conf_data.write(resp)
                self.suc_list.append(
                    "Success: get screen capture successfully")
        except (IOError, OSError, TypeError,
                ValueError, KeyError, Exception) as err:
            self.err_list.append(str(err))
            raise FailException(*self.err_list)
