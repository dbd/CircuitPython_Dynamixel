# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Derek Daniels
#
# SPDX-License-Identifier: MIT
import time
from dynamixel.devices import XL430_W250_T
m = XL430_W250_T('', 1)
res = m.ping()
assert res.ok
while True:
    m.ledOff()
    time.sleep(.5)
    m.ledOn()
    time.sleep(.5)
