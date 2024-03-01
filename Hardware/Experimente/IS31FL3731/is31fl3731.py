# ******************************************************************************
#
#  IS31FL3731.py
# ================
# Uwe Berger; 2023
#
# python library to access IS31PL3731-Chip via i2c
#
# Datasheed of IS31FL3731: https://www.lumissil.com/assets/pdf/core/IS31FL3731_DS.pdf
#
# The origin of this library is:
#   https://github.com/adafruit/Adafruit_CircuitPython_IS31FL3731/tree/main/adafruit_is31fl3731
#
# My adjustments to the original library source code are:
#   * Porting to native Python3
#   * Improved sending speed for i2c_write_reg (sending more than 32 bytes over i2c via methode
#     i2c_rdwr--)
#
# ---------
# Have fun!
# 
# ******************************************************************************

# imports
import math
import time
import smbus2

from smbus2 import i2c_msg

_MODE_REGISTER      = 0x00
_FRAME_REGISTER     = 0x01
_AUTOPLAY1_REGISTER = 0x02
_AUTOPLAY2_REGISTER = 0x03
_BLINK_REGISTER     = 0x05
_AUDIOSYNC_REGISTER = 0x06
_BREATH1_REGISTER   = 0x08
_BREATH2_REGISTER   = 0x09
_SHUTDOWN_REGISTER  = 0x0A
_GAIN_REGISTER      = 0x0B
_ADC_REGISTER       = 0x0C

_CONFIG_BANK        = 0x0B
_BANK_ADDRESS       = 0xFD

_PICTURE_MODE       = 0x00
_AUTOPLAY_MODE      = 0x08
_AUDIOPLAY_MODE     = 0x18

_ENABLE_OFFSET      = 0x00
_BLINK_OFFSET       = 0x12
_COLOR_OFFSET       = 0x24


