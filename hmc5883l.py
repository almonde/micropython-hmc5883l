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
    
    __sample_rate_bits__ = {
        0.75: 0b000,
        1.5:  0b001,
        3:    0b010,
        7.5:  0b011,
        15:   0b100,
        30:   0b101,
        75:   0b110,
    }
    
    def __init__(self, i2c, address=0x1E, gauss='1.3', declination=(0,0), sample_rate=15, samples_avg=8):
        self.i2c = i2c
        self.address = address
        
        # Validate sample rate
        if sample_rate not in self.__sample_rate_bits__:
            raise ValueError("Invalid sample_rate, valid options: " + ", ".join(str(k) for k in self.__sample_rate_bits__))
        
        # Samples averaged (1, 2, 4, 8) -> bits 7-5
        samples_map = {1: 0b000, 2: 0b001, 4: 0b010, 8: 0b011}
        if samples_avg not in samples_map:
            raise ValueError("Invalid samples_avg, valid options: 1, 2, 4, 8")
        
        samples_bits = samples_map[samples_avg] << 5
        rate_bits = self.__sample_rate_bits__[sample_rate] << 2
        mode_bits = 0b00  # normal measurement
        
        config_reg_a = samples_bits | rate_bits | mode_bits
        
        # Write to config register A
        self.i2c.writeto_mem(self.address, 0x00, pack('B', config_reg_a))
        
        # Set gain (Config Register B)
        reg_value, self.gain = self.__gain__[gauss]
        self.i2c.writeto_mem(self.address, 0x01, pack('B', reg_value))
        
        # Mode Register: continuous measurement mode
        self.i2c.writeto_mem(self.address, 0x02, pack('B', 0x00))
        
        # Declination in radians
        self.declination = (declination[0] + declination[1]/60) * math.pi / 180
        
        # Buffer for data
        self.data = array('B', [0]*6)


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
    
    def total_field_strength(self) -> float:
        """
        Read the magnetometers and calculate the total magnetic field strength.

        Returns:
            float: total magnetic field in the same units as x, y, z
        """
        x, y, z = self.read()
        
        return math.sqrt(x*x + y*y + z*z)


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
