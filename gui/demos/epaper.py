# epaper.py micro-gui demo of multiple controls on an ePaper display type
# https://www.waveshare.com/pico-epaper-4.2.htm
# Use with setup_examples/pico_epaper_42_pico.py

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2023-2024 Peter Hinch

# Colors:
# The driver is designed so that code written for color displays produces an acceptable
# result. Unlike other displays an EPD has a white background, with the highest luminance
# colors displaying as black. When writing code for an EPD, use WHITE for foreground color
# and BLACK for background. i.e. treat as if it were an emissive screen.

# Initialise hardware and framebuf before importing modules.
# Create SSD instance. Must be done first because of RAM use.
import hardware_setup

from gui.core.ugui import Screen, ssd
from gui.core.writer import CWriter
import gui.fonts.arial10 as arial10  # Font for CWriter
import gui.fonts.freesans20 as large

from gui.core.colors import *

# Option to leave image in place on exit:
# ssd.blank_on_exit = False
# Widgets
from gui.widgets import (
    Label,
    Dial,
    Pointer,
    Meter,
    Scale,
    Button,
    ButtonList,
    RadioButtons,
    CloseButton,
    Checkbox,
    LED,
)
from gui.widgets.graph import CartesianGraph, Curve

from math import sin, pi
import cmath
import uasyncio as asyncio
import utime
import gc


async def full_refresh():
    async with Screen.rfsh_lock:
        ssd.set_full()
    await asyncio.sleep_ms(0)  # Lock released, allow a refresh to start
    await set_partial()  # Waits for it to complete before changing


async def set_partial():
    await ssd.complete.wait()  # Ensure 1st refresh is a full refresh
    async with Screen.rfsh_lock:
        ssd.set_partial()  # Subsequent refreshes are partial.


