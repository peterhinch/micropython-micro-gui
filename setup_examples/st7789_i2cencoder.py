# hardware_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch, Ihor Nehrutsa

# Supports:
# Waveshare Pico LCD 1.14" 135*240(Pixel) based on ST7789V
# https://www.waveshare.com/wiki/Pico-LCD-1.14
# https://www.waveshare.com/pico-lcd-1.14.htm

from machine import Pin, SPI, I2C
import i2cEncoderLibV2
import gc
from drivers.st7789.st7789_4bit import *
SSD = ST7789

SPI_CHANNEL = 0
SPI_SCK = 2
SPI_MOSI = 3
SPI_CS = 5
SPI_DC = 4
SPI_RST = 0
SPI_BAUD = 30_000_000
DISPLAY_BACKLIGHT = 1
I2C_CHANNEL = 1
I2C_SDA = 18
I2C_SCL = 19
I2C_INTERRUPT = 22
I2C_ENCODER_ADDRESS = 0x50

mode = LANDSCAPE

gc.collect()  # Precaution before instantiating framebuf
# Conservative low baudrate. Can go to 62.5MHz.
spi = SPI(SPI_CHANNEL, SPI_BAUD, sck=Pin(SPI_SCK), mosi=Pin(SPI_MOSI), miso=None)
pcs = Pin(SPI_CS, Pin.OUT, value=1)
prst = Pin(SPI_RST, Pin.OUT, value=1)
pbl = Pin(DISPLAY_BACKLIGHT, Pin.OUT, value=1)
pdc = Pin(SPI_DC, Pin.OUT, value=0)

portrait = mode & PORTRAIT
ssd = SSD(spi, height=240, width=320, dc=pdc, cs=pcs, rst=prst, disp_mode=mode, display=PI_PICO_LCD_2)

# Setup the Interrupt Pin from the encoder.
INT_pin = Pin(I2C_INTERRUPT, Pin.IN, Pin.PULL_UP)

# Initialize the device.
i2c = I2C(I2C_CHANNEL, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))

encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE
             | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE
             | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)

encoder = i2cEncoderLibV2.i2cEncoderLibV2(i2c, I2C_ENCODER_ADDRESS)
encoder.reset()

# Create and export a Display instance
from gui.core.ugui import Display

# I2cEncoder Rotary w/ Button only
display = Display(ssd, None, None, None, False, None, encoder)  # Encoder