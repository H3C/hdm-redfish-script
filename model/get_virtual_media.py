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
from utils.common import Constant
from utils.model import BaseModule


class Connect:

    def __init__(self):
        self.media_index = None
        self.image_name = None
        self.media_types = None

    @property
    def dict(self):

        return {
            "MediaIndex": self.media_index,
            "ImageName": self.image_name,
            "MediaTypes": self.media_types
        }

    def pack_resource(self, resp):

        self.media_index = resp.get("MediaIndex", None)
        self.image_name = resp.get("ImageName", None)
        self.media_types = resp.get("MediaTypes", None)


class NotConnect:

    def __init__(self):
        self.id = None
        self.image_name = None
        self.media_types = None

    @property
    def dict(self):

        return {
            "ID": self.id,
            "ImageName": self.image_name,
            "MediaTypes": self.media_types
        }

    def pack_resource(self, resp):

        self.id = resp.get("ID", None)
        self.image_name = resp.get("ImageName", None)
        self.media_types = resp.get("MediaTypes", None)


class GetVmm(BaseModule):

    def __init__(self):
        super().__init__()

        self.connects = []
        self.not_connects = []

        self.connect_none = {}
        self.not_connect_none = {}

        self.connect_tag = {}
        self.not_connect_tag = {}

    @property
    def dict(self):

        return self.__dict__

    def run(self, args):

        client = RedfishClient(args)
        systems_id = client.get_systems_id()

        url = ("/redfish/v1/Managers/%s/VirtualMedia/%s" %
               (systems_id, args.type))
        resp = client.send_request("get", url)
        if isinstance(resp, dict) and resp.get(
                "status_code", None) in Constant.SUC_CODE:
            self._pack_resource(resp["resource"])
        else:
            self.err_list.append(
                "Failure: failed to get virtual media information")
            raise FailException(*self.err_list)

        return self.suc_list

    def _pack_resource(self, resp):

        vmm_conn_list = resp.get("Connected", None)
        vmm_unconn_list = resp.get("NotConnected", None)
        try:
            vmm_conn_list = (
                sorted(vmm_conn_list, key=lambda s: int(s["MediaIndex"])) if
                (vmm_conn_list is not None) else None)
            vmm_unconn_list = (
                sorted(vmm_unconn_list, key=lambda s: int(s["ID"])) if
                (vmm_unconn_list is not None) else None)
        except (OSError, TypeError, ValueError, KeyError, Exception) as err:
            self.err_list.append(str(err))
            raise FailException(*self.err_list)

        if not vmm_conn_list:
            self.connect_none["Connected"] = None
            self.connect_tag = None
        else:
            for vmm_conn in vmm_conn_list:
                connect = Connect()
                connect.pack_resource(vmm_conn)
                self.connects.append(connect)
        if not vmm_unconn_list:
            self.not_connect_none["NotConnected"] = None
            self.not_connect_tag = None
        else:
            for vmm_unconn in vmm_unconn_list:
                not_connect = NotConnect()
                not_connect.pack_resource(vmm_unconn)
                self.not_connects.append(not_connect)
