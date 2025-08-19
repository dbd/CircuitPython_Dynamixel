# The MIT License (MIT)
#
# Copyright (c) 2025 Derek Daniels
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from dynamixel.protocol import Protocol1, Response
from dynamixel.servo import Servo, paramUnit
from dynamixel import utils
import asyncio


class operatingMode:
    OP_JOINT = [0, 0]
    OP_WHEEL = [1, 1]


class controlTable:
    MODEL_NUMBER = (0, 2)
    FIRMWARE_VERSION = (2, 1)
    ID = (3, 1)
    BAUD = (4, 1)
    RETURN_DELAY_TIME = (5, 1)
    CW_ANGLE_LIMIT = (6, 2)
    CCW_ANGLE_LIMIT = (8, 2)
    TEMPERATURE_LIMIT = (11, 1)
    MIN_VOLTAGE_LIMIT = (12, 1)
    MAX_VOLTAGE_LIMIT = (13, 1)
    MAX_TORQUE = (14, 2)
    STATUS_RETURN_LEVEL = (16, 1)
    ALARM_LED = (17, 1)
    SHUTDOWN = (18, 1)

    TORQUE_ENABLE = (24, 1)
    LED = (25, 1)
    CW_COMPLIANCE_MARGIN = (26, 1)
    CCW_COMPLIANCE_MARGIN = (27, 1)
    CW_COMPLIANCE_SLOPE = (28, 1)
    CCW_COMPLIANCE_SLOPE = (29, 1)
    GOAL_POSITION = (30, 2)
    MOVING_SPEED = (32, 2)
    TORQUE_LIMIT = (34, 2)
    PRESENT_POSITION = (36, 2)
    PRESENT_SPEED = (38, 2)
    PRESENT_LOAD = (40, 2)
    PRESENT_VOLTAGE = (42, 1)
    PRESENT_TEMPERATURE = (43, 1)
    REGISTERED = (44, 1)
    MOVING = (46, 1)
    LOCK = (47, 1)
    PUNCH = (48, 2)


class AX12A(Servo):
    CONTROL_TABLE = controlTable
    PARAM_UNIT = paramUnit
    OPERATING_MODE = operatingMode

    def __init__(self, *args, unit=PARAM_UNIT.UNIT_DEGREE, **kwargs):
        super(AX12A, self).__init__(*args, **kwargs)
        self.protocol = Protocol1(**kwargs)
        self.unit = unit
        self.resolution = 1024
        self.torqueEnabled = False
        self.moving = False
        self.presentPosition = 0

    async def run(self):
        while True:
            res = self.getPresentPosition()
            if (res := self.getPresentPosition()).ok:
                self.presentPosition = res.data

            if (res := self.readControlTableItem(self.CONTROL_TABLE.MOVING)).ok:
                self.moving = bool(res.data)

            if (res := self.readControlTableItem(self.CONTROL_TABLE.TORQUE_ENABLE)).ok:
                self.torqueEnabled = bool(res.data)
            await asyncio.sleep(0.1)

    def ping(self):
        res = self.protocol.ping(self.id)
        return res

    def torqueOn(self) -> Response:
        return self.writeControlTableItem(self.CONTROL_TABLE.TORQUE_ENABLE, 1)

    def torqueOff(self):
        return self.writeControlTableItem(self.CONTROL_TABLE.TORQUE_ENABLE, 0)

    def getBaud(self):
        res = self.readControlTableItem(self.CONTROL_TABLE.BAUD)
        return res

    def getModelNumber(self):
        res = self.readControlTableItem(self.CONTROL_TABLE.BAUD)
        return res

    def setBaudrate(self, baud: int):
        return self.writeControlTableItem(self.CONTROL_TABLE.BAUD, baud)

    def ledOn(self):
        return self.writeControlTableItem(self.CONTROL_TABLE.LED, 1)

    def ledOff(self):
        return self.writeControlTableItem(self.CONTROL_TABLE.LED, 0)

    def setOperationMode(self, operatingMode):
        self.writeControlTableItem(self.CONTROL_TABLE.CW_ANGLE_LIMIT, operatingMode[0])
        return self.writeControlTableItem(
            self.CONTROL_TABLE.CCW_ANGLE_LIMIT, operatingMode[1]
        )

    def convertToNegative(self, value, length):
        if value < 0:
            maxInt = int.from_bytes(bytes([0xFF] * length), "little")
            maxInt += value
            return list(maxInt.to_bytes(length, "little"))

    def convertFromNegative(self, value, length):
        return utils.twosComplement(value, length)

    def setGoalPosition(self, value, unit=None):
        # Need to do a unit conversion
        unit = unit or self.unit
        value = self.convertUnits(value, unit)
        if value < 0:
            value = self.convertToNegative(value, self.CONTROL_TABLE.GOAL_POSITION[1])
        return self.writeControlTableItem(self.CONTROL_TABLE.GOAL_POSITION, value)

    def getPresentPosition(self, unit=None):
        unit = unit or self.unit
        res = self.readControlTableItem(self.CONTROL_TABLE.PRESENT_POSITION)
        data = None
        if res.ok:
            data = self.convertFromNegative(
                res.data, self.CONTROL_TABLE.GOAL_POSITION[1]
            )
            data = self.convertRaw(data, unit)
        return Response(data, res.err)

    def setMaxPosition(self, value, unit=None):
        unit = unit or self.unit
        value = self.convertUnits(value, unit)
        return self.writeControlTableItem(self.CONTROL_TABLE.CW_ANGLE_LIMIT, value)

    def setMinPosition(self, value, unit=None):
        unit = unit or self.unit
        value = self.convertUnits(value, unit)
        return self.writeControlTableItem(self.CONTROL_TABLE.CCW_ANGLE_LIMIT, value)

    def getPositionLimits(self, unit=None):
        unit = unit or self.unit
        maxRes = self.readControlTableItem(self.CONTROL_TABLE.CW_ANGLE_LIMIT)
        minRes = self.readControlTableItem(self.CONTROL_TABLE.CCW_ANGLE_LIMIT)
        if isinstance(maxRes, int):
            maxRes = self.convertRaw(maxRes, unit)
        if isinstance(minRes, int):
            minRes = self.convertRaw(minRes, unit)
        return (minRes, maxRes)

    def setGoalVelocity(self, value):
        return self.writeControlTableItem(self.CONTROL_TABLE.MOVING_SPEED, value)

    def getPresentVelocity(self):
        return self.readControlTableItem(self.CONTROL_TABLE.PRESENT_SPEED)

    def getTorqueEnabled(self):
        return self.readControlTableItem(self.CONTROL_TABLE.TORQUE_ENABLE)