class FooScreen(Screen):
    def __init__(self):
        buttons = []

        # A ButtonList with two entries
        table_buttonset = (
            {"fgcolor": WHITE, "text": "Disable", "args": (buttons, True)},
            {"fgcolor": WHITE, "text": "Enable", "args": (buttons, False)},
        )

        def bcb(b):
            print("Button pressed", b)

        super().__init__()
        self.rb0 = None
        self.bs0 = None
        wri = CWriter(ssd, arial10, WHITE, BLACK, verbose=False)
        wri_large = CWriter(ssd, large, WHITE, BLACK, verbose=False)
        lbltim = Label(wri, 65, 100, "00:00:00 ", bdcolor=WHITE)

        m0 = Meter(
            wri,
            10,
            240,
            divisions=4,
            ptcolor=WHITE,
            height=80,
            width=15,
            label="Meter",
            style=Meter.BAR,
            legends=("0.0", "0.5", "1.0"),
        )
        # Instantiate displayable objects. bgcolor forces complete redraw.
        dial = Dial(wri, 2, 2, height=75, ticks=12, bdcolor=None, label=120)
        scale = Scale(wri, 2, 100, width=124)

        row = 105
        col = 2
        Label(wri, row, col, "Normal buttons")
        # Four Button instances
        row = 120
        ht = 30
        for i, s in enumerate(("a", "b", "c", "d")):
            col = 2 + i * (ht + 5)
            buttons.append(
                Button(
                    wri,
                    row,
                    col,
                    height=ht,
                    callback=bcb,
                    text=s,
                    litcolor=WHITE,
                    shape=CIRCLE,
                )
            )

        # ButtonList
        self.bs = ButtonList(self.callback)
        self.bs0 = None
        col += 50
        Label(wri, row - 15, col, "ButtonList")
        for t in table_buttonset:  # Buttons overlay each other at same location
            button = self.bs.add_button(wri, row, col, shape=RECTANGLE, height=30, **t)
            if self.bs0 is None:  # Save for reset button callback
                self.bs0 = button

        # Reset button
        col += 60
        btn = Button(wri, row, col, height=30, callback=self.rstcb, text="reset", litcolor=WHITE)

        col = btn.mcol + 15
        # Checkbox
        Label(wri, row - 15, col, "Checkbox and LED")
        Checkbox(wri, row, col, callback=self.cbcb)
        col += 40
        self.led = LED(wri, row, col, bdcolor=WHITE)

        row = self.bs0.mrow + 5
        col = 20
        ht = 75
        wd = 200
        self.graph = CartesianGraph(wri, row, col, height=ht, width=wd, bdcolor=False)
        Label(wri, row + ht + 5, col - 10, "-2.0")
        Label(wri, row + ht + 5, col - 8 + int(wd // 2), "0.0")
        lbl = Label(wri, row + ht + 5, col - 10 + wd, "2.0")
        Label(wri_large, lbl.mrow + 5, col, "y = sinc(x)")
        # Power on hours
        col = 240
        l = Label(wri, row, col, "Running hours")
        row = l.mrow + 2
        Label(wri, row, col, "Power")
        self.lpon = Label(wri, row, col + 40, "0000", bdcolor=WHITE)
        row = self.lpon.mrow + 4
        Label(wri, row, col, "Reset")
        self.lrst = Label(wri, row, col + 40, "0000", bdcolor=WHITE)
        row = self.lrst.mrow + 4
        Label(wri, row, col, "Total")
        self.ltot = Label(wri, row, col + 40, "0000", bdcolor=WHITE)
        self.hrs = [0, 0, 0]  # pon, reset, total
        self.fn = "hours"
        try:
            with open(self.fn, "r") as f:
                self.hrs[2] = int(f.read())
        except OSError:
            self.hrs[2] = 0

        CloseButton(wri, bgcolor=BLACK)
        asyncio.create_task(set_partial())  # After 1st full refresh
        asyncio.create_task(run(dial, lbltim, m0, scale))
        asyncio.create_task(self.runtime())

    async def runtime(self):
        while True:
            self.lpon.value(f"{self.hrs[0]:04d}")
            self.lrst.value(f"{self.hrs[1]:04d}")
            self.ltot.value(f"{self.hrs[2]:04d}")
            for n, v in enumerate(self.hrs):
                self.hrs[n] = v + 1
            with open(self.fn, "w") as f:
                f.write(f"{self.hrs[2]:d}")
            await asyncio.sleep(3600)

    def callback(self, button, buttons, val):
        buttons[2].greyed_out(val)

    def rstcb(self, button):
        print("Reset button: init ButtonList, do full refresh.")
        self.bs.value(self.bs0)
        asyncio.create_task(full_refresh())
        self.hrs[1] = 0  # Reset time since reset
        self.lrst.value(f"{self.hrs[1]:04d}")

    def cbcb(self, cb):
        self.led.value(cb.value())
        gc.collect()
        print("Free RAM:", gc.mem_free())

    def after_open(self):
        def populate():
            x = -0.998
            while x < 1.01:
                z = 6 * pi * x
                y = sin(z) / z
                yield x, y
                x += 0.05

        Curve(self.graph, None, populate())


async def run(dial, lbltim, m0, scale):
    days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    months = (
        "Jan",
        "Feb",
        "March",
        "April",
        "May",
        "June",
        "July",
        "Aug",
        "Sept",
        "Oct",
        "Nov",
        "Dec",
    )
    uv = lambda phi: cmath.rect(1, phi)  # Return a unit vector of phase phi
    pi = cmath.pi
    hrs = Pointer(dial)
    mins = Pointer(dial)
    secs = Pointer(dial)

    hstart = 0 + 0.7j  # Pointer lengths and position at top
    mstart = 0 + 0.92j
    sstart = 0 + 0.92j

    cv = -1.0  # Scale
    dv = 0.005
    while True:
        t = utime.localtime()
        hrs.value(hstart * uv(-t[3] * pi / 6 - t[4] * pi / 360))  # , YELLOW)
        mins.value(mstart * uv(-t[4] * pi / 30))  # , YELLOW)
        secs.value(sstart * uv(-t[5] * pi / 30))  # , RED)
        lbltim.value("{:02d}.{:02d}.{:02d}".format(t[3], t[4], t[5]))
        dial.text("{} {} {} {}".format(days[t[6]], t[2], months[t[1] - 1], t[0]))
        m0.value(t[5] / 60)
        scale.value(cv)
        await asyncio.sleep_ms(200)
        cv += dv
        if abs(cv) > 1.0:
            dv = -dv
            cv += dv


def test():
    print("Testing micro-gui...")
    Screen.change(FooScreen)
    print("End")
    ssd.sleep()  # Tidy shutdown of EPD


test()
