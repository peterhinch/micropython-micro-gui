# hardware_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch, Ihor Nehrutsa

# TTGO T-Display 1.14" 135*240(Pixel) based on ST7789V
# http://www.lilygo.cn/claprod_view.aspx?TypeId=62&Id=1274
# http://www.lilygo.cn/prod_view.aspx?TypeId=50044&Id=1126
# https://github.com/Xinyuan-LilyGO/TTGO-T-Display
# https://github.com/Xinyuan-LilyGO/TTGO-T-Display/blob/master/image/pinmap.jpg
# https://github.com/Xinyuan-LilyGO/TTGO-T-Display/blob/master/schematic/ESP32-TFT(6-26).pdf

# This version is based on a touch button interface.

from machine import Pin, SPI, ADC, freq
import gc

from drivers.st7789.st7789_4bit import *
SSD = ST7789

pdc = Pin(16, Pin.OUT, value=0)  # Arbitrary pins
pcs = Pin(5, Pin.OUT, value=1)
prst = Pin(23, Pin.OUT, value=1)
pbl = Pin(4, Pin.OUT, value=1)  # Backlight
gc.collect()  # Precaution before instantiating framebuf
# Conservative low baudrate. Can go to 62.5MHz.
spi = SPI(1, 30_000_000, sck=Pin(18), mosi=Pin(19))
freq(160_000_000)

# Right way up landscape: defined as top left adjacent to pin 36
ssd = SSD(spi, height=135, width=240, dc=pdc, cs=pcs, rst=prst, disp_mode=LANDSCAPE, display=TDISPLAY)
# Normal portrait display: consistent with TTGO logo at top
# ssd = SSD(spi, height=240, width=135, dc=pdc, cs=pcs, rst=prst, disp_mode=PORTRAIT, display=TDISPLAY)

from gui.core.ugui import Display
# Create and export a Display instance
# Define control buttons
nxt = Pin(13)  # Move to next control
sel = Pin(15)  # Operate current control
prev = Pin(33)  # Move to previous control
increase = Pin(32)  # Increase control's value
decrease = Pin(27)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease, False, 85)

