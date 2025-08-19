# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Derek Daniels
#
# SPDX-License-Identifier: MIT

from dynamixel.protocol import Protocol1, Protocol2, Response


class paramUnit:
    UNIT_RAW = 0
    UNIT_PERCENT = 1
    UNIT_RPM = 2
    UNIT_DEGREE = 3
    UNIT_MILLI_AMPERE = 4


class Servo:
    def __init__(self, name: str, servo_id: int, **kwargs):
        self.name = name
        self.id = servo_id
        self.torque = False
        self.position = None
        self.initial_position = None
        self.protocol: Protocol1 | Protocol2 = None
        self.resolution = None
        self.moving = False
        _ = kwargs

    def convertUnits(self, raw: int, unit: int) -> int:
        unitMap = {
            paramUnit.UNIT_DEGREE: lambda raw: int((raw / 360) * self.resolution)
        }
        return unitMap.get(unit, lambda raw: raw)(raw)

    def convertRaw(self, raw: int, unit: int) -> int:
        unitMap = {
            paramUnit.UNIT_DEGREE: lambda raw: int((raw / self.resolution) * 360)
        }
        return unitMap.get(unit, lambda raw: raw)(raw)

    def read(self, addr: int, length: int) -> Response:
        return self.protocol.read(self.id, addr, length)

    def write(self, message: tuple, *args) -> Response:
        return self.protocol.write(self.id, *message, *args)

    def reboot(self):
        self.protocol.reboot(self.id)

    def clear(self, position: bool = False, error: bool = False):
        if isinstance(self.protocol, Protocol2):
            self.protocol.clear(self.id, position=position, error=error)
        else:
            return "Not supported on Protocol v1.0"

    def ping(self) -> Response:
        return Response(None, "Not implemented")

    def torqueOn(self) -> Response:
        return Response(None, "Not implemented")

    def torqueOff(self) -> Response:
        return Response(None, "Not implemented")

    def getBaud(self) -> Response:
        return Response(None, "Not implemented")

    def setModelNumber(self) -> Response:
        return Response(None, "Not implemented")

    def getModelNumber(self) -> Response:
        return Response(None, "Not implemented")

    def setProtocol(self) -> Response:
        return Response(None, "Not implemented")

    def setBaudrate(self, baud: int) -> Response:
        return Response(None, "Not implemented")

    def ledOn(self) -> Response:
        return Response(None, "Not implemented")

    def ledOff(self) -> Response:
        return Response(None, "Not implemented")

    def setOperationMode(self, operatingMode) -> Response:
        return Response(None, "Not implemented")

    def setGoalPosition(self, value, unit=None) -> Response:
        return Response(None, "Not implemented")

    def getPresentPosition(self, unit=None) -> Response:
        return Response(None, "Not implemented")

    def setGoalVelocity(self, value) -> Response:
        return Response(None, "Not implemented")

    def getPresentVelocity(self) -> Response:
        return Response(None, "Not implemented")

    def setGoalPwm(self, value) -> Response:
        return Response(None, "Not implemented")

    def getPresentPwm(self) -> Response:
        return Response(None, "Not implemented")

    def setGoalCurrent(self) -> Response:
        return Response(None, "Not implemented")

    def getPresentCurrent(self) -> Response:
        return Response(None, "Not implemented")

    def readControlTableItem(self, item) -> Response:
        if not isinstance(item, tuple):
            return Response(None, f"readControlTableItem takes a tuple, got {item}")
        return self.read(*item)

    def writeControlTableItem(self, item, data) -> Response:
        if not isinstance(item, tuple):
            return Response(None, f"writeControlTableItem takes a tuple, got {item}")
        return self.write(item, data)
