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
from utils.client import RestfulClient
from utils.common import Constant
from utils.tools import init_args
from utils.model import BaseModule


class SetPowerLimit(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["exception", "limit_value", "status"]

    def run(self, args):

        init_args(args, self.args_lst)
        client = RedfishClient(args)
        systems_id = client.get_systems_id()
        url = "/redfish/v1/Chassis/%s/Power" % systems_id
        resp = client.send_request("get", url)
        if (isinstance(resp, dict) and resp.get("status_code", None) ==
                Constant.SUCCESS_200):
            if resp["resource"].get("PowerControl", None) is not None:
                try:
                    power_metrics = (
                        resp["resource"]["PowerControl"][0].get("PowerMetrics",
                                                                None))
                    power_limit = (
                        resp["resource"]["PowerControl"][0].get("PowerLimit",
                                                                None))
                except (TypeError, ValueError, KeyError, SyntaxError) as err:
                    self.err_list.append(str(err))
                    raise FailException(*self.err_list)
                else:
                    max_value = power_metrics.get("MaxConsumedWatts")
                    min_value = power_metrics.get("MinConsumedWatts")
                    exception = power_limit.get("LimitException")
                    limit_in_watts = power_limit.get('LimitInWatts')
                    payload = self.construct_request_parameters(
                        args, max_value, min_value, limit_in_watts, exception)
                    client = RestfulClient(args)
                    try:
                        url = "/api/power/capping"
                        resp = client.send_request("POST", url, payload)
                        if (isinstance(resp, dict) and
                                resp.get(Constant.COMPLETE_CODE) ==
                                Constant.SUCCESS_0):
                            suc_info = "Success: set power limit succeed"
                            self.suc_list.append(suc_info)
                        else:
                            err_info = "Failure: set power limit failed"
                            self.err_list.append(err_info)
                            raise FailException(*self.err_list)
                    finally:
                        if client.cookie:
                            client.delete_session()
            else:
                err_info = ("Failure: the machine does not "
                            "support setting power cap")
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        else:
            err_info = "Failure: failed to get the value range of the power cap"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return self.suc_list

    def construct_request_parameters(self, args, max_value, min_value,
                                     limit_in_watts, exception):

        payload = dict()
        if args.status == "Disable":
            if args.limit_value or args.exception:
                para_lst = []
                if args.limit_value:
                    para_lst.append(str(args.limit_value))
                if args.exception:
                    para_lst.append(args.exception)
                err_info = (
                    "Argument: parameters are not available "
                    "when setting power off: %s" % ", ".join(para_lst))
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            else:
                payload["power_meter_enable"] = 0
                payload["power_meter_set"] = ""
        else:
            payload["power_meter_enable"] = 1
            limit_value = (args.limit_value if args.limit_value
                           else limit_in_watts)
            if limit_value < min_value or limit_value > max_value:
                err_info = ("Argument: invalid choice: "
                            "(choose from %s to %s)" % (min_value, max_value))
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            payload["power_meter_set"] = limit_value
            exception = args.exception if args.exception else exception
        payload['power_meter_shutdown'] = (0 if exception == "NoAction" else 1)
        return payload
