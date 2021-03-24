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
from utils.client import RestfulClient
from utils.common import Constant
from utils.model import BaseModule
from utils.tools import init_args
from utils import globalvar
from utils.predo import GetVersion


class Ipv4Address:

    def __init__(self):
        self.address_origin = None
        self.address = None
        self.subnet_mask = None
        self.gate_way = None

    @property
    def dict(self):

        return {
            "AddressOrigin": self.address_origin,
            "Address": self.address,
            "SubnetMask": self.subnet_mask,
            "Gateway": self.gate_way
        }

    def pack_ip_address(self, resp):

        self.address_origin = resp.get("AddressOrigin", None)
        self.address = resp.get("Address", None)
        self.subnet_mask = resp.get("SubnetMask", None)
        self.gate_way = resp.get("Gateway", None)


class Ipv6Address:

    def __init__(self):
        self.address_origin = None
        self.address = None
        self.prefix_length = None
        self.ipv6_default_gateway = None

    @property
    def dict(self):

        return {
            "AddressOrigin": self.address_origin,
            "Address": self.address,
            "PrefixLength": self.prefix_length,
            "IPv6DefaultGateway": self.ipv6_default_gateway
        }

    def pack_ip_address(self, resp):

        self.address_origin = resp.get("AddressOrigin", None)
        self.address = resp.get("Address", None)
        self.prefix_length = resp.get("PrefixLength", None)
        self.ipv6_default_gateway = resp.get("IPv6DefaultGateway", None)


