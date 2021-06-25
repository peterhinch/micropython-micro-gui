# dial.py Dial and Pointer classes for micro-gui

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

import cmath
from gui.core.ugui import Widget, display
from gui.widgets.label import Label

# Line defined by polar coords; origin and line are complex
def polar(display, origin, line, color):
    xs, ys = origin.real, origin.imag
    theta = cmath.polar(line)[1]
    display.line(round(xs), round(ys), round(xs + line.real), round(ys - line.imag), color)

def conj(v):  # complex conjugate
    return v.real - v.imag * 1j

# Draw an arrow; origin and vec are complex, scalar lc defines length of chevron.
# cw and ccw are unit vectors of +-3pi/4 radians for chevrons (precompiled)
def arrow(display, origin, vec, lc, color, ccw=cmath.exp(3j * cmath.pi/4), cw=cmath.exp(-3j * cmath.pi/4)):
    length, theta = cmath.polar(vec)
    uv = cmath.rect(1, theta)  # Unit rotation vector
    start = -vec
    if length > 3 * lc:  # If line is long
        ds = cmath.rect(lc, theta)
        start += ds  # shorten to allow for length of tail chevrons
    chev = lc + 0j
    polar(display, origin, vec, color)  # Origin to tip
    polar(display, origin, start, color)  # Origin to tail
    polar(display, origin + conj(vec), chev*ccw*uv, color)  # Tip chevron
    polar(display, origin + conj(vec), chev*cw*uv, color)
    if length > lc:  # Confusing appearance of very short vectors with tail chevron
        polar(display, origin + conj(start), chev*ccw*uv, color)  # Tail chevron
        polar(display, origin + conj(start), chev*cw*uv, color)


class Pointer:
    def __init__(self, dial):
        self.dial = dial
        dial.vectors.add(self)
        self.val = 0 + 0j
        self.color = None

    def value(self, v=None, color=None):
        self.color = color
        if v is not None:
            if isinstance(v, complex):
                l = cmath.polar(v)[0]
                if l > 1:
                    self.val = v/l
                else:
                    self.val = v
            else:
                raise ValueError('Pointer value must be complex.')
        self.dial.draw = True
        return self.val

class Dial(Widget):
    CLOCK = 0
    COMPASS = 1
    def __init__(self, writer, row, col, *, height=100,
                 fgcolor=None, bgcolor=None, bdcolor=False, ticks=4,
                 label=None, style=0, pip=None):
        super().__init__(writer, row, col, height, height, fgcolor, bgcolor, bdcolor)
        self.style = style
        self.pip = self.fgcolor if pip is None else pip
        if label is not None:
            self.label = Label(writer, row + height + 3, col, label)
            # Adjust metrics
            self.mrow = self.label.mrow - 2  # Label never has border
            self.mcol = max(self.mcol, self.label.mcol - 2)
        radius = int(height / 2)
        self.radius = radius
        self.ticks = ticks
        self.xorigin = col + radius
        self.yorigin = row + radius
        self.vectors = set()

    def show(self):
        if super().show():
            # cache bound variables
            ticks = self.ticks
            radius = self.radius
            xo = self.xorigin
            yo = self.yorigin
            # vectors (complex)
            vor = xo + 1j * yo
            vtstart = 0.9 * radius + 0j  # start of tick
            vtick = 0.1 * radius + 0j  # tick
            vrot = cmath.exp(2j * cmath.pi/ticks)  # unit rotation
            for _ in range(ticks):
                polar(display, vor + conj(vtstart), vtick, self.fgcolor)
                vtick *= vrot
                vtstart *= vrot
            display.circle(xo, yo, radius, self.fgcolor)
            vshort = 1000  # Length of shortest vector
            for v in self.vectors:
                color = self.fgcolor if v.color is None else v.color
                val = v.value() * radius  # val is complex
                vshort = min(vshort, cmath.polar(val)[0])
                if self.style == Dial.CLOCK:
                    polar(display, vor, val, color)
                else:
                    arrow(display, vor, val, 5, color)
            if isinstance(self.pip, int) and vshort > 5:
                display.fillcircle(xo, yo, 2, self.pip)
