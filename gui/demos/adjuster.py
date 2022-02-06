# adjuster.py Demo of Adjusters linked to Labels

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets import Label, CloseButton, Adjuster, FloatAdj
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
        self.lbl1 = Label(wri, row, col, 60, bdcolor=RED)
        a = Adjuster(wri, row, self.lbl1.mcol + 2, fgcolor=RED,
                     callback=self.adj1_callback)
        Label(wri, row, a.mcol + 2, "0-1")
        row = self.lbl1.mrow + 5
        self.lbl2 = Label(wri, row, col, 60, bdcolor=RED)
        a = Adjuster(wri, row, self.lbl2.mcol + 2,
                     fgcolor=RED, value=0.5,
                     callback=self.adj2_callback)
        Label(wri, row, a.mcol + 2, "Scale")
        row = self.lbl2.mrow + 5
        self.lbl3 = Label(wri, row, col, 60, bdcolor=YELLOW)
        a = Adjuster(wri, row, self.lbl3.mcol + 2, fgcolor=YELLOW,
                     callback=self.adj3_callback)
        Label(wri, row, a.mcol + 2, "Log")
        # Demo of FloatAdj class
        self.fa = FloatAdj(wri, a.mrow + 5, col, color=BLUE,
                      map_func=lambda x: (x - 0.5) * 20,
                      value=0.5, fstr="{:6.2f}", text="class")
        CloseButton(wri)  # Quit the application

    def adj1_callback(self, adj):
        v = adj.value()  # Typically do mapping here
        self.lbl1.value(f"{v:4.2f}")

    def adj2_callback(self, adj):
        v = (adj.value() - 0.5) * 10  # Scale and offset
        self.lbl2.value(f"{v:4.2f}")

    def adj3_callback(self, adj):
        v = 10 ** (3 * adj.value())  # Log 3 decades
        self.lbl3.value(f"{v:4.2f}")

    #def after_open(self):  # Demo of programmatic change
        #self.fa.value(0.8)

def test():
    print("Demo of Adjuster control.")
    Screen.change(BaseScreen)  # A class is passed here, not an instance.


test()
