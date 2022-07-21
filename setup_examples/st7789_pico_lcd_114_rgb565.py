# hardware_setup.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# Supports:
# Waveshare Pico LCD 1.14" 135*240(Pixel) based on ST7789V


# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

from machine import Pin, SPI
import gc

from drivers.st7789.pico import *
SSD = LCD_1inch14

pcs = Pin(9, Pin.OUT, value=1)
prst = Pin(12, Pin.OUT, value=1)
pbl = Pin(13, Pin.OUT, value=1)

gc.collect()  # Precaution before instantiating framebuf
# Conservative low baudrate. Can go to 62.5MHz.
spi = SPI(1, 10_000_000, sck=Pin(10), mosi=Pin(11), miso=None)  # miso on pin 8 seems to cattle it
pdc = Pin(8, Pin.OUT, value=0)  # Bloody Waveshare use the MISO pin for d/c

'''            TTGO 
     v  +----------------+
 40  |  |                |
     ^  |    +------+    | pin 36
     |  |    |      |    |
     |  |    |      |    |
240  |  |    |      |    |
     |  |    |      |    |
     |  |    |      |    |
     v  |    +------+    |
 40  |  |                | Reset button
     ^  +----------------+
        >----<------>----<        
          52   135    xx
        BUTTON2    BUTTON1
'''

ssd = SSD(spi, dc=pdc, spics=pcs, rst=prst)

from gui.core.ugui import Display
# Create and export a Display instance
# Define control buttons
nxt = Pin(20, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(3, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(16, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(2, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(18, Pin.IN, Pin.PULL_UP)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease)
