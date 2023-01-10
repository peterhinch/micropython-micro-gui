# ili9486_pico.py Customise for your hardware config

# Released under the MIT License (MIT). See LICENSE.

# ILI9486 on Pi Pico
# See DRIVERS.md for wiring details.

from machine import Pin, SPI, freq
import gc

from drivers.ili94xx.ili9486 import ILI9486 as SSD
freq(250_000_000)  # RP2 overclock

pdc = Pin(8, Pin.OUT, value=0)  # Arbitrary pins
prst = Pin(9, Pin.OUT, value=1)
pcs = Pin(10, Pin.OUT, value=1)
spi = SPI(0, sck=Pin(6), mosi=Pin(7), miso=Pin(4), baudrate=30_000_000)
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst)
gc.collect()
from gui.core.ugui import Display
# Create and export a Display instance
# Define control buttons
nxt = Pin(19, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(16, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(18, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(20, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(17, Pin.IN, Pin.PULL_UP)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease)  # Pushbutton control
