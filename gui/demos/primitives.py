# primitives.py micro-gui demo of use of graphics primitives

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, Window, ssd, display

from gui.widgets.label import Label
from gui.widgets.buttons import CloseButton
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.font10 as font
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):

        super().__init__()
        wri = CWriter(ssd, font, GREEN, BLACK, verbose=False)

        col = 2
        row = 2
        Label(wri, row, col, 'Primitives')
        CloseButton(wri)  # Quit the application


    def after_open(self):
        display.usegrey(False)
        # Coordinates are x, y as per framebuf
        # circle method is in Display class only
        display.circle(70, 70, 30, RED, 2)
        # These methods exist in framebuf, so also in SSD and Display
        ssd.hline(0, 127, 128, BLUE)
        ssd.vline(127, 0, 128, BLUE)

def test():
    print('Primitives demo.')
    Screen.change(BaseScreen)

test()
