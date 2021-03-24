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
from utils.client import RedfishClient
from utils.common import Constant
from utils.model import BaseModule


class Firmware:

    def __init__(self):

        self.name = None
        self.type = None
        self.version = None
        self.update_able = None
        self.support_activate_type = None

    @property
    def dict(self):

        return {
            "Name": self.name,
            "Type": self.type,
            "Version": self.version,
            "UpdateAble": self.update_able,
            "SupportActivateType": self.support_activate_type
        }


class GetFirmware(BaseModule):

    def __init__(self):

        super().__init__()
        self.firmware = []

    @property
    def dict(self):

        return {
            "Firmware": self.firmware
        }

    def run(self, args):

        firmware_list = []
        client = RestfulClient(args)
        try:

            version = self.get_hdm_firmware(client)

            if version < "1.11.00":
                self.get_all_firmware(client, firmware_list)
            else:
                client1 = RedfishClient(args)
                self.get_redfish_firmware(client1, firmware_list)
                self.get_restful_firmware(client, firmware_list)
        finally:
            if client.cookie:
                client.delete_session()
        self.firmware = deal_firmware_info(firmware_list)
        return self.suc_list

    def get_restful_firmware(self, client, lst):

        try:
            get_backup_firmware(client, lst)
            get_me_firmware(client, lst)
            get_nic_firmware(client, lst)
            get_storage_firmware(client, lst)
            get_psu_firmware(client, lst)
        except (KeyError, ValueError, SyntaxError, Exception) as err:
            self.err_list.append(str(err))
            raise FailException(*self.err_list)

    def get_redfish_firmware(self, client, lst):

        url = "/redfish/v1/UpdateService/FirmwareInventory"
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and resp.get("status_code",
                                                None) in Constant.SUC_CODE):
            for member in resp["resource"]["Members"]:
                sub_resp = client.send_request("GET", member["@odata.id"])
                if (isinstance(sub_resp, dict) and sub_resp.get(
                        "status_code", None) in Constant.SUC_CODE):
                    package = deal_redfish_firmware(sub_resp)
                    if package:
                        lst.append(package)
                else:
                    err_info = "Failure: failed to get firmware information"
                    self.err_list.append(err_info)
                    break
        else:
            err_info = "Failure: failed to get firmware collection"
            self.err_list.append(err_info)
        if self.err_list:
            raise FailException(*self.err_list)

    def get_hdm_firmware(self, client):

        url = "/api/system/firmware"
        resp = client.send_request("get", url)
        if isinstance(resp, list):
            for firmware in resp:
                if "bmc_revision" in firmware:
                    info = resp[0]
                    version = info.get("bmc_revision", None)
                    if version is not None:
                        versions = version.split(" ")
                        hdm_version = versions[0]
                        return hdm_version
        return None

    def get_all_firmware(self, client, lst):

        url = "/api/system/firmware"
        resp = client.send_request("get", url)
        if isinstance(resp, list):
            for firmware in resp:
                if "bmc_revision" in firmware:
                    detail = dict()
                    info = resp[0]
                    detail["name"] = "HDM"
                    detail["type"] = "HDM"
                    detail["version"] = info.get("bmc_revision", None)
                    detail["update_able"] = info.get("Updateable", None)
                    detail["support_activate_type"] = (info.get(
                        "SupportActivateType", None))
                    lst.append(detail)
                if "bios_revision" in firmware:
                    detail = dict()
                    info = resp[0]
                    detail["name"] = "BIOS"
                    detail["type"] = "BIOS"
                    detail["version"] = info.get("bios_revision", None)
                    detail["update_able"] = info.get("Updateable", None)
                    detail["support_activate_type"] = (info.get(
                        "SupportActivateType", None))
                    lst.append(detail)
                if "cpld_revision" in firmware:
                    detail = dict()
                    info = resp[0]
                    detail["name"] = "CPLD"
                    detail["type"] = "CPLD"
                    detail["version"] = info.get("cpld_revision", None)
                    detail["update_able"] = info.get("Updateable", None)
                    detail["support_activate_type"] = (info.get(
                        "SupportActivateType", None))
                    lst.append(detail)
                if "me_revision" in firmware:
                    detail = dict()
                    info = resp[0]
                    detail["name"] = "ME"
                    detail["type"] = "ME"
                    detail["version"] = info.get("me_revision", None)
                    detail["update_able"] = info.get("Updateable", None)
                    detail["support_activate_type"] = (info.get(
                        "SupportActivateType", None))
                    lst.append(detail)


