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


from view.common_view import common_show
from view.json_view import json_show, ipmi_show


def show(data=None, err_list=None, suc_list=None, formatter=None):

    if formatter is not None:
        if formatter.get("json") == "True":
            if formatter.get("ipmi") == "True":
                ipmi_show(data, err_list, suc_list, formatter)
            elif formatter.get("raw") == "True":
                json_show(data, err_list, suc_list, formatter, True)
            else:
                json_show(data, err_list, suc_list, formatter)
        else:
            if formatter.get("raw") == "True":
                common_show(data, err_list, suc_list, formatter, True)
            else:
                common_show(data, err_list, suc_list, formatter)
