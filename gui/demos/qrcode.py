# qrcode.py Minimal micro-gui demo.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import gc
import hardware_setup  # Create a display instance
from uQR import QRCode
from gui.core.ugui import Screen, ssd
from gui.widgets import Label, Button, CloseButton, QRMap
# Create buffer for bitmapped graphic before fragmentation sets in
scale = 3  # Magnification of graphic
qr_ht = scale * 41
qr_wd = scale * 41
qr_buf = QRMap.make_buffer(qr_ht, qr_wd)
gc.collect()
from gui.core.writer import CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):

        def my_callback(button, graphic, qr):
            qr.clear()
            qr.add_data("https://en.wikipedia.org/wiki/QR_code")
            graphic.value(qr.get_matrix())

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK)
        col = 2
        row = 2
        Label(wri, row, col, "QR code Demo.")
        row = 50
        graphic = QRMap(wri, row, col, (qr_ht, qr_wd), scale, fgcolor=BLACK, bgcolor=WHITE, buf=qr_buf)
        qr = QRCode(version=4)  # Gives 41x41 matrix
        qr.add_data("uQR rocks!")
        graphic.value(qr.get_matrix())
        col = 160
        Button(wri, row, col, text="URL", callback=my_callback, args=(graphic, qr))
        CloseButton(wri)  # Quit the application

def test():
    print("QR code demo.")
    Screen.change(BaseScreen)  # A class is passed here, not an instance.

test()
