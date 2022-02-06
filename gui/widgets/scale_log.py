# scale_log.py Extension to micro-gui providing the ScaleLog class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# A logarithmic Scale which responds to user input
# Usage:
# from gui.widgets.scale_log import ScaleLog


import uasyncio as asyncio
from time import ticks_ms, ticks_diff
from math import log10

from gui.core.ugui import LinearIO, display
from hardware_setup import ssd  # Display driver for Writer
from gui.core.writer import Writer
from gui.core.colors import *

# Null function
dolittle = lambda *_ : None


# Start value is 1.0. User applies scaling to value and ticks callback.
class ScaleLog(LinearIO):
    encoder_rate = 5
    def __init__(self, writer, row, col, *,
                 decades=5, height=0, width=160,
                 bdcolor=None, fgcolor=None, bgcolor=None,
                 pointercolor=None, fontcolor=None, prcolor=None,
                 legendcb=None, tickcb=None,
                 callback=dolittle, args=[],
                 value=1.0, delta=0.01, active=False):
        # For correct text rendering inside control must explicitly set bgcolor
        bgcolor = BLACK if bgcolor is None else bgcolor
        if decades < 3:
            raise ValueError('decades must be >= 3')
        self.mval = 10**decades   # Max value
        self.tickcb = tickcb
        self.delta = delta  # Min multiplier = 1 + delta
        def lcb(f):
            return '{:<1.0f}'.format(f)
        self.legendcb = legendcb if legendcb is not None else lcb
        text_ht = writer.height
        ctrl_ht = 12  # Minimum height for ticks
        min_ht = text_ht + 8  # Ht of text and gap between text and ticks
        if height < min_ht + ctrl_ht:
            height = min_ht + ctrl_ht  # min workable height
        else:
            ctrl_ht = height - min_ht  # adjust ticks for greater height
        width &= 0xfffe  # Make divisible by 2: avoid 1 pixel pointer offset
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor, self._constrain(value), active, prcolor)
        super()._set_callbacks(callback, args)
        self.fontcolor = fontcolor if fontcolor is not None else self.fgcolor

        self.x0 = col + 2
        self.x1 = col + self.width - 2
        self.y0 = row + 2
        self.y1 = row + self.height - 2
        self.ptrcolor = pointercolor if pointercolor is not None else self.fgcolor
        # Define tick dimensions
        ytop = self.y0 + text_ht + 2  # Top of scale graphic (2 pixel gap)
        ycl = ytop + (self.y1 - ytop) // 2  # Centre line
        self.sdl = round(ctrl_ht * 1 / 3)  # Length of small tick.
        self.sdy0 = ycl - self.sdl // 2
        self.mdl = round(ctrl_ht * 2 / 3)  # Medium tick
        self.mdy0 = ycl - self.mdl // 2
        self.ldl = ctrl_ht  # Large tick
        self.ldy0 = ycl - self.ldl // 2
        self.dw = (self.x1 - self.x0) // 2  # Pixel width of a decade
        self.draw = True  # Ensure a redraw on next refresh
        # Run callback (e.g. to set dynamic colors)
        self.callback(self, *self.args)

    # Pre calculated log10(x) for x in range(1, 10)
    def show(self, logs=(0.0, 0.3010, 0.4771, 0.6021, 0.6990, 0.7782, 0.8451, 0.9031, 0.9542)):
        #start = ticks_ms()
        x0: int = self.x0  # Internal rectangle occupied by scale and text
        x1: int = self.x1
        y0: int = self.y0
        y1: int = self.y1
        xc: int = x0 + (x1 - x0) // 2  # x location of pointer
        dw: int = self.dw  # Width of a decade in pixels
        wri = self.writer
        if super().show():
            vc = self._value  # Current value, corresponds to centre of display
            d = int(log10(vc)) - 1  # 10**d is start of a decade guaranteed to be outside display
            vs = max(10 ** d, 1.0)  # vs: start value of current decade
            txtcolor = GREY if self.greyed_out() else self.fontcolor
            while True:  # For each decade until we run out of space
                done = True  # Assume completion
                xs: float = xc - dw * log10(vc / vs)  # x location of start of scale
                tick: int
                q: float
                # log10 ~38us on Pi Pico
                for tick, q in enumerate(logs):
                    vt: float = vs * (1 + tick)  # Value of current tick
                    x: int = round(xs + q * dw)  # x location of current tick
                    if x >= x1:
                        break  # All visible ticks drawn
                    elif x > x0:  # Tick is visible
                        if not tick:
                            txt = self.legendcb(vt)
                            tlen = wri.stringlen(txt)
                            Writer.set_textpos(ssd, y0, min(x, x1 - tlen))
                            wri.setcolor(txtcolor, self.bgcolor)
                            wri.printstring(txt)
                            ys = self.ldy0  # Large tick
                            yl = self.ldl
                        elif tick == 4:
                            ys = self.mdy0
                            yl = self.mdl
                        else:
                            ys = self.sdy0
                            yl = self.sdl
                        if self.tickcb is None:
                            color = self.fgcolor
                        else:
                            color = self.tickcb(vt, self.fgcolor)
                        display.vline(x, ys, yl, color)  # Draw tick
                        if (not tick) and (vt > 0.999 * self.mval):
                            break  # Drawn last tick at end of data
                else:
                    vs *= 10  # More to do. Next decade.
                    done = False
                if done:
                    break

            display.vline(xc, y0, y1 - y0, self.ptrcolor) # Draw pointer
            #print(ticks_diff(ticks_ms(), start)) 75-95ms on Pyboard D depending on calbacks

    def _constrain(self, v):
        return min(max(v, 1.0), self.mval)

    def value(self, val=None): # User method to get or set value
        if val is not None:
            v = self._constrain(val)
            if self._value is None or v != self._value:
                self._value = v
                self.draw = True  # Ensure a redraw on next refresh
                self.callback(self, *self.args)
        return self._value


    # Adjust widget's value. Args: button pressed, amount of increment
    def do_adj(self, button, val):
        if isinstance(button, int):  # Using an encoder
            delta = self.delta * self.encoder_rate * 0.1 if self.precision() else self.delta * self.encoder_rate
            self.value(self.value() * (1 + delta)**val)
        else:  # val == 1 or -1
            asyncio.create_task(self.btnhan(button, val))

    async def btnhan(self, button, up):
        up = up == 1
        if self.precision():
            delta = self.delta * 0.1
            maxdelta = self.delta
        else:
            delta = self.delta
            maxdelta = 0.64
        smul= (1 + delta) if up else (1 / (1 + delta))
        self.value(self.value() * smul)
        t = ticks_ms()
        while button():
            await asyncio.sleep_ms(0)  # Quit fast on button release
            if ticks_diff(ticks_ms(), t) > 500:  # Button was held down
                delta = min(maxdelta, delta * 2)
                smul = (1 + delta) if up else (1 / (1 + delta))
                self.value(self.value() * smul)
                t = ticks_ms()
