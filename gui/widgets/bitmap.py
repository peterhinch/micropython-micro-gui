# bitmap.py Provides the BMG (bitmapped graphics) class
# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Peter Hinch

# Graphics are files created by Linux bitmap utility.
# Widget writes data direct to the FrameBuffer.
# There is no scaling: declared size of the widget must exactly
# match the size of the bitmap.

from gui.core.ugui import Widget
from gui.core.colors import *
from gui.core.ugui import ssd


class BitMap(Widget):

    def __init__(self, writer, row, col, height, width, *, fgcolor=None, bgcolor=None, bdcolor=RED):
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor)

    def show(self):
        if not super().show(True):  # Draw or erase border
            return
        if self._value is None:
            return
        with open(self._value, "r") as f:
            g = self._gen_bytes(f)
            bit = 1
            wrap = False
            for row in range(self.height):
                if not wrap:
                    byte = next(g)  # Each row starts on a new byte
                    bit = 1
                for col in range(self.width):
                    c = self.fgcolor if byte & bit else self.bgcolor
                    ssd.pixel(self.col + col, self.row + row, c)
                    wrap = (bit := bit << 1) == 0x100
                    if wrap:
                        byte = next(g)
                        bit = 1

    def _gen_bytes(self, f):  # Yield data bytes from file stream
        f.readline()
        f.readline()  # Advance file pointer to data start
        s = f.readline()
        if not s.startswith("static"):
            raise ValueError("Bad file format.")
        while s := f.readline():
            if (lb := s.find("}")) != -1:
                s = s[:lb]  # Strip trailing };
            p = s.strip().split(',')
            for x in p:
                if x:
                    yield int(x, 16)

    # Get height/width dimension from file stream.
    def _get_dim(self, f, name):
        s = f.readline()
        elements = s.split(" ")
        if not elements[1].endswith(name):
            raise ValueError("Bad file format.")
        return int(elements[2])

    def _validate(self, fn):
        if not isinstance(fn, str):
            raise ValueError("Value must be a filename.")
        with open(fn, "r") as f:
            wd = self._get_dim(f, "width")
            ht = self._get_dim(f, "height")
            if not (wd  == self.width and ht == self.height):
                raise ValueError(f"Object dimensions {ht}x{wd} do not match widget {self.height}x{self.width}")

    def value(self, fn):
        self._validate(fn)  # Throws on failure
        super().value(fn)

    def color(self, fgcolor=None, bgcolor=None):
        if fgcolor is not None:
            self.fgcolor = fgcolor
        if bgcolor is not None:
            self.bgcolor = bgcolor
        self.draw = True
