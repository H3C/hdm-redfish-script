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
from utils.model import BaseModule
from utils import globalvar
from utils.predo import GetVersion


MODE_DICT = {
    0: "Legacy",
    1: "UEFI"
}
DEV_DICT = {
    0: "HDD",
    1: "PXE",
    2: "BIOS",
    3: "Floppy/USB",
    4: "CDROM",
    5: "SAFE",
    6: "DIAG",
    7: "No override"
}


class GetSysBoot(BaseModule):

    def __init__(self):
        super().__init__()

        self.boot_source_override_target = None
        self.boot_source_override_enabled = None
        self.boot_source_override_mode = None

    @property
    def dict(self):

        return {
            "BootSourceOverrideTarget": self.boot_source_override_target,
            "BootSourceOverrideEnabled": self.boot_source_override_enabled,
            "BootSourceOverrideMode": self.boot_source_override_mode
        }

    @GetVersion()
    def run(self, args):

        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                url = "/api/config/boot"
                resp = client.send_request("get", url)
                if isinstance(resp, dict) and Constant.SUCCESS_0 == \
                        resp.get("cc"):
                    self.boot_source_override_target = MODE_DICT.get(
                        resp.get("mode"), None)
                    self.boot_source_override_enabled = resp.get("alwaysflag",
                                                                 "Once")
                    self.boot_source_override_mode = DEV_DICT.get(
                        resp.get("dev"), None)
                else:
                    err_info = "Failure: failed to get boot startup information"
                    self.err_list.append(err_info)
                    raise FailException(*self.err_list)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            systems_id = client.get_systems_id()
            url = "/redfish/v1/Systems/%s" % systems_id
            resp = client.send_request("get", url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                boot = resp["resource"].get("Boot", None)
                if isinstance(boot, dict):
                    self.boot_source_override_target = (
                        boot.get("BootSourceOverrideTarget", None))
                    self.boot_source_override_enabled = (
                        boot.get("BootSourceOverrideEnabled", None))
                    self.boot_source_override_mode = (
                        boot.get("BootSourceOverrideMode", None))
            else:
                err_info = "Failure: failed to get boot startup information"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