def deal_redfish_firmware(resp):

    detail = dict()
    info = resp["resource"]
    tmp_name = info.get("Name", None)
    if tmp_name == "HDM":
        fw_name = "ActiveBMC"
    elif tmp_name == "CPLD":
        fw_name = "MainBoard_CPLD"
    elif tmp_name == "BIOS":
        fw_name = "BIOS"
    else:
        return None
    detail["name"] = fw_name
    tmp_type = info.get("SoftwareId")
    if tmp_type == "HDM":
        fw_type = "BMC"
    elif tmp_type == "CPLD":
        fw_type = "CPLD"
    elif tmp_type == "BIOS":
        fw_type = "BIOS"
    else:
        fw_type = None
    detail["type"] = fw_type
    if isinstance(info.get("Version", None),
                  list) and len(info["Version"]) != 0:
        detail["version"] = info["Version"][0]
    elif isinstance(info.get("Version", None), str):
        detail["version"] = info["Version"]
    else:
        detail["version"] = None
    detail["update_able"] = info.get("Updateable", None)
    detail["support_activate_type"] = info.get("SupportActivateType", None)
    return detail


def deal_firmware_info(lst):

    tmp_lst = []
    for firmware in lst:
        f_v = Firmware()
        f_v.__dict__.update(firmware)
        tmp_lst.append(f_v)
    return tmp_lst


def get_backup_firmware(client, lst):

    url = "/api/maintenance/primary_backup_version"
    resp = client.send_request("get", url)
    if isinstance(resp, dict) and resp.get("cc") == 0:
        detail = dict()
        detail["name"] = "BackupBMC"
        detail["type"] = "BMC"
        detail["version"] = resp.get("backup_version", None)
        detail["update_able"] = resp.get("Updateable", None)
        detail["support_activate_type"] = (resp.get(
            "SupportActivateType", None))
        lst.insert(1, detail)


def get_me_firmware(client, lst):

    url = "/api/system/firmware"
    resp = client.send_request("get", url)
    if isinstance(resp, list):
        for firmware in resp:
            if "me_revision" in firmware:
                detail = dict()
                info = resp[0]
                detail["name"] = "ME"
                detail["type"] = "ME"
                detail["version"] = info.get("me_revision", None)
                detail["update_able"] = info.get("Updateable", None)
                detail["support_activate_type"] = (info.get(
                    "SupportActivateType", None))
                lst.append(detail)


def get_nic_firmware(client, lst):

    url = "/api/system/nic"
    resp = client.send_request("get", url)
    if isinstance(resp, dict) and resp.get("cc") == Constant.SUCCESS_0:
        tmp = dict()
        for nic in resp["nic_info"]:
            tmp.setdefault(nic["product_name"],
                           set()).add(nic.get('firmware_version'))
        for key_, value in tmp.items():
            for nic in resp["nic_info"]:
                if key_ == nic["product_name"]:
                    detail = dict()
                    detail["name"] = nic.get("product_name")
                    detail["type"] = nic.get("device_type")
                    detail["version"] = r"/".join(sorted(list(value)))
                    detail["update_able"] = nic.get("Updateable", None)
                    detail["support_activate_type"] = (nic.get(
                        "SupportActivateType", None))
                    lst.append(detail)
                    break


def get_storage_firmware(client, lst):

    url = "/api/system/storageinfo/ctrl/list"
    resp = client.send_request("get", url)
    if isinstance(resp, dict) and resp.get("cc") == Constant.SUCCESS_0:
        card_list_len = len(resp["card_list"])
        for i in range(card_list_len):
            sub_url = "/api/system/storageinfo/ctrl/%s" % i
            sub_resp = client.send_request("get", sub_url)
            if (isinstance(sub_resp, dict) and sub_resp.get("cc", None) ==
                    Constant.SUCCESS_0):
                detail = dict()
                detail["name"] = sub_resp["adapter"].get("type")
                detail["type"] = "RAID"
                detail["version"] = sub_resp["adapter"].get("firmware_ver")
                detail["update_able"] = sub_resp["adapter"].get("Updateable")
                detail["support_activate_type"] = (sub_resp["adapter"].get(
                    "SupportActivateType"))
                lst.append(detail)


def get_psu_firmware(client, lst):

    url = "/api/system/hardware_power"
    resp = client.send_request("get", url)
    if isinstance(resp, list):
        for firmware in resp:
            if firmware.get("present") == 0:
                continue
            detail = dict()
            if firmware.get("id") is not None:
                name = "PSU%d" % firmware.get("id")
            else:
                name = None
            detail["name"] = name
            detail["type"] = "FW"
            detail["version"] = firmware.get("version", None)
            detail["update_able"] = firmware.get("Updateable", None)
            detail["support_activate_type"] = firmware.get(
                "SupportActivateType", None)
            lst.append(detail)
