# bitmap.py Minimal micro-gui demo.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import gc
import uasyncio as asyncio
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd
from gui.widgets import Label, Button, CloseButton, BMG
# Create buffer for bitmapped graphic before fragmentation sets in
scale = 1
qr_ht = 100
qr_wd = 100
qr_buf = BMG.make_buffer(qr_ht, qr_wd)
gc.collect()
from gui.core.writer import CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK)
        col = 2
        row = 2
        Label(wri, row, col, "Bitmap Demo.")
        row = 50
        self.graphic = BMG(wri, row, col, qr_ht, qr_wd, scale, fgcolor=WHITE, bgcolor=BLACK, buf=qr_buf)
        #Button(wri, row, col, text="URL", callback=my_callback, args=(graphic, qr))
        asyncio.create_task(self.animate())
        CloseButton(wri)  # Quit the application

    async def animate(self):
        while True:
            for n in range(13):
                fn = f"/moon/m{n}.c"
                #print(fn)
                await asyncio.sleep_ms(200)
                self.graphic.value(fn)

def test():
    print("Bitmap demo.")
    Screen.change(BaseScreen)  # A class is passed here, not an instance.

test()
