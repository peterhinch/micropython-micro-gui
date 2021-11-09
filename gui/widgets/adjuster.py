# adjuster.py Tiny control knob (rotary potentiometer) widget

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

from gui.core.ugui import LinearIO, display
from gui.widgets.label import Label
import math

TWOPI = 2 * math.pi
# Null function
dolittle = lambda *_: None

# *********** CONTROL KNOB CLASS ***********


class Adjuster(LinearIO):
    def __init__(self, writer, row, col, *,
                 value=0.0, fgcolor=None, bgcolor=None, color=None,
                 prcolor=None, callback=dolittle, args=[]):
        height = writer.height  # Match a user-linked Label
        super().__init__(writer, row, col, height, height,
                         fgcolor, bgcolor, False, value,
                         True, prcolor)
        super()._set_callbacks(callback, args)
        radius = height / 2
        self.arc = 1.5 * math.pi  # Usable angle of control
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
            self._drawpointer(self._value, self.fgcolor)  # draw new

    def _drawpointer(self, value, color):
        arc = self.arc
        length = self.radius - 1
        angle = value * arc - arc / 2
        x_end = int(self.xorigin + length * math.sin(angle))
        y_end = int(self.yorigin - length * math.cos(angle))
        display.line(int(self.xorigin), int(self.yorigin), x_end, y_end, color)

# This class combines an Adjuster with one or two labels. Numerous layout
# options exist: users may wish to write their own versions of this example.
# The map_func enables instances to have their own mapping of Adjuster value
# to perform offset, scaling, log mapping etc.
# The object's value is that of the Adjuster, in range 0.0-1.0. The scaled
# value is retrieved with .mapped_value()
class FloatAdj:
    def __init__(self, wri, row, col, *,
                 lbl_width=60, value=0.0, color=None,
                 fstr="{:4.2f}", map_func=lambda v: v, text="",
                 callback=dolittle, args=[]):

        self.fstr = fstr
        self.map_func = map_func
        self.callback = callback
        self.args = args

        self.lbl = Label(wri, row, col, lbl_width, bdcolor=color)
        self.adj = Adjuster(wri, row, self.lbl.mcol + 2, value=value,
                            fgcolor=color, callback=self.cb)
        l = Label(wri, row, self.adj.mcol + 2, text) if text else self.adj
        # Facilitate relative positioning.
        self.mcol = l.mcol
        self.mrow = self.adj.mrow

    def cb(self, adj):
        self.lbl.value(self.fstr.format(self.mapped_value(adj)))
        self.callback(self, *self.args)

    # Behave like a Widget.
    def value(self, v=None):
        return self.adj.value(v)

    def mapped_value(self, adj=None):  # Special handling for initial callback
        return self.map_func(self.value() if adj is None else adj.value())