class GetIp(BaseModule):

    def __init__(self):
        super().__init__()
        self.args_lst = ["network_port_id"]
        self.ip_version = "IPv4andIPv6"
        self.permanent_mac_address = None
        self.ipv4_addresses = []
        self.ipv6_addresses = []
        self.vlan_enable_str = None
        self.vlan_id = None

        self.id = None
        self.name = None
        self.description = None
        self.auto_neg = None
        self.fqdn = None
        self.full_duplex = None
        self.host_name = None
        self.mac_address = None
        self.ipv6_default_gateway = None
        self.interface_enabled = None
        self.mtu_size = None
        self.max_ipv6_static_addresses = None
        self.name_servers = None
        self.speed_mbps = None
        self.health = None
        self.state = None

        self.vlan_enable = None

    @property
    def dict(self):

        return {
            "IPVersion": self.ip_version,
            "PermanentMACAddress": self.permanent_mac_address,
            "IPv4Addresses": self.ipv4_addresses,
            "IPv6Addresses": self.ipv6_addresses,
            "VLANEnableStr": self.vlan_enable_str,
            "VLANId": self.vlan_id,
            "Id": self.id,
            "Name": self.name,
            "Description": self.description,
            "AutoNeg": self.auto_neg,
            "FQDN": self.fqdn,
            "FullDuplex": self.full_duplex,
            "HostName": self.host_name,
            "MACAddress": self.mac_address,
            "IPv6DefaultGateway": self.ipv6_default_gateway,
            "InterfaceEnabled": self.interface_enabled,
            "MTUSize": self.mtu_size,
            "MaxIPv6StaticAddresses": self.max_ipv6_static_addresses,
            "NameServers": self.name_servers,
            "SpeedMbps": self.speed_mbps,
            "Health": self.health,
            "State": self.state,
            "VLANEnable": self.vlan_enable
        }

    @GetVersion()
    def run(self, args):

        init_args(args, self.args_lst)
        is_adapt_b01 = globalvar.IS_ADAPT_B01
        if is_adapt_b01:
            client = RestfulClient(args)
            try:
                url = "/api/settings/network"
                resp = client.send_request("GET", url)
                if args.network_port_id is not None:
                    if isinstance(resp, list):
                        data = self._choose_port_resp(args, resp)
                        if data is not None:
                            self._pack_b01_ip_resource(data)
                            return self.suc_list
                    else:
                        err_info = "Failure: failed to get the ip info"
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
                else:
                    if isinstance(resp, list):
                        data = self._check_b01_resp(args, resp)
                        if data is not None:
                            self._pack_b01_ip_resource(data)
                            return self.suc_list
                    else:
                        err_info = "Failure: failed to get the ip info"
                        self.err_list.append(err_info)
                        raise FailException(*self.err_list)
            finally:
                if client.cookie:
                    client.delete_session()
        else:
            client = RedfishClient(args)
            systems_id = client.get_systems_id()
            url = "/redfish/v1/Managers/%s/EthernetInterfaces" % systems_id
            if args.network_port_id is not None:
                url = ("/redfish/v1/Managers/%s/EthernetInterfaces/%s" %
                       (systems_id, args.network_port_id))
                resp = client.send_request("GET", url)
                if (isinstance(resp, dict) and
                        resp.get("status_code", None) in Constant.SUC_CODE):
                    self._pack_ip_resource(resp["resource"])
                else:
                    self.err_list.append("Failure: failed to get ip "
                                         "information")
                    raise FailException(*self.err_list)
            else:
                resp = client.send_request("GET", url)
                if (isinstance(resp, dict) and
                        resp.get("status_code", None) in Constant.SUC_CODE):
                    eth_list = resp["resource"]["Members"]
                    for eth in eth_list:
                        url = eth.get("@odata.id", None)
                        resp = client.send_request("GET", url)
                        if self._check_resp(args, resp):
                            self._pack_ip_resource(resp["resource"])
                            return self.suc_list
                    else:
                        self.err_list.append("Failure: failed to "
                                             "get ip information")
                        raise FailException(*self.err_list)
                else:
                    self.err_list.append("Failure: failed to get network port "
                                         "collection information!")
                    raise FailException(*self.err_list)

        return self.suc_list

    @staticmethod
    def _check_resp(args, resp):

        flag = False
        if (isinstance(resp, dict) and
                resp.get("status_code", None) in Constant.SUC_CODE and
                resp["resource"].get("InterfaceEnabled", None) is True and
                resp["resource"].get("IPv4Addresses", None) is not None and
                resp["resource"].get("IPv6Addresses", None) is not None):
            ipv4_list = resp["resource"]["IPv4Addresses"]
            ipv6_list = resp["resource"]["IPv6Addresses"]
            for ipv4 in ipv4_list:
                if ipv4.get("Address") == args.host:
                    flag = True
                    break
            if not flag:
                for ipv6 in ipv6_list:
                    if (args.host.startswith("[") and args.host.endswith("]")
                            and ipv6.get("Address") == args.host[1:-1]):
                        flag = True
                        break
        return flag

    @staticmethod
    def _choose_port_resp(args, resp):

        if isinstance(resp, list):
            for info in resp:
                if info.get("interface_name") == args.network_port_id:
                    return info
        return dict()

    @staticmethod
    def _check_b01_resp(args, resp):

        if isinstance(resp, list):
            for info in resp:
                if info.get("ipv4_address") == args.host:
                    return info
                if (args.host.startswith("[") and args.host.endswith("]")
                        and info.get("ipv6_address") == args.host[1:-1]):
                    return info
        return list()

    def _pack_ip_resource(self, resp):

        self.permanent_mac_address = resp.get("PermanentMACAddress", None)
        if resp.get("IPv4Addresses", None) is not None:
            ipv4_addresses = resp["IPv4Addresses"]
            for ipv4 in ipv4_addresses:
                ipv4_address = Ipv4Address()
                ipv4_address.pack_ip_address(ipv4)
                self.ipv4_addresses.append(ipv4_address)
        if resp.get("IPv6Addresses", None) is not None:
            ipv6_addresses = resp["IPv6Addresses"]
            for ipv6 in ipv6_addresses:
                ipv6["IPv6DefaultGateway"] = resp.get("IPv6DefaultGateway",
                                                      None)
                ipv6_address = Ipv6Address()
                ipv6_address.pack_ip_address(ipv6)
                self.ipv6_addresses.append(ipv6_address)
        if resp.get("VLAN", None):
            self.vlan_enable = resp["VLAN"].get("VLANEnable", None)
            self.vlan_enable_str = (
                "Enabled" if resp["VLAN"].get("VLANEnable",
                                              None) else "Disabled")
            self.vlan_id = resp["VLAN"].get("VLANId", None)

        self.id = resp.get("Id", None)
        self.name = resp.get("Name", None)
        self.description = resp.get("Description", None)
        self.auto_neg = resp.get("AutoNeg", None)
        self.fqdn = resp.get("FQDN", None)
        self.full_duplex = resp.get("FullDuplex", None)
        self.host_name = resp.get("HostName", None)
        self.mac_address = resp.get("MACAddress", None)
        self.ipv6_default_gateway = resp.get("IPv6DefaultGateway", None)
        self.interface_enabled = resp.get("InterfaceEnabled", None)
        self.mtu_size = resp.get("MTUSize", None)
        self.max_ipv6_static_addresses = resp.get('MaxIPv6StaticAddresses',
                                                  None)
        name_servers = resp.get("NameServers", None)
        if name_servers is not None:
            self.name_servers = ", ".join(name_servers)
        self.speed_mbps = resp.get("SpeedMbps", None)
        if resp.get("Status", None):
            self.health = resp["Status"].get("Health", None)
            self.state = resp["Status"].get("State", None)

    def _pack_b01_ip_resource(self, resp):

        ipv4_address_origin_dict = {
            1: "DHCPv4",
            0: "Static"
        }
        ipv6_address_origin_dict = {
            1: "DHCPv6",
            0: "Static"
        }
        vlan_state_dict = {
            1: "Enable",
            0: "Disabled"
        }
        self.mac_address = resp.get("mac_address", None)
        if resp.get("ipv4_address", None) is not None:
            ipv4_address = Ipv4Address()
            ipv4_address.address = resp.get("ipv4_address", None)
            ipv4_address.address_origin = ipv4_address_origin_dict.get(
                resp.get("ipv4_dhcp_enable"), None)
            ipv4_address.subnet_mask = resp.get("ipv4_subnet", None)
            ipv4_address.gate_way = resp.get("ipv4_gateway", None)
            self.ipv4_addresses.append(ipv4_address)
        if resp.get("ipv6_address", None) is not None:
            ipv6_address = Ipv6Address()
            ipv6_address.address = resp.get("ipv6_address", None)
            ipv6_address.address_origin = ipv6_address_origin_dict.get(
                resp.get("ipv6_dhcp_enable"), None)
            ipv6_address.ipv6_default_gateway = resp.get("ipv6_gateway", None)
            ipv6_address.prefix_length = resp.get("ipv6_prefix", None)
            self.ipv6_addresses.append(ipv6_address)
        if resp.get("ipv6_localLinkAddress", None) is not None:
            ipv6_address = Ipv6Address()
            ipv6_address.address = resp.get("ipv6_localLinkAddress", None)
            ipv6_address.address_origin = "LinkLocal"
            ipv6_address.ipv6_default_gateway = resp.get("ipv6_gateway", None)
            ipv6_address.prefix_length = resp.get("ipv6_prefix", None)
            self.ipv6_addresses.append(ipv6_address)
        if resp.get("ipv6_StatelessAddress", None) is not None:
            ipv6_address = Ipv6Address()
            ipv6_address.address = resp.get("ipv6_StatelessAddress", None)
            ipv6_address.address_origin = "StatelessAddress"
            ipv6_address.ipv6_default_gateway = resp.get("ipv6_gateway", None)
            ipv6_address.prefix_length = resp.get("ipv6_prefix", None)
            self.ipv6_addresses.append(ipv6_address)
        self.vlan_enable_str = vlan_state_dict.get(
            resp.get("vlan_enable"), None)
        self.vlan_id = resp.get("vlan_id", None)
