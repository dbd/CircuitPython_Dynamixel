# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2025 Derek Daniels
#
# SPDX-License-Identifier: MIT

# gnarly way to handle auto imports if you don't include all the devices in the lib
# when adding a new devicves add them to imports with (file_name, class_name) format

imports = [("xl430w250t", "XL430_W250_T"), ("ax12a", "AX12A")]
for filename, classname in imports:
    mod = __import__(filename, None, None, (), 1)
    globals()[classname] = getattr(mod, classname)

del mod
del filename
del imports
del classname
