# knob.py Extension to microgui providing a control knob (rotary potentiometer) widget

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

from gui.core.ugui import LinearIO, display
import math

TWOPI = 2 * math.pi
# Null function
dolittle = lambda *_ : None

# *********** CONTROL KNOB CLASS ***********

class Knob(LinearIO):
    def __init__(self, writer, row, col, *, height=70, arc=TWOPI, ticks=9, value=0.0,
                 fgcolor=None, bgcolor=None, color=None, bdcolor=None,
                 callback=dolittle, args=[], active=True):
        super().__init__(writer, row, col, height, height, fgcolor, bgcolor, bdcolor, value, active)
        super()._set_callbacks(callback, args)
        radius = height / 2
        self.arc = min(max(arc, 0), TWOPI) # Usable angle of control
        self.radius = radius
        self.xorigin = col + radius
        self.yorigin = row + radius
        self.ticklen = 0.1 * radius
        self.pointerlen = radius - self.ticklen - 5
        self.ticks = max(ticks, 2) # start and end of travel
        self.color = color
        self.draw = True  # Ensure a redraw on next refresh
        if active:  # Run callback (e.g. to set dynamic colors)
            self.callback(self, *self.args)

    def show(self):
        if super().show(False):  # Honour bgcolor
            arc = self.arc
            ticks = self.ticks
            radius = self.radius
            ticklen = self.ticklen
            for tick in range(ticks):
                theta = (tick / (ticks - 1)) * arc - arc / 2
                x_start = int(self.xorigin + radius * math.sin(theta))
                y_start = int(self.yorigin - radius * math.cos(theta))
                x_end = int(self.xorigin + (radius - ticklen) * math.sin(theta))
                y_end = int(self.yorigin - (radius - ticklen) * math.cos(theta))
                display.line(x_start, y_start, x_end, y_end, self.fgcolor)
            if self.color is not None:
                display.fillcircle(self.xorigin, self.yorigin, radius - ticklen, self.color)
            display.circle(self.xorigin, self.yorigin, radius - ticklen, self.fgcolor)
            display.circle(self.xorigin, self.yorigin, radius - ticklen - 3, self.fgcolor)

            self._drawpointer(self._value, self.fgcolor) # draw new

    def _drawpointer(self, value, color):
        arc = self.arc
        length = self.pointerlen
        angle = value * arc - arc / 2
        x_end = int(self.xorigin + length * math.sin(angle))
        y_end = int(self.yorigin - length * math.cos(angle))
        display.line(int(self.xorigin), int(self.yorigin), x_end, y_end, color)
