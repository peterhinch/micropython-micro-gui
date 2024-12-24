# qrcode.py Provides the QRMap widget to display the output of uQR library.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Peter Hinch
from framebuf import FrameBuffer, MONO_HLSB
from gui.core.ugui import Widget
from gui.core.colors import *
from gui.core.ugui import ssd
from optional_extras.py.uQR import QRCode
from utime import ticks_diff, ticks_ms


class QRMap(Widget):
    @staticmethod
    def len_side(version):
        return 4 * version + 17

    @staticmethod
    def make_buffer(version, scale):
        side = QRMap.len_side(version) * scale
        width = (side >> 3) + int(side & 7 > 0)  # Width in bytes
        return bytearray(side * width)

    def __init__(self, writer, row, col, version=4, scale=1, *, bdcolor=RED, buf=None):
        self._version = version
        self._scale = scale
        self._iside = self.len_side(version)  # Dimension of unscaled QR image less border
        side = self._iside * scale
        # Widget allows 4 * scale border around each edge
        border = 4 * scale
        wside = side + 2 * border  # Widget dimension
        super().__init__(writer, row, col, wside, wside, BLACK, WHITE, bdcolor, False)
        super()._set_callbacks(self._update, ())
        if buf is None:
            buf = QRMap.make_buffer(version, scale)
        self._fb = FrameBuffer(buf, side, side, MONO_HLSB)
        self._irow = row + border
        self._icol = col + border
        self._qr = QRCode(version, border=0)

    def show(self):
        if super().show(False):  # Show white border
            palette = ssd.palette
            palette.bg(self.bgcolor)
            palette.fg(self.fgcolor)
            ssd.blit(self._fb, self._icol, self._irow, -1, palette)

    def _update(self, _):  # Runs when value changes
        t = ticks_ms()
        qr = self._qr
        qr.clear()
        qr.add_data(self._value)
        matrix = qr.get_matrix()  # 750ms. Rest of the routine adds 50ms
        if qr.version != self._version:
            raise ValueError("Text too long for QR version.")
        wd = self._iside
        s = self._scale
        for row in range(wd):
            for col in range(wd):
                v = matrix[row][col]
                for nc in range(s):
                    for nr in range(s):
                        self._fb.pixel(col * s + nc, row * s + nr, v)
