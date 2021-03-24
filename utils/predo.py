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
from utils import globalvar


class GetVersion:

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            is_adapt_b01 = globalvar.IS_ADAPT_B01
            flag = False
            if is_adapt_b01:
                client = RestfulClient(args[1])
                try:

                    version = get_hdm_firmware(client)

                    globalvar.HDM_VERSION = version
                    if version is not None and version < "1.11.00":
                        flag = True
                    else:
                        flag = False
                finally:
                    if client.cookie:
                        client.delete_session()

            globalvar.IS_ADAPT_B01 = flag
            return func(*args, **kwargs)
        return wrapper


class AllowCommand:
    def __init__(self, version=None):
        self.version = version

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            client = RestfulClient(args[1])
            try:

                version = get_hdm_firmware(client)
                if version is not None and version < "1.11.00":

                    err_list = []
                    err_info = ("Failure: this hdm version does not "
                                "support this command")
                    err_list.append(err_info)
                    raise FailException(*err_list)
                else:
                    return func(*args, **kwargs)
            finally:
                if client.cookie:
                    client.delete_session()
        return wrapper


def get_hdm_firmware(client):

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
