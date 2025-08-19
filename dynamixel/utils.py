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

import time


class Lock:
    """Simple lock to use with half duplex UART

    Not "thread" safe so it should only be initialized by a singleton.
    """

    def __init__(self):
        self.locked = False

    def __enter__(self):
        while self.locked:
            time.sleep(0.01)
        self.locked = True

    def __exit__(self, *args):
        _ = args
        self.locked = False


def twosComplement(value: int, length: int) -> int:
    """Compute the 2's complement of int value

    Given an unsigned integer return signed value.

    Would be better to do this with [from/to]_bytes but
    the "signed" arg is not implemented in circuitpython ¯\_(ツ)_/¯

    :param value: Unsigned integer
    :type value: int
    :param length: Length of unsigned integer in bytes
    :type length: int
    :returns: Signed integer
    :rtype: int
    """
    width = length * 8
    sign_bit = 1 << (width - 1)
    if value & sign_bit:
        value -= 1 << width
    return value
