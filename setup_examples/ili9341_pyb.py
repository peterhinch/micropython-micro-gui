# ili9341_pyb.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# As written, supports:
# ili9341 240x320 displays on Pyboards. On a Pyboard 1.1 frozen bytecode
# is required.
# Edit the driver import for other displays.

# Demo of initialisation procedure designed to minimise risk of memory fail
# when instantiating the frame buffer. The aim is to do this as early as
# possible before importing other modules.

# WIRING
# PB        Display
# GPIO Pin
# Vin       Vin
# X6        CLK  Hardware SPI0
# X8        DATA (AKA SI MOSI)
# Y9        DC
# Y10       Rst
# Gnd       Gnd
# Y11       CS

# Pushbuttons are wired between the pin and Gnd
# PB pin    Meaning
# X1        Operate current control
# X2        Decrease value of current control
# X3        Select previous control
# X4        Select next control
# X5        Increase value of current control

from machine import Pin, SPI, freq
import gc

from drivers.ili93xx.ili9341 import ILI9341 as SSD
# Create and export an SSD instance
pdc = Pin('Y9', Pin.OUT, value=0)  # Arbitrary pins
prst = Pin('Y10', Pin.OUT, value=1)
pcs = Pin('Y11', Pin.OUT, value=1)
spi = SPI(1, baudrate=30_000_000)
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst, usd=True)

from gui.core.ugui import Display
# Create and export a Display instance
# Define control buttons
nxt = Pin('X4', Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin('X1', Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin('X3', Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin('X5', Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin('X2', Pin.IN, Pin.PULL_UP)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease)
