# sliders.py Extension to ugui providing linear "potentiometer" widgets.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

from micropython import const
from gui.core.ugui import LinearIO, display
from gui.core.colors import *

# Null function
dolittle = lambda *_ : None

# *********** SLIDER CLASSES ***********
# A slider's text items lie outside its bounding box.

_SLIDE_DEPTH = const(6)  # Must be divisible by 2
_TICK_VISIBLE = const(3)  # No. of tick pixels visible either side of slider
_HALF_SLOT_WIDTH = const(2)  # Width of slot /2

class Slider(LinearIO):
    def __init__(self, writer, row, col, *,
                 height=100, width=20, divisions=10, legends=None,
                 fgcolor=None, bgcolor=None, fontcolor=None, bdcolor=None, slotcolor=None,
                 callback=dolittle, args=[], value=0.0, active=True):
        width &= 0xfe # ensure divisible by 2
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor, value, active)
        if active:
            super()._set_callbacks(callback, args)
        self.divisions = divisions
        self.legends = legends
        self.fontcolor = self.fgcolor if fontcolor is None else fontcolor
        self.slotcolor = self.bgcolor if slotcolor is None else slotcolor
        # Define slider
        self.slide_x0 = col + _TICK_VISIBLE  # Draw slider shorter than ticks
        self.slide_w = width - 2 * _TICK_VISIBLE
        # y coord of top left hand corner of slide when value == 0
        self.slide_y0 = row + height - _SLIDE_DEPTH - 1
        # Slot coordinates
        centre = col + width // 2
        self.slot_x0 = centre - _HALF_SLOT_WIDTH
        self.slot_y0 = row + _SLIDE_DEPTH // 2
        self.slot_h = height - _SLIDE_DEPTH - 1
        self.draw = True  # Ensure a redraw on next refresh
        if active:  # Run callback (e.g. to set dynamic colors)
            self.callback(self, *self.args)

    def show(self):
        # Blank slot, ticks and slider
        if super().show(False):  # Honour bgcolor
            x = self.col
            y = self.slot_y0
            # Length of travel of slider
            slot_len = self.slot_h # Dimensions of slot
            slot_w = 2 * _HALF_SLOT_WIDTH
            if self.divisions > 0:
                dy = slot_len / (self.divisions) # Tick marks
                xs = x + 1
                xe = x + self.width -1
                for tick in range(self.divisions + 1):
                    ypos = int(y + dy * tick)
                    display.line(xs, ypos, xe, ypos, self.fgcolor)
            # Blank and redraw slot
            display.fill_rect(self.slot_x0, self.slot_y0, slot_w, slot_len, self.slotcolor)
            display.rect(self.slot_x0, self.slot_y0, slot_w, slot_len, self.fgcolor)

            txtcolor = GREY if self.greyed_out() else self.fontcolor
            if self.legends is not None:
                if len(self.legends) <= 1:
                    dy = 0
                else:
                    dy = slot_len / (len(self.legends) -1)
                yl = y + slot_len # Start at bottom
                wri = self.writer
                fhdelta = wri.height / 2
                for legend in self.legends:
                    display.print_left(wri, x + self.width + 4, int(yl - fhdelta),
                                       legend, txtcolor, self.bgcolor)
                    yl -= dy

            slide_y = round(self.slide_y0 - self._value * slot_len)
            display.fill_rect(self.slide_x0, slide_y, self.slide_w, _SLIDE_DEPTH, self.fgcolor)
            self.drawn = True

    def color(self, color):
        if color != self.fgcolor:
            self.fgcolor = color
            self.draw = True


class HorizSlider(LinearIO):
    def __init__(self, writer, row, col, *,
                 height=20, width=100, divisions=10, legends=None,
                 fgcolor=None, bgcolor=None, fontcolor=None, bdcolor=None,
                 slotcolor=None,
                 callback=dolittle, args=[], value=0.0, active=True):
        height &= 0xfe # ensure divisible by 2
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor, value, active)
        if active:
            super()._set_callbacks(callback, args)
        self.divisions = divisions
        self.legends = legends
        self.fontcolor = self.fgcolor if fontcolor is None else fontcolor
        self.slotcolor = self.bgcolor if slotcolor is None else slotcolor

        # Define slider
        self.slide_y0 = row + _TICK_VISIBLE  # Draw slider shorter than ticks
        self.slide_h = height - 2 * _TICK_VISIBLE

        # Slot coordinates
        self.slot_x0 = col + _SLIDE_DEPTH // 2
        self.slot_w = width - _SLIDE_DEPTH - 1
        centre = row + height // 2
        self.slot_y0 = centre - _HALF_SLOT_WIDTH
        self.draw = True  # Ensure a redraw on next refresh
        if active:  # Run callback (e.g. to set dynamic colors)
            self.callback(self, *self.args)

    def show(self):
        # Blank slot, ticks and slider
        if super().show(False):  # Honour bgcolor
            x = self.slot_x0
            y = self.row
            slot_len = self.slot_w  # Slot dimensions
            slot_h = 2 * _HALF_SLOT_WIDTH
            if self.divisions > 0:
                dx = slot_len / (self.divisions) # Tick marks
                ys = y + 1
                ye = y + self.height - 1
                for tick in range(self.divisions + 1):
                    xpos = int(x + dx * tick)
                    display.line(xpos, ys, xpos, ye, self.fgcolor)
            # Blank and redraw slot
            display.fill_rect(self.slot_x0, self.slot_y0, slot_len, slot_h, self.slotcolor)
            display.rect(self.slot_x0, self.slot_y0, slot_len, slot_h, self.fgcolor)

            txtcolor = GREY if self.greyed_out() else self.fontcolor
            if self.legends is not None:
                if len(self.legends) <= 1:
                    dx = 0
                else:
                    dx = slot_len / (len(self.legends) -1)
                xl = x
                wri = self.writer
                for legend in self.legends:
                    offset = wri.stringlen(legend) / 2
                    display.print_left(wri, int(xl - offset), y - wri.height - 4,
                                       legend, txtcolor, self.bgcolor)
                    xl += dx

            self.slide_x = round(self.col + self._value * slot_len)
            display.fill_rect(self.slide_x, self.slide_y0, _SLIDE_DEPTH, self.slide_h, self.fgcolor)
            self.drawn = True

    def color(self, color):
        if color != self.fgcolor:
            self.fgcolor = color
            self.draw = True
