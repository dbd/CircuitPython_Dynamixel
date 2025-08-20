# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Derek Daniels
#
# SPDX-License-Identifier: MIT

import asyncio

from dynamixel import utils
from dynamixel.protocol import Protocol2, Response
from dynamixel.servo import ControlTableItem, Servo, controlTable, paramUnit


class operatingMode:
    OP_VELOCITY = 1
    OP_POSITION = 3
    OP_EXTENDED_POSITION = 4
    OP_PWM = 16


class ControlTable(controlTable):
    MODEL_NUMBER = ControlTableItem(0, 2, False)
    MODEL_INFORMATION = ControlTableItem(2, 4, False)
    FIRMWARE_VERSION = ControlTableItem(6, 1, False)
    ID = ControlTableItem(7, 1, True)
    BAUD = ControlTableItem(8, 1, True)
    RETURN_DELAY_TIME = ControlTableItem(9, 1, True)
    DRIVE_MODE = ControlTableItem(10, 1, True)
    OPERATING_MODE = ControlTableItem(11, 1, True)
    SECONDARY_SHADOW_ID = ControlTableItem(12, 1, True)
    PROTOCOL_TYPE = ControlTableItem(13, 1, True)
    HOMING_OFFSET = ControlTableItem(20, 4, True)
    MOVING_THRESHOLD = ControlTableItem(24, 4, True)
    TEMPERATURE_LIMIT = ControlTableItem(31, 1, True)
    MAX_VOLTAGE_LIMIT = ControlTableItem(32, 2, True)
    MIN_VOLTAGE_LIMIT = ControlTableItem(34, 2, True)
    PWM_LIMIT = ControlTableItem(36, 2, True)
    VELOCITY_LIMIT = ControlTableItem(44, 4, True)
    MAX_POSITION_LIMIT = ControlTableItem(48, 4, True)
    MIN_POSITION_LIMIT = ControlTableItem(52, 4, True)
    STARTUP_CONFIGURATION = ControlTableItem(60, 1, True)
    SHUTDOWN = ControlTableItem(63, 1, True)
    TORQUE_ENABLE = ControlTableItem(64, 1, True)
    LED = ControlTableItem(65, 1, True)
    STATUS_RETURN_LEVEL = ControlTableItem(68, 1, True)
    REGISTERED_INSTRUCTION = ControlTableItem(69, 1, False)
    HARDWARE_ERROR_STATUS = ControlTableItem(70, 1, False)
    VELOCITY_I_GAIN = ControlTableItem(76, 2, True)
    VELOCITY_P_GAIN = ControlTableItem(78, 2, True)
    POSITION_D_GAIN = ControlTableItem(80, 2, True)
    POSITION_I_GAIN = ControlTableItem(82, 2, True)
    POSITION_P_GAIN = ControlTableItem(84, 2, True)
    FEEDFORWARD_2ND_GAIN = ControlTableItem(88, 2, True)
    FEEDFORWARD_1ST_GAIN = ControlTableItem(90, 2, True)
    BUS_WATCHDOG = ControlTableItem(98, 1, True)
    GOAL_PWM = ControlTableItem(100, 2, True)
    GOAL_VELOCITY = ControlTableItem(104, 4, True)
    PROFILE_ACCELERATION = ControlTableItem(108, 4, True)
    PROFILE_VELOCITY = ControlTableItem(112, 4, True)
    GOAL_POSITION = ControlTableItem(116, 4, True)
    REALTIME_TICK = ControlTableItem(120, 2, False)
    MOVING = ControlTableItem(122, 1, False)
    MOVING_STATUS = ControlTableItem(123, 1, False)
    PRESENT_PWM = ControlTableItem(124, 2, False)
    PRESENT_LOAD = ControlTableItem(126, 2, False)
    PRESENT_VELOCITY = ControlTableItem(128, 4, False)
    PRESENT_POSITION = ControlTableItem(132, 4, False)
    VELOCITY_TRAJECTORY = ControlTableItem(136, 4, False)
    POSITION_TRAJECTORY = ControlTableItem(140, 4, False)
    PRESENT_INPUT_VOLTAGE = ControlTableItem(144, 2, False)
    PRESENT_TEMPERATURE = ControlTableItem(146, 1, False)
    BACKUP_READY = ControlTableItem(147, 1, False)


def convertToNegative(value, length):
    if value < 0:
        maxInt = int.from_bytes(bytes([0xFF] * length), "little")
        maxInt += value
        return list(maxInt.to_bytes(length, "little"))


def convertFromNegative(value, length):
    return utils.twosComplement(value, length)


class XL430_W250_T(Servo):
    CONTROL_TABLE = ControlTable
    PARAM_UNIT = paramUnit
    OPERATING_MODE = operatingMode

    def __init__(self, *args, unit=PARAM_UNIT.UNIT_DEGREE, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit = unit
        self.protocol = Protocol2(**kwargs)
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
        if not isinstance(self.protocol, Protocol2):
            return
        self.protocol.clear(self.id, position=position, error=error)
