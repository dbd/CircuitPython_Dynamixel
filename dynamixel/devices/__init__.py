# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Derek Daniels
#
# SPDX-License-Identifier: MIT

# gnarly way to handle auto imports if you don't include all the devices in the lib
# when adding a new devicves add them to imports with (file_name, class_name) format
from dynamixel.servo import ControlTableItem

imports = [("xl430w250t", "XL430_W250_T"), ("ax12a", "AX12A")]


def make_getter(addr, size):
    def getter(self, _addr=addr, _size=size):
        return self.readControlTableItem(_addr, _size)

    return getter


def make_setter(addr, size):
    def setter(self, data, _addr=addr, _size=size):
        return self.writeControlTableItem(_addr, _size, data)

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
            setattr(cls, methodName, make_setter(*ct[:2]))

        methodName = f"get{baseName}"
        setattr(cls, methodName, make_getter(*ct[:2]))
