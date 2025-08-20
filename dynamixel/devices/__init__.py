# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Derek Daniels
#
# SPDX-License-Identifier: MIT

# gnarly way to handle auto imports if you don't include all the devices in the lib
# when adding a new devicves add them to imports with (file_name, class_name) format
from dynamixel.servo import ControlTableItem

imports = [("xl430w250t", "XL430_W250_T"), ("ax12a", "AX12A")]


def make_getter(ct):
    addr, length, _, _, defaultUnit = ct

    def getter(self, _addr=addr, _length=length, unit=None):
        data = None
        res = self.readControlTableItem(_addr, _length)
        unit = unit or self.unit or defaultUnit
        if res.ok:
            data = self.convertFromNegative(res.data, _length)
            data = self.convertRaw(data, unit)
            res.data = data
        return res

    return getter


def make_setter(ct):
    addr, length, _, limits, defaultUnit = ct

    def setter(self, data, _addr=addr, _length=length, _limits=limits, unit=None):
        unit = unit or self.unit or defaultUnit
        data = self.convertUnits(data, unit)
        if data < 0:
            data = self.convertToNegative(data)
        if isinstance(_limits, list):
            assert data in _limits, f"{data} should be one of {_limits}"
        if isinstance(limits, tuple):
            assert _limits[0] <= data <= _limits[1], (
                f"{data} should be within {_limits[0]} and {_limits[1]}"
            )
        return self.writeControlTableItem(_addr, _length, data)

    return setter


for filename, classname in imports:
    mod = __import__(filename, None, None, (), 1)
    cls = getattr(mod, classname)
    globals()[classname] = cls
    for key, ct in cls.CONTROL_TABLE.items():
        if not isinstance(ct, ControlTableItem):
            continue
        baseName = "".join([word[0] + word[1:].lower() for word in key.split("_")])
        if ct.writable:
            methodName = f"set{baseName}"
            setattr(cls, methodName, make_setter(ct))

        methodName = f"get{baseName}"
        setattr(cls, methodName, make_getter(ct))
