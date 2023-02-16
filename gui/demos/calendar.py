# calendar.py Test Grid class.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2023 Peter Hinch
# As written requires a 240*320 pixel display, but could easily be reduced
# with smaller fonts.

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets import Grid, CloseButton, Label, Button
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.font10 as font
import gui.fonts.font14 as font1
from gui.core.colors import *

from time import mktime, localtime
SECS_PER_DAY = const(86400)

class Date:

    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')
    months = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
              'September', 'October', 'November', 'December')

    def __init__(self):
        self.now()

    def now(self):
        lt = list(localtime())
        lt[3] = 6  # Disambiguate midnight
        self.cur = mktime(lt) // SECS_PER_DAY
        self.update()

    def update(self, lt=None):
        if lt is not None:
            lt[3] = 6
            self.cur = mktime(lt) // SECS_PER_DAY
        lt = localtime(self.cur * SECS_PER_DAY)
        self.year = lt[0]
        self.month = lt[1]
        self.mday = lt[2]
        self.wday = lt[6]
        ml = self.mlen(self.month)
        self.month_length = ml
        self.wday1 = (self.wday - self.mday + 1) % 7  # Weekday of 1st of month
        # Commented out code provides support for UK DST calculation
        #wdayld = (self.wday1 + ml -1) % 7  # Weekday of last day of month
        #self.mday_sun = ml - (wdayld + 1) % 7  # Day of month of last Sunday

    def add_days(self, n):
        self.cur += n
        self.update()
    
    def add_months(self, n):  # Crude algorithm for small n
        for _ in range(abs(n)):
            self.cur += self.month_length if n > 0 else -self.mlen(self.month - 1)
            self.update()

    def add_years(self, n):
        lt = list(localtime(self.cur * SECS_PER_DAY))
        lt[0] += n
        self.update(lt)

    def mlen(self, month):
        days = (31, 0, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[month - 1]
        year = self.year
        return days if days else (28 if year % 4 else (29 if year % 100 else 28))
    

class BaseScreen(Screen):

    def __init__(self):

        super().__init__()
        self.date = Date()
        wri = CWriter(ssd, font, GREEN, BLACK, False)
        wri1 = CWriter(ssd, font1, WHITE, BLACK, False)
        col = 2
        row = 2
        rows = 6
        cols = 7
        colwidth = 35
        self.lbl = Label(wri, row, col, text = (colwidth + 4) * cols, justify=Label.CENTRE)
        row = self.lbl.mrow
        self.grid = Grid(wri, row, col, colwidth, rows, cols, justify=Label.CENTRE)
        for n, day in enumerate(Date.days):
            self.grid[[0, n]] = day[:3]

        row = self.grid.mrow + 4
        ht = 30
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="y-", callback=self.adjust, args=(self.date.add_years, -1))
        col = b.mcol + 2
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="y+", callback=self.adjust, args=(self.date.add_years, 1))
        col = b.mcol + 5
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="m-", callback=self.adjust, args=(self.date.add_months, -1))
        col = b.mcol + 2
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="m+", callback=self.adjust, args=(self.date.add_months, 1))
        col = b.mcol + 5
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="w-", callback=self.adjust, args=(self.date.add_days, -7))
        col = b.mcol + 2
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="w+", callback=self.adjust, args=(self.date.add_days, 7))
        col = b.mcol + 5
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="d-", callback=self.adjust, args=(self.date.add_days, -1))
        col = b.mcol + 2
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="d+", callback=self.adjust, args=(self.date.add_days, 1))
        col = b.mcol + 5
        b = Button(wri, row, col, height=ht, shape=CIRCLE, fgcolor=BLUE, text="H", callback=self.adjust, args=(self.date.now,))
        #row = b.mrow + 10
        col = 2
        row = ssd.height - (wri1.height + 2)
        self.lblnow = Label(wri1, row, col, text =ssd.width - 4, fgcolor=WHITE)
        self.update()
        CloseButton(wri)  # Quit the application

    def adjust(self, _, f, n=0):
        f(n) if n else f()
        self.update()

    def update(self):
        def cell():
            #d.clear()
            if cur.year == today.year and cur.month == today.month and mday == today.mday:  # Today
                d["fgcolor"] = RED
            elif mday == cur.mday:  # Currency
                d["fgcolor"] = YELLOW
            else:
                d["fgcolor"] = GREEN
            d["text"] = str(mday)
            self.grid[idx] = d

        today = Date()
        cur = self.date  # Currency
        self.lbl.value(f"{Date.months[cur.month - 1]} {cur.year}")
        d = {}  # Args for Label.value
        wday = 0
        mday = 1
        seek = True
        for idx in range(7, self.grid.ncells):
            self.grid[idx] = ""
        for idx in range(7, self.grid.ncells):
            if seek:  # Find column for 1st of month
                if wday < cur.wday1:
                    self.grid[idx] = ""
                    wday += 1
                else:
                    seek = False
            if not seek:
                if mday <= cur.month_length:
                    cell()
                    mday += 1
                else:
                    self.grid[idx] = ""
        idx = 7
        while mday <= cur.month_length:
            cell()
            idx += 1
            mday += 1
        day = Date.days[today.wday]
        month = Date.months[today.month - 1]
        self.lblnow.value(f"{day} {today.mday} {month} {today.year}")


def test():
    print('Calendar demo.')
    Screen.change(BaseScreen)  # A class is passed here, not an instance.

test()
