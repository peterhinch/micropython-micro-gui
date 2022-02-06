# adjust_vec.py Demo of Adjusters linked to a dial

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
import cmath
from gui.core.ugui import Screen, ssd

from gui.widgets import Label, CloseButton, Adjuster, Dial, Pointer
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.font10 as font
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):

        super().__init__()
        wri = CWriter(ssd, font, GREEN, BLACK)
        col = 2
        row = 2
        self.dial = Dial(wri, row, col, bdcolor=None, style=Dial.COMPASS)
        self.vec = Pointer(self.dial)
        a = Adjuster(wri, row, self.dial.mcol + 2, fgcolor=BLUE, callback=self.phi_cb)
        Label(wri, row, a.mcol + 2, "ϕ", fgcolor=BLUE)
        a = Adjuster(wri, row + 20, self.dial.mcol + 2, value=1, fgcolor=MAGENTA, callback=self.r_cb)
        Label(wri, row + 20, a.mcol + 2, "r", fgcolor=MAGENTA)
        CloseButton(wri)  # Quit the application

    def phi_cb(self, adj):
        v = adj.value()
        r, phi = cmath.polar(self.vec.value())
        self.vec.value(cmath.rect(r, v * 2 * cmath.pi))

    def r_cb(self, adj):
        v = adj.value()
        r, phi = cmath.polar(self.vec.value())
        self.vec.value(cmath.rect(v, phi))

def test():
    print('Alter a vector using Adjuster control.')
    Screen.change(BaseScreen)  # A class is passed here, not an instance.

test()
