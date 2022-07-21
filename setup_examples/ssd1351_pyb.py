# ssd1351_setup.py


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

from machine import Pin, SPI
import gc
import time

from drivers.ssd1351.ssd1351 import SSD1351 as SSD
pp = Pin('EN_3V3')
pp(1)
time.sleep(1)

# height = 96  # 1.27 inch 96*128 (rows*cols) display
height = 128 # 1.5 inch 128*128 display

pdc = Pin('X1', Pin.OUT_PP, value=0)
pcs = Pin('X2', Pin.OUT_PP, value=1)
prst = Pin('X3', Pin.OUT_PP, value=1)
spi = SPI(2, baudrate=20_000_000)
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(spi, pcs, pdc, prst, height)  # Create a display instance
from gui.core.ugui import Display

# Create and export a Display instance
# Define control buttons
nxt = Pin(Pin.board.Y11, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(Pin.board.Y10, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(Pin.board.Y12, Pin.IN, Pin.PULL_UP)  # Move to previous control
increase = Pin(Pin.board.W32, Pin.IN, Pin.PULL_UP)  # Increase control's value
decrease = Pin(Pin.board.Y9, Pin.IN, Pin.PULL_UP)  # Decrease control's value
display = Display(ssd, nxt, sel, prev, increase, decrease, 4)
