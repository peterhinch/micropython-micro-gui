# hardware_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch, Ihor Nehrutsa

# Supports:
# Waveshare Pico LCD 1.14" 135*240(Pixel) based on ST7789V
# https://www.waveshare.com/wiki/Pico-LCD-1.14
# https://www.waveshare.com/pico-lcd-1.14.htm

from machine import Pin, SPI
import gc

from drivers.st7789.st7789_4bit import *
SSD = ST7789

gc.collect()  # Precaution before instantiating framebuf
# Conservative low baudrate. Can go to 62.5MHz.
spi = SPI(1, 30_000_000, sck=Pin(10), mosi=Pin(11), miso=None)
pcs = Pin(9, Pin.OUT, value=1)
prst = Pin(12, Pin.OUT, value=1)
pbl = Pin(13, Pin.OUT, value=1)
pdc = Pin(8, Pin.OUT, value=0)

ssd = SSD(spi, height=135, width=240, dc=pdc, cs=pcs, rst=prst, disp_mode=LANDSCAPE, display=TDISPLAY)

# Create and export a Display instance
from gui.core.ugui import Display
# Define control buttons
nxt = Pin(20, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(3, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(16, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(2, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(18, Pin.IN, Pin.PULL_UP)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease)
