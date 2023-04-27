# ili9341_esp32.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2023 Peter Hinch

# As written, supports:
# ili9341 240x320 displays on ESP32.
# This requires either an ESP32 with SPIRAM or the use of frozen bytecode.


from machine import Pin, SPI, freq
import gc

from drivers.ili93xx.ili9341 import ILI9341 as SSD
# Create and export an SSD instance
pdc = Pin(27, Pin.OUT, value=0)  # Arbitrary pins borrowed from st7735r_esp32.py
prst = Pin(26, Pin.OUT, value=1)
pcs = Pin(25, Pin.OUT, value=1)
gc.collect()  # Precaution before instantiating framebuf
spi = SPI(1, 30_000_000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))  # No need to wire MISO.
freq(160_000_000)
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, cs=pcs, dc=pdc, rst=prst)
from gui.core.ugui import Display  # Must perform this import after instantiating SSD (see other examples)
gc.collect()  # Precaution before instantiating framebuf

# Create and export a Display instance
# Define control buttons
nxt = Pin(4, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(33, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(18, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(19, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(5, Pin.IN, Pin.PULL_UP)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease)
