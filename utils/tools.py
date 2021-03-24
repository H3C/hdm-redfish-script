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


import platform
import re
import socket
from subprocess import getstatusoutput


class GlobalVar:
    import_ipmi_lib = True

    @classmethod
    def set_import_ipmi_lib(cls, flag):
        cls.import_ipmi_lib = flag

    @classmethod
    def get_import_ipmi_lib(cls):
        return cls.import_ipmi_lib


def get_os():

    os_platform = platform.system()
    if os_platform == "Windows":
        return "n"
    else:
        return "c"


def ping_ip(ip_str):

    op_ = get_os()
    ip_version = ""
    if ip_str.startswith("[") and ip_str.endswith("]"):
        ip_str = ip_str[1:-1]
        if op_ == "c":
            ip_version = 6
    command = "ping%s -%s 1 %s" % (ip_version, op_, ip_str)
    ret_code, output = getstatusoutput(command)
    return True if ret_code == 0 else False


def init_args(args, self_args):

    for arg in self_args:
        if not hasattr(args, arg):
            setattr(args, arg, None)


def is_domain(domain):

    domain_regex = re.compile(r"^(([a-zA-Z])|([a-zA-Z][a-zA-Z])|(["
                              r"a-zA-Z][0-9])|([0-9][a-zA-Z])|"
                              r"([a-zA-Z0-9][a-zA-Z0-9-_]{1,61}[a-zA-Z0-9]))"
                              r"(.*\.)?.*\.([a-zA-Z]{2,6}|[a-zA-Z0-9-]{2,30}\."
                              r"[a-zA-Z]{2,3})$")

    return (True if (domain_regex.match(domain) and len(domain) <= 255) else
            False)


def is_ipv6(ip):

    try:
        socket.inet_pton(socket.AF_INET6, ip)
    except socket.error:
        return False
    return True


def is_ipv4(ip):

    try:
        socket.inet_pton(socket.AF_INET, ip)
    except AttributeError:
        try:
            socket.inet_aton(ip)
        except socket.error:
            return False
        return ip.count('.') == 3
    except socket.error:
        return False
    return True


def is_mac(mac):

    if re.match(r"^\s*([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\s*$", mac):
        return True
    return False
