# meter.py Extension to ugui providing a linear "meter" widget.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

from gui.core.ugui import Widget, display
from gui.widgets.label import Label
from gui.core.colors import *

# Null function
dolittle = lambda *_ : None

class Meter(Widget):
    BAR = 1
    LINE = 0
    def __init__(self, writer, row, col, *, height=50, width=10,
                 fgcolor=None, bgcolor=BLACK, ptcolor=None, bdcolor=None,
                 divisions=5, label=None, style=0, legends=None, value=0):
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor)
        self.divisions = divisions
        if label is not None:
            # Ensure bottom legend has space
            Label(writer, row + height + writer.height // 2, col, label)
        self.style = style
        self.ptcolor = ptcolor if ptcolor is not None else self.fgcolor
        if legends is not None:  # Legends are static
            x = col + width + 4
            y = row + height
            dy = 0 if len(legends) <= 1 else height / (len(legends) -1)
            yl = y - writer.height / 2 # Start at bottom
            for legend in legends:
                l = Label(writer, round(yl), x, legend)
                yl -= dy
        self.value(value)

    def value(self, n=None, color=None):
        if n is None:
            return super().value()
        n = super().value(min(1, max(0, n)))
        if color is not None:
            self.ptcolor = color
        return n
        
    def show(self):
        if super().show():  # Draw or erase border
            val = super().value()
            wri = self.writer
            width = self.width
            height = self.height
            x0 = self.col
            x1 = self.col + width
            y0 = self.row
            y1 = self.row + height
            if self.divisions > 0:
                dy = height / (self.divisions) # Tick marks
                for tick in range(self.divisions + 1):
                    ypos = int(y0 + dy * tick)
                    display.hline(x0 + 2, ypos, x1 - x0 - 4, self.fgcolor)

            y = int(y1 - val * height) # y position of slider
            if self.style == self.LINE:
                display.hline(x0, y, width, self.ptcolor) # Draw pointer
            else:
                w = width / 2
                display.fill_rect(int(x0 + w - 2), y, 4, y1 - y, self.ptcolor)
