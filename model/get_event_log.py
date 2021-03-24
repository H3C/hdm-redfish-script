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


import os
import time
from exception.ToolException import FailException
from utils.client import RestfulClient
from datetime import datetime
from datetime import timezone
from dateutil import tz
from dateutil.parser import parse
from utils.model import BaseModule
from utils.tools import init_args


class EventLog:

    def __init__(self):
        self.id = None
        self.level = None
        self.event_time = None
        self.sensor_name = None
        self.sensor_number = None
        self.event_description = None
        self.event_direction = None

        self.record_type = None
        self.time = None
        self.system_software_type = None
        self.generator_type = None
        self.channel_number = None
        self.ipmb_lun = None
        self.event_format_ipmi_version = None
        self.sensor_type = None
        self.type_number = None
        self.event_reading_class = None
        self.sensor_reading_value = None
        self.triggered_value = None
        self.sensor_reading_value_type = None
        self.triggered_type = None

    @property
    def dict(self):

        return {
            "id": self.id,
            "level": self.level,
            "event_time": self.event_time,
            "sensor_name": self.sensor_name,
            "sensor_number": self.sensor_number,
            "event_description": self.event_description,
            "event_direction": self.event_direction,

            "record_type": self.record_type,
            "time": self.time,
            "system_software_type": self.system_software_type,
            "generator_type": self.generator_type,
            "channel_number": self.channel_number,
            "ipmb_lun": self.ipmb_lun,
            "event_format_ipmi_version": self.event_format_ipmi_version,
            "sensor_type": self.sensor_type,
            "type_number": self.type_number,
            "event_reading_class": self.event_reading_class,
            "sensor_reading_value": self.sensor_reading_value,
            "triggered_value": self.triggered_value,
            "sensor_reading_value_type": self.sensor_reading_value_type,
            "triggered_type": self.triggered_type
        }

    def pack_log_resource(self, resp):

        level_dict = {
            "0": "Reserved",
            "1": "OK",
            "2": "Caution",
            "3": "Warning",
            "4": "Critical"
        }
        self.id = resp.get("id", None)
        self.level = level_dict.get(str(resp.get("level")))
        timestamp = resp.get("timestamp", None)
        try:
            time_stamp = datetime.strftime(datetime.
                                           utcfromtimestamp(timestamp).
                                           replace(tzinfo=tz.gettz('UTC')),
                                           "%Y-%m-%dT%H:%M:%S%z")
            timestamp = datetime.strftime(datetime.
                                          utcfromtimestamp(timestamp).
                                          replace(tzinfo=tz.gettz('UTC')),
                                          "%Y-%m-%d %H:%M:%S")
        except (OSError, TypeError, ValueError, KeyError, SyntaxError):
            time_stamp = None
            timestamp = None
        self.event_time = time_stamp
        self.time = timestamp
        self.sensor_name = resp.get("sensor_name", None)
        self.sensor_number = resp.get("sensor_number", None)
        self.event_description = resp.get("event_description", None)
        tmp_status = resp.get("event_direction")
        if tmp_status == "asserted":
            status = "Assert"
        elif tmp_status == "deasserted":
            status = "Deassert"
        else:
            status = tmp_status
        self.event_direction = status
        self.record_type = resp.get("record_type", None)
        self.system_software_type = resp.get("system_software_type", None)
        self.generator_type = resp.get("generator_type", None)
        self.channel_number = resp.get("channel_number", None)
        self.ipmb_lun = resp.get("ipmb_lun", None)
        self.event_format_ipmi_version = resp.get(
            "event_format_ipmi_version", None)
        self.sensor_type = resp.get("sensor_type", None)
        self.type_number = resp.get("type_number", None)
        self.event_reading_class = resp.get("event_reading_class", None)
        self.sensor_reading_value = resp.get("sensor_reading_value", None)
        self.triggered_value = resp.get("triggered_value", None)
        self.sensor_reading_value_type = resp.get(
            "sensor_reading_value_type", None)
        self.triggered_type = resp.get("triggered_type", None)


class GetEventLog(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["count", "time", "file_path"]
        self.event_logs = []
        self.is_write_file = None
        self.file_path = None

    @property
    def dict(self):

        return {
            "event_logs": self.event_logs,
            "is_write_file": self.is_write_file,
            "file_path": self.file_path
        }

    def run(self, args):

        init_args(args, self.args_lst)
        self._check_args(args)
        client = RestfulClient(args)
        try:
            url = "/api/logs/event"
            resp = client.send_request("GET", url)
        finally:
            if client.cookie:
                client.delete_session()
        if isinstance(resp, list):
            if not resp:
                suc_info = "Success: event log list is empty"
                self.suc_list.append(suc_info)
            else:
                self._package_results(args, resp)
        else:
            self.err_list.append("Failure: failed to get event log list!")
            raise FailException(*self.err_list)
        return self.suc_list

    def _check_args(self, args):

        if args.file_path is not None:
            try:
                with open(args.file_path, 'w'):
                    pass
            except IOError as err:
                self.err_list.append(str(err))
                raise FailException(*self.err_list)
            else:
                os.remove(args.file_path)
        if args.time is not None and args.count is not None:
            self.err_list.append("Argument: time parameter and quantity "
                                 "parameter cannot be used at the same time")
            raise FailException(*self.err_list)
        if args.time is not None:
            time_org_str = args.time
            try:
                time_str = parse(time_org_str)
                utc_time_str = time_str.replace(tzinfo=timezone.utc)

                args.time = (time.mktime(time_str.timetuple()) +
                             (time_str - utc_time_str).total_seconds() + 28800)
            except (ValueError, TypeError, Exception):
                err_info = ("Argument: invalid choice: "
                            "%s (the time format is incorrect, "
                            "exp: 2019-03-13T03:24:45+08:00)" % time_org_str)
                self.err_list.append(err_info)
                raise FailException(*self.err_list)

    def _package_results(self, args, resp):

        resp = sorted(resp, key=lambda s: s["id"], reverse=True)

        if args.count is not None and args.count < len(resp):
            count = args.count
        else:
            count = len(resp)
        resp = resp[:count]

        if args.time is not None:
            resp = sorted(resp, key=lambda s: s["timestamp"], reverse=True)
            for i, log in enumerate(resp):
                if args.time > log.get("timestamp", None):
                    resp = resp[:i]
                    break

        for log in resp:
            event_log = EventLog()
            event_log.pack_log_resource(log)
            self.event_logs.append(event_log)
        if args.file_path is not None:
            self.is_write_file = True
            self.file_path = args.file_path
            suc_info = ("Success: successfully get the event "
                        "log(filepath: %s)" % args.file_path)
            self.suc_list.append(suc_info)
