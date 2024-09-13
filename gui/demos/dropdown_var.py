# dropdown_var.py micro-gui demo of Dropdown widget with changeable elements

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2024 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, Window, ssd

from gui.widgets import Label, Button, CloseButton, Dropdown
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.font10 as font
from gui.core.colors import *


def newtext():  # Create new listbox entries
    strings = ("Iron", "Copper", "Lead", "Zinc")
    n = 0
    while True:
        yield strings[n]
        n = (n + 1) % len(strings)


ntxt = newtext()  # Instantiate the generator


class BaseScreen(Screen):
    def __init__(self):

        super().__init__()
        wri = CWriter(ssd, font, GREEN, BLACK, verbose=False)

        col = 2
        row = 2
        self.els = ["Hydrogen", "Helium", "Neon", "Argon", "Krypton", "Xenon", "Radon"]
        self.dd = Dropdown(
            wri,
            row,
            col,
            elements=self.els,
            dlines=5,  # Show 5 lines
            bdcolor=GREEN,
            callback=self.ddcb,
        )
        row += 30
        self.lbl = Label(wri, row, col, self.dd.width, bdcolor=RED)
        b = Button(wri, 2, 120, text="del", callback=self.delcb)
        b = Button(wri, b.mrow + 2, 120, text="add", callback=self.addcb)
        b = Button(wri, b.mrow + 10, 120, text="h2", callback=self.gocb, args=("Hydrogen",))
        b = Button(wri, b.mrow + 2, 120, text="fe", callback=self.gocb, args=("Iron",))
        CloseButton(wri)

    def gocb(self, _, txt):  # Go button callback: Move currency to specified entry
        self.dd.textvalue(txt)

    def addcb(self, _):  # Add button callback
        self.els.append(next(ntxt))  # Append a new entry
        self.dd.update()

    def delcb(self, _):  # Delete button callback
        del self.els[self.dd.value()]  # Delete current entry
        self.dd.update()

    def ddcb(self, dd):
        if hasattr(self, "lbl"):
            self.lbl.value(dd.textvalue())

    def after_open(self):
        self.lbl.value(self.dd.textvalue())


def test():
    print("Dropdown demo.")
    Screen.change(BaseScreen)


test()
