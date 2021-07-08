# tstat.py nanogui demo for the Tstat class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# Usage:
# import gui.demos.tstat

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets.buttons import Button, CloseButton
from gui.widgets.sliders import Slider
from gui.widgets.label import Label
from gui.widgets.tstat import Tstat, Region
from gui.widgets.led import LED
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):
        def btncb(btn, reg, low, high):  # Button callbck
            reg.adjust(low, high)

        def delete_alarm(btn, ts, reg):
            ts.del_region(reg)

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        col = 2
        row = 10
        sl = Slider(wri, row, col, callback=self.slider_cb,
               bdcolor=RED, slotcolor=BLUE,
               legends=('0.0', '0.5', '1.0'))
        self.ts = Tstat(wri, row, sl.mcol + 5, divisions = 4, ptcolor=YELLOW, height=100, width=15,
                        style=Tstat.BAR, legends=('0.0', '0.5', '1.0'))
        reg = Region(self.ts, 0.4, 0.55, MAGENTA, self.ts_cb)
        al = Region(self.ts, 0.9, 1.0, RED, self.al_cb)
        col = self.ts.mcol + 5
        self.lbl = Label(wri, row, col, 35, bdcolor=RED, bgcolor=BLACK)
        self.alm = LED(wri, self.lbl.mrow + 5, col, height=20, color=RED, bdcolor=BLACK)
        self.led = LED(wri, self.alm.mrow + 5, col, height=20, color=YELLOW, bdcolor=BLACK)
        self.grn = LED(wri, self.led.mrow + 5, col, height=20, color=GREEN, bdcolor=BLACK)
        col = self.lbl.mcol + 5
        btn = Button(wri, row + 30, col, width=0,
                     text='down', litcolor=RED,
                     callback=btncb, args=(reg, 0.2, 0.3))
        btn1 = Button(wri, btn.mrow + 5, col, width=btn.width,
               text='up', litcolor=RED,
               callback=btncb, args=(reg, 0.5, 0.6))
        Button(wri, btn1.mrow + 5, col, width=btn.width,
               text='del', litcolor=RED,
               callback=delete_alarm, args=(self.ts, al))
        CloseButton(wri)

    def after_open(self):
        self.ts.value(0)  # Trigger callback

    def slider_cb(self, s):
        if hasattr(self, 'lbl'):
            v = s()
            self.lbl('{:5.3f}'.format(v))
            self.ts(v)

    def ts_cb(self, reg, reason):
        # Hysteresis
        if reason == reg.EX_WA_IB or reason == reg.T_IB:
            self.led(False)
            self.grn(True)
        elif reason == reg.EX_WB_IA or reason == reg.T_IA:
            self.led(True)
            self.grn(False)

    def al_cb(self, reg, reason):
        if reason == reg.EN_WB or reason == reg.T_IA:  # Logical OR
            self.alm(True)
        elif reason & (reg.EX_WB_IB | reg.EX_WA_IB | reg.T_IB):  # Bitwise OR alternative
            self.alm(False)

def test():
    if ssd.height < 128 or ssd.width < 128:
        print(' This test requires a display of at least 128x128 pixels.')
    else:
        print('Tstat demo.')
        Screen.change(BaseScreen)

test()
