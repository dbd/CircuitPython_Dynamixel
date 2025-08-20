# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Derek Daniels
#
# SPDX-License-Identifier: MIT

import asyncio

from dynamixel import utils
from dynamixel.protocol import Protocol2, Response
from dynamixel.servo import ControlTableItem, Servo, controlTable, units


class operatingMode:
    OP_VELOCITY = 1
    OP_POSITION = 3
    OP_EXTENDED_POSITION = 4
    OP_PWM = 16


class ControlTable(controlTable):
    MODEL_NUMBER = ControlTableItem(0, 2, False)
    MODEL_INFORMATION = ControlTableItem(2, 4, False)
    FIRMWARE_VERSION = ControlTableItem(6, 1, False)
    ID = ControlTableItem(7, 1, True, (0, 252))
    BAUD = ControlTableItem(8, 1, True, (0, 7), units.BAUD)
    RETURN_DELAY_TIME = ControlTableItem(9, 1, True, (0, 254))
    DRIVE_MODE = ControlTableItem(10, 1, True, (0, 13))
    OPERATING_MODE = ControlTableItem(11, 1, True, [1, 3, 4, 16])
    SECONDARY_SHADOW_ID = ControlTableItem(12, 1, True, (0, 255))
    PROTOCOL_TYPE = ControlTableItem(13, 1, True, [1, 2])
    HOMING_OFFSET = ControlTableItem(20, 4, True, (-1044479, 1044479))
    MOVING_THRESHOLD = ControlTableItem(24, 4, True, (0, 1023))
    TEMPERATURE_LIMIT = ControlTableItem(31, 1, True, (0, 100))
    MAX_VOLTAGE_LIMIT = ControlTableItem(32, 2, True, (65, 140), units.VOLTAGE)
    MIN_VOLTAGE_LIMIT = ControlTableItem(34, 2, True, (65, 140), units.VOLTAGE)
    PWM_LIMIT = ControlTableItem(36, 2, True, (0, 885))
    VELOCITY_LIMIT = ControlTableItem(44, 4, True, (0, 1024), units.RPM)
    MAX_POSITION_LIMIT = ControlTableItem(48, 4, True, (0, 4095))
    MIN_POSITION_LIMIT = ControlTableItem(52, 4, True, (0, 4095))
    STARTUP_CONFIGURATION = ControlTableItem(60, 1, True)
    SHUTDOWN = ControlTableItem(63, 1, True)

    TORQUE_ENABLE = ControlTableItem(64, 1, True, [0, 1])
    LED = ControlTableItem(65, 1, True, [0, 1])
    STATUS_RETURN_LEVEL = ControlTableItem(68, 1, True, [0, 1, 2])
    REGISTERED_INSTRUCTION = ControlTableItem(69, 1, False, [0, 1])
    HARDWARE_ERROR_STATUS = ControlTableItem(70, 1, False)
    VELOCITY_I_GAIN = ControlTableItem(76, 2, True, (0, 16383))
    VELOCITY_P_GAIN = ControlTableItem(78, 2, True, (0, 16383))
    POSITION_D_GAIN = ControlTableItem(80, 2, True, (0, 16383))
    POSITION_I_GAIN = ControlTableItem(82, 2, True, (0, 16383))
    POSITION_P_GAIN = ControlTableItem(84, 2, True, (0, 16383))
    FEEDFORWARD_2ND_GAIN = ControlTableItem(88, 2, True, (0, 16383))
    FEEDFORWARD_1ST_GAIN = ControlTableItem(90, 2, True, (0, 16383))
    BUS_WATCHDOG = ControlTableItem(98, 1, True, (0, 127))
    GOAL_PWM = ControlTableItem(100, 2, True, (-885, 885))
    GOAL_VELOCITY = ControlTableItem(104, 4, True, (-1024, 1024))
    PROFILE_ACCELERATION = ControlTableItem(108, 4, True, (0, 32767))
    PROFILE_VELOCITY = ControlTableItem(112, 4, True, (0, 32767))
    GOAL_POSITION = ControlTableItem(116, 4, True, (-1048575, 1048575), units.DEGREE)
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


class XL430_W250_T(Servo):
    CONTROL_TABLE = ControlTable
    OPERATING_MODE = operatingMode

    def __init__(self, *args, unit=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.unit = unit
        self.protocol = Protocol2(**kwargs)
        self.resolution = 4096
        self.torqueEnabled = False
        self.moving = False
        self.presentPosition = 0
        self._rpm = 0.229
        self.bauds = {
            7: 4500000,
            6: 4000000,
            5: 3000000,
            4: 2000000,
            3: 1000000,
            2: 115200,
            1: 57600,
            0: 9600,
        }

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

    @classmethod
    def convertToNegative(cls, value, length):
        if value < 0:
            maxInt = int.from_bytes(bytes([0xFF] * length), "little")
            maxInt += value
            return list(maxInt.to_bytes(length, "little"))

    @classmethod
    def convertFromNegative(cls, value, length):
        return utils.twosComplement(value, length)
