# dropdown.py Extension to ugui providing the Dropdown class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021-2024 Peter Hinch

# 13 Sep 24 Support dynamic elements list.
# 12 Sep 21 Support for scrolling.

from gui.core.ugui import Widget, display, Window, Screen
from gui.core.colors import *

from gui.widgets.listbox import Listbox

dolittle = lambda *_: None

# Next and Prev close the listbox without updating the Dropdown. This is
# handled by Screen .move bound method
# Callback where elements are tuples: the listbox calls its local _ListDialog callback.
# This changes the DialogBox value, so its callback runs. This is the ._despatch method
# which runs the callback of the currently selected element.
class _ListDialog(Window):
    def __init__(self, writer, row, col, dd, dlines, els):  # dd is parent dropdown
        # Need to determine Window dimensions from size of Listbox, which
        # depends on number and length of elements.
        _, lb_height, dlines, tw = Listbox.dimensions(writer, els, dlines)
        lb_width = tw + 2  # Text width + 2
        # Calculate Window dimensions
        ap_height = lb_height + 6  # Allow for listbox border
        ap_width = lb_width + 6
        super().__init__(row, col, ap_height, ap_width, draw_border=False)
        self.listbox = Listbox(
            writer,
            row + 3,
            col + 3,
            elements=els,
            dlines=dlines,
            width=lb_width,
            fgcolor=dd.fgcolor,
            bgcolor=dd.bgcolor,
            bdcolor=False,
            fontcolor=dd.fontcolor,
            select_color=dd.select_color,
            value=dd.value(),
            callback=self.callback,
            also=Listbox.NOCB,  # Force passed callback even if elements are tuples
        )
        self.dd = dd

    def callback(self, obj_listbox):
        display.ipdev.adj_mode(False)  # If in 3-button mode, leave adjust mode
        Screen.back()
        self.dd.value(obj_listbox.value())  # Update it


class Dropdown(Widget):
    def __init__(
        self,
        writer,
        row,
        col,
        *,
        elements,
        dlines=None,
        width=None,
        value=0,
        fgcolor=None,
        bgcolor=None,
        bdcolor=False,
        fontcolor=None,
        select_color=DARKBLUE,
        callback=dolittle,
        args=[],
    ):

        self.entry_height = writer.height + 2  # Allow a pixel above and below text
        height = self.entry_height
        self.select_color = select_color
        self.dlines = dlines  # Passed to _ListDialog

        # Check whether elements specified as (str, str,...) or ([str, callback, args], [...)
        self.simple = isinstance(elements[0], str)
        self.els = elements  # Retain original
        if width is None:  # Allow for square at end for arrow
            if self.simple:
                self.textwidth = max(writer.stringlen(s) for s in elements)
            else:
                self.textwidth = max(writer.stringlen(s[0]) for s in elements)
            width = self.textwidth + 2 + height
        else:
            self.textwidth = width
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor, value, True)
        self.fontcolor = self.fgcolor if fontcolor is None else fontcolor
        if not self.simple:
            if callback is not dolittle:
                raise ValueError("Cannot specify callback.")
            callback = self._despatch  # Override passed CB if each element has a CB.
        super()._set_callbacks(callback, args)  # Callback runs on value change

    def update(self):  # Elements list has changed. Extract text component for dropdown.
        # Ensure sensible _value if list size is reduced.
        self._value = min(self._value, len(self.els) - 1)
        self.show()

    def show(self):
        if not super().show():
            return
        self._draw(x := self.col, y := self.row)
        if self._value is not None:
            s = self.els[self._value] if self.simple else self.els[self._value][0]
            display.print_left(self.writer, x, y + 1, s, self.fontcolor)

    def textvalue(self, text=None):  # if no arg return current text
        if text is None:
            r = self.els[self._value]
            return r if self.simple else r[0]
        else:  # set value by text
            try:
                if self.simple:
                    v = self.els.index(text)
                else:  # More RAM-efficient than converting to list and using .index
                    q = (p[0] for p in self.els)
                    v = 0
                    while next(q) != text:
                        v += 1
            except (ValueError, StopIteration):
                v = None
            else:
                if v != self._value:
                    self.value(v)
            return v

    def _draw(self, x, y):
        # self.draw_border()
        display.vline(x + self.width - self.height, y, self.height, self.fgcolor)
        xcentre = x + self.width - self.height // 2  # Centre of triangle
        ycentre = y + self.height // 2
        halflength = (self.height - 8) // 2
        length = halflength * 2
        if length > 0:
            display.hline(xcentre - halflength, ycentre - halflength, length, self.fgcolor)
            display.line(
                xcentre - halflength,
                ycentre - halflength,
                xcentre,
                ycentre + halflength,
                self.fgcolor,
            )
            display.line(
                xcentre + halflength,
                ycentre - halflength,
                xcentre,
                ycentre + halflength,
                self.fgcolor,
            )

    def do_sel(self):  # Select was pushed
        if len(self.els) > 1:
            args = (self.writer, self.row - 2, self.col - 2, self, self.dlines, self.els)
            Screen.change(_ListDialog, args=args)
            display.ipdev.adj_mode(True)  # If in 3-button mode, go into adjust mode

    def _despatch(self, _):  # Run the callback specified in elements
        x = self.els[self()]
        x[1](self, *x[2])
