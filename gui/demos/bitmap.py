# bitmap.py Display a changing bitmap via the BitMap widget.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd
from gui.widgets import Label, Button, CloseButton, BitMap
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
        row = 25
        self.graphic = BitMap(wri, row, col, 99, 99, fgcolor=WHITE, bgcolor=BLACK)
        col = 120
        Button(wri, row, col, text="Next", callback=self.cb)
        CloseButton(wri)  # Quit the application
        self.image = 0

    def cb(self, _):
        self.graphic.value(f"/gui/fonts/bitmaps/m{self.image:02d}")
        self.image += 1
        self.image %= 4
        if self.image == 3:
            self.graphic.color(BLUE)
        else:
            self.graphic.color(WHITE)

def test():
    print("Bitmap demo.")
    Screen.change(BaseScreen)  # A class is passed here, not an instance.

test()
