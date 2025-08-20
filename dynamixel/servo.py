# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Derek Daniels
#
# SPDX-License-Identifier: MIT

from collections import namedtuple

from dynamixel.protocol import Protocol1, Protocol2, Response


class paramUnit:
    UNIT_RAW = 0
    UNIT_PERCENT = 1
    UNIT_RPM = 2
    UNIT_DEGREE = 3
    UNIT_MILLI_AMPERE = 4


ControlTableItem = namedtuple("ControlTableItem", ["address", "length", "writable"])


class controlTable:
    @classmethod
    def items(cls):
        """Iterate over all ControlTableItems as (name, ControlTableItem)."""
        for key, val in cls.__dict__.items():
            if isinstance(val, ControlTableItem):
                yield key, val


class Servo:
    CONTROL_TABLE = controlTable

    def __init__(self, name: str, servo_id: int, **kwargs):
        self.name = name
        self._id = servo_id
        self.protocol: Protocol1 | Protocol2 = None
        self.resolution = None
        _ = kwargs

    def convertUnits(self, raw: int, unit: int) -> int:
        unitMap = {paramUnit.UNIT_DEGREE: lambda raw: int((raw / 360) * self.resolution)}
        return unitMap.get(unit, lambda raw: raw)(raw)

    def convertRaw(self, raw: int, unit: int) -> int:
        unitMap = {paramUnit.UNIT_DEGREE: lambda raw: int((raw / self.resolution) * 360)}
        return unitMap.get(unit, lambda raw: raw)(raw)

    def read(self, address: int, length: int) -> Response:
        return self.protocol.read(self._id, address, length)

    def write(self, address: int, length: int, *args) -> Response:
        return self.protocol.write(self._id, address, length, *args)

    def reboot(self):
        self.protocol.reboot(self._id)

    def clear(self, position: bool = False, error: bool = False):
        if isinstance(self.protocol, Protocol2):
            self.protocol.clear(self._id, position=position, error=error)
        else:
            return "Not supported on Protocol v1.0"

    def ping(self):
        res = self.protocol.ping(self._id)
        return res

    def readControlTableItem(self, address, size) -> Response:
        return self.read(address, size)

    def writeControlTableItem(self, address, size, data) -> Response:
        return self.write(address, size, data)

    def ping(self):
        res = self.protocol.ping(self.id)
        return res
