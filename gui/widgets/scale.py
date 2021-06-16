# scale.py Extension to micro-gui providing the Scale class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# Usage:
# from gui.widgets.scale import Scale

from gui.core.ugui import LinearIO, display
from hardware_setup import ssd  # Display driver for Writer
from gui.core.writer import Writer
from gui.core.colors import *

dolittle = lambda *_ : None

class Scale(LinearIO):
    def __init__(self, writer, row, col, *,
                 ticks=200, legendcb=None, tickcb=None,
                 height=0, width=100, bdcolor=None, fgcolor=None, bgcolor=None,
                 callback=dolittle, args=[], 
                 pointercolor=None, fontcolor=None, prcolor=None,
                 value=0.0, active=False):
        if ticks % 2:
            raise ValueError('ticks arg must be divisible by 2')
        self.ticks = ticks
        self.tickcb = tickcb
        def lcb(f):
            return '{:3.1f}'.format(f)
        self.legendcb = legendcb if legendcb is not None else lcb
        bgcolor = BLACK if bgcolor is None else bgcolor
        text_ht = writer.font.height()
        ctrl_ht = 12  # Minimum height for ticks
        # Add 2 pixel internal border to give a little more space
        min_ht = text_ht + 6  # Ht of text, borders and gap between text and ticks
        if height < min_ht + ctrl_ht:
            height = min_ht + ctrl_ht  # min workable height
        else:
            ctrl_ht = height - min_ht  # adjust ticks for greater height
        width &= 0xfffe  # Make divisible by 2: avoid 1 pixel pointer offset
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor, self._to_int(value), active)
        if active:
            super()._set_callbacks(callback, args)
        self.minval = -1.0  # By default scales run from -1.0 to +1.0
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
        self.draw = True  # Ensure a redraw on next refresh
        if active:  # Run callback (e.g. to set dynamic colors)
            if prcolor is not None:
                self.prcolor = prcolor  # Option for different bdcolor in precision mode
            self.callback(self, *self.args)

    def show(self):
        wri = self.writer
        x0: int = self.x0  # Internal rectangle occupied by scale and text
        x1: int = self.x1
        y0: int = self.y0
        y1: int = self.y1
        if super().show():
            # Scale is drawn using ints. Each division is 10 units.
            val: int = self._value  # 0..ticks*10
            # iv increments for each tick. Its value modulo N determines tick length
            iv: int  # val / 10 at a tick position
            d: int  # val % 10: offset relative to a tick position
            fx: int  # X offset of current tick in value units 
            if val >= 100:  # Whole LHS of scale will be drawn
                iv, d = divmod(val - 100, 10)  # Initial value
                fx = 10 - d
                iv += 1
            else:  # Scale will scroll right
                iv = 0
                fx = 100 - val

            # Window shows 20 divisions, each of which corresponds to 10 units of value.
            # So pixels per unit value == win_width/200
            win_width: int = x1 - x0
            ticks: int = self.ticks  # Total # of ticks visible and hidden
            txtcolor = GREY if self.greyed_out() else self.fontcolor
            while True:
                x: int = x0 + (fx * win_width) // 200  # Current X position
                ys: int  # Start Y position for tick
                yl: int  # tick length
                if x > x1 or iv > ticks:  # Out of space or data (scroll left)
                    break
                if not iv % 10:
                    txt = self.legendcb(self._fvalue(iv * 10))
                    tlen = wri.stringlen(txt)
                    Writer.set_textpos(ssd, y0, min(x, x1 - tlen))
                    wri.setcolor(txtcolor, self.bgcolor)
                    wri.printstring(txt)
                    wri.setcolor()
                    ys = self.ldy0  # Large tick
                    yl = self.ldl
                elif not iv % 5:
                    ys = self.mdy0
                    yl = self.mdl
                else:
                    ys = self.sdy0
                    yl = self.sdl
                if self.tickcb is None:
                    color = self.fgcolor
                else:
                    color = self.tickcb(self._fvalue(iv * 10), self.fgcolor)
                display.vline(x, ys, yl, color)  # Draw tick
                fx += 10
                iv += 1

            display.vline(x0 + (x1 - x0) // 2, y0, y1 - y0, self.ptrcolor) # Draw pointer

    def _to_int(self, v):
        return round((v + 1.0) * self.ticks * 5)  # 0..self.ticks*10

    def _fvalue(self, v=None):
        return v / (5 * self.ticks) - 1.0

    def value(self, val=None): # User method to get or set value
        if val is not None:
            val = min(max(val, - 1.0), 1.0)
            v = self._to_int(val)
            if v != self._value:
                self._value = v
                self.draw = True  # Ensure a redraw on next refresh
                self.callback(self, *self.args)
        return self._fvalue(self._value)
