# ili9486_pico.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2023 Peter Hinch

# As written, supports:
# ili9486 320x480 displays on Pi Pico with ILI9486 or HX8357D controller.
# Edit the driver import statement for other displays.
# Large frame buffer requires GUI to be frozen as bytecode.

# Tested displays:
# https://www.adafruit.com/product/2050
# https://www.waveshare.com/product/3.5inch-rpi-lcd-a.htm

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

# WIRING
# Pico      Display
# GPIO Pin
# 3v3  36   Vin
# IO6   9   CLK  Hardware SPI0
# IO7  10   DATA (AKA SI MOSI)
# IO8  11   DC
# IO9  12   Rst
# Gnd  13   Gnd
# IO10 14   CS

# Pushbuttons are wired between the pin and Gnd
# Pico pin  Meaning
# 16        Operate current control
# 17        Decrease value of current control
# 18        Select previous control
# 19        Select next control
# 20        Increase value of current control

from machine import Pin, SPI, freq
import gc

from drivers.ili94xx.ili9486 import ILI9486 as SSD
freq(250_000_000)  # RP2 overclock
# Create and export an SSD instance
pdc = Pin(8, Pin.OUT, value=0)  # Arbitrary pins
prst = Pin(9, Pin.OUT, value=1)
pcs = Pin(10, Pin.OUT, value=1)
spi = SPI(0, sck=Pin(6), mosi=Pin(7), miso=Pin(4), baudrate=30_000_000)
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst)

from gui.core.ugui import Display
# Create and export a Display instance
# Define control buttons
nxt = Pin(19, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(16, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(18, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(20, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(17, Pin.IN, Pin.PULL_UP)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease)
