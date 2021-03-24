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

UNIT_TYPE = [
    " ", "&deg;C", "&deg;F", "&deg;K", "V", "A", "W", "Joules", "Coulombs",
    "VA", "Nits", "lumen", "lux", "Candela", "kPa", "PSI", "Newton", "CFM",
    "RPM", "Hz", "microsecond", "millisecond", "second", "minute", "hour",
    "day", "week", "mil", "inches", "feet", "cu in", "cu feet", "mm", "cm", "m",
    "cu cm", "cu m", "liters", "fluid ounce", "radians", "steradians",
    "revolutions", "cycles", "gravities", "ounce", "pound", "ft-lb", "oz-in",
    "gauss", "gilberts", "henry", "millihenry", "farad", "microfarad", "ohms",
    "becquerel", "PPM (parts /million)", " ", "Decibels", "DbA", "DbC", "gray",
    "sievert", "color temp &deg;K", "bit", "kilobit", "megabit", "gigabit",
    "byte", "kilobyte", "megabyte", "gigabyte", "word (data)", "dword", "qword",
    "line", "hit", "miss", "retry", "reset", "overrun/overflow", "underrun",
    "collision", "packets", "messages", "characters", "error",
    "correctable error", "uncorrectable error"
]


class Sensor:

    def __init__(self):

        self.sensor_number = None
        self.name = None
        self.type = None
        self.reading = None
        self.unit = None
        self.sensor_state = None
        self.higher_non_critical_threshold = None
        self.higher_critical_threshold = None
        self.higher_non_recoverable_threshold = None
        self.lower_non_critical_threshold = None
        self.lower_critical_threshold = None
        self.lower_non_recoverable_threshold = None

    @property
    def dict(self):

        return {
            "SensorNumber": self.sensor_number,
            "SensorName": self.name,
            "SensorType": self.type,
            "Reading": self.reading,
            "Unit": self.unit,
            "Status": self.sensor_state,
            "unr": self.higher_non_critical_threshold,
            "uc": self.higher_critical_threshold,
            "unc": self.higher_non_recoverable_threshold,
            "lnc": self.lower_non_critical_threshold,
            "lc": self.lower_critical_threshold,
            "lnr": self.lower_non_recoverable_threshold,
        }


class GetSensor(BaseModule):

    def __init__(self):
        super().__init__()
        self.sensors = []
        self.maximum = None

    @property
    def dict(self):

        return {
            "Maximum": self.maximum,
            "Sensor": self.sensors
        }

    def run(self, args):

        client = RestfulClient(args)
        try:
            restful_sensor = self.get_hardware_sensor(client)
            if restful_sensor:
                self.sensors = pack_sensor_resource(restful_sensor)
        finally:
            if client.cookie:
                client.delete_session()
        return self.suc_list

    def get_hardware_sensor(self, client):

        url = "/api/sensors"
        resp = client.send_request("GET", url)
        if isinstance(resp, list):
            if not resp:
                self.suc_list.append("Success: sensor resource is empty")
            else:
                self.maximum = len(resp)
        else:
            self.err_list.extend(client.err_message)
            self.err_list.append("Failure: failed to get Sensor collection")
            raise FailException(*self.err_list)
        return resp


def pack_sensor_resource(sensors):

    sensor_list = list()
    for sensor in sensors:
        detail = dict()
        detail["sensor_number"] = sensor.get("sensor_number")
        detail["name"] = sensor.get("name")
        detail["type"] = sensor.get("type")
        detail["reading"] = sensor.get("reading")
        try:
            detail["unit"] = UNIT_TYPE[sensor.get("unit")]
        except (IndexError, TypeError):
            detail["unit"] = "unknown"
        detail["sensor_state"] = sensor.get("sensor_state")
        detail["higher_non_critical_threshold"] = (sensor.get(
            "higher_non_critical_threshold"))
        detail["higher_critical_threshold"] = (sensor.get(
            "higher_critical_threshold"))
        detail["higher_non_recoverable_threshold"] = (sensor.get(
            "higher_non_recoverable_threshold"))
        detail["lower_non_critical_threshold"] = (sensor.get(
            "lower_non_critical_threshold"))
        detail["lower_critical_threshold"] = (sensor.get(
            "lower_critical_threshold"))
        detail["lower_non_recoverable_threshold"] = (sensor.get(
            "lower_non_recoverable_threshold"))
        s_d = Sensor()
        s_d.__dict__.update(detail)
        sensor_list.append(s_d)
    return sensor_list
