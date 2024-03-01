# ******************************************************************************
#
# My MAX7219-Python-Driver
# ===========================
#     Uwe Berger, 2024
#
#
# "my" means --> my 7-segment matrix :-)...
#
# datasheed of max7219: https://www.analog.com/media/en/technical-documentation/data-sheets/max7219-max7221.pdf
#
# The origin of this library is:
#   https://github.com/JennaSys/rpi-max7219
#
# ---------
# Have fun!
#
# ******************************************************************************

import spidev

# --------------------------------------------------------------------------------------
#   AAA
#  F   B
#  F   B
#   GGG
#  E   C
#  E   C
#   DDD  P
#
# max7219: segments bit in digit-byte
#   0b00001000  --> D
#   0b00000100  --> E
#   0b00000001  --> G
#   0b00000010  --> F
#   0b01000000  --> A
#   0b10000000  --> P (dp)
#   0b00010000  --> C
#   0b00100000  --> B
#
# ------------------------------
# matrix-version 2 (with dp)
# ------------------------------
#
#                  \x|  0   1
#    aaa           y\|  
#   f   b         ---+--------   
#   f   b          0 |  a
#    ggg           1 |  f   b
#   e   c          2 |  g
#   e   c          3 |  e   c
#    ddd  p        4 |  d   p
#    
# -----------------------------
digit_matrix_v2 = [
                    [0b00001000, 0b00000100, 0b00000001, 0b00000010, 0b01000000],
                    [0b10000000, 0b00010000, 0b00000000, 0b00100000, 0b00000000]
               ]
# --------------------------------------------------------------------------------------
#
# --------------------------------
# matrix-version 1 (without dp)
# --------------------------------
#  
#                  \x|  0   1   2
#    aaa           y\|  
#   f   b         ---+------------   
#   f   b          0 |      a
#    ggg           1 |  f       b
#   e   c          2 |      g
#   e   c          3 |  e       c
#    ddd  p        4 |      d   
# --------------------------------
digit_matrix_v1 = [
                    [0b00000000, 0b00000010, 0b00000000, 0b00000100, 0b00000000],
                    [0b01000000, 0b00000000, 0b00000001, 0b00000000, 0b00001000],
                    [0b00000000, 0b00100000, 0b00000000, 0b00010000, 0b00000000]
               ]
# --------------------------------------------------------------------------------------

MAX7219_DIGITS = 8

MAX7219_REG_NOOP = 0x0
MAX7219_REG_DIGIT0 = 0x1
MAX7219_REG_DIGIT1 = 0x2
MAX7219_REG_DIGIT2 = 0x3
MAX7219_REG_DIGIT3 = 0x4
MAX7219_REG_DIGIT4 = 0x5
MAX7219_REG_DIGIT5 = 0x6
MAX7219_REG_DIGIT6 = 0x7
MAX7219_REG_DIGIT7 = 0x8
MAX7219_REG_DECODEMODE = 0x9
MAX7219_REG_INTENSITY = 0xA
MAX7219_REG_SCANLIMIT = 0xB
MAX7219_REG_SHUTDOWN = 0xC
MAX7219_REG_DISPLAYTEST = 0xF

SPI_BUS = 0  # hardware SPI
SPI_BAUDRATE = 1000000
SPI_DEVICE = 0  # using CE0

# ************************************************************************************************************************
class SevenSegment:

    # *******************************************
    def __init__(self, digits=8, scan_digits=MAX7219_DIGITS, baudrate=SPI_BAUDRATE, spi_device=SPI_DEVICE, reverse=True, matrix_pattern=digit_matrix_v2):
        # Constructor:
        #   digits         --> should be the total number of individual digits being displayed
        #   scan_digits    --> is the number of digits each individual max7219 displays
        #   baudrate       --> defaults to 1MHz, note that excessive rates may result in instability (and is probably unnecessary)
        #   spi_device     --> indicates the CEx chip enable (CS) pin on the RasPi (0 or 1 for CE0 or CE1)
        #   reverse        --> changes the write-order of characters for displays where digits are wired R-to-L instead of L-to-R
        #   matrix_pattern --> the passed array determines the arrangement of the digit segments in the xy coordinate system (examples above)

        self.digits = digits
        self.devices = -(-digits // scan_digits)  # ceiling integer division
        self.scan_digits = scan_digits
        self.reverse = reverse
        self._buffer = [0] * digits

        self._spi = spidev.SpiDev()
        self._spi.open(SPI_BUS, spi_device)
        self._spi.max_speed_hz = baudrate
        
        self.matrix_pattern = matrix_pattern
        self.digit_dx  = len(self.matrix_pattern)
        self.digit_dy  = len(matrix_pattern[0])

        self._command(MAX7219_REG_SCANLIMIT, scan_digits-1)    # digits to display on each device  0-7
        self._command(MAX7219_REG_DECODEMODE, 0)               # use segments (not digits)
        self._command(MAX7219_REG_DISPLAYTEST, 0)              # no display test
        self._command(MAX7219_REG_SHUTDOWN, 1)                 # not blanking mode
        self.brightness(7)                                     # intensity: range: 0..15
        
        self.clear()

    # *******************************************
    def _command(self, register, data):
        # Sets a specific register some data, replicated for all cascaded devices.
        self._write([register, data] * self.devices)

    # *******************************************
    def _write(self, data):
        # Send the bytes (which should be comprised of alternating command, data values) over the SPI device.
        self._spi.xfer2(data)

    # *******************************************
    def clear(self, flush=True):
        # Clears the buffer and if specified, flushes the display.
        self._buffer = [0] * self.digits
        if flush:
            self.flush()

    # *******************************************
    def brightness(self, intensity):
        # Sets the brightness level of all cascaded devices to the same intensity level, ranging from 0..15.
        self._command(MAX7219_REG_INTENSITY, intensity)

    # *******************************************
    def flush(self):
        # write out the contents of the buffer items to the SPI device.
        buffer = self._buffer.copy()
        if self.reverse:
            buffer.reverse()

        for dev in range(self.devices):
            if self.reverse:
                current_dev = self.devices - dev - 1
            else:
                current_dev = dev

            for pos in range(self.scan_digits):
                self._write([pos + MAX7219_REG_DIGIT0, buffer[pos + (current_dev * self.scan_digits)]] + ([MAX7219_REG_NOOP, 0] * dev))
        
    # *******************************************
    def set_pixel(self, x, y):
        # set matrix pixel in buffer (without flushes the diplay)
        position = int(y/self.digit_dy) * self.scan_digits + int(x/self.digit_dx)
        byte_x = x % self.digit_dx
        byte_y = y % self.digit_dy
        if (position < self.digits) and (0 <= byte_x <= (self.digit_dx - 1)) and (0 <= byte_y <= (self.digit_dy - 1)):
            self._buffer[position] = self._buffer[position] | self.matrix_pattern[byte_x][byte_y]

# ************************************************************************************************************************
        
