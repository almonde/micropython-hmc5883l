HMC5883L Raspberry Pi Micropython
=================================

A class for working with the HMC5883L_ 3-axis magnetomter / digital compass IC with
Micropython on the Raspberry Pi Pico.

This project is a fork of: https://github.com/gvalkov/micropython-esp8266-hmc5883l which targets ESP.

Usage
-----

Upload ``hmc5883l.py`` to the Raspberry Pi Pico:

.. code-block:: python

   from machine import I2C, Pin
   from hmc5883l import HMC5883L

   # Setup an I2C instance, can pass this to multiple sensors on the bus as required.
   # ID = 0 or 1 for Raspberry Pi Pico, set pins as needed.
   i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)

   # Create an instance of HMC5883L, pass it the i2c instance.
   # Local magnetic declination (true vs magnetic north) as a tuple in degrees and minutes.  
   mags = HMC5883L(i2c, declination=(0, 0))

   x, y, z = mags.read()
   print(mags.format_result(x, y, z))

The above will produce a line similar to::

   X: -300.8398, Y: 106.7199, Z: -3768.3181, Heading: 160 degrees 28 mins

That's about it - everything else can be figured out from the code and the links below.

Resources
---------

- `Datasheet <https://cdn-shop.adafruit.com/datasheets/HMC5883L_3-Axis_Digital_Compass_IC.pdf>`_
- `Knock-off board I bought from Amazon <https://www.amazon.com/dp/B0DPG3KVSN>`_
- `HMC5883L driver for the PyBoard <https://github.com/CRImier/hmc5883l>`_

.. _adafruit-ampy: https://github.com/adafruit/ampy/tree/master/ampy
.. _HMC5883L: https://cdn-shop.adafruit.com/datasheets/HMC5883L_3-Axis_Digital_Compass_IC.pdf
.. _hmc5883l.py: https://github.com/gvalkov/micropython-esp8266-hmc5883l/blob/master/hmc5883l.py

License
-------

All code and documentation released under the terms of the Revised BSD License.
