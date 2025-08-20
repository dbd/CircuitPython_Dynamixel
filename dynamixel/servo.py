# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Derek Daniels
#
# SPDX-License-Identifier: MIT

from collections import namedtuple

from dynamixel.protocol import Protocol1, Protocol2, Response


class units:
    RAW = 0
    PERCENT = 1
    RPM = 2
    DEGREE = 3
    MILLI_AMPERE = 4
    VOLTAGE = 5
    BAUD = 6


class ControlTableItem:
    def __init__(self, address, length, writable, limits=None, defaultUnit=units.RAW):
        self.address = address
        self.length = length
        self.writable = writable
        self.limits = limits
        self.defaultUnit = defaultUnit

    def __iter__(self):
        yield from [self.address, self.length, self.writable, self.limits, self.defaultUnit]


class controlTable:
    @classmethod
    def items(cls):
        """Iterate over all ControlTableItems as (name, ControlTableItem)."""
        for key, val in cls.__dict__.items():
            if isinstance(val, ControlTableItem):
                yield key, val


class Servo:
    CONTROL_TABLE = controlTable
    UNITS = units

    def __init__(self, name: str, servo_id: int, **kwargs):
        self.name = name
        self._id = servo_id
        self.protocol: Protocol1 | Protocol2 = None
        self.resolution = None
        self.bauds = {}
        self._rpm = 1
        _ = kwargs

    def convertUnits(self, raw: int, unit: int) -> int:
        if unit == units.BAUD:
            inverseBauds = {v: k for k, v in self.bauds.items()}
        else:
            inverseBauds = {}

        unitMap = {
            units.DEGREE: lambda raw: int((raw / 360) * self.resolution),
            units.VOLTAGE: lambda raw: int(raw * 10),
            units.BAUD: lambda raw: inverseBauds[raw],
            units.RPM: lambda raw: self._rpm * raw,
        }
        return unitMap.get(unit, lambda raw: raw)(raw)

    def convertRaw(self, raw: int, unit: int) -> int:
        unitMap = {
            units.DEGREE: lambda raw: int((raw / self.resolution) * 360),
            units.VOLTAGE: lambda raw: raw / 10,
            units.BAUD: lambda raw: self.bauds[raw],
            units.RPM: lambda raw: raw / self._rpm,
        }
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

    @classmethod
    def convertToNegative(cls, value, length):
        _ = length
        return value

    @classmethod
    def convertFromNegative(cls, value, length):
        _ = length
        return value
