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

from dynamixel.protocol import Protocol2, Response
from dynamixel.servo import Servo, paramUnit
from dynamixel import utils
import asyncio


class operatingMode:
    OP_VELOCITY = 1
    OP_POSITION = 3
    OP_EXTENDED_POSITION = 4
    OP_PWM = 16


class controlTable:
    MODEL_NUMBER = (0, 2)
    MODEL_INFORMATION = (2, 4)
    FIRMWARE_VERSION = (6, 1)
    ID = (7, 1)
    BAUD = (8, 1)
    RETURN_DELAY_TIME = (9, 1)
    DRIVE_MODE = (10, 1)
    OPERATING_MODE = (11, 1)
    SECONDARY_SHADO = (12, 1)
    PROTOCOL_TYPE = (13, 1)
    HOMING_OFFSET = (20, 4)
    MOVING_THRESHOLD = (24, 4)
    TEMPERATURE_LIMIT = (31, 1)
    MAX_VOLTAGE_LIMIT = (32, 2)
    MIN_VOLTAGE_LIMIT = (34, 2)
    PWM_LIMIT = (36, 2)
    VELOCITY_LIMIT = (44, 4)
    MAX_POSITION_LIMIT = (48, 4)
    MIN_POSITION_LIMIT = (52, 4)
    STARTUP_CONFIGURATION = (60, 1)
    SHUTDOWN = (63, 1)
    TORQUE_ENABLE = (64, 1)
    LED = (65, 1)
    STATUS_RETURN_LEVEL = (68, 1)
    REGISTERED_INSTRUCTION = (69, 1)
    HARDWARE_ERROR_STATUS = (70, 1)
    VELOCITY_I_GAIN = (76, 2)
    VELOCITY_P_GAIN = (78, 2)
    POSITION_D_GAIN = (80, 2)
    POSITION_I_GAIN = (82, 2)
    POSITION_P_GAIN = (84, 2)
    FEEDFORWARD_2ND_GAIN = (88, 2)
    FEEDFORWARD_1ST_GAIN = (90, 2)
    BUS_WATCHDOG = (98, 1)
    GOAL_PWM = (100, 2)
    GOAL_VELOCITY = (104, 4)
    PROFILE_ACCELERATION = (108, 4)
    PROFILE_VELOCITY = (112, 4)
    GOAL_POSITION = (116, 4)
    REALTIME_TICK = (120, 2)
    MOVING = (122, 1)
    MOVING_STATUS = (123, 1)
    PRESENT_PWM = (124, 2)
    PRESENT_LOAD = (126, 2)
    PRESENT_VELOCITY = (128, 4)
    PRESENT_POSITION = (132, 4)
    VELOCITY_TRAJECTORY = (136, 4)
    POSITION_TRAJECTORY = (140, 4)
    PRESENT_INPUT_VOLTAGE = (144, 2)
    PRESENT_TEMPERATURE = (146, 1)
    BACKUP_READY = (147, 1)


class XL430_W250_T(Servo):
    CONTROL_TABLE = controlTable
    PARAM_UNIT = paramUnit
    OPERATING_MODE = operatingMode

    def __init__(self, *args, unit=PARAM_UNIT.UNIT_DEGREE, **kwargs):
        super(XL430_W250_T, self).__init__(*args, **kwargs)
        self.unit = unit
        self.protocol: Protocol2 = Protocol2(**kwargs)
        self.resolution = 4096
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

    def clear(self, position: bool = False, error: bool = False):
        self.protocol.clear(self.id, position=position, error=error)

    def setProtocolVersion(self, protocol):
        return self.writeControlTableItem(self.CONTROL_TABLE.PROTOCOL_TYPE, protocol)

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
        return self.writeControlTableItem(
            self.CONTROL_TABLE.OPERATING_MODE, operatingMode
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
        return self.writeControlTableItem(self.CONTROL_TABLE.MAX_POSITION_LIMIT, value)

    def setMinPosition(self, value, unit=None):
        unit = unit or self.unit
        value = self.convertUnits(value, unit)
        return self.writeControlTableItem(self.CONTROL_TABLE.MIN_POSITION_LIMIT, value)

    def getPositionLimits(self, unit=None):
        unit = unit or self.unit
        maxRes = self.readControlTableItem(self.CONTROL_TABLE.MAX_POSITION_LIMIT)
        minRes = self.readControlTableItem(self.CONTROL_TABLE.MIN_POSITION_LIMIT)
        if isinstance(maxRes, int):
            maxRes = self.convertRaw(maxRes, unit)
        if isinstance(minRes, int):
            minRes = self.convertRaw(minRes, unit)
        return (minRes, maxRes)

    def setGoalVelocity(self, value):
        return self.writeControlTableItem(self.CONTROL_TABLE.GOAL_VELOCITY, value)

    def getPresentVelocity(self):
        return self.readControlTableItem(self.CONTROL_TABLE.PRESENT_VELOCITY)

    def setGoalPwm(self, value):
        return self.writeControlTableItem(self.CONTROL_TABLE.GOAL_PWM, value)

    def getPresentPwm(self):
        return self.readControlTableItem(self.CONTROL_TABLE.PRESENT_PWM)

    def getTorqueEnabled(self):
        return self.readControlTableItem(self.CONTROL_TABLE.TORQUE_ENABLE)
