# bitmap.py Provides the BMG (bitmapped graphics) class
# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Peter Hinch

# Graphics are created by [utils/image_converter.py](utils/image_converter.py). Images
# have variable PPB encoding and a palette which is decoded by bitmap widget
# Processed image is a python module that has the bitstream and the palette of the image.

from gui.core.ugui import Widget
from gui.core.colors import *
from gui.core.ugui import ssd
import struct

def little_to_big_endian(value):
    # A Helper function to convert 16 bit int from little to big endian
    # Pack the value as little-endian
    packed = struct.pack(f'<H', value)
    # Unpack it as big-endian
    return struct.unpack(f'>H', packed)[0]

class ColorBitMap(Widget):

    def __init__(
        self,
        writer,
        row,
        col,
        height,
        width,
        *,
        fgcolor=None,
        bgcolor=None,
        bdcolor=RED,
    ):
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor)

    # Transform palette to match display color format
    # this will be run for with all image palette members
    palette_transformer_cb = lambda self, x: ~little_to_big_endian(x) & 0xffff

    def show(self):
        if not super().show(True):  # Draw or erase border
            return
        if self._value is None:
            return
        self.bitmap(self._value)

    def bitmap(self, bitmap, index=0):
        """
        Draw a bitmap on display at the specified column and row
        Image has to be a module that is generated with image_converter.py

        Args:
            bitmap (bitmap_module): The module containing the bitmap to draw
            index (int): Optional index of bitmap to draw from multiple bitmap
                module
            palette_transformer_cb (callable): Trans
        """
        width = bitmap.WIDTH
        height = bitmap.HEIGHT
        bitmap_size = height * width
        buffer_len = bitmap_size * 2
        bpp = bitmap.BPP
        bs_bit = bpp * bitmap_size * index  # if index > 0 else 0

        if self.palette_transformer_cb is not None:
            palette = list(map(self.palette_transformer_cb, bitmap.PALETTE))
        else:
            palette = bitmap.PALETTE

        pixel = 0
        for i in range(0, buffer_len, 2):
            color_index = 0
            for _ in range(bpp):
                color_index = (color_index << 1) | (
                    (bitmap.BITMAP[bs_bit >> 3] >> (7 - (bs_bit & 7))) & 1
                )
                bs_bit += 1
            color = palette[color_index]

            col = pixel % width
            row = (pixel // width) % height
            ssd.pixel(self.col + col, self.row + row, color)
            pixel += 1

    def _validate(self, fn):
        if not str(type(fn)) == "<class 'module'>":
            raise ValueError("Value must be a module")
        wd = fn.WIDTH
        ht = fn.HEIGHT
        if not (wd == self.width and ht == self.height):
            raise ValueError(
                f"Object dimensions {ht}x{wd} do not match widget {self.height}x{self.width}"
            )

    def value(self, fn=None):
        if fn is not None:
            self._validate(fn)  # Throws on failure
        return super().value(fn)

