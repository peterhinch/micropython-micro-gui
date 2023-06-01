# pico_epaper_42.py on my PCB (non-standard connection)

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2023 Peter Hinch

# This Hardware_setup.py is for # https://www.waveshare.com/pico-epaper-4.2.htm
# wired to the Pico using the ribbon cable rather than the default socket.
# This was to enable testing using my ILI9341 PCB and its pushbuttons.
# Use commented-out code below if using the built-in Pico socket.

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
from drivers.epaper.pico_epaper_42 import EPD as SSD
freq(250_000_000)  # RP2 overclock
# Create and export an SSD instance
prst = Pin(9, Pin.OUT, value=1)
pcs = Pin(10, Pin.OUT, value=1)
pdc = Pin(8, Pin.OUT, value=0)  # Arbitrary pins
busy = Pin(15, Pin.IN)
# Datasheet allows 10MHz
spi = SPI(0, sck=Pin(6), mosi=Pin(7), miso=Pin(4), baudrate=10_000_000)
gc.collect()  # Precaution before instantiating framebuf

# Using normal socket connection default args apply
# ssd = SSD()
ssd = SSD(spi, pcs, pdc, prst, busy)
gc.collect()
from gui.core.ugui import Display, quiet
# quiet()
# Create and export a Display instance
# Define control buttons
nxt = Pin(19, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(16, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(18, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(20, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(17, Pin.IN, Pin.PULL_UP)  # Decrease control's value
# display = Display(ssd, nxt, sel, prev)  # 3-button mode
display = Display(ssd, nxt, sel, prev, increase, decrease)  # 5-button mode
ssd.wait_until_ready()  # Blocking wait
