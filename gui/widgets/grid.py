# grid.py micro-gui widget providing the Grid class: a 2d array of Label instances.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2023 Peter Hinch

from gui.core.ugui import Widget, display
from gui.core.writer import Writer
from gui.core.colors import *
from gui.widgets import Label
from .parse2d import do_args

# Given a slice and a maximum address return start and stop addresses (or None on error)
# Step value must be 1, hence does not support start > stop (used with step < 0)
def _do_slice(sli, nbytes):
    if not (sli.step is None or sli.step == 1):
        raise NotImplementedError("only slices with step=1 (or None) are supported")
    start = sli.start if sli.start is not None else 0
    stop = sli.stop if sli.stop is not None else nbytes
    start = min(start if start >= 0 else max(nbytes + start, 0), nbytes)
    stop = min(stop if stop >= 0 else max(nbytes + stop, 0), nbytes)
    return (start, stop) if start < stop else None  # Caller should check


# lwidth may be integer Label width in pixels or a tuple/list of widths
class Grid(Widget):
    def __init__(
        self,
        writer,
        row,
        col,
        lwidth,
        nrows,
        ncols,
        invert=False,
        fgcolor=None,
        bgcolor=BLACK,
        bdcolor=None,
        justify=0,
    ):
        self.nrows = nrows
        self.ncols = ncols
        self.ncells = nrows * ncols
        self.cheight = writer.height + 4  # Cell height including borders
        # Build column width list. Column width is Label width + 4.
        if isinstance(lwidth, int):
            self.cwidth = [lwidth + 4] * ncols
        else:  # Ensure len(.cwidth) == ncols
            self.cwidth = [w + 4 for w in lwidth][:ncols]
            self.cwidth.extend([lwidth[-1] + 4] * (ncols - len(lwidth)))
        width = sum(self.cwidth) - 4  # Dimensions of widget interior
        height = nrows * self.cheight - 4
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor)
        self.cells = []
        r = row
        c = col
        for _ in range(self.nrows):
            for cw in self.cwidth:
                self.cells.append(
                    Label(writer, r, c, cw - 4, invert, fgcolor, bgcolor, False, justify)
                )  # No border
                c += cw
            r += self.cheight
            c = col

    def __getitem__(self, *args):
        indices = do_args(args, self.nrows, self.ncols)
        for i in indices:
            yield self.cells[i]

    # allow grid[[r, c]] = "foo" or kwargs for Label:
    # grid[[r, c]] = {"text": str(n), "fgcolor" : RED}
    def __setitem__(self, *args):
        x = args[1]  # Value
        indices = do_args(args[:-1], self.nrows, self.ncols)
        for i in indices:
            try:
                z = next(x)  # May be a generator
            except StopIteration:
                pass  # Repeat last value
            except TypeError:
                z = x
            v = self.cells[i].value  # method of Label
            _ = v(**z) if isinstance(x, dict) else v(z)

    def __call__(self, row, col=None):  # Return a single Label
        return self.cells[row if col is None else col + row * self.ncols]

    def show(self):
        super().show()  # Draw border
        if self.has_border:  # Draw grid
            color = self.bdcolor
            x = self.col - 2  # Border top left corner
            y = self.row - 2
            dy = self.cheight
            for row in range(1, self.nrows):
                display.hline(x, y + row * dy, self.width + 4, color)
            for cw in self.cwidth[:-1]:
                x += cw
                display.vline(x, y, self.height + 4, color)
