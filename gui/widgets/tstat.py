# tstat.py Extension to nanogui providing the Tstat class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# Usage:
# from gui.widgets.tstat import Tstat

from gui.core.ugui import display
from gui.core.colors import *
from gui.widgets.meter import Meter

class Region:
    # Callback reasons
    EX_WB_IA = 1  # Exit region. Was below. Is above.
    EX_WB_IB = 2  # Exit, was below, is below
    EX_WA_IA = 4  # Exit, was above, is above.
    EX_WA_IB = 8  # Exit, was above, is below
    T_IA = 16  # Transit, is above
    T_IB = 32  # Transit, is below
    EN_WA = 64  # Entry, was above
    EN_WB = 128  # Entry, was below

    def __init__(self, tstat, vlo, vhi, color, callback, args=()):
        tstat.regions.add(self)
        tstat.draw = True
        self.tstat = tstat
        if vlo >= vhi:
            raise ValueError('TStat Region: vlo must be < vhi')
        self.vlo = vlo
        self.vhi = vhi
        self.color = color
        self.cb = callback
        self.args = args
        v = self.tstat.value()  # Get current value
        self.is_in = vlo <= v <= vhi  # Is initial value in region
        # .wa: was above. Value prior to any entry to region.
        self.wa = None # None indicates unknown
        
    # Where prior state is unknown because instantiation occurred with a value
    # in the region (.wa is None) we make the assumption that, on exit, it is
    # leaving from the opposite side from purported entry.
    def do_check(self, v):
        cb = self.cb
        args = self.args
        if v < self.vlo:
            if not self.is_in:
                if self.wa is None or self.wa:  # Low going transit
                    cb(self, self.T_IB, *args)
                return  # Was and is outside: no action.
            # Was in the region, find direction of exit
            reason = self.EX_WA_IB if (self.wa is None or self.wa) else self.EX_WB_IB
            cb(self, reason, *args)
        elif v > self.vhi:
            if not self.is_in:
                if self.wa is None or not self.wa:
                    cb(self, self.T_IA, *args)
                return
            # Was already in region
            reason = self.EX_WB_IA if (self.wa is None or not self.wa) else self.EX_WA_IA
            cb(self, reason, *args)
        else:  # v is in range
            if self.is_in:
                return  # Nothing to do
            if self.wa is None or self.wa:
                cb(self, self.EN_WA, *args)
            else:
                cb(self, self.EN_WB, *args)

    def check(self, v):
        self.do_check(v)
        self.is_in = self.vlo <= v <= self.vhi
        if not self.is_in:  # Current value is outside
            self.wa = v > self.vhi  # Save state for next check

    def adjust(self, vlo, vhi):
        if vlo >= vhi:
            raise ValueError('TStat Region: vlo must be < vhi')
        old_vlo = self.vlo
        old_vhi = self.vhi
        self.vlo = vlo
        self.vhi = vhi
        v = self.tstat.value()
        self.tstat.draw = True
        # Despatch cases where there is nothing to do.
        # Outside both regions on same side
        if v < vlo and v < old_vlo:
            return
        if v > vhi and v > old_vhi:
            return
        is_in = vlo <= v <= vhi  # Currently inside
        if is_in and self.is_in:  # Regions overlapped
            return  # Still inside so no action

        if is_in:  # Inside new region but not in old
            self.check(v)  # Treat as if entering new region from previous value
        else:  # Outside new region
            if not self.is_in:  # Also outside old region. Hence it lay
                # between old and new regions. Force a traverse of new.
                self.wa = v < vlo
            # If it was in old region treat as if leaving it
            self.check(v)


class Tstat(Meter):
    def __init__(self, *args, **kwargs):
        self.regions = set()
        super().__init__(*args, **kwargs)

    def del_region(self, reg):
        self.regions.discard(reg)
        self.draw = True

    # Called by subclass prior to drawing scale and data
    def preshow(self, x, y, width, height):
        for r in self.regions:
            ht = round(height * (r.vhi - r.vlo))
            y1 = y - round(height * r.vhi)
            display.fill_rect(x, y1, width, ht, r.color)

    def value(self, n=None, color=None):
        if n is None:
            return super().value()
        v = super().value(n, color)
        for r in self.regions:
            r.check(v)
        return v
