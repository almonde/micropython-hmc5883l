import math
from ustruct import pack
from array import array

class HMC5883L:
    __gain__ = {
        '0.88': (0 << 5, 0.73),
        '1.3':  (1 << 5, 0.92),
        '1.9':  (2 << 5, 1.22),
        '2.5':  (3 << 5, 1.52),
        '4.0':  (4 << 5, 2.27),
        '4.7':  (5 << 5, 2.56),
        '5.6':  (6 << 5, 3.03),
        '8.1':  (7 << 5, 4.35)
    }

    def __init__(self, i2c, address=0x1E, gauss='1.3', declination=(0, 0)):
        self.i2c = i2c
        self.address = address

        # Configure Register A: 8 samples, 15Hz, normal measurement
        self.i2c.writeto_mem(self.address, 0x00, pack('B', 0b01110000))

        # Configure Register B: gain
        reg_value, self.gain = self.__gain__[gauss]
        self.i2c.writeto_mem(self.address, 0x01, pack('B', reg_value))

        # Mode Register: continuous measurement mode
        self.i2c.writeto_mem(self.address, 0x02, pack('B', 0x00))

        # Convert declination to radians
        self.declination = (declination[0] + declination[1] / 60) * math.pi / 180

        # Allocate buffer
        self.data = array('B', [0] * 6)

    def read(self):
        data = self.data
        self.i2c.readfrom_mem_into(self.address, 0x03, data)

        x = (data[0] << 8) | data[1]
        z = (data[2] << 8) | data[3]
        y = (data[4] << 8) | data[5]

        # Convert to signed 16-bit
        x = x - (1 << 16) if x & (1 << 15) else x
        y = y - (1 << 16) if y & (1 << 15) else y
        z = z - (1 << 16) if z & (1 << 15) else z

        # Apply gain
        x = round(x * self.gain, 4)
        y = round(y * self.gain, 4)
        z = round(z * self.gain, 4)

        return x, y, z

    def heading(self, x, y):
        heading_rad = math.atan2(y, x)
        heading_rad += self.declination

        if heading_rad < 0:
            heading_rad += 2 * math.pi
        elif heading_rad > 2 * math.pi:
            heading_rad -= 2 * math.pi

        heading_deg = heading_rad * 180 / math.pi
        degrees = math.floor(heading_deg)
        minutes = round((heading_deg - degrees) * 60)
        return degrees, minutes

    def format_result(self, x, y, z):
        degrees, minutes = self.heading(x, y)
        return 'X: {:.4f}, Y: {:.4f}, Z: {:.4f}, Heading: {} deg {} min'.format(x, y, z, degrees, minutes)
