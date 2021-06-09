# led.py Extension to ugui providing the LED class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

from gui.core.ugui import Widget, display
from gui.core.colors import *


class LED(Widget):
    def __init__(self, writer, row, col, *, height=30, fgcolor=None, bgcolor=None, bdcolor=False, color=RED):
        super().__init__(writer, row, col, height, height, fgcolor, bgcolor, bdcolor, False)
        self._value = False
        self._color = color
        self.radius = self.height // 2
        self.x = col + self.radius
        self.y = row + self.radius

    def show(self):
        if super().show():  # Draw or erase border
            color = self._color if self._value else BLACK
            display.fillcircle(int(self.x), int(self.y), int(self.radius), color)
            display.circle(int(self.x), int(self.y), int(self.radius), self.fgcolor)

    def color(self, color):
        self._color = color
        self.draw = True
