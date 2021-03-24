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
import time
from exception.ToolException import FailException
from utils.model import BaseModule
from utils.client import RestfulClient
from utils.common import Constant
from utils.tools import init_args

URL_DICT = {'BIOS': 'bios_upload_restore',
            'BMC': 'hdm_upload_restore',
            'RAID': 'raid_upload_restore'}


class UploadCfg(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["file_uri", "config_type"]

    def run(self, args):

        init_args(args, self.args_lst)
        config_file = args.file_uri
        if not os.path.exists(config_file):
            err_info = ("Failure: upload config file failed, "
                        "reason: File Not Exist")
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        config_type = args.config_type
        url = "/api/maintenance/%s" % URL_DICT[config_type]
        try:
            with open(config_file, "rb") as config_file_data:
                file_read = config_file_data.read()
        except (TypeError, ValueError, KeyError, IOError, Exception) as err:
            self.err_list.append(str(err))
            raise FailException(*self.err_list)
        else:
            _, file_name = os.path.split(config_file)
            fields = {
                "config": (file_name, file_read, "application/octet-stream")
            }
        client = RestfulClient(args)
        try:
            resp = client.upload_request("POST", url, fields=fields)
            if (isinstance(resp, dict) and resp.get(Constant.COMPLETE_CODE)
                    == Constant.SUCCESS_0):
                self.get_process(client, config_type)
            elif (isinstance(resp, dict) and resp.get(Constant.COMPLETE_CODE)
                  != Constant.SUCCESS_0):
                err_info = ("Failure: import %s config file failed, reason: %s"
                            % (config_type, resp.get(Constant.COMPLETE_CODE)))
                self.err_list.append(err_info)
            else:
                err_info = ("Failure: import %s config file failed, "
                            "reason: Response can not parse" % config_type)
                self.err_list.append(err_info)
            if self.err_list:
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def get_process(self, client, config_type):

        url = '/api/maintenance/upload_restore_process'
        time.sleep(5)
        index = 0
        while index < 100:
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and resp.get(Constant.COMPLETE_CODE)
                    == 0 and isinstance(resp.get('progress', None), int)):

                if resp['progress'] == 255:
                    suc_info = ("Success: import %s configuration "
                                "successfully" % config_type)
                    self.suc_list.append(suc_info)
                    break
            else:
                err_info = ("Failure: get upload restore process failed, "
                            "reason: %s" % resp.get(Constant.COMPLETE_ERROR))
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            time.sleep(2)
            index += 1
        else:
            err_info = "Failure: get file upload progress timeout"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
