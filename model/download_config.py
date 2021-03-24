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
import json
from exception.ToolException import FailException
from utils.model import BaseModule
from utils.common import Constant
from utils.tools import init_args
from utils.client import RestfulClient

URL_DICT = {
    "BIOS": "bios_download_config",
    "BMC": "hdm_download_config",
    "RAID": "raid_download_config"
}


class DownloadCfg(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["config_type", "file_uri"]

    def run(self, args):

        init_args(args, self.args_lst)
        config_type = args.config_type
        config_file = args.file_uri
        try:
            with open(config_file, "w"):
                pass
        except IOError as err:
            self.err_list.append(str(err))
            raise FailException(*self.err_list)
        else:
            os.remove(config_file)
        client = RestfulClient(args)
        url = "/api/maintenance/%s" % URL_DICT[config_type]
        try:
            resp = client.send_request("GET", url)
            if resp and isinstance(resp, dict):
                if not (resp.get(Constant.COMPLETE_CODE) or resp.get(
                        Constant.COMPLETE_ERROR)):

                    with open(config_file, "w") as file_output:
                        file_output.write(json.dumps(resp, indent=4,
                                                     separators=(",", ": ")))
                    suc_info = ("Success: export %s configuration "
                                "is successful" % config_type)
                    self.suc_list.append(suc_info)
                else:

                    err_info = ("Failure: export %s config file failed, "
                                "reason: %s" %
                                (config_type,
                                 resp.get(Constant.COMPLETE_ERROR)))
                    self.err_list.append(err_info)
            else:
                err_info = ("Failure: export %s config file failed, reason: "
                            "Response can not parse" % config_type)
                self.err_list.append(err_info)
        except (IOError, Exception) as err:
            self.err_list.append((str(err)))
            raise FailException(*self.err_list)
        else:
            if self.err_list:
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list
