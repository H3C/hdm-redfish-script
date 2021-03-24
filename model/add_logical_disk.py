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


class AddLDisk(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = [
            "controller_id",
            "volume_name",
            "opt_size_bytes",
            "initialization_mode",
            "volume_raid_level",
            "drives_id",
            "span_number",
            "number_in_span",
            "read_policy",
            "write_policy",
            "io_policy",
            "drive_cache_policy",
            "access_policy",
            "capacity_bytes",
            "size_unit",
            "acceleration_method"
        ]

    def run(self, args):

        init_args(args, self.args_lst)
        payload = self._construct_param(args)
        client = RestfulClient(args)
        url = "/api/remote/logical_config"
        try:
            resp = client.send_request("POST", url, payload)
            if (isinstance(resp, dict) and
                    Constant.SUCCESS_0 == resp.get("cc", None)):
                self.suc_list.append("Success: add logical drive successfully")
            else:
                err = "Failure: failed to add logical drive"
                self.err_list.append(err)
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()

        return self.suc_list

    def _construct_param(self, args):

        payload = dict()
        payload["raid_name"] = ""
        payload["ctrl_id"] = args.controller_id
        payload["name"] = (
            args.volume_name if args.volume_name is not None else "")
        strip_size_dict = {
            "16": 5,
            "32": 6,
            "64": 7,
            "128": 8,
            "256": 9,
            "512": 10,
            "1024": 11
        }
        payload["strip_size"] = (strip_size_dict[args.opt_size_bytes]
                                 if args.opt_size_bytes is not None else 7)
        init_state_dict = {
            "No": 0,
            "Fast": 1,
            "Full": 2
        }
        payload["init_state"] = (init_state_dict[args.initialization_mode]
                                 if args.initialization_mode is not None else 0)
        level_dict = {
            "RAID0": 0,
            "RAID1": 1,
            "RAID5": 2,
            "RAID6": 3,
            "RAID00": 4,
            "RAID10": 5,
            "RAID50": 6,
            "RAID60": 7
        }
        payload["level"] = (level_dict[args.volume_raid_level]
                            if args.volume_raid_level is not None else 0)
        payload["span_num"] = args.span_number
        payload["physical_drive_num"] = args.number_in_span
        payload["acceleration_method"] = (
            args.acceleration_method if
            args.acceleration_method is not None else None
        )
        num_drives_list = self._physical_disk_dict(args.drives_id)
        if num_drives_list is None:
            return None
        try:
            payload["num_drives"] = len(num_drives_list) // args.span_number
        except ZeroDivisionError as err:
            self.err_list.append("Argument: %s" % err)
            raise FailException(*self.err_list)
        payload["physical_drive_num"] = len(num_drives_list)
        read_policy_dict = {"NoReadAhead": 0, "ReadAhead": 1}
        payload["read_policy"] = (
            read_policy_dict[args.read_policy] if
            args.read_policy is not None else 0
        )
        write_policy_dict = {
            "WriteThrough": 0,
            "WriteBack": 1,
            "AlwaysWriteBack": 2
        }
        payload["write_policy"] = (
            write_policy_dict[args.write_policy] if
            args.write_policy is not None else 0
        )
        io_policy_dict = {"Direct": 0, "Cached": 1}
        payload['io_policy'] = (io_policy_dict[args.io_policy]
                                if args.io_policy is not None else 0)
        disk_cache_policy_dict = {
            "Unchanged": 0,
            "Enabled": 1,
            "Disabled": 2
        }
        payload["disk_cache_policy"] = (
            disk_cache_policy_dict[args.drive_cache_policy] if
            args.drive_cache_policy is not None else 0
        )
        access_policy_dict = {
            "ReadWrite": 0,
            "ReadOnly": 1,
            "Blocked": 2
        }
        payload["access_policy"] = (
            access_policy_dict[args.access_policy] if
            args.access_policy is not None else 0
        )
        size_unit_dict = {"MB": 0, "GB": 1, "TB": 2}
        payload["size_unit"] = (
            size_unit_dict[args.size_unit] if args.size_unit is not None else 0)
        payload["physical"] = num_drives_list
        payload["size"] = (
            args.capacity_bytes if args.capacity_bytes is not None else 0)
        return payload

    def _physical_disk_dict(self, phy_str):

        try:
            disk_list = list()
            if phy_str[0] != "[" or phy_str[-1] != "]":
                self.err_list.append("Argument: parameter error")
                raise FailException(*self.err_list)
            phy_str = phy_str[1:-1]
            phy_list = phy_str.split("_")
            for phy_info in phy_list:
                s_dict = dict()
                connect_id, group_id = phy_info.split(":")
                s_dict["id"] = int(connect_id)
                s_dict["group_id"] = int(group_id)
                s_dict["panel"] = ""
                s_dict["location"] = ""
                disk_list.append(s_dict)
        except (OSError, TypeError, ValueError, KeyError, Exception):
            self.err_list.append("Argument: parameter error")
            raise FailException(*self.err_list)

        return disk_list
