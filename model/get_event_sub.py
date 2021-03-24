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
from utils.predo import AllowCommand


class EventSub:

    def __init__(self):

        self.id = None
        self.destination = None
        self.event_types = None
        self.http_headers = None
        self.protocol = None
        self.context = None
        self.message_ids = None
        self.origin_resources = None

    @property
    def dict(self):

        return {
            "Id": self.id,
            "Destination": self.destination,
            "EventTypes": self.event_types,
            "HttpHeaders": self.http_headers,
            "Protocol": self.protocol,
            "Context": self.context,
            "MessageIds": self.message_ids,
            "OriginResources": self.origin_resources
        }

    def pack_redfish_resource(self, resp):

        self.id = resp.get("Id", None)
        self.destination = resp.get("Destination", None)
        if isinstance(resp.get("EventTypes", None), list):
            event_type = ", ".join(resp["EventTypes"])
        else:
            event_type = None
        self.event_types = event_type
        self.http_headers = resp.get("HttpHeaders", None)
        self.protocol = resp.get("Protocol", None)
        self.context = resp.get("Context", None)
        self.message_ids = resp.get("MessageIds", None)
        self.origin_resources = resp.get("OriginResources", None)


class GetEventSub(BaseModule):

    def __init__(self):

        super().__init__()
        self.subscriber = []

    @property
    def dict(self):

        return {
            "Subscriber": self.subscriber
        }

    @AllowCommand()
    def run(self, args):

        client = RedfishClient(args)
        url = "/redfish/v1/EventService/Subscriptions"
        resp = client.send_request("get", url)
        event_sub_list = []
        if (isinstance(resp, dict) and resp.get("status_code", None) in
                Constant.SUC_CODE):
            members = resp["resource"].get("Members", None)
            for member in members:
                url = member.get("@odata.id", None)
                resp = client.send_request("GET", url)
                if (isinstance(resp, dict) and
                        resp.get("status_code", None) in Constant.SUC_CODE):
                    event_sub = EventSub()
                    event_sub.pack_redfish_resource(resp["resource"])
                    event_sub_list.append(event_sub)
                else:
                    self.err_list.append("Failure: failed to get event "
                                         "subscription details")
                    raise FailException(*self.err_list)
            try:
                event_sub_list = sorted(
                    event_sub_list, key=lambda s: int(s.id))
            except (KeyError, ValueError, Exception) as err:
                self.err_list.append(str(err))
                raise FailException(*self.err_list)
        else:
            self.err_list.append("Failure: failed to get event subscription "
                                 "information collection")
            raise FailException(*self.err_list)
        self.subscriber = event_sub_list
        if not self.subscriber:
            suc_info = ("Success: "
                        "event subscription information collection is empty")
            self.suc_list.append(suc_info)
        return self.suc_list
