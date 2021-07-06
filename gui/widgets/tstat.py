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

    def __init__(self, tstat, vlo, vhi, color, callback, args):
        self.tstat = tstat
        if vlo >= vhi:
            raise ValueError('TStat Region: vlo must be <= vhi')
        self.vlo = vlo
        self.vhi = vhi
        self.color = color
        self.cb = callback
        self.args = args
        self.is_in = False  # Value is in region
        self.fa = False  # Entered from above
        self.vprev = self.tstat.value()
        
    def do_check(self, v):
        cb = self.cb
        args = self.args
        if v < self.vlo:
            if not self.is_in:
                if self.vprev > self.vhi:  # Low going transit
                    cb(self, self.T_IB, *args)
                return  # Was and is outside: no action.
            # Was in the region, find direction of exit
            self.is_in = False
            reason = self.EX_WA_IB if self.fa else self.EX_WB_IB
            cb(self, reason, *args)
        elif v > self.vhi:
            if not self.is_in:
                if self.vprev < self.vlo:
                    cb(self, self.T_IA, *args)
                return
            # Was already in region
            self.is_in = False
            reason = self.EX_WA_IA if self.fa else self.EX_WB_IA
            cb(self, reason, *args)
        else:  # v is in range
            if self.is_in:
                return  # Nothing to do
            self.is_in = True
            if self.vprev > self.vhi:
                self.fa = True  # Save entry direction
                cb(self, self.EN_WA, *args)
            elif self.vprev < self.vlo:
                self.fa = False
                cb(self, self.EN_WB, *args)

    def check(self, v):
        self.do_check(v)
        self.vprev = v  # do_check gets value at prior check

    def adjust(self, vlo, vhi):
        old_vlo = self.vlo
        old_vhi = self.vhi
        self.vlo = vlo
        self.vhi = vhi
        vc = self.tstat.value()
        self.tstat.draw = True
        # Despatch cases where there is nothing to do.
        # Outside both regions on same side
        if vc < vlo and vc < old_vlo:
            return
        if vc > vhi and vc > old_vhi:
            return
        is_in = vlo <= vc <= vhi  # Currently inside
        if is_in and self.is_in:  # Regions overlapped
            return  # Still inside so no action

        if is_in:  # Inside new region but not in old
            self.check(vc)  # Treat as if entering new region from previous value
        else:  # Outside new region
            if not self.is_in:  # Also outside old region
                # Lay between old and new regions. Force
                # a traverse of new
                self.vprev = vlo - 0.1 if vc > vhi else vhi + 0.1
            # If it was in old region treat as if leaving it
            self.check(vc)


class Tstat(Meter):
    def __init__(self, *args, **kwargs):
        self.regions = set()
        super().__init__(*args, **kwargs)

    def add_region(self, vlo, vhi, color, callback, args=()):
        reg = Region(self, vlo, vhi, color, callback, args)
        self.regions.add(reg)
        return reg

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
