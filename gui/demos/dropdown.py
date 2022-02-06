# dropdown.py micro-gui demo of Dropdown class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, Window, ssd

from gui.widgets import Label, CloseButton, Dropdown
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as font
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):

        super().__init__()
        wri = CWriter(ssd, font, GREEN, BLACK, verbose=False)

        col = 2
        row = 2
        els = ('hydrogen', 'helium', 'neon', 'argon', 'krypton', 'xenon', 'radon')
        self.dd = Dropdown(wri, row, col,
                           elements = els,
                           dlines = 5,  # Show 5 lines
                           bdcolor = GREEN,
                           callback=self.ddcb)
        row += 30
        self.lbl = Label(wri, row, col, self.dd.width, bdcolor=RED)
        CloseButton(wri)  # Quit the application

    def after_open(self):
        self.lbl.value(self.dd.textvalue())

    def ddcb(self, dd):
        if hasattr(self, 'lbl'):
            self.lbl.value(dd.textvalue())

def test():
    print('Dropdown demo.')
    Screen.change(BaseScreen)

test()
