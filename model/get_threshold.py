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
from utils.predo import AllowCommand


class GetThreshold(BaseModule):

    def __init__(self):
        super().__init__()
        self.reserved_block = None
        self.remain_life_percents = None
        self.pre_fail_count = None
        self.media_error = None

    @property
    def dict(self):

        return {
            "ReservedBlock": self.reserved_block,
            "RemainLifePercents": self.remain_life_percents,
            "PrefailCount": self.pre_fail_count,
            "MediaError": self.media_error
        }

    @AllowCommand()
    def run(self, args):

        client = RedfishClient(args)
        systems_id = client.get_systems_id()
        url = "/redfish/v1/Chassis/%s/Drives/AlarmThreshold" % systems_id
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and
                resp.get("status_code", None) in Constant.SUC_CODE):
            threshold_info = resp["resource"]
            if threshold_info.get("RevBlock") is not None:
                self.reserved_block = (
                    threshold_info["RevBlock"].get("AlarmLimit"))
            if threshold_info.get("Life") is not None:
                self.remain_life_percents = (
                    threshold_info["Life"].get("AlarmLimit"))
            if threshold_info.get("PredFail") is not None:
                self.pre_fail_count = (
                    threshold_info["PredFail"].get("PredFailCnt"))
            if threshold_info.get("MediaError") is not None:
                self.media_error = (
                    threshold_info["MediaError"].get("MediaErrorCnt"))
        else:
            self.err_list.append("Failure: failed to get predictive failure "
                                 "threshold")
            raise FailException(*self.err_list)
        return self.suc_list
