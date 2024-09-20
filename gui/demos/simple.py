# simple.py Minimal micro-gui demo.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021-2024 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets import Label, Button, CloseButton
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *


class BaseScreen(Screen):
    def __init__(self):
        def my_callback(button, arg):
            print("Button pressed", arg)

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK)
        col = 2
        row = 2
        Label(wri, row, col, "Simple Demo")
        row = 50
        Button(wri, row, col, text="Yes", callback=my_callback, args=("Yes",))
        col += 60
        Button(wri, row, col, text="No", callback=my_callback, args=("No",))
        CloseButton(wri)  # Quit the application


def test():
    print("Simple demo: button presses print to REPL.")
    Screen.change(BaseScreen)  # A class is passed here, not an instance.


test()
