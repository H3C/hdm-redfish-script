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
from utils.tools import init_args


class LogicalInfo:

    def __init__(self):
        self.dev_no = None
        self.status = None
        self.type = None
        self.capacity = None
        self.element_num = None
        self.drives = None

    @property
    def dict(self):

        return self.__dict__

    def pack_logic(self, resp, drive_list):

        self.dev_no = resp.get("dev_no", None)
        self.status = resp.get("status", None)
        self.type = resp.get("type", None)
        self.capacity = resp.get("capacity", None)
        self.element_num = resp.get("element_num", None)

        physical_drive_list = resp.get("nondis_phys_info", None)
        physical_id_list = list()
        if physical_drive_list:
            for physical_drive in physical_drive_list:
                physical_id = physical_drive.get("dev_no", None)
                if physical_id is not None:
                    drive_list.append(physical_id)
                    physical_id_list.append(physical_id)
        physical_id_list.sort()
        physical_id_list = [str(s) for s in physical_id_list]
        self.drives = ','.join(physical_id_list)


class Ctrl:

    def __init__(self):
        self.ctrl_id = None
        self.type = None
        self.firmware_ver = None
        self.serial = None
        self.ddr_size = None
        self.subsys_stat = None
        self.cap_stat = None
        self.cap_perc = None
        self.raid_level = None
        self.logical_info = []
        self.drives = None

    @property
    def dict(self):

        return self.__dict__

    def pack_ctrl_resource(self, resp):

        self.ctrl_id = resp.get("ctrl_id", None)
        adapter = resp.get("adapter", None)
        if adapter:
            self.type = adapter.get("type", None)
            self.firmware_ver = adapter.get("firmware_ver", None)
            self.serial = adapter.get("serial", None)
            self.ddr_size = adapter.get("ddr_size", None)
            self.subsys_stat = adapter.get("subsys_stat", None)
            self.cap_stat = adapter.get("cap_stat", None)
            self.cap_perc = adapter.get("cap_perc", None)
            self.raid_level = adapter.get("raid_level", None)
        logic_list = resp.get("logical_info", None)
        drive_list = []
        for logic in logic_list:
            logical_info = LogicalInfo()
            logical_info.pack_logic(logic, drive_list)
            self.logical_info.append(logical_info)
        physicals = resp.get("dis_phys_info", None)
        for phy in physicals:
            physical_id = phy.get("dev_no", None)
            if physical_id is not None:
                drive_list.append(physical_id)
        drive_list.sort()
        drive_list = [str(s) for s in drive_list]
        self.drives = ", ".join(drive_list)


class GetStorage(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["controller_id"]
        self.ctrls = []

    @property
    def dict(self):

        return {"ctrls": self.ctrls}

    def run(self, args):

        init_args(args, self.args_lst)
        client = RestfulClient(args)
        try:
            self._get_ctrl(client, args)
        finally:
            if client.cookie:
                client.delete_session()

        return self.suc_list

    def _get_ctrl(self, client, args):

        url = "/api/system/storageinfo/ctrl/list"
        resp = client.send_request("get", url)
        if (not resp or Constant.SUCCESS_0 != resp.get("cc", None) or
                not isinstance(resp.get("card_list", None), list)):
            err_info = "Failure: failed to get controller card information"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        card_list = resp["card_list"]
        if args.controller_id is None and not card_list:
            suc = "Success: resource is empty"
            self.suc_list.append(suc)
            return self.suc_list

        flag = False
        for card in card_list:
            ctrl_id = card.get("ctrl_id", None)
            if args.controller_id is None:
                flag = True
                self._get_ctrl_detail(ctrl_id, client)
            elif args.controller_id == card.get("ctrl_id", None):
                flag = True
                self._get_ctrl_detail(ctrl_id, client)
                break
        if not flag:
            err_info = "Failure: resource was not found"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)

    def _get_ctrl_detail(self, ctrl_id, client):

        ctrl_url = "/api/system/storageinfo/ctrl/%s" % ctrl_id
        ctrl_resp = client.send_request("get", ctrl_url)
        if (isinstance(ctrl_resp, dict) and
                Constant.SUCCESS_0 == ctrl_resp.get("cc", None)):
            ctrl_resp["ctrl_id"] = ctrl_id
            ctrl = Ctrl()
            ctrl.pack_ctrl_resource(ctrl_resp)
            self.ctrls.append(ctrl)
        else:
            self.err_list.append("Failure: failed to get storage information")
            raise FailException(*self.err_list)
