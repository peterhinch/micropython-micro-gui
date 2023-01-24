# hardware_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch, Ihor Nehrutsa, Austin St. Aubin

# Supports:
# Pico Display Pack 1.14" 240*240(Pixel) based on ST7789V
# https://shop.pimoroni.com/products/pico-display-pack
# https://shop.pimoroni.com/products/pico-enviro-pack

from machine import Pin, SPI
import gc

from drivers.st7789.st7789_4bit import *
SSD = ST7789

gc.collect()  # Precaution before instantiating framebuf

# Conservative low baudrate. Can go to 62.5MHz.
spi = SPI(0, 30_000_000, sck=Pin(18), mosi=Pin(19), miso=None)
pdc = Pin(16, Pin.OUT, value=0)
pcs = Pin(17, Pin.OUT, value=1)
pbl = Pin(20, Pin.OUT, value=1)
prst = Pin(21, Pin.OUT, value=1)

# Note: LANDSCAPE = PORTRAIT, is flipped with this display
ssd = SSD(spi, height=240, width=240, dc=pdc, cs=pcs, rst=prst, disp_mode=LANDSCAPE, display=GENERIC)

# - - - - - - - - - - - - - - - - - - - - - - - - - -

# Create and export a Display instance
from gui.core.ugui import Display

# https://cdn.shopify.com/s/files/1/0174/1800/files/pico_enviro_pack_schematic.pdf
# Button Pinout
BUTTON_A = 12
BUTTON_B = 13
BUTTON_X = 14
BUTTON_Y = 15

# Define control buttons
nxt = Pin(BUTTON_X, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(BUTTON_A, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(BUTTON_Y, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = None ### Pin(BUTTON_A, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = None ### Pin(11, Pin.IN, Pin.PULL_UP)  # Decrease control's value

display = Display(ssd, nxt, sel, prev, increase, decrease, False)
