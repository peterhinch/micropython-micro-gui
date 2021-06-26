# st7735r144_setup.py For my PCB with 1.44 inch 128*128 TFT Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

# As written, supports:
# Adfruit 1.44 inch Color TFT LCD display with MicroSD Card Breakout:
# https://www.adafruit.com/product/2088

# WIRING (Adafruit pin nos and names).
# Pyb   SSD
# Gnd   Gnd
# 3V3   Vcc
# Y11   RESET
# Y12   D/C
# W32   TFT_CS
# Y8    MOSI
# Y6    SCK
# Vin   LITE (10) Backlight

# Switch wiring
# X1 Next
# X2 Sel
# X3 Prev
# X4 Increase
# X5 Decrease

import machine
import gc

from machine import Pin, SPI
import gc
import time

from drivers.st7735r.st7735r144_4bit import ST7735R as SSD
pp = Pin('EN_3V3')
pp(1)
time.sleep(1)

pdc = Pin('Y12', Pin.OUT_PP, value=0)
pcs = Pin('W32', Pin.OUT_PP, value=1)
prst = Pin('Y11', Pin.OUT_PP, value=1)
spi = SPI(2, baudrate=6_000_000)
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst)  # Create a display instance
from gui.core.ugui import Display

# Create and export a Display instance
# Define control buttons
nxt = Pin(Pin.board.X5, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(Pin.board.X1, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(Pin.board.X4, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(Pin.board.X2, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(Pin.board.X3, Pin.IN, Pin.PULL_UP)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease)





