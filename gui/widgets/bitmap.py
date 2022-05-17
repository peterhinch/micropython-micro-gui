# bitmap.py Provides the BMG (bitmapped graphics) class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Peter Hinch
import gc
from framebuf import FrameBuffer, MONO_HLSB
from gui.core.ugui import Widget
from gui.core.colors import *
from gui.core.ugui import ssd

def rbit8(v):
    v = (v & 0x0f) << 4 | (v & 0xf0) >> 4
    v = (v & 0x33) << 2 | (v & 0xcc) >> 2
    return (v & 0x55) << 1 | (v & 0xaa) >> 1

class BMG(Widget):

    @staticmethod
    def make_buffer(height, width):
        w = (width >> 3) + int(width & 7 > 0)
        return bytearray(height * w)
        
    def __init__(self, writer, row, col, height, width, scale=1, *, fgcolor=None, bgcolor=None, bdcolor=RED, buf=None):
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor, False)
        if buf is None:
            buf = BMG.make_buffer(height, width)
        self._fb = FrameBuffer(buf, width, height, MONO_HLSB)
        self._scale = scale
        self._buf = buf

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

    def value(self, obj):
        if isinstance(obj, list):  # 2d list of booleans
            self._fb.fill(1)
            s = self._scale
            wd = len(obj[0])
            ht = len(obj)
            if wd * s > self.width or ht * s > self.height:
                print('Object too large for buffer', wd * s, self.width, ht * s, self.height)
            else:
                print(f"Object is {wd} x {ht}")
            for row in range(ht):
                for col in range(wd):
                    v = obj[row][col]
                    for nc in range(s):
                        for nr in range(s):
                            self._fb.pixel(col * s + nc, row * s + nr, v)
        elif isinstance(obj, str):  # Assume filename
            try:
                with open(obj, "r") as f:
                    g = self.handle_stream(f)
                    n = 0
                    for x in g:
                        self._buf[n] = rbit8(x)
                        n += 1
            except OSError:
                print(f"Failed to input from {obj}")
        self.draw = True
        gc.collect()
# TODO graphic must be exactly the right size. Get dims from file in app, pass stream?
    def handle_stream(self, f):
        m = self._scale
        s = f.readline()
        elements = s.split(" ")
        if elements[1].endswith("width"):
            wd = int(elements[2])
        else:
            raise OSError
        s = f.readline()
        elements = s.split(" ")
        if elements[1].endswith("height"):
            ht = int(elements[2])
        else:
            raise OSError
        if wd * m > self.width or ht * m > self.height:
            print("Object too large for buffer", wd * m, self.width, ht * m, self.height)
            raise OSError
        s = f.readline()
        if not s.startswith("static"):
            raise OSError
        while s := f.readline():
            if (lb := s.find("}")) != -1:
                s = s[:lb]  # Strip trailing };
            p = s.strip().split(',')
            for x in p:
                if x:
                    yield int(x, 16)
