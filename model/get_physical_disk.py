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
from utils.model import BaseModule
from utils.common import Constant
from utils.tools import init_args
from collections import namedtuple
from utils import globalvar
from utils.predo import GetVersion


Pdisk = namedtuple("Pdisk", ["raid", "logic", "url"])


class Physical:

    def __init__(self):
        self.id = None
        self.name = None
        self.panel = None
        self.manufacturer = None
        self.model = None
        self.protocol = None
        self.failure_predicted = None
        self.capacity_gib = None
        self.hot_spare_type = None
        self.indicator_led = None
        self.predicted_media_life_left_percent = None
        self.media_type = None
        self.capable_speed_gbs = None
        self.negotiated_speed_gbs = None
        self.revision = None
        self.status_indicator = None
        self.temperature_celsius = None
        self.hours_of_powered_up = None
        self.sas_address = None
        self.patrol_state = None
        self.rebuild_state = None
        self.rebuild_progress = None
        self.spare_for_logical_drives = None
        self.raid_controller_id = None
        self.state = None
        self.health = None
        self.panel_location = None
        self.slot_phys_no = None
        self.connection_id = None
        self.drive_number_in_bios = None
        self.drive_number_in_os = None
        self.firmware_status = None
        self.manufacturer_model = None
        self.serial_number = None
        self.property = None
        self.capacity_tib = None
        self.volumes = None

    @property
    def dict(self):

        return {
            "Id": self.id,
            "Name": self.name,
            "Panel": self.panel,
            "Manufacturer": self.manufacturer,
            "Model": self.model,
            "Protocol": self.protocol,
            "FailurePredicted": self.failure_predicted,
            "CapacityGiB": self.capacity_gib,
            "HotspareType": self.hot_spare_type,
            "IndicatorLED": self.indicator_led,
            "PredictedMediaLifeLeftPercent": (
                self.predicted_media_life_left_percent),
            "MediaType": self.media_type,
            "SerialNumber": self.serial_number,
            "CapableSpeedGbs": self.capable_speed_gbs,
            "NegotiatedSpeedGbs": self.negotiated_speed_gbs,
            "Revision": self.revision,
            "StatusIndicator": self.status_indicator,
            "TemperatureCelsius": self.temperature_celsius,
            "HoursOfPoweredUp": self.hours_of_powered_up,
            "FirmwareStatus": self.firmware_status,
            "SASAddress": self.sas_address,
            "PatrolState": self.patrol_state,
            "RebuildState": self.rebuild_state,
            "RebuildProgress": self.rebuild_progress,
            "SpareforLogicalDrives": self.spare_for_logical_drives,
            "RaidControllerID": self.raid_controller_id,
            "State": self.state,
            "Health": self.health,
            "Volumes": self.volumes,
            "PanelLocation": self.panel_location,
            "SlotPhysNo": self.slot_phys_no,
            "ConnectionID": self.connection_id,
            "DriveNumberInBios": self.drive_number_in_bios,
            "DriveNumberInOS": self.drive_number_in_os,
            "ManufacturerModel": self.manufacturer_model,
            "Property": self.property,
            "CapacityTiB": self.capacity_tib,
        }

    def pack_physical_resource(self, raid_name, logical_name, resp):

        self.id = resp.get("Id", None)
        self.name = resp.get("Name", None)

        if (resp.get("Oem", None) and
                isinstance(resp["Oem"].get("Public", None), dict)):
            oem_info = resp["Oem"]["Public"]
            self.panel = oem_info.get("Panel", None)
            self.temperature_celsius = oem_info.get("TemperatureCelsius", None)
            self.firmware_status = oem_info.get("FirmwareStatus", None)
            if oem_info.get("OwnerVolume", None) is not None:
                self.raid_controller_id = (oem_info["OwnerVolume"].get(
                    "RaidControllerID", None))
            else:
                self.raid_controller_id = None
            self.connection_id = oem_info.get("ConnectionID", None)
            self.drive_number_in_bios = oem_info.get("DriveNumberInBios", None)
            self.drive_number_in_os = oem_info.get("DriveNumberInOS", None)

            if oem_info.get("HotspareType", None) is not None:
                self.hot_spare_type = oem_info.get("HotspareType")
            else:
                self.hot_spare_type = resp.get("HotspareType", None)
            if oem_info.get("IndicatorLED", None) is not None:
                self.indicator_led = oem_info.get("IndicatorLED")
            else:
                self.indicator_led = resp.get("IndicatorLED", None)
            if oem_info.get("StatusIndicator", None) is not None:
                self.status_indicator = oem_info.get("StatusIndicator")
            else:
                self.status_indicator = resp.get("StatusIndicator", None)
            if oem_info.get("HoursOfPoweredUp", None) is not None:
                self.hours_of_powered_up = oem_info.get("HoursOfPoweredUp")
            else:
                self.hours_of_powered_up = resp.get("HoursOfPoweredUp", None)
            if oem_info.get("SASAddress", None) is not None:
                self.sas_address = oem_info.get("SASAddress")
            else:
                self.sas_address = resp.get("SASAddress", None)
            if oem_info.get("PatrolState", None) is not None:
                self.patrol_state = oem_info.get("PatrolState")
            else:
                self.patrol_state = resp.get("PatrolState", None)
            if oem_info.get("RebuildState", None) is not None:
                self.rebuild_state = oem_info.get("RebuildState")
            else:
                self.rebuild_state = resp.get("RebuildState", None)
            if oem_info.get("RebuildProgress", None) is not None:
                self.rebuild_progress = oem_info.get("RebuildProgress")
            else:
                self.rebuild_progress = resp.get("RebuildProgress", None)
            if oem_info.get("SpareforLogicalDrives", None) is not None:
                self.spare_for_logical_drives = oem_info.get(
                    "SpareforLogicalDrives")
            else:
                self.spare_for_logical_drives = resp.get(
                    "SpareforLogicalDrives", None)

        self.manufacturer = resp.get("Manufacturer", None)
        self.model = resp.get("Model", None)
        self.protocol = resp.get("Protocol", None)
        self.failure_predicted = resp.get("FailurePredicted", None)

        try:
            self.capacity_gib = int(resp.get("CapacityBytes", None) // 1024
                                    ** 3)
            self.capacity_tib = str('%.2f' %
                                    (self.capacity_gib / 1024)) + "TiB"
        except TypeError:
            pass
        self.predicted_media_life_left_percent = (
            resp.get("PredictedMediaLifeLeftPercent", None))
        self.media_type = resp.get("MediaType", None)
        self.serial_number = resp.get("SerialNumber", None)
        self.capable_speed_gbs = resp.get("CapableSpeedGbs", None)
        self.negotiated_speed_gbs = resp.get("NegotiatedSpeedGbs", None)
        self.revision = resp.get("Revision", None)
        if resp.get("Status", None):
            self.state = resp["Status"].get("State", None)
            self.health = resp["Status"].get("Health", None)
        if self.panel:
            panel_location, slot_phys_no = self.panel.split(" ", 1)
            if panel_location and slot_phys_no:
                self.panel_location = panel_location
                self.slot_phys_no = int(slot_phys_no)
        if self.manufacturer and self.model:
            self.manufacturer_model = "%s %s" % (self.manufacturer, self.model)
        if self.capable_speed_gbs and self.protocol and self.media_type:
            self.property = "%s Gbps %s %s" % (self.capable_speed_gbs,
                                               self.protocol, self.media_type)
        self.raid_controller_id = resp.get("MemberId", None)
        self.volumes = "%s-%s" % (raid_name, logical_name)

    def pack_b01_physical_resource(self, resp):

        self.panel = resp.get("panel") + " " + str(resp.get("slot_phys_no"))
        self.name = "Disk" + resp.get("panel") + str(resp.get("slot_phys_no"))
        self.manufacturer = resp.get("vendor")
        self.model = resp.get("product_id")
        self.protocol = resp.get("type")
        self.failure_predicted = resp.get("status")
        self.capacity_gib = resp.get("capacity")
        self.hot_spare_type = resp.get("status")
        self.media_type = resp.get("type")
        self.serial_number = resp.get("serial")
        self.negotiated_speed_gbs = resp.get("type")
        self.revision = resp.get("revision_lv")
        self.firmware_status = resp.get("status")
        self.health = resp.get("status")


