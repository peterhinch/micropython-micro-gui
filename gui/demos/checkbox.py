# checkbox.py Minimal micro-gui demo showing a Checkbox updating an LED.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets.buttons import CloseButton
from gui.widgets.checkbox import Checkbox
from gui.widgets.led import LED
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        col = 2
        row = 2
        self.cb = Checkbox(wri, row, col, callback=self.cbcb)
        col+= 40
        self.led = LED(wri, row, col, color=YELLOW, bdcolor=GREEN)
        CloseButton(wri)

    def cbcb(self, cb):
        self.led.value(cb.value())

def test():
    print('Checkbox demo.')
    Screen.change(BaseScreen)

test()
