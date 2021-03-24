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


import json
import collections
from json import dumps
from utils.common import Constant


def _parse_show(data, formatter, message, is_raw):

    if not is_raw and not formatter:
        return
    if not is_raw:
        for child in formatter:
            if Constant.PROPERTY == child.tag:

                name = child.get("name", None)
                reference = child.get("reference")
                if not name:
                    name = reference
                message[name] = (
                    None if (
                        data.get(
                            reference,
                            None) == "N/A" or data.get(
                            reference,
                            None) == "NULL") else data.get(
                        reference,
                        None))
            elif Constant.TAG == child.tag:

                name = child.get("name", None)
                tag = collections.OrderedDict()
                message[name] = tag
                _parse_show(data, child, tag, is_raw)

            elif Constant.LIST == child.tag:

                name = child.get("name")
                reference = child.get("reference")
                list_ = data.get(reference, None)
                sub_list = []
                message[name] = sub_list
                if list_:
                    for sub_info in list_:
                        sub_info = sub_info.dict
                        list_mess = collections.OrderedDict()
                        sub_list.append(list_mess)
                        flag = child.get("flag")

                        if Constant.IS_ABSENT == flag:

                            status = child.get("status")
                            value = child.get("value")

                            if value == sub_info.get(status, None):
                                absent = child.find(Constant.ABSENT)
                                _parse_show(
                                    sub_info, absent, list_mess, is_raw)
                            else:

                                present = child.find(Constant.PRESENT)
                                _parse_show(sub_info, present,
                                            list_mess, is_raw)
                        else:

                            _parse_show(sub_info, child, list_mess, is_raw)
    else:
        message.update(data)


def json_show(data=None, err_list=None, suc_list=None,
              formatter=None, is_raw=False):

    result = collections.OrderedDict()

    if err_list:
        result["State"] = "Failure"
        result["Message"] = err_list
    elif suc_list:
        result["State"] = "Success"
        result["Message"] = suc_list
        if hasattr(data, "dict"):
            data = data.dict
            if data is not None and data.get("is_write_file", None) and \
                    data.get("file_path", None):
                file_path = data["file_path"]
                flag = _write_file(data, formatter, file_path)
                if not flag:
                    return
    else:
        result["State"] = "Success"
        result["Message"] = []
        message = collections.OrderedDict()
        data = data.dict
        _parse_show(data, formatter, message, is_raw)
        result["Message"].append(message)

    print(dumps(result, indent=4, separators=(',', ': ')))


def ipmi_show(data=None, err_list=None, suc_list=None, formatter=None):

    result = collections.OrderedDict()
    if err_list:
        result["ipmirsp"] = err_list
    elif suc_list:

        if suc_list == "This hdm version does not support this command!":
            result["State"] = "Success"
            result["Message"] = suc_list
        else:
            result["ipmirsp"] = suc_list

        if hasattr(data, "dict"):
            data = data.dict
            if data.get("is_write_file", None) and data.get("file_path", None):
                file_path = data["file_path"]
                flag = _write_file(data, formatter, file_path)
                if not flag:
                    return
    else:
        result["ipmirsp"] = []
        message = collections.OrderedDict()
        data = data.dict
        _parse_show(data, formatter, message, False)
        result["ipmirsp"].append(message)

    print(dumps(result, indent=4, separators=(",", ": ")))


def _write_file(data, formatter, file_path):
    message = collections.OrderedDict()
    _parse_show(data, formatter, message, False)
    try:
        with open(file_path, "w") as file_:
            file_.write(json.dumps(message, indent=4,
                                   separators=(',', ': ')))
    except IOError as err:
        err_list = [str(err)]
        json_show(err_list=err_list, formatter=formatter)
        return False

    return True
