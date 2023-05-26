# calendar.py Test Grid class. Requires date.py.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2023 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets import Grid, CloseButton, Label, Button
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.font10 as font
import gui.fonts.font14 as font1
from gui.core.colors import *
from .date import DateCal

class BaseScreen(Screen):

    def __init__(self):

        super().__init__()
        self.date = DateCal()
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
        for n, day in enumerate(DateCal.days):
            self.grid[0, n] = day[:3]

        row = self.grid.mrow + 4
        ht = 30
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="y-", callback=self.adjust, args=("y", -1))
        col = b.mcol + 2
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="y+", callback=self.adjust, args=("y", 1))
        col = b.mcol + 5
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="m-", callback=self.adjust, args=("m", -1))
        col = b.mcol + 2
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="m+", callback=self.adjust, args=("m", 1))
        col = b.mcol + 5
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="w-", callback=self.adjust, args=("d", -7))
        col = b.mcol + 2
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="w+", callback=self.adjust, args=("d", 7))
        col = b.mcol + 5
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="d-", callback=self.adjust, args=("d", -1))
        col = b.mcol + 2
        b = Button(wri, row, col, height=ht, shape=CIRCLE, text="d+", callback=self.adjust, args=("d", 1))
        col = b.mcol + 5
        b = Button(wri, row, col, height=ht, shape=CIRCLE, fgcolor=BLUE, text="H", callback=self.adjust, args=("h",))
        #row = b.mrow + 10
        col = 2
        row = ssd.height - (wri1.height + 2)
        self.lblnow = Label(wri1, row, col, text =ssd.width - 4, fgcolor=WHITE)
        self.update()
        CloseButton(wri)  # Quit the application

    def adjust(self, _, f, n=0):
        d = self.date
        if f == "y":
            d.year += n
        elif f == "m":
            d.month += n
        elif f == "d":
            d.day += n
        elif f =="h":
            d.now()
        self.update()

    def update(self):
        def cell():
            if cur.year == today.year and cur.month == today.month and mday == today.mday:  # Today
                d["fgcolor"] = RED
            elif mday == cur.mday:  # Currency
                d["fgcolor"] = YELLOW
            elif mday in sundays:
                d["fgcolor"] = BLUE
            else:
                d["fgcolor"] = GREEN
            d["text"] = str(mday)
            self.grid[idx] = d

        today = DateCal()
        cur = self.date  # Currency
        self.lbl.value(f"{DateCal.months[cur.month - 1]} {cur.year}")
        d = {}  # Args for Label.value
        wday = 0
        wday_1 = cur.wday_n(1)  # Weekday of 1st of month
        mday = 1
        seek = True
        sundays = cur.mday_list(6)
        for idx in range(7, self.grid.ncells):
            if seek:  # Find column for 1st of month
                if wday < wday_1:
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
        idx = 7  # Where another row would be needed, roll over to top few cells.
        while mday <= cur.month_length:
            cell()
            idx += 1
            mday += 1
        self.lblnow.value(f"{today.day_str} {today.mday} {today.month_str} {today.year}")


def test():
    print('Calendar demo.')
    Screen.change(BaseScreen)  # A class is passed here, not an instance.

test()
