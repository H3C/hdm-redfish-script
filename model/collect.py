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
import os
from time import mktime
from time import sleep
from time import strptime
from dateutil.parser import parse
from utils.common import Constant
from exception.ToolException import FailException
from utils.client import RestfulClient
from utils.model import BaseModule


class Collect(BaseModule):

    def __init__(self):

        super().__init__()
        self.args_lst = ["file_name", "start_date", "end_date"]

    def run(self, args):

        is_dir = False
        if os.path.isdir(args.file_name):
            is_dir = True
        else:
            try:
                with open(args.file_name, "wb"):
                    pass
            except IOError as err:
                self.err_list.append(str(err))
                raise FailException(*self.err_list)
            else:
                os.remove(args.file_name)
        payload = self.check_package_args(args)
        client = RestfulClient(args)
        try:
            self.get_sds_log(client, args, payload, is_dir)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def check_package_args(self, args):

        payload = dict()
        if args.start_date is not None and not is_valid_date(args.start_date):
            err_info = ("Argument: invalid choice: %s "
                        "(the date format is incorrect)" % args.start_date)
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        if args.end_date is not None and not is_valid_date(args.end_date):
            err_info = ("Argument: invalid choice: %s "
                        "(the date format is incorrect)" % args.end_date)
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        if args.end_date is not None and args.start_date is not None:
            end_date = string2time(args.end_date)
            start_date = string2time(args.start_date)
            if start_date > end_date:
                err_info = ("Argument: the end date must be later than the "
                            "start date")
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            payload["start_date"] = args.start_date
            payload["end_date"] = args.end_date
        elif ((not args.end_date and args.start_date) or
                (args.end_date and not args.start_date)):
            err_info = "Argument: start time and end time must appear in pairs"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        else:
            payload["start_date"] = "0"
            payload["end_date"] = "0"
        payload["EmailNumber"] = ""
        payload["ContactName"] = ""
        payload["PhoneNumber"] = ""
        return payload

    def get_sds_log(self, client, args, payload, is_dir):

        url = "/api/health/sds/log"
        resp = client.send_request("POST", url, payload)
        if (isinstance(resp, dict) and resp.get(Constant.COMPLETE_CODE)
                == Constant.SUCCESS_0):
            file_name = str(resp.get("filename", None))
            if is_dir:
                args.file_name = os.path.join(args.file_name, file_name)
                try:
                    with open(args.file_name, "wb"):
                        pass
                except (IOError, Exception) as err:
                    self.err_list.append(str(err))
                    raise FailException(*self.err_list)
                else:
                    os.remove(args.file_name)
            index = 0

            while index < 200:
                url = "/api/health/sds/status"
                status_resp = client.send_request("GET", url)
                if (not isinstance(resp, dict) or resp.get(
                        Constant.COMPLETE_CODE) != Constant.SUCCESS_0):
                    err_info = ("Failure: one-click collection of log "
                                "progress failed to get")
                    self.err_list.append(err_info)
                    raise FailException(*self.err_list)
                sds_status = status_resp.get("sds_status", None)
                if sds_status == 100:
                    url = "/sds/%s" % file_name
                    sds_resp = client.http_get(url)
                    if sds_resp is None:
                        err_info = "Log data acquisition failed"
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
                    flag = download_sds_log(args.file_name, sds_resp)
                    if not flag:
                        err_info = ("Failure: one-click collection of log "
                                    "requests failed")
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
                    else:
                        suc_info = ("Success: one-click collection of log "
                                    "requests succeeded")
                        self.suc_list.append(suc_info)
                    break
                index += 1
                sleep(2)
            else:
                err_info = ("Failure: one-click collection of log requests "
                            "timed out")
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
        elif isinstance(resp, dict) and not resp.get('filename', None):
            err_info = "Failure: no sds log found in the specified period"
            self.err_list.append(err_info)
        else:
            err_info = "Failed to get SDS log file name"
            self.err_list.append(err_info)
        if self.err_list:
            raise FailException(*self.err_list)


def download_sds_log(file_name, sds_resp):

    try:
        with open(file_name, 'wb') as log_file:
            log_file.write(sds_resp)
    except IOError:
        return False
    return True


def string2time(str_time):

    return int(mktime(parse(str_time).timetuple()))


def is_valid_date(date_str):

    flag = True
    try:
        strptime(date_str, "%Y-%m-%d")
    except (ValueError, KeyError, Exception):
        flag = False
    else:
        if not re.match(r"\d{4}-\d{2}-\d{2}", date_str):
            flag = False
    return flag
