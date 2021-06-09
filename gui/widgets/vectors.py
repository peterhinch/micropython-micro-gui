# vectors.py Extension to ugui providing vector display

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# VectorDial class is display-only: no practical way to perform
# input on multiple vectors

from micropython import const
from gui.core.ugui import Screen, Widget, display
from gui.widgets.label import Label
from gui.core.colors import *
import cmath

conj = lambda v : v.real - v.imag * 1j  # Complex conjugate

# Draw a vector in complex coordinates. Origin and end are complex.
# End is relative to origin.
def pline(origin, vec, color):
    xs, ys = origin.real, origin.imag
    display.line(round(xs), round(ys), round(xs + vec.real), round(ys - vec.imag), color)

# Draw an arrow; origin and vec are complex, scalar lc defines length of chevron.
# cw and ccw are unit vectors of +-3pi/4 radians for chevrons.
def arrow(origin, vec, lc, color):
    ccw = cmath.exp(3j * cmath.pi/4)  # Unit vectors
    cw = cmath.exp(-3j * cmath.pi/4)
    length, theta = cmath.polar(vec)
    uv = cmath.rect(1, theta)  # Unit rotation vector
    start = -vec
    if length > 3 * lc:  # If line is long
        ds = cmath.rect(lc, theta)
        start += ds  # shorten to allow for length of tail chevrons
    chev = lc + 0j
    pline(origin, vec, color)  # Origin to tip
    pline(origin, start, color)  # Origin to tail
    pline(origin + conj(vec), chev*ccw*uv, color)  # Tip chevron
    pline(origin + conj(vec), chev*cw*uv, color)
    if length > lc:  # Confusing appearance of very short vectors with tail chevron
        pline(origin + conj(start), chev*ccw*uv, color)  # Tail chevron
        pline(origin + conj(start), chev*cw*uv, color)

# Vector display
class Pointer:
    def __init__(self, dial):
        dial.vectors.add(self)
        self.dial = dial
        self.color = WHITE
        self.val = 0j

    def value(self, v=None, color=None):
        if color is not None:
            self.color = color
        if v is not None:
            if isinstance(v, complex):
                l = cmath.polar(v)[0]
                newval = v / l if l > 1 else v  # Max length = 1.0
            else:
                raise ValueError('Pointer value must be complex.')
            if v != self.val and self.dial.screen is Screen.current_screen:
                self.show(newval)
            self.val = newval
        return self.val

    def show(self, newval=None):
        v = self.val if newval is None else newval
        dial = self.dial
        color = self.color
        vor = dial.vor  # Dial's origin as a vector
        r = dial.radius * (1 - dial.TICKLEN)
        if dial.arrow:
            arrow(vor, r * v, 5, color)
        else:
            pline(vor, r * v, color)
        self.dial.draw = True  # Mark dial as dirty


class VectorDial(Widget):
    TICKLEN = 0.1
    def __init__(self, writer, row, col, *,
                 height=100, fgcolor=None, bgcolor=None, bdcolor=None,
                 ticks=4, arrow=False, pip=None):
        super().__init__(writer, row, col, height, height,
                         fgcolor, bgcolor, bdcolor, 0, False)  # Display only
        self.arrow = arrow
        self.pip = self.fgcolor if pip is None else pip
        radius = height / 2
        self.radius = radius
        self.ticks = ticks
        self.xorigin = col + radius
        self.yorigin = row + radius
        self.vor = self.xorigin + 1j * self.yorigin  # Origin as a vector
        self.vectors = set()
        self.draw = True

    def show(self):
        if super().show():
            # cache bound variables
            ticks = self.ticks
            radius = self.radius
            xo = self.xorigin
            yo = self.yorigin
            vor = self.vor
            vtstart = (1 - self.TICKLEN) * radius + 0j  # start of tick
            vtick = self.TICKLEN * radius + 0j  # tick
            vrot = cmath.exp(2j * cmath.pi/ticks)  # unit rotation
            for _ in range(ticks):
                pline(vor + conj(vtstart), vtick, self.fgcolor)
                vtick *= vrot
                vtstart *= vrot
            display.circle(xo, yo, radius, self.fgcolor)

            vshort = 1000  # Length of shortest vector
            for v in self.vectors:
                val = v.value() * radius  # val is complex
                vshort = min(vshort, cmath.polar(val)[0])
                v.show()
            if isinstance(self.pip, tuple) and vshort > 9:
                display.fillcircle(xo, yo, 3, self.pip)
            self.draw = False
