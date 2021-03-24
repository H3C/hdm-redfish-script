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
from utils.client import RedfishClient
from utils.common import Constant
from utils.tools import init_args
from utils.model import BaseModule
from utils.predo import AllowCommand


class SetThreshold(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["failure_type", "threshold", "status"]

    @AllowCommand()
    def run(self, args):

        init_args(args, self.args_lst)
        payload = self.check_args(args)
        client = RedfishClient(args)
        systems_id = client.get_systems_id()
        url = "/redfish/v1/Chassis/%s/Drives/AlarmThreshold" % systems_id
        resp = client.send_request("PATCH", url, payload)
        if (isinstance(resp, dict) and resp.get("status_code") in
                Constant.SUC_CODE):
            suc_info = ("Success: successfully set the "
                        "predictive failure threshold")
            self.suc_list.append(suc_info)
        else:
            err_message = ("Failure: failure to set predictive failure "
                           "threshold")
            self.err_list.append(err_message)
            raise FailException(*self.err_list)
        return self.suc_list

    def check_args(self, args):

        args.status = False if args.status == "Disable" else True
        if args.failure_type == "reservedblock":
            if args.threshold < 0 or args.threshold > 100:
                err_info = (
                    "Argument: invalid choice of hard disk reserved "
                    "block: %s (choose from 0 to 100)" %
                    args.threshold)
                self.err_list.append(err_info)
            config_dict = {
                "RevBlock": {
                    "AlarmLimit": args.threshold,
                    "EnableFlag": args.status
                }
            }
        elif args.failure_type == "remainlife":
            if args.threshold < 0 or args.threshold > 100:
                err_info = ("Argument: invalid choice of erasing life: "
                            "%s (choose  from 0 to 100)" % args.threshold)
                self.err_list.append(err_info)
            config_dict = {
                "Life": {
                    "AlarmLimit": args.threshold,
                    "EnableFlag": args.status
                }
            }
        elif args.failure_type == "prefailcount":
            if args.threshold < 0 or args.threshold > 255:
                err_info = (
                    "Argument: invalid choice of pred fail: %s (choose "
                    "from 0 to 255)" %
                    args.threshold)
                self.err_list.append(err_info)
            config_dict = {
                "PredFail": {
                    "PredFailCnt": args.threshold,
                    "PredFailEnableFlag": args.status
                }
            }
        else:
            if args.threshold < 0 or args.threshold > 65535:
                err_info = ("Argument: invalid choice of media error: %s ("
                            "choose from 0 to 65535)" % args.threshold)
                self.err_list.append(err_info)
            config_dict = {
                "MediaError": {
                    "MediaErrorCnt": args.threshold,
                    "MediaErrorEnableFlag": args.status
                }
            }
        if self.err_list:
            raise FailException(*self.err_list)

        return config_dict
