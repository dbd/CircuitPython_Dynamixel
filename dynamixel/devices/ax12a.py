# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Derek Daniels
#
# SPDX-License-Identifier: MIT

import asyncio

from dynamixel import utils
from dynamixel.protocol import Protocol1, Response
from dynamixel.servo import ControlTableItem, Servo, controlTable, paramUnit


class operatingMode:
    OP_JOINT = [0, 0]
    OP_WHEEL = [1, 1]


class ControlTable(controlTable):
    MODEL_NUMBER = ControlTableItem(0, 2, False)
    FIRMWARE_VERSION = ControlTableItem(2, 1, False)
    ID = ControlTableItem(3, 1, True)
    BAUD = ControlTableItem(4, 1, True)
    RETURN_DELAY_TIME = ControlTableItem(5, 1, True)
    CW_ANGLE_LIMIT = ControlTableItem(6, 2, True)
    CCW_ANGLE_LIMIT = ControlTableItem(8, 2, True)
    TEMPERATURE_LIMIT = ControlTableItem(11, 1, True)
    MIN_VOLTAGE_LIMIT = ControlTableItem(12, 1, True)
    MAX_VOLTAGE_LIMIT = ControlTableItem(13, 1, True)
    MAX_TORQUE = ControlTableItem(14, 2, True)
    STATUS_RETURN_LEVEL = ControlTableItem(16, 1, True)
    ALARM_LED = ControlTableItem(17, 1, True)
    SHUTDOWN = ControlTableItem(18, 1, True)

    TORQUE_ENABLE = ControlTableItem(24, 1, True)
    LED = ControlTableItem(25, 1, True)
    CW_COMPLIANCE_MARGIN = ControlTableItem(26, 1, True)
    CCW_COMPLIANCE_MARGIN = ControlTableItem(27, 1, True)
    CW_COMPLIANCE_SLOPE = ControlTableItem(28, 1, True)
    CCW_COMPLIANCE_SLOPE = ControlTableItem(29, 1, True)
    GOAL_POSITION = ControlTableItem(30, 2, True)
    MOVING_SPEED = ControlTableItem(32, 2, True)
    TORQUE_LIMIT = ControlTableItem(34, 2, True)
    PRESENT_POSITION = ControlTableItem(36, 2, False)
    PRESENT_SPEED = ControlTableItem(38, 2, False)
    PRESENT_LOAD = ControlTableItem(40, 2, False)
    PRESENT_VOLTAGE = ControlTableItem(42, 1, False)
    PRESENT_TEMPERATURE = ControlTableItem(43, 1, False)
    REGISTERED = ControlTableItem(44, 1, False)
    MOVING = ControlTableItem(46, 1, False)
    LOCK = ControlTableItem(47, 1, True)
    PUNCH = ControlTableItem(48, 2, True)


class AX12A(Servo):
    CONTROL_TABLE = ControlTable
    PARAM_UNIT = paramUnit
    OPERATING_MODE = operatingMode

    def __init__(self, *args, unit=PARAM_UNIT.UNIT_DEGREE, **kwargs):
        super().__init__(*args, **kwargs)
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
