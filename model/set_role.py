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
from utils.tools import init_args
from utils import globalvar
from utils.predo import GetVersion


PRIVILEGE_DICT = {
    "Kvm": "OemKvm",
    "Vmm": "OemVmm",
    "SecurityMgmt": "OemSecurityMgmt",
    "ConfigureComponents": "ConfigureComponents",
    "PowerControl": "OemPowerControl",
    "Diagnosis": "OemDiagnosis",
    "ConfigureSelf": "ConfigureSelf"
}


class SetRole(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["role_id", "privileges"]

    @GetVersion()
    def run(self, args):

        init_args(args, self.args_lst)
        if globalvar.HDM_VERSION < "2.08.00":
            err = "Failure: this hdm version does not support this command"
            self.err_list.append(err)
            raise FailException(*self.err_list)
        else:
            payload = self._parse_args(args)
            url = "/redfish/v1/AccountService/Roles/%s" % args.role_id
            client = RedfishClient(args)
            resp = client.send_request("PATCH", url, payload)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                suc = "Success: set user role information successfully"
                self.suc_list.append(suc)
            else:
                err = "Failure: failed to set user role information"
                self.err_list.append(err)
                raise FailException(*self.err_list)

        return self.suc_list

    def _parse_args(self, args):

        self.role_id = args.role_id
        payload = {
            "AssignedPrivileges": [],
            "OemPrivileges": []
        }
        if args.privileges:
            tmp_lst = args.privileges.split(",")
            for priv in tmp_lst:
                if priv not in PRIVILEGE_DICT.keys():
                    err_info = (
                        "Argument: the parameter value is invalid: %s, "
                        "please select from [%s]" %
                        (priv, ", ".join(
                            PRIVILEGE_DICT.keys())))
                    self.err_list.append(err_info)
                    raise FailException(*self.err_list)
                if priv == "ConfigureComponents" or priv == "ConfigureSelf":
                    payload["AssignedPrivileges"].append(
                        PRIVILEGE_DICT.get(priv))
                else:
                    payload["OemPrivileges"].append(PRIVILEGE_DICT.get(priv))
        return payload
