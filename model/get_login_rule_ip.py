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
from utils.model import BaseModule


class Rule:

    def __init__(self):

        self.ip_address_from = None
        self.ip_address_to = None
        self.mac_address = None
        self.rule = None
        self.timeout_status = None
        self.start_time = None
        self.end_time = None

    @property
    def dict(self):

        return {
            "IpFrom": self.ip_address_from,
            "IpTo": self.ip_address_to,
            "MacAddress": self.mac_address,
            "Rule": self.rule,
            "TimeRange": self.timeout_status,
            "TimeFrom": self.start_time,
            "TimeTo": self.end_time
        }


class GetLoginRuleIp(BaseModule):

    def __init__(self):

        super().__init__()
        self.rules_ip = []

    @property
    def dict(self):

        return {
            "RuleIp": self.rules_ip
        }

    def run(self, args):

        client = RestfulClient(args)
        ip_rules = list()
        try:
            url = "/api/settings/firewall-ip-mac-rule-forbid"
            ip_rules.extend(self.get_rule_ip(client, url, "block"))
            url = "/api/settings/firewall-ip-mac-rule-allow"
            ip_rules.extend(self.get_rule_ip(client, url))
            if not ip_rules:
                suc_info = "Success: login rule is empty"
                self.suc_list.append(suc_info)
            else:
                self.rules_ip = _pack_ip_rules_resource(ip_rules)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def get_rule_ip(self, client, url, flag=None):

        rule_list = list()
        resp = client.send_request("GET", url)
        if isinstance(resp, list):
            for rule in resp:
                rule["rule"] = "block" if flag else "allow"
                rule_list.append(rule)
        else:
            err_info = "Failure: failed to get blacklist/whitelist rules"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
        return rule_list


def _pack_ip_rules_resource(rules):

    rule_ip = list()
    for rule in rules:
        tmp = dict()
        tmp["ip_address_from"] = rule.get("ip_address_from")
        tmp["ip_address_to"] = rule.get("ip_address_to")
        tmp["mac_address"] = rule.get("mac_address")
        tmp["timeout_status"] = (
            "Enabled" if rule.get("timeout_status") == 1 else "Disabled")
        start_time, end_time = new_time_convert(rule)
        tmp["start_time"] = start_time
        tmp["end_time"] = end_time
        tmp["rule"] = ("Blacklist" if rule.get("rule") == "block" else
                       "Whitelist")
        r = Rule()
        r.__dict__.update(tmp)
        rule_ip.append(r)
    return rule_ip


def new_time_convert(rule):

    start_time, end_time = None, None
    try:
        start_time = "%04d-%02d-%02dT%02d:%02d" % (rule["date_from_yy"],
                                                   rule["date_from_mm"],
                                                   rule["date_from_dd"],
                                                   rule["time_from_hh"],
                                                   rule["time_from_mm"])
        end_time = "%04d-%02d-%02dT%02d:%02d" % (rule["date_to_yy"],
                                                 rule["date_to_mm"],
                                                 rule["date_to_dd"],
                                                 rule["time_to_hh"],
                                                 rule["time_to_mm"])
    except (KeyError, ValueError, Exception):
        pass
    return start_time, end_time