class GetPDisk(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["physical_id"]
        self.overall_health = None
        self.maximum = None
        self.physicals = []

    @property
    def dict(self):

        return {
            "OverallHealth": self.overall_health,
            "Maximum": None,
            "Physicals": self.physicals
        }

    @GetVersion()
    def run(self, args):

        init_args(args, self.args_lst)
        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            physical_disk_list = self._get_b01_physical_disk_list(client)
            if not physical_disk_list:
                suc_info = "Success: raid card resource is empty"
                self.suc_list.append(suc_info)
                return self.suc_list
        else:
            client = RedfishClient(args)
            physical_disk_list = self._get_physical_disk_list(client)

            if args.physical_id is None and not physical_disk_list:
                suc_info = "Success: raid card resource is empty"
                self.suc_list.append(suc_info)
                return self.suc_list
            if not self._get_physical_disk_detail(client, physical_disk_list,
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
            disk_health = status_dict.get(str(resp.get("disk", None)), None)
            self.overall_health = disk_health
        else:
            self.err_list.append("Failure: failed to get overall health "
                                 "status information")
            raise FailException(*self.err_list)

    def _get_physical_disk_detail(self, client, physical_disk_list, args):

        flag = False
        for physical_disk in physical_disk_list:
            for phy in physical_disk["url"]:
                raid_name, logical_name, p_url = phy
                resp = client.send_request("GET", p_url)
                if (isinstance(resp, dict) and
                        resp.get("status_code", None) in Constant.SUC_CODE):
                    resp = resp["resource"]
                    if args.physical_id is None:
                        flag = True
                        resp["AssetTag"] = physical_disk.get("AssetTag", None)
                        resp["MemberId"] = physical_disk.get("MemberId", None)
                        physical = Physical()
                        physical.pack_physical_resource(raid_name,
                                                        logical_name, resp)
                        self.physicals.append(physical)
                    elif (resp.get("Oem", None) and
                          isinstance(resp["Oem"].get("Public", None), dict)):
                        if (resp["Oem"]["Public"].get("ConnectionID", None) ==
                                args.physical_id):
                            resp["AssetTag"] = physical_disk.get("AssetTag")
                            resp["MemberId"] = physical_disk.get("MemberId")
                            physical = Physical()
                            physical.pack_physical_resource(raid_name,
                                                            logical_name, resp)
                            self.physicals.append(physical)
                            flag = True
                            return flag
                else:
                    err = "Failure: failed to get physical disk details"
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
        if flag and self.physicals:
            try:
                self.physicals = sorted(self.physicals,
                                        key=lambda s: s.slot_phys_no)
            except TypeError:
                pass
        return flag

    def _get_physical_disk_list(self, client):

        physical_disk_list = list()
        systems_id = client.get_systems_id()

        url = "/redfish/v1/Systems/%s/Storages" % systems_id
        resp = client.send_request("GET", url)
        if (isinstance(resp, dict) and
                resp.get("status_code", None) in Constant.SUC_CODE):
            self.get_storages_disk_driver(resp, client, physical_disk_list,
                                          systems_id)
        else:

            url = "/redfish/v1/Systems/%s/Storage" % systems_id
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                self.get_storage_disk_driver(resp, client, physical_disk_list)
            else:
                err = "Failure: failed to get raid card collection information"
                self.err_list.append(err)
                raise FailException(*self.err_list)
        return physical_disk_list

    def _get_b01_physical_disk_list(self, client):

        try:
            url = "/api/settings/storageinfo"
            resp1 = client.send_request("GET", url)
            if isinstance(resp1, dict) and Constant.SUCCESS_0 == \
                    resp1.get("cc"):
                physical_disk = resp1.get("dis_phys_info")
                for member in physical_disk:
                    physical = Physical()
                    physical.pack_b01_physical_resource(member)
                    self.physicals.append(physical)
            else:
                err = "Failure: failed to get raid card collection information"
                self.err_list.append(err)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return physical_disk

    def get_storages_disk_driver(self, resp, client, physical_disk_list, s_id):

        raid_members = resp["resource"].get("Members", None)
        if not raid_members:
            url = "/redfish/v1/Chassis/%s/Drives" % s_id
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                physical_drivers = resp["resource"].get("Members", None)
                if physical_drivers:
                    ctrl = dict()
                    ctrl["AssetTag"] = None
                    ctrl["MemberId"] = None
                    physical_url = list()
                    for driver in physical_drivers:
                        pd = Pdisk(None, None, driver.get("@odata.id"))
                        physical_url.append(pd)
                    ctrl["url"] = physical_url
                    physical_disk_list.append(ctrl)
            else:
                err = ("Failure: failed to get physical disk"
                       " collection information")
                self.err_list.append(err)
                raise FailException(*self.err_list)
        for member in raid_members:
            url = member.get("@odata.id", None)
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                raid_name = resp["resource"].get("Name")
                physical_drivers = resp["resource"].get("Drives", None)
                if physical_drivers:
                    ctrl = dict()
                    storage_controllers = (
                        resp["resource"].get("StorageControllers", None))
                    if storage_controllers:
                        ctrl["AssetTag"] = (
                            storage_controllers[0].get("AssetTag", None))
                        ctrl["MemberId"] = (
                            storage_controllers[0].get("MemberId", None))
                    physical_url = list()
                    for driver in physical_drivers:
                        pd = Pdisk(raid_name, None, driver.get("@odata.id"))
                        physical_url.append(pd)
                    ctrl["url"] = physical_url
                    physical_disk_list.append(ctrl)
            else:
                err = "Failure: failed to get raid card details"
                self.err_list.append(err)
                raise FailException(*self.err_list)

    def get_storage_disk_driver(self, resp, client, physical_disk_list):

        raid_members = resp["resource"].get("Members", None)
        for member in raid_members:
            url = member.get("@odata.id", None)
            resp = client.send_request("GET", url)
            if (isinstance(resp, dict) and
                    resp.get("status_code", None) in Constant.SUC_CODE):
                raid_name = resp["resource"].get("Name")
                physical_drivers = resp["resource"].get("Drives", None)
                logical_physical_drivers = []
                logical_physical_url = (
                    resp["resource"]["Volumes"].get("@odata.id"))
                logical_physical_resp = client.send_request(
                    "GET", logical_physical_url)
                if (isinstance(logical_physical_resp, dict) and
                        logical_physical_resp.get("status_code",
                                                  None) in Constant.SUC_CODE):
                    logical_members = (
                        logical_physical_resp["resource"].get("Members", []))
                    for logical in logical_members:
                        logical_resp = client.send_request(
                            "GET", logical.get("@odata.id"))
                        if (isinstance(logical_resp, dict) and
                                logical_resp.get("status_code", None) in
                                Constant.SUC_CODE):
                            logical_name = logical_resp["resource"].get("Name")
                            lp_ds = (
                                logical_resp["resource"]["Links"].get("Drives",
                                                                      []))
                            for lp_d in lp_ds:
                                lp_tmp = Pdisk(raid_name, logical_name,
                                               lp_d.get("@odata.id"))
                                logical_physical_drivers.append(lp_tmp)
                if physical_drivers or logical_physical_drivers:
                    ctrl = dict()
                    storage_controllers = (
                        resp["resource"].get("StorageControllers", None))
                    if storage_controllers:
                        ctrl["AssetTag"] = (
                            storage_controllers[0].get("AssetTag", None))
                        ctrl["MemberId"] = (
                            storage_controllers[0].get("MemberId", None))
                    physical_url = list()
                    for driver in physical_drivers:
                        pd = Pdisk(raid_name, None, driver.get("@odata.id"))
                        physical_url.append(pd)
                    physical_url.extend(logical_physical_drivers)
                    ctrl["url"] = physical_url
                    physical_disk_list.append(ctrl)
            else:
                err = "Failure: failed to get raid card details"
                self.err_list.append(err)
                raise FailException(*self.err_list)
