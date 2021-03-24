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
from utils.model import BaseModule


class SetPowerRedundancy(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["power_id", "power_standby"]

    def run(self, args):

        client = RedfishClient(args)
        systems_id = client.get_systems_id()
        url = "/redfish/v1/Chassis/%s/Power" % systems_id
        payload = construct_request_parameters(args)
        resp = client.send_request("PATCH", url, payload)
        if (isinstance(resp, dict) and
                resp.get("status_code", None) in Constant.SUC_CODE):
            suc_info = "Success: set power redundancy succeed"
            self.suc_list.append(suc_info)
        else:
            err_info = "Failure: set power redundancy failed"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return self.suc_list


def construct_request_parameters(args):

    payload = {
        "PowerControl": {
            "Oem": {
                "Public": {
                    "PowerID": args.power_id,
                    "ActiveStandby": args.power_standby
                }
            }
        }
    }
    return payload
