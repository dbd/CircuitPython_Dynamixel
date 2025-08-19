Introduction
============




.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord


.. image:: https://github.com/dbd/CircuitPython_Dynamixel/workflows/Build%20CI/badge.svg
    :target: https://github.com/dbd/CircuitPython_Dynamixel/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

CircuitPython library to interface with Dynamixel motors.


Dependencies
=============
This is designed for [Adafruit Metro ESP32-S3](https://learn.adafruit.com/adafruit-metro-esp32-s3). A HAT that supports out of the box UART and power with only a single cable is also available [here](https://github.com/dbd/AdafruitMetroESP32-DynamixelHat/tree/main). While not required a circuit is required to handle the TX/RX in half duplex.

This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Asyncio <https://github.com/adafruit/Adafruit_CircuitPython_Asyncio>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.

Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install dynamixel

Or the following command to update an existing version:

.. code-block:: shell

    circup update

Usage Example
=============

.. code-block:: python
    import time
    from dynamixel.devices import XL430_W250_T
    m = XL430_W250_T('roll', 1)
    n = XL430_W250_T('pitch', 2)
    o = XL430_W250_T('yaw', 3)
    while True:
        m.ledOff()
        n.ledOff()
        o.ledOff()
        time.sleep(.5)
        m.ledOn()
        n.ledOn()
        o.ledOn()
        time.sleep(.5)

Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-dxl.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/dbd/CircuitPython_Dynamixel/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
