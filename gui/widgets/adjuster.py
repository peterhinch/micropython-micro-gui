# adjuster.py Tiny control knob (rotary potentiometer) widget

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

from gui.core.ugui import LinearIO, display
import math

TWOPI = 2 * math.pi
# Null function
dolittle = lambda *_ : None

# *********** CONTROL KNOB CLASS ***********

class Adjuster(LinearIO):
    def __init__(self, writer, row, col, *, value=0.0,
                 fgcolor=None, bgcolor=None, color=None, prcolor=None, 
                 callback=dolittle, args=[]):
        height = writer.height  # Match a user-linked Label
        super().__init__(writer, row, col, height, height, fgcolor,
                         bgcolor, False, value, True, prcolor)
        super()._set_callbacks(callback, args)
        radius = height / 2
        self.arc = 1.5 * math.pi # Usable angle of control
        self.radius = radius
        self.xorigin = col + radius
        self.yorigin = row + radius
        self.color = color
        self.draw = True  # Ensure a redraw on next refresh
        # Run callback (e.g. to set dynamic colors)
        self.callback(self, *self.args)

    def show(self):
        if super().show(False):  # Honour bgcolor
            arc = self.arc
            radius = self.radius
            if self.color is not None:
                display.fillcircle(self.xorigin, self.yorigin, radius, self.color)
            display.circle(self.xorigin, self.yorigin, radius, self.fgcolor)
            display.circle(self.xorigin, self.yorigin, radius, self.fgcolor)
            self._drawpointer(self._value, self.fgcolor) # draw new

    def _drawpointer(self, value, color):
        arc = self.arc
        length = self.radius - 1
        angle = value * arc - arc / 2
        x_end = int(self.xorigin + length * math.sin(angle))
        y_end = int(self.yorigin - length * math.cos(angle))
        display.line(int(self.xorigin), int(self.yorigin), x_end, y_end, color)