class IS31FL3731:
    """
    The IS31FL3731 is an abstract class contain the main function related to this chip.
    Each board needs to define width, height and pixel_addr.

    :param ~busio.I2C i2c: the connected i2c bus i2c_device
    :param int address: the device address; defaults to 0x74
    """

    # This  must be replaced for each board
    width = 16
    height = 9

    # *************************************************************
    def __init__(self, i2c, address=0x74, frames=None):
        
        self._i2c_device = i2c
        self._i2c_address = address
        self._frame = None
        self._init(frames=frames)

    # *************************************************************
    def _i2c_read_reg(self, reg):
        # Read a buffer of data from the specified 8-bit I2C register address.
        return self._i2c_device.read_byte_data(self._i2c_address, reg)
        
    # *************************************************************
    # ...more than 32 bytes can be sent with this method!
    def _i2c_write_reg(self, reg, data):
        data = bytearray([reg]) + data
        msg = i2c_msg.write(self._i2c_address, data)
        self._i2c_device.i2c_rdwr(msg)

    # *************************************************************
    def _bank(self, bank=None):
        if bank is None:
            return self._i2c_read_reg(_BANK_ADDRESS)
        self._i2c_write_reg(_BANK_ADDRESS, bytearray([bank]))
        return None

    # *************************************************************
    def _register(self, bank, register, value=None):
        self._bank(bank)
        if value is None:
            return self._i2c_read_reg(register)
        self._i2c_write_reg(register, bytearray([value]))
        return None

    # *************************************************************
    def _mode(self, mode=None):
        return self._register(_CONFIG_BANK, _MODE_REGISTER, mode)

    # *************************************************************
    def _init(self, frames=None):
        self.sleep(True)
        # Clear config; sets to Picture Mode, no audio sync, maintains sleep
        self._bank(_CONFIG_BANK)
        self._i2c_write_reg(0, bytes([0] * 13))
        enable_data = bytes([255] * 18)
        fill_data = bytearray([0] * (self.width * self.height)) # ...we can more than 32 byte send!
        # Initialize requested frames, or all 8 if unspecified
        for frame in frames if frames else range(8):
            self._bank(frame)
            self._i2c_write_reg(_ENABLE_OFFSET, enable_data)  # Set all enable bits
            self._i2c_write_reg(_COLOR_OFFSET, fill_data)
        self._frame = 0  # To match config bytes above
        self.sleep(False)

    # *************************************************************
    def reset(self):
        """Kill the display for 10MS"""
        self.sleep(True)
        time.sleep(0.01)  # 10 MS pause to reset.
        self.sleep(False)

    # *************************************************************
    def sleep(self, value):
        """
        Set the Software Shutdown Register bit

        :param value: True to set software shutdown bit; False unset
        """
        return self._register(_CONFIG_BANK, _SHUTDOWN_REGISTER, not value)

    # *************************************************************
    def autoplay(self, delay=0, loops=0, frames=0):
        """
        Start autoplay

        :param delay: in ms
        :param loops: number of loops - 0->7
        :param frames: number of frames: 0->7
        """
        if delay == 0:
            self._mode(_PICTURE_MODE)
            return
        delay //= 11
        if not 0 <= loops <= 7:
            raise ValueError("Loops out of range")
        if not 0 <= frames <= 7:
            raise ValueError("Frames out of range")
        if not 1 <= delay <= 64:
            raise ValueError("Delay out of range")
        self._register(_CONFIG_BANK, _AUTOPLAY1_REGISTER, loops << 4 | frames)
        self._register(_CONFIG_BANK, _AUTOPLAY2_REGISTER, delay % 64)
        self._mode(_AUTOPLAY_MODE | self._frame)

    # *************************************************************
    def fade(self, fade_in=None, fade_out=None, pause=0):
        """
        Start and stop the fade feature.  If both fade_in and fade_out are None (the
        default), the breath feature is used for fading.  if fade_in is None, then
        fade_in = fade_out.  If fade_out is None, then fade_out = fade_in

        :param fade_in: positive number; 0->100
        :param fade-out: positive number; 0->100
        :param pause: breath register 2 pause value
        """
        if fade_in is None and fade_out is None:
            self._register(_CONFIG_BANK, _BREATH2_REGISTER, 0)
            return
        if fade_in is None:
            fade_in = fade_out
        elif fade_out is None:
            fade_out = fade_in

        if fade_in != 0:
            fade_in = int(math.log(fade_in / 26, 2))
        if fade_out != 0:
            fade_out = int(math.log(fade_out / 26, 2))
        if pause != 0:
            pause = int(math.log(pause / 26, 2))
        if not 0 <= fade_in <= 7:
            raise ValueError("Fade in out of range")
        if not 0 <= fade_out <= 7:
            raise ValueError("Fade out out of range")
        if not 0 <= pause <= 7:
            raise ValueError("Pause out of range")
        self._register(_CONFIG_BANK, _BREATH1_REGISTER, fade_out << 4 | fade_in)
        self._register(_CONFIG_BANK, _BREATH2_REGISTER, 1 << 4 | pause)

    # *************************************************************
    def frame(self, frame=None, show=True):
        """
        Set the current frame

        :param frame: frame number; 0-7 or None. If None function returns current frame
        :param show: True to show the frame; False to not show.
        """
        if frame is None:
            return self._frame
        if not 0 <= frame <= 8:
            raise ValueError("Frame out of range")
        self._frame = frame
        if show:
            self._register(_CONFIG_BANK, _FRAME_REGISTER, frame)
        return None

    # *************************************************************
    def audio_sync(self, value=None):
        """Set the audio sync feature register"""
        return self._register(_CONFIG_BANK, _AUDIOSYNC_REGISTER, value)

    # *************************************************************
    def audio_play(self, sample_rate, audio_gain=0, agc_enable=False, agc_fast=False):
        """Controls the audio play feature"""
        if sample_rate == 0:
            self._mode(_PICTURE_MODE)
            return
        sample_rate //= 46
        if not 1 <= sample_rate <= 256:
            raise ValueError("Sample rate out of range")
        self._register(_CONFIG_BANK, _ADC_REGISTER, sample_rate % 256)
        audio_gain //= 3
        if not 0 <= audio_gain <= 7:
            raise ValueError("Audio gain out of range")
        self._register(
            _CONFIG_BANK,
            _GAIN_REGISTER,
            bool(agc_enable) << 3 | bool(agc_fast) << 4 | audio_gain,
        )
        self._mode(_AUDIOPLAY_MODE)

    # *************************************************************
    def blink(self, rate=None):
        """Updates the blink register"""
        if rate is None:
            return (self._register(_CONFIG_BANK, _BLINK_REGISTER) & 0x07) * 270
        elif rate == 0:
            self._register(_CONFIG_BANK, _BLINK_REGISTER, 0x00)
            return None
        rate //= 270
        self._register(_CONFIG_BANK, _BLINK_REGISTER, rate & 0x07 | 0x08)
        return None

    # *************************************************************
    def fill(self, color=None, blink=None, frame=None):
        """
        Fill the display with a brightness level

        :param color: brightness 0->255
        :param blink: True if blinking is required
        :param frame: which frame to fill 0->7
        """
        if frame is None:
            frame = self._frame
        self._bank(frame)
        if color is not None:
            if not 0 <= color <= 255:
                raise ValueError("Color out of range")
            data = bytearray([color] * (self.width * self.height))
            # ...this methode can bee send more than 32 bytes!
            self._i2c_write_reg(_COLOR_OFFSET, data)
            
        if blink is not None:
            data = bool(blink) * 0xFF
            for col in range(18):
                self._register(frame, _BLINK_OFFSET + col, data)



    # *************************************************************
    # This function must be replaced for each board (...or not?)
    def pixel_addr(self, x, y):
        """Calulate the offset into the device array for x,y pixel"""
        return x + y * self.width

    # *************************************************************
    def pixel(self, x, y, color=None, blink=None, frame=None):
        """
        Blink or brightness for x-, y-pixel

        :param x: horizontal pixel position
        :param y: vertical pixel position
        :param color: brightness value 0->255
        :param blink: True to blink
        :param frame: the frame to set the pixel
        """
        if not 0 <= x <= self.width:
            return None
        if not 0 <= y <= self.height:
            return None
        pixel = self.pixel_addr(x, y)
        if color is None and blink is None:
            return self._register(self._frame, pixel)
        if frame is None:
            frame = self._frame
        if color is not None:
            if not 0 <= color <= 255:
                raise ValueError("Color out of range")
            self._register(frame, _COLOR_OFFSET + pixel, color)
        if blink is not None:
            addr, bit = divmod(pixel, 8)
            bits = self._register(frame, _BLINK_OFFSET + addr)
            if blink:
                bits |= 1 << bit
            else:
                bits &= ~(1 << bit)
            self._register(frame, _BLINK_OFFSET + addr, bits)
        return None

    # *************************************************************
    def image(self, img, blink=None, frame=None):
        """
        Set buffer to value of Python Imaging Library image.  The image should
        be in 8-bit mode (L) and a size equal to the display size.

        :param img: Python Imaging Library image
        :param blink: True to blink
        :param frame: the frame to set the image
        """
        if img.mode != "L":
            raise ValueError("Image must be in mode L.")
        imwidth, imheight = img.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError(
                "Image must be same dimensions as display ({0}x{1}).".format(
                    self.width, self.height
                )
            )
        # Grab all the pixels from the image, faster than getpixel.
        pixels = img.load()

        # Iterate through the pixels
        for x in range(self.width):  # yes this double loop is slow,
            for y in range(self.height):  #  but these displays are small!
                self.pixel(x, y, pixels[(x, y)], blink=blink, frame=frame)

    # *************************************************************
    def picture_array(self, array, blink=None, frame=None):
        """
        Fill the display with colorvalues from a bytearray.

        :param array: bytearray with colorvalues
        :param blink: True to blink
        :param frame: the frame to set the image
        """

        if len(array) != (self.width * self.height):
            raise ValueError("Parameter array must be have {0} elements!".format(self.width * self.height))
        
        if type(array) is not bytearray:
            raise ValueError("Parameter array must be a bytearray!")

        if frame is None:
            frame = self._frame
        self._bank(frame)

        self._i2c_write_reg(_COLOR_OFFSET, array)
        
        # ok?
        if blink is not None:
            data = bool(blink) * 0xFF
            for col in range(18):
                self._register(frame, _BLINK_OFFSET + col, data)


# *******************************************************************
# *******************************************************************
# *******************************************************************
