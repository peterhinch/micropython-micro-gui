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
        def btncb(btn, reg, low, high):
            reg.adjust(low, high)

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        col = 2
        row = 10
        sl = Slider(wri, row, col, callback=self.slider_cb,
               bdcolor=RED, slotcolor=BLUE,
               legends=('0.0', '0.5', '1.0'))
        self.ts = Tstat(wri, row, sl.mcol + 5, divisions = 4, ptcolor=YELLOW, height=100, width=15,
                        style=Tstat.BAR, legends=('0.0', '0.5', '1.0'))
        reg = Region(self.ts, 0.4, 0.6, LIGHTRED, self.ts_cb)
        al = Region(self.ts, 0.9, 1.0, RED, self.al_cb)
        self.lbl = Label(wri, row, self.ts.mcol + 5, 35, bdcolor=RED, bgcolor=BLACK)
        self.led = LED(wri, row + 30, self.ts.mcol + 5, color=YELLOW, bdcolor=BLACK)
        btn = Button(wri, row, self.lbl.mcol + 5,
                     text='down', litcolor=RED, bgcolor=DARKGREEN,
                     callback=btncb, args=(reg, 0.2, 0.3))
        Button(wri, btn.mrow + 5, self.lbl.mcol + 5,
               text='up', litcolor=RED, bgcolor=DARKGREEN,
               callback=btncb, args=(reg, 0.5, 0.6))

        CloseButton(wri)

    def slider_cb(self, s):
        if hasattr(self, 'lbl'):
            v = s.value()
            self.lbl.value('{:5.3f}'.format(v))
            self.ts.value(v)

    def ts_cb(self, reg, reason):
        # Turn on if T drops below low threshold when it had been above high threshold. Or
        # in the case of a low going drop so fast it never registered as being within bounds
        if reason == reg.EX_WA_IB or reason == reg.T_IB:
            print('Turning on')
            self.led.value(True)
        elif reason == reg.EX_WB_IA or reason == reg.T_IA:
            print('Turning off')
            self.led.value(False)

    def al_cb(self, reg, reason):
        if reason == reg.EN_WB or reason == reg.T_IA:
            print('Alarm')

def test():
    print('Tstat demo.')
    Screen.change(BaseScreen)

test()
