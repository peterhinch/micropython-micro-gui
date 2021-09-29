# listbox.py Extension to ugui providing the Listbox class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# 12 Sep 21 Support for scrolling.

from gui.core.ugui import Widget, display
from gui.core.colors import *

dolittle = lambda *_ : None

# Behaviour has issues compared to touch displays because movement between
# entries is sequential. This can affect the choice in when the callback runs.
# It always runs when select is pressed. See 'also' ctor arg.

class Listbox(Widget):
    ON_MOVE = 1  # Also run whenever the currency moves.
    ON_LEAVE = 2  # Also run on exit from the control.

    # This is used by dropdown.py
    @staticmethod
    def dimensions(writer, elements, dlines):
        # Height of a single entry in list.
        entry_height = writer.height + 2 # Allow a pixel above and below text
        # Number of displayable lines
        dlines = len(elements) if dlines is None else dlines
        # Height of control
        height = entry_height * dlines + 2
        textwidth = max(writer.stringlen(s) for s in elements) + 4
        return entry_height, height, dlines, textwidth

    def __init__(self, writer, row, col, *, 
                 elements,
                 dlines=None, width=None, value=0,
                 fgcolor=None, bgcolor=None, bdcolor=False,
                 fontcolor=None, select_color=DARKBLUE,
                 callback=dolittle, args=[], also=0):

        e0 = elements[0]
        # Check whether elements specified as (str, str,...) or ([str, callback, args], [...)
        if isinstance(e0, tuple) or isinstance(e0, list):
            self.els = elements  # Retain original for .despatch
            self.elements = [x[0] for x in elements]  # Copy text component
            if callback is not dolittle:
                raise ValueError('Cannot specify callback.')
            self.cb = self.despatch
        else:
            self.cb = callback
            self.elements = elements
        if any(not isinstance(s, str) for s in self.elements):
            raise ValueError('Invalid elements arg.')
        # Calculate dimensions
        self.entry_height, height, self.dlines, tw = self.dimensions(
            writer, self.elements, dlines)
        if width is None:
            width = tw  # Text width

        self.also = also
        self.ntop = 0  # Top visible line
        if not isinstance(value, int):
            value = 0  # Or ValueError?
        elif value >= self.dlines:  # Must scroll
            value = min(value, len(elements) - 1)
            self.ntop = value - self.dlines + 1
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor, value, True)
        self.cb_args = args
        self.select_color = select_color
        self.fontcolor = fontcolor
        self._value = value # No callback until user selects
        self.ev = value  # Value change detection

    def show(self):
        if not super().show(False):  # Clear to self.bgcolor
            return

        x = self.col
        y = self.row
        eh = self.entry_height
        ntop = self.ntop
        dlines = self.dlines
        nlines = min(dlines, len(self.elements))  # Displayable lines
        for n in range(ntop, ntop + nlines):
            text = self.elements[n]
            if self.writer.stringlen(text) > self.width:  # Clip
                font = self.writer.font
                pos = 0
                nch = 0
                for ch in text:
                    pos += font.get_ch(ch)[2]  # width of current char
                    if pos > self.width:
                        break
                    nch += 1
                text = text[: nch]
            if n == self._value:
                display.fill_rect(x, y + 1, self.width, eh - 1, self.select_color)
                display.print_left(self.writer, x + 2, y + 1, text, self.fontcolor, self.select_color)
            else:
                display.print_left(self.writer, x + 2, y + 1, text, self.fontcolor, self.bgcolor)
            y += eh
        # Draw a vertical line to hint at scrolling
        x = self.col + self.width - 2
        if ntop:
            display.vline(x, self.row, eh - 1, self.fgcolor)
        if ntop + dlines < len(self.elements):
            y = self.row + (dlines - 1) * eh
            display.vline(x, y, eh - 1, self.fgcolor)

    def textvalue(self, text=None): # if no arg return current text
        if text is None:
            return self.elements[self._value]
        else: # set value by text
            try:
                v = self.elements.index(text)
            except ValueError:
                v = None
            else:
                if v != self._value:
                    self.value(v)
            return v

    def _vchange(self, vnew):  # A value change is taking place
        # Handle scrolling
        if vnew >= self.ntop + self.dlines:
            self.ntop = vnew - self.dlines + 1
        elif vnew < self.ntop:
            self.ntop = vnew
        self.value(vnew)
        if (self.also & Listbox.ON_MOVE):  # Treat as if select pressed
            self.do_sel()

    def do_adj(self, _, val):
        v = self._value
        if val > 0:
            if v:
                self._vchange(v -1)
        elif val < 0:
            if v < len(self.elements) - 1:
                self._vchange(v + 1)

    # Callback runs if select is pressed. Also (if ON_LEAVE) if user changes
    # list currency and then moves off the control. Otherwise if we have a
    # callback that refreshes another control, that second control does not
    # track currency.
    def do_sel(self): # Select was pushed
        self.ev = self._value
        self.cb(self, *self.cb_args)

    def enter(self):
        self.ev = self._value  # Value change detection

    def leave(self):
        if (self.also & Listbox.ON_LEAVE) and self._value != self.ev:
            self.do_sel()

    def despatch(self, _):  # Run the callback specified in elements
        x = self.els[self()]
        x[1](self, *x[2])
