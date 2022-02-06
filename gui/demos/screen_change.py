# screen_change.py Minimal micro-gui demo showing a Button causing a screen change.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets import Button, CloseButton, Label
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as font
from gui.core.colors import *

# Defining a button in this way enables it to be re-used on
# multiple Screen instances. Note that a Screen class is
# passed, not an instance.
def fwdbutton(wri, row, col, cls_screen, text='Next'):
    def fwd(button):
        Screen.change(cls_screen)  # Callback

    Button(wri, row, col, callback = fwd,
           fgcolor = BLACK, bgcolor = GREEN,
           text = text, shape = RECTANGLE)

wri = CWriter(ssd, font, GREEN, BLACK, verbose=False)

# This screen overlays BaseScreen.
class BackScreen(Screen):

    def __init__(self):
        super().__init__()
        Label(wri, 2, 2, 'New screen.')
        CloseButton(wri)


class BaseScreen(Screen):

    def __init__(self):

        super().__init__()
        Label(wri, 2, 2, 'Base screen.')
        fwdbutton(wri, 40, 2, BackScreen)
        CloseButton(wri)


def test():
    print('Screen change demo.')
    Screen.change(BaseScreen)  # Pass class, not instance!

test()
