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
from utils.tools import is_ipv4
from utils.tools import is_ipv6
from utils.model import BaseModule
from utils.tools import init_args


class SetIp(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["version", "gateway", "address", "mode",
                         "mask_prefix", "network_port_id"]

        self.network_port_id = None
        self.ipv4_enable = None
        self.ipv4_dhcp_enable = None
        self.ipv4_address = None
        self.ipv4_subnet = None
        self.ipv4_gateway = None

        self.ipv6_enable = None
        self.ipv6_dhcp_enable = None
        self.ipv6_address = None
        self.ipv6_prefix = None
        self.ipv6_gateway = None

        self.vlan_enable = None
        self.vlan_id = None
        self.vlan_priority = None

    def run(self, args):

        init_args(args, self.args_lst)
        self._check_args(args)
        client = RestfulClient(args)

        try:
            url = "/api/settings/network"
            resp = client.send_request("GET", url)
            if resp and isinstance(resp, list):
                for eth in resp:
                    if args.network_port_id is not None:
                        if (args.network_port_id ==
                                eth.get("interface_name", None)):
                            self._construct_request(client, eth)
                            break
                    elif (eth.get("ipv4_address", None) == args.host
                          or eth.get('ipv6_address', None) == args.host or (
                        args.host.startswith("[") and
                        args.host.endswith("]") and
                        (eth.get('ipv6_address', None) ==
                         args.host[1:-1] or
                         eth.get('ipv6_localLinkAddress', None) ==
                         args.host[1:-1]))):
                        self._construct_request(client, eth)
                        break
                else:
                    err_info = "Argument: the network port does not exist"
                    self.err_list.append(err_info)
                    raise FailException(*self.err_list)
            else:
                self.err_list.append("Failure: failed to get ip information "
                                     "list")
                raise FailException(*self.err_list)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def _construct_request(self, client, payload):

        url = "/api/settings/network/%s" % payload.get("id", None)

        if (payload.get("ipv4_dhcp_enable", None) == 1 and
                self.ipv4_dhcp_enable is None and
                (self.ipv4_address or self.ipv4_gateway or self.ipv4_subnet)):
            self.err_list.append("Argument: parameter is not available in "
                                 "DHCP mode")
            raise FailException(*self.err_list)
        elif (payload.get("ipv6_dhcp_enable", None) == 1 and
              self.ipv6_dhcp_enable is None and
              (self.ipv6_address or self.ipv6_gateway or self.ipv6_prefix)):
            self.err_list.append("Argument: parameter is not available in "
                                 "DHCP mode")
            raise FailException(*self.err_list)

        if self.ipv4_enable is not None:
            payload["ipv4_enable"] = self.ipv4_enable
        if self.ipv4_dhcp_enable is not None:
            payload["ipv4_dhcp_enable"] = self.ipv4_dhcp_enable
        if self.ipv4_address is not None:
            payload["ipv4_address"] = self.ipv4_address
        if self.ipv4_subnet is not None:
            payload["ipv4_subnet"] = self.ipv4_subnet
        if self.ipv4_gateway is not None:
            payload["ipv4_gateway"] = self.ipv4_gateway

        if self.ipv6_enable is not None:
            payload["ipv6_enable"] = self.ipv6_enable
        if self.ipv6_dhcp_enable is not None:
            payload["ipv6_dhcp_enable"] = self.ipv6_dhcp_enable
        if self.ipv6_address is not None:
            payload["ipv6_address"] = self.ipv6_address
        if self.ipv6_prefix is not None:
            payload["ipv6_prefix"] = self.ipv6_prefix
        if self.ipv6_gateway is not None:
            payload["ipv6_gateway"] = self.ipv6_gateway

        if self.vlan_enable is not None:
            payload["vlan_enable"] = self.vlan_enable
        if self.vlan_id is not None:
            payload["vlan_id"] = self.vlan_id
        if self.vlan_priority is not None:
            payload["vlan_priority"] = self.vlan_priority
        resp = client.send_request("PUT", url, payload)
        if (isinstance(resp, dict) and
                Constant.SUCCESS_0 == resp.get("cc", None)):
            suc_info = "Success: set network successfully"
            self.suc_list.append(suc_info)
        else:
            err_info = "Failure: failed to set network"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)

    def _check_args(self, args):

        flag = False
        ipv4 = "4"
        if "mode" in args and "DHCP" == args.mode:
            flag = True
            if (("address" in args and args.address) or
                    ("gateway" in args and args.gateway) or
                    ("mask_prefix" in args and args.mask_prefix)):
                err_info = "Argument: parameter is not available in DHCP mode"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            if "version" in args and args.version:
                if ipv4 == args.version:
                    self.ipv4_dhcp_enable = 1
                else:
                    self.ipv6_dhcp_enable = 1
        if "version" in args and args.version:
            if ipv4 == args.version:
                if "address" in args and args.address:
                    flag = True
                    if not is_ipv4(args.address):
                        err_info = ("Argument: invalid choice: %s "
                                    "(the ipv4 address format is incorrect)" %
                                    args.address)
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
                    else:
                        self.ipv4_address = args.address
                if "gateway" in args and args.gateway:
                    flag = True
                    if not is_ipv4(args.gateway):
                        err_info = ("Argument: invalid choice: %s "
                                    "(the ipv4 gateway format is incorrect)" %
                                    args.gateway)
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
                    else:
                        self.ipv4_gateway = args.gateway
                if "mask_prefix" in args and args.mask_prefix:
                    flag = True
                    if not is_ipv4(args.mask_prefix):
                        err_info = ("Argument: invalid choice: %s "
                                    "(the ipv4 subnetmask format is incorrect)"
                                    % args.mask_prefix)
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
                    else:
                        self.ipv4_subnet = args.mask_prefix
                if "mode" in args and "Static" == args.mode:
                    flag = True
                    self.ipv4_dhcp_enable = 0
            else:
                if "address" in args and args.address:
                    flag = True
                    if not is_ipv6(args.address):
                        err_info = ("Argument: invalid choice: %s "
                                    "(the ipv6 address format is incorrect)" %
                                    args.address)
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
                    else:
                        self.ipv6_address = args.address
                if "gateway" in args and args.gateway:
                    flag = True
                    if not is_ipv6(args.gateway):
                        err_info = ("Argument: invalid choice: %s "
                                    "(the ipv6 gateway format is incorrect)" %
                                    args.gateway)
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
                    else:
                        self.ipv6_gateway = args.gateway
                if "mask_prefix" in args and args.mask_prefix:
                    flag = True
                    try:
                        self.ipv6_prefix = int(args.mask_prefix)
                        if self.ipv6_prefix <= 0 or self.ipv6_prefix > 127:
                            err_info = ("Argument: invalid choice: %s "
                                        "(the ipv6 prefix length is incorrect)"
                                        % args.mask_prefix)
                            self.err_list.append(err_info)
                            raise FailException(*self.err_list)
                    except ValueError:
                        err_info = ("Argument: invalid choice: %s "
                                    "(the ipv6 prefix length is incorrect)" %
                                    args.mask_prefix)
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
                if "mode" in args and "Static" == args.mode:
                    flag = True
                    self.ipv6_dhcp_enable = 0

        if "network_port_id" in args and args.network_port_id:
            self.network_port_id = args.network_port_id

        if "ipv4_enable" in args and "Disabled" == args.ipv4_enable:
            flag = True
            if (("ipv4_mode" in args and args.ipv4_mode) or
                    ("ipv4_address" in args and args.ipv4_address) or
                    ("ipv4_gateway" in args and args.ipv4_gateway) or
                    ("ipv4_subnet" in args and args.ipv4_subnet)):
                err_info = "Parameter is not available in IPv4 disable mode"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            else:
                self.ipv4_enable = 0
        elif "ipv4_enable" in args and "Enabled" == args.ipv4_enable:
            flag = True
            self.ipv4_enable = 1

        if "ipv6_enable" in args and "Disabled" == args.ipv6_enable:
            flag = True
            if (("ipv6_mode" in args and args.ipv6_mode) or
                    ("ipv6_address" in args and args.ipv6_address) or
                    ("ipv6_gateway" in args and args.ipv6_gateway) or
                    ("ipv6_prefix" in args and args.ipv6_prefix)):
                err_info = (
                    "Argument: parameter is not available in IPv6 disable mode")
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            else:
                self.ipv6_enable = 0
        elif "ipv6_enable" in args and "Enabled" == args.ipv6_enable:
            flag = True
            self.ipv6_enable = 1

        if "ipv4_mode" in args and "DHCP" == args.ipv4_mode:
            flag = True
            if (("ipv4_address" in args and args.ipv4_address) or
                    ("ipv4_gateway" in args and args.ipv4_gateway) or
                    ("ipv4_subnet" in args and args.ipv4_subnet)):
                err_info = "Argument: parameter is not available in DHCP mode"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            else:
                self.ipv4_dhcp_enable = 1
        elif "ipv4_mode" in args and "Static" == args.ipv4_mode:
            flag = True
            self.ipv4_dhcp_enable = 0

        if "ipv6_mode" in args and "DHCP" == args.ipv6_mode:
            flag = True
            if (("ipv6_address" in args and args.ipv6_address) or
                    ("ipv6_gateway" in args and args.ipv6_gateway) or
                    ("ipv6_prefix" in args and args.ipv6_prefix)):
                err_info = "Argument: parameter is not available in DHCP mode"
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            else:
                self.ipv6_dhcp_enable = 1
        elif "ipv6_mode" in args and "Static" == args.ipv6_mode:
            flag = True
            self.ipv6_dhcp_enable = 0

        if "ipv4_address" in args and args.ipv4_address:
            flag = True
            if not is_ipv4(args.ipv4_address):
                err_info = ("Argument: invalid choice: %s "
                            "(the ipv4 address format is incorrect)" %
                            args.ipv4_address)
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            else:
                self.ipv4_address = args.ipv4_address
        if "ipv4_gateway" in args and args.ipv4_gateway:
            flag = True
            if not is_ipv4(args.ipv4_gateway):
                err_info = ("Argument: invalid choice: %s "
                            "(the ipv4 gateway format is incorrect)" %
                            args.ipv4_gateway)
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            else:
                self.ipv4_gateway = args.ipv4_gateway
        if "ipv4_subnet" in args and args.ipv4_subnet:
            flag = True
            if not is_ipv4(args.ipv4_subnet):
                err_info = ("Argument: invalid choice: %s "
                            "(the ipv4 subnetmask format is incorrect)" %
                            args.ipv4_subnet)
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            else:
                self.ipv4_subnet = args.ipv4_subnet

        if "ipv6_address" in args and args.ipv6_address:
            flag = True
            if not is_ipv6(args.ipv6_address):
                err_info = ("Argument: invalid choice: %s "
                            "(the ipv6 address format is incorrect)" %
                            args.ipv6_address)
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            else:
                self.ipv6_address = args.ipv6_address
        if "ipv6_gateway" in args and args.ipv6_gateway:
            flag = True
            if not is_ipv6(args.ipv6_gateway):
                err_info = ("Argument: invalid choice: %s "
                            "(the ipv6 gateway format is incorrect)" %
                            args.ipv6_gateway)
                self.err_list.append(err_info)
                raise FailException(*self.err_list)
            else:
                self.ipv6_gateway = args.ipv6_gateway
        if "ipv6_prefix" in args and args.ipv6_prefix is not None:
            flag = True
            self.ipv6_prefix = args.ipv6_prefix
            if self.ipv6_prefix <= 0 or self.ipv6_prefix > 127:
                err_info = ("Argument: invalid choice: %d "
                            "(the ipv6 prefix length is incorrect)" %
                            args.ipv6_prefix)
                self.err_list.append(err_info)
                raise FailException(*self.err_list)

        if "vlan_enable" in args and args.vlan_enable:
            flag = True
            if "Enabled" == args.vlan_enable:
                self.vlan_enable = 1
                if "vlan_id" in args and args.vlan_id is None:
                    err = "Argument: VLAN enablement needs to specify VLAN ID"
                    self.err_list.append(err)
                    raise FailException(*self.err_list)
            else:
                self.vlan_enable = 0
        if "vlan_id" in args and args.vlan_id is not None:
            flag = True
            self.vlan_id = args.vlan_id
            if ("vlan_id" in args and args.vlan_id is not None
                    and (args.vlan_id < 2 or args.vlan_id > 4094)):
                err = ("Argument: invalid parameter: "
                       "VLAN ID ranges from 2 to 4094")
                self.err_list.append(err)
                raise FailException(*self.err_list)
        if "vlan_priority" in args and args.vlan_priority is not None:
            flag = True
            self.vlan_priority = args.vlan_priority

        if not flag:
            err_info = "Argument: at least one parameter must be specified"
            self.err_list.append(err_info)
            raise FailException(*self.err_list)
