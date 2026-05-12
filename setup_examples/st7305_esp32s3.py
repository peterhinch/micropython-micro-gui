# st7305_esp32s3.py Customise for ESP32-S3-RLCD-4.2 hardware config

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2024 Peter Hinch

# Supports:
# Waveshare ESP32-S3-RLCD-4.2 with ST7305 display (400x300 monochrome)
# https://www.waveshare.com/esp32-s3-rlcd-4.2.htm


from machine import Pin, SPI, freq
import gc

from drivers.st7305.st7305 import ST7305 as SSD, LANDSCAPE

freq(240_000_000)

TFT_RST = 41
TFT_DC = 5
TFT_CS = 40
TFT_CLK = 11
TFT_MOSI = 12

pdc = Pin(TFT_DC, Pin.OUT, value=0)
prst = Pin(TFT_RST, Pin.OUT, value=1)
pcs = Pin(TFT_CS, Pin.OUT, value=1)

gc.collect()
spi = SPI(2, baudrate=10_000_000, sck=Pin(TFT_CLK), mosi=Pin(TFT_MOSI))

ssd = SSD(spi, cs=pcs, dc=pdc, rst=prst, height=300, width=400, orientation=LANDSCAPE)

from gui.core.ugui import Display

nxt = Pin(18, Pin.IN, Pin.PULL_UP)
sel = Pin(0, Pin.IN, Pin.PULL_UP)

display = Display(ssd, nxt, sel)
