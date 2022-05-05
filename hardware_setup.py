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

mode = LANDSCAPE  # Options PORTRAIT, USD, REFLECT combined with |

gc.collect()  # Precaution before instantiating framebuf
# Conservative low baudrate. Can go to 62.5MHz.
spi = SPI(1, 30_000_000, sck=Pin(10), mosi=Pin(11), miso=None)
pcs = Pin(9, Pin.OUT, value=1)
prst = Pin(12, Pin.OUT, value=1)
pbl = Pin(13, Pin.OUT, value=1)
pdc = Pin(8, Pin.OUT, value=0)

portrait = mode & PORTRAIT
ht, wd = (240, 135) if portrait else (135, 240)
ssd = SSD(spi, height=ht, width=wd, dc=pdc, cs=pcs, rst=prst, disp_mode=mode, display=TDISPLAY)

# Create and export a Display instance
from gui.core.ugui import Display
# Define control buttons: adjust joystick orientation to match display
# Orientation is only correct for basic LANDSCAPE and PORTRAIT modes
pnxt, pprev, pin, pdec = (2, 18, 16, 20) if portrait else (20, 16, 2, 18)
nxt = Pin(pnxt, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(3, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(pprev, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(pin, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(pdec, Pin.IN, Pin.PULL_UP)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease)
