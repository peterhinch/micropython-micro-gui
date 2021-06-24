# checkbox.py Extension to ugui providing the Checkbox class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019-2021 Peter Hinch

from gui.core.ugui import Widget, display

dolittle = lambda *_ : None

class Checkbox(Widget):
    def __init__(self, writer, row, col, *, height=30, fillcolor=None,
                 fgcolor=None, bgcolor=None, bdcolor=False,
                 callback=dolittle, args=[], value=False, active=True):
        super().__init__(writer, row, col, height, height, fgcolor,
                         bgcolor, bdcolor, value, active)
        super()._set_callbacks(callback, args)
        self.fillcolor = fillcolor

    def show(self):
        if super().show():
            x = self.col
            y = self.row
            ht = self.height
            x1 = x + ht - 1
            y1 = y + ht - 1
            if self._value:
                if self.fillcolor is not None:
                    display.fill_rect(x, y, ht, ht, self.fillcolor)
            else:
                display.fill_rect(x, y, ht, ht, self.bgcolor)
            display.rect(x, y, ht, ht, self.fgcolor)
            if self.fillcolor is None and self._value:
                display.line(x, y, x1, y1, self.fgcolor)
                display.line(x, y1, x1, y, self.fgcolor)

    def do_sel(self): # Select was pushed
        self.value(not self._value) # Upddate and refresh
