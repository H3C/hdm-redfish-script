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


from utils.common import Constant

_pf = '{0}{1:26}: {2}'


def _parse_show(data, formatter, is_raw, indent="0", status=None, value=None):

    if not is_raw and not formatter:
        return

    if not is_raw:

        if status:
            if data.get(status, None) != value:
                return

        indent_space = Constant.STR_NULL * int(indent)

        for child in formatter:
            if Constant.LI == child.tag:

                len_line = Constant.LEN_LINE - int(indent)
                print(indent_space + '-' * len_line)
            elif Constant.BL == child.tag:

                print()
            elif Constant.TAG == child.tag:

                name = child.get("name", None)
                reference = child.get("reference")
                indent_sub = child.get("indent")
                if indent_sub is None:
                    indent_sub = indent
                reference_tag = data
                if reference:

                    reference_tag = data.get(reference, None)
                    if reference_tag is None:
                        continue
                print(indent_space + name)
                indent_total = str(int(indent) + int(indent_sub))
                _parse_show(reference_tag, child, is_raw, indent=indent_total,
                            status=status, value=value)
            elif Constant.RAW == child.tag:

                name = child.get("name", None)
                reference = child.get("reference")
                sub_data = data.get(reference, None)
                if name is not None:
                    print(indent_space + name)
                if isinstance(sub_data, dict):
                    for key, value in sub_data.items():
                        _format_out(key, value, indent)
            elif Constant.PROPERTY == child.tag:

                name = child.get("name", None)
                reference = child.get("reference")
                if not name:
                    name = reference
                _format_out(name, data.get(reference, None), indent)
            elif Constant.LIST == child.tag:

                reference = child.get("reference")
                status = child.get("status")
                value = child.get("value")
                list_ = data.get(reference, None)
                indent_sub = child.get("indent")
                if indent_sub is None:
                    indent_sub = indent
                name = child.get("name")
                if _is_exist_resource(list_, status, value):
                    indent_total = str(int(indent) + int(indent_sub))
                    if name is not None:
                        print(indent_space + name)
                    for sub_info in list_:
                        sub_info = sub_info.dict
                        _parse_show(sub_info, child, is_raw,
                                    indent=indent_total,
                                    status=status, value=value)
                else:
                    if name:
                        print(indent_space + name)
    else:
        len_line = Constant.LEN_LINE
        print("-" * len_line)
        for key, value in data.items():
            _format_out(key, value, "0")
        print("-" * len_line)


def _show_error(err_list):

    for err in err_list:
        print(err)


def _show_success(suc_list):

    for suc in suc_list:
        print(suc)


def common_show(data=None, err_list=None, suc_list=None, formatter=None,
                is_raw=False):

    if err_list:
        _show_error(err_list)
    elif suc_list:
        _show_success(suc_list)
    else:
        if hasattr(data, "dict"):
            data = data.dict
            _parse_show(data, formatter, is_raw)


def _format_out(name, value, indent):

    left_align = Constant.PRINT_DEFAULT - int(indent)
    pf = '{0}{1:%s}: {2}' % left_align
    indent = Constant.STR_NULL * int(indent)

    print(pf.format(indent, name, value))


def _is_exist_resource(list_, status, value):

    flag = False
    if not list_:
        return False
    if status:
        for item in list_:
            item = item.dict
            if item.get(status, None) == value:
                flag = True
    else:
        flag = True
    return flag
