# pico_epaper_42_v2.py
# hardware_setup file for a Pico ePaper 4.2" V2 with a Pico plugged in.
# The two user buttons on the display provide the interface
from machine import Pin, SPI, freq
import gc
from drivers.epaper.pico_epaper_42_v2 import EPD as SSD

freq(250_000_000)  # RP2 overclock

gc.collect()  # Precaution before instantiating framebuf

# Using the onboard socket connection default args apply
ssd = SSD()
gc.collect()
from gui.core.ugui import Display, quiet

# quiet()
# Create and export a Display instance
# Define control buttons: these are the buttons on the display unit.
nxt = Pin(17, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(15, Pin.IN, Pin.PULL_UP)  # Operate current control
# display = Display(ssd, nxt, sel, prev)  # 3-button mode
display = Display(ssd, nxt, sel)  # 2-button mode
ssd.wait_until_ready()  # Blocking wait
