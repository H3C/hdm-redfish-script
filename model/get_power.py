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


import re
from exception.ToolException import FailException
from utils.client import RestfulClient
from utils.model import BaseModule


class Power:

    def __init__(self):

        self.name = None
        self.sensor_number = None
        self.reading = None

    @property
    def dict(self):

        return {
            "Name": self.name,
            "SensorNumber": self.sensor_number,
            "ReadingWatt": self.reading
        }


class GetPower(BaseModule):

    def __init__(self):

        super().__init__()
        self.power = []

    @property
    def dict(self):

        return {
            "Power": self.power
        }

    def run(self, args):

        client = RestfulClient(args)
        url = "/api/sensors"
        try:
            resp = client.send_request("GET", url)
            psu_sensor = (self.package_results(list(filter(is_power_sensor,
                                                           resp))))
            self.power = psu_sensor
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def package_results(self, resp):

        sensors = resp
        try:
            sensors = sorted(sensors, key=lambda s: s["sensor_number"])
        except KeyError as err:
            self.err_list.append(str(err))
            raise FailException(*self.err_list)
        sensor_list = list()
        for sensor in sensors:
            detail = dict()
            detail["name"] = sensor.get("name", None)
            detail["sensor_number"] = sensor.get("sensor_number", None)
            detail["reading"] = sensor.get("reading", None)
            power = Power()
            power.__dict__.update(detail)
            sensor_list.append(power)
        return sensor_list


def is_power_sensor(sensor_dict):

    if (sensor_dict.get("name") is not None and
            re.match(r"PSU\d*_PIN$", sensor_dict["name"])):
        return True
    return False
