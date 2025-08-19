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
