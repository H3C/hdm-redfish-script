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


import re
from exception.ToolException import FailException
from utils.client import RedfishClient
from utils.client import RestfulClient
from utils.common import Constant
from utils.model import BaseModule
from utils.tools import init_args
from utils import globalvar
from utils.predo import GetVersion


class Logic:

    def __init__(self):
        self.id = None
        self.name = None
        self.raid_controller_id = None
        self.volume_raid_level = None
        self.capacity_gib = None
        self.optimum_io_size_bytes = None
        self.redundant_type = None
        self.default_read_policy = None
        self.default_write_policy = None
        self.default_cache_policy = None
        self.read_policy = None
        self.write_policy = None
        self.current_cache_policy = None
        self.access_policy = None
        self.bgi_enable = None
        self.boot_enable = None
        self.drive_cache = None
        self.ssd_cachecade_volume = None
        self.consistency_check = None
        self.ssd_caching_enable = None
        self.drives = None
        self.health = None
        self.io_policy = None
        self.logical_id = None
        self.capacity_tib = None
        self.element = None

    @property
    def dict(self):

        return {
            "Id": self.id,
            "Name": self.name,
            "RaidControllerID": self.raid_controller_id,
            "VolumeRaidLevel": self.volume_raid_level,
            "CapacityGiB": self.capacity_gib,
            "OptimumIOSizeBytes": self.optimum_io_size_bytes,
            "RedundantType": self.redundant_type,
            "DefaultReadPolicy": self.default_read_policy,
            "DefaultWritePolicy": self.default_write_policy,
            "DefaultCachePolicy": self.default_cache_policy,
            "ReadPolicy": self.read_policy,
            "WritePolicy": self.write_policy,
            "IOPolicy": self.io_policy,
            "CachePolicy": self.current_cache_policy,
            "AccessPolicy": self.access_policy,
            "BGIEnable": self.bgi_enable,
            "BootEnable": self.boot_enable,
            "DriveCache": self.drive_cache,
            "SSDCachecadeVolume": self.ssd_cachecade_volume,
            "ConsistencyCheck": self.consistency_check,
            "SSDCachingEnable": self.ssd_caching_enable,
            "Drives": self.drives,
            "Health": self.health,

            "LogicalId": self.logical_id,
            "CapacityTiB": self.capacity_tib,
            "Element": self.element
        }

    def pack_logic_resource(self, resp):

        self.id = resp.get("Id", None)
        self.name = resp.get("Name", None)
        if (resp.get("Oem", None) and
                isinstance(resp["Oem"].get("Public", None), dict)):
            oem_info = resp["Oem"]["Public"]
            self.raid_controller_id = oem_info.get("RaidControllerID", None)
            self.volume_raid_level = oem_info.get("VolumeRaidLevel", None)
            self.optimum_io_size_bytes = (
                oem_info.get("OptimumIOSizeBytes", None))
            self.read_policy = oem_info.get("ReadPolicy", None)
            self.write_policy = oem_info.get("WritePolicy", None)
            self.access_policy = oem_info.get("AccessPolicy", None)
            self.boot_enable = oem_info.get("BootEnable", None)
            self.drive_cache = oem_info.get("DriveCache", None)
            self.io_policy = oem_info.get("IOPolicy", None)

            if oem_info.get("DefaultReadPolicy", None) is not None:
                self.default_read_policy = oem_info.get("DefaultReadPolicy")
            else:
                self.default_read_policy = resp.get("DefaultReadPolicy", None)
            if oem_info.get("DefaultWritePolicy", None) is not None:
                self.default_write_policy = oem_info.get("DefaultWritePolicy")
            else:
                self.default_write_policy = resp.get(
                    "DefaultWritePolicy", None)
            if oem_info.get("DefaultCachePolicy", None) is not None:
                self.default_cache_policy = oem_info.get("DefaultCachePolicy")
            else:
                self.default_read_policy = resp.get("DefaultReadPolicy", None)
            if oem_info.get("CurrentCachePolicy", None) is not None:
                self.current_cache_policy = oem_info.get("CurrentCachePolicy")
            else:
                self.current_cache_policy = resp.get(
                    "CurrentCachePolicy", None)
            if oem_info.get("BGIEnable", None) is not None:
                self.bgi_enable = oem_info.get("BGIEnable")
            else:
                self.bgi_enable = resp.get("BGIEnable", None)
            if oem_info.get("SSDCachecadeVolume", None) is not None:
                self.ssd_cachecade_volume = oem_info.get("SSDCachecadeVolume")
            else:
                self.ssd_cachecade_volume = resp.get(
                    "SSDCachecadeVolume", None)
            if oem_info.get("ConsistencyCheck", None) is not None:
                self.consistency_check = oem_info.get("ConsistencyCheck")
            else:
                self.consistency_check = resp.get("ConsistencyCheck", None)
            if oem_info.get("SSDCachingEnable", None) is not None:
                self.ssd_caching_enable = oem_info.get("SSDCachingEnable")
            else:
                self.ssd_caching_enable = resp.get("SSDCachingEnable", None)

        try:
            self.capacity_gib = int(resp.get("CapacityBytes",
                                             None) // 1024 ** 3)

            self.capacity_tib = str('%.2f' %
                                    (self.capacity_gib / 1024)) + "TiB"
        except TypeError:
            pass

        self.redundant_type = resp.get("RedundantType", None)
        drive_list = list()
        try:
            drives = resp["Links"].get("Drives", None)
            self.element = len(drives)
            for member in drives:
                drive = re.findall(r"\d+",
                                   member.get("@odata.id").split("/")[-1])[-1]
                drive_list.append(str(int(drive)))
                self.drives = ", ".join(drive_list)
        except (KeyError, AttributeError, TypeError, ValueError, Exception):
            self.drives = None
        if resp.get("Status", None):
            self.health = resp["Status"].get("Health", None)

        try:
            logic_id = self.id.split("Drive")[-1]
            self.logical_id = int(logic_id)
        except (KeyError, AttributeError, TypeError, ValueError, Exception):
            pass

    def pack_b01_logic_resource(self, resp):

        self.id = resp.get("dev_no", None)
        self.volume_raid_level = resp.get("type", None)
        self.capacity_gib = resp.get("capacity", None)
        self.optimum_io_size_bytes = resp.get("strip_size", None)
        self.health = resp.get("status", None)
        drives = resp.get("nondis_phys_info", None)
        non = ""
        for member in drives:
            non = non + "%s%s" % (str(member.get("slot_phys_no", None)), ",")

        non = non[0:len(non) - 1]
        self.drives = non


class GetLDisk(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["controller_id", "logical_id"]
        self.overall_health = None
        self.maximum = None
        self.logics = []

    @property
    def dict(self):

        return {
            "OverallHealth": self.overall_health,
            "Maximum": None,
            "Logics": self.logics
        }

    @GetVersion()
    def run(self, args):

        init_args(args, self.args_lst)
        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            logic_disk_list = self._get_b01_logical_disk_list(client)
            if not logic_disk_list:
                suc_info = "Success: raid card resource is empty"
                self.suc_list.append(suc_info)
                return self.suc_list
        else:
            if ((args.controller_id is None and args.logical_id is not None) or (
                    args.controller_id is not None and args.logical_id is None)):
                err = ("Argument: RAID card ID and logical disk "
                       "ID must be specified at the same time")
                self.err_list.append(err)
                raise FailException(*self.err_list)
            client = RedfishClient(args)
            logical_disk_list_url = self._get_logical_disk_list(client)

            if args.logical_id is None and not logical_disk_list_url:
                suc = "Success: raid card resource is empty"
                self.suc_list.append(suc)
                return self.suc_list
            if not self._get_logical_disk_detail(client, logical_disk_list_url,
                                                 args):
                err_info = "Failure: resource was not found"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        client = RestfulClient(args)
        try:

            self._get_health_info(client)
        finally:
            if client.cookie:
                client.delete_session()

        return self.suc_list

    def _get_health_info(self, client):

        status_dict = {
            "0": "OK",
            "1": "Caution",
            "2": "Warning",
            "3": "Critical"
        }
        url = "/api/health_info"
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_0 == resp.get("cc", None)):
            psu_health = status_dict.get(str(resp.get("disk", None)), None)
            self.overall_health = psu_health
        else:
            self.err_list.append("Failure: failed to get overall health "
                                 "status information")
            raise FailException(*self.err_list)

    def _get_logical_disk_detail(self, client, logic_url, args):

        flag = False
        for l_url in logic_url:
            resp = client.send_request("GET", l_url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                resp = resp["resource"]
                if args.logical_id is None:
                    flag = True
                    logic = Logic()
                    logic.pack_logic_resource(resp)
                    self.logics.append(logic)
                elif (resp.get("Oem", None) and
                      isinstance(resp["Oem"].get("Public", None), dict)):
                    try:
                        logic_id = int(resp["Id"].split("Drive")[-1])
                    except (ValueError, IndexError, Exception):
                        pass
                    else:
                        if ((args.controller_id ==
                             resp["Oem"]["Public"].get("RaidControllerID",
                                                       None) and
                             args.logical_id == logic_id)):
                            logic = Logic()
                            logic.pack_logic_resource(resp)
                            self.logics.append(logic)
                            flag = True
                            break
            else:
                err = "Failure: failed to get logical disk details"
                self.err_list.append(err)
                raise FailException(*self.err_list)
        return flag

    def _get_logical_disk_list(self, client):

        logical_disk_list_url = list()
        systems_id = client.get_systems_id()
        url = "/redfish/v1/Systems/%s/Storages" % systems_id
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and
                resp.get("status_code", None) in Constant.SUC_CODE):
            raid_members = resp["resource"].get("Members", None)
            for member in raid_members:
                url = "%s/Volumes" % member.get("@odata.id", None)
                resp = client.send_request("GET", url)
                if (isinstance(resp, dict) and
                        resp.get("status_code", None) in Constant.SUC_CODE):
                    logical_drivers = resp["resource"].get("Members", None)
                    for driver in logical_drivers:
                        logical_disk_list_url.append(driver.get("@odata.id"))
                else:
                    err = ("Failure: failed to get logical disk "
                           "collection information")
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
        else:
            err = ("Failure: failed to get logical disk "
                   "collection information")
            self.err_list.append(err)
            raise FailException(*self.err_list)
        return logical_disk_list_url

    def _get_b01_logical_disk_list(self, client):

        try:
            url = "/api/settings/storageinfo"
            resp1 = client.send_request("GET", url)
            if isinstance(resp1, dict) and Constant.SUCCESS_0 == \
                    resp1.get("cc"):
                logical_disk = resp1.get("logical_info")
                for member in logical_disk:
                    logic = Logic()
                    logic.pack_b01_logic_resource(member)
                    self.logics.append(logic)
            else:
                err = "Failure: failed to get raid card collection information"
                self.err_list.append(err)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return logical_disk
