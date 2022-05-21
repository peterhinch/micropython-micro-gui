# qrcode.py Provides the QRMap widget to display the output of uQR library.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Peter Hinch
import gc
from framebuf import FrameBuffer, MONO_HLSB
from gui.core.ugui import Widget
from gui.core.colors import *
from gui.core.ugui import ssd


class QRMap(Widget):

    @staticmethod
    def make_buffer(height, width):  # Given dimensions in pixels
        w = (width >> 3) + int(width & 7 > 0)
        return bytearray(height * w)
        
    def __init__(self, writer, row, col, image, scale=1, *, fgcolor=None, bgcolor=None, bdcolor=RED, buf=None):
        self._scale = scale
        self._image = image
        try:
            height, width = self.dimensions()
        except OSError:
            print(f"Failed to access {obj}.")
            raise
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor, False)
        if buf is None:
            buf = QRMap.make_buffer(height, width)
        else:
            if len(buf) != ((width >> 3) + int(width & 7 > 0)) * height:
                raise OSError("Buffer size does not match width and height.")
        self._fb = FrameBuffer(buf, width, height, MONO_HLSB)
        if isinstance(image, list):
            self.value(image)

    def show(self):
        if super().show(True):  # Draw or erase border
            palette = ssd.palette
            palette.bg(self.bgcolor)
            palette.fg(self.fgcolor)
            ssd.blit(self._fb, self.col, self.row, -1, palette)

    def color(self, fgcolor=None, bgcolor=None):
        if fgcolor is not None:
            self.fgcolor = fgcolor
        if bgcolor is not None:
            self.bgcolor = bgcolor
        self.draw = True

    def dimensions(self):  # Dimensions of current image in pixels
        obj = self._image
        if isinstance(obj, list):  # 2d list of booleans
            return len(obj) * self._scale, len(obj[0] * self._scale)
        if isinstance(obj, tuple):
            return obj
        raise OSError

    def value(self, obj):
        self._image = obj
        self._fb.fill(self.bgcolor)  # In case tuple was passed or image smaller than buffer
        if isinstance(obj, list):  # 2d list of booleans
            wd, ht = self.dimensions()
            s = self._scale
            if wd > self.width or ht > self.height:
                print('Object too large for buffer', wd, self.width, ht, self.height)
            else:
                print(f"Object is {wd} x {ht} pixels")
            for row in range(ht//s):
                for col in range(wd//s):
                    v = obj[row][col]
                    for nc in range(s):
                        for nr in range(s):
                            self._fb.pixel(col * s + nc, row * s + nr, v)
        else:
            print(f"Invalid QR code {obj}.")
        self.draw = True
        gc.collect()
