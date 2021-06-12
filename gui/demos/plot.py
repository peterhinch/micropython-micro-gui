# plot.py Test/demo program for micro-gui plot. Cross-patform,
# but requires a large enough display.
# Tested on Adafruit ssd1351-based OLED displays:
# Adafruit 1.5" 128*128 OLED display: https://www.adafruit.com/product/1431
# Adafruit 1.27" 128*96 display https://www.adafruit.com/product/1673

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# Create SSD instance. Must be done first because of RAM use.
from hardware_setup import ssd

import cmath
import math
import uasyncio as asyncio
from collections import OrderedDict

from gui.core.writer import Writer, CWriter
from gui.core.ugui import Screen
from gui.widgets.graph import PolarGraph, PolarCurve, CartesianGraph, Curve, TSequence
from gui.widgets.label import Label
from gui.widgets.buttons import Button, CloseButton
from gui.widgets.listbox import Listbox

# Fonts & colors
import gui.fonts.arial10 as arial10
from gui.core.colors import *

wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)

def fwdbutton(writer, row, col, cls_screen, text, color, *args, **kwargs):
    def fwd(button):
        Screen.change(cls_screen, args = args, kwargs = kwargs)
    Button(writer, row, col, callback = fwd, bgcolor = color,
           text = text, textcolor = BLACK, height = 20, width = 60)


class EmptyScreen(Screen):
    def __init__(self):
        super().__init__()
        Label(wri, 2, 2, 'Test of overlay.')
        Label(wri, 20, 2, 'Check redraw of underlying screen.')
        CloseButton(wri)

class CartesianScreen(Screen):
    def __init__(self):
        super().__init__()
        self.g = CartesianGraph(wri, 2, 2, yorigin = 2, fgcolor=GREEN,
                                gridcolor=LIGHTGREEN) # Asymmetric y axis
        Label(wri, 100, 2, 'Asymmetric axes.')
        fwdbutton(wri, 30, 130, EmptyScreen, 'Forward', GREEN)
        CloseButton(wri)
        # At this point in time the Screen and graph have been constructed but
        # not rendered. If we drew the curves now they would be overwritten by
        # the graph

    # Now the graph has been drawn and we can overlay it with graphics primitives.
    # This is not a uasyncio issue, but is the way Screen.change() is coded.
    def after_open(self):
        def populate_1(func):
            x = -1
            while x < 1.01:
                yield x, func(x)  # x, y
                x += 0.1

        def populate_2():
            x = -1
            while x < 1.01:
                yield x, x**2  # x, y
                x += 0.1

        Curve(self.g, YELLOW, populate_1(lambda x : x**3 + x**2 -x,)) # args demo
        Curve(self.g, RED, populate_2())

class PolarScreen(Screen):
    def __init__(self):
        super().__init__()
        self.g = PolarGraph(wri, 2, 2, fgcolor=GREEN, gridcolor=LIGHTGREEN)
        fwdbutton(wri, 30, 130, EmptyScreen, 'Forward', GREEN)
        CloseButton(wri)

    def after_open(self):  # After graph has been drawn
        def populate():
            def f(theta):
                return cmath.rect(math.sin(3 * theta), theta) # complex
            nmax = 150
            for n in range(nmax + 1):
                yield f(2 * cmath.pi * n / nmax)  # complex z

        PolarCurve(self.g, YELLOW, populate())

class Lissajous(Screen):
    def __init__(self):
        super().__init__()
        self.g = CartesianGraph(wri, 2, 2, fgcolor=GREEN, gridcolor=LIGHTGREEN)
        Label(wri, 100, 2, 'Lissajous figure.')
        fwdbutton(wri, 30, 130, EmptyScreen, 'Forward', GREEN)
        CloseButton(wri)

    def after_open(self):  # After graph has been drawn
        def populate():
            t = -math.pi
            while t <= math.pi:
                yield math.sin(t), math.cos(3*t)  # x, y
                t += 0.1

        Curve(self.g, YELLOW, populate())

class Lemniscate(Screen):
    def __init__(self):
        super().__init__()
        self.g = CartesianGraph(wri, 2, 2, height = 75, fgcolor=GREEN, gridcolor=LIGHTGREEN)
        Label(wri, 82, 2, 'To infinity and beyond...')
        fwdbutton(wri, 30, 130, EmptyScreen, 'Forward', GREEN)
        CloseButton(wri)

    def after_open(self):  # After graph has been drawn
        def populate():
            t = -math.pi
            while t <= math.pi + 0.1:
                x = 0.5*math.sqrt(2)*math.cos(t)/(math.sin(t)**2 + 1)
                y = math.sqrt(2)*math.cos(t)*math.sin(t)/(math.sin(t)**2 + 1)
                yield x, y
                t += 0.1

        Curve(self.g, YELLOW, populate())

class PolarClip(Screen):
    def __init__(self):
        super().__init__()
        self.g = PolarGraph(wri, 2, 2, fgcolor=GREEN, gridcolor=LIGHTGREEN)
        Label(wri, 100, 2, 'Clipping of polar data.')
        fwdbutton(wri, 30, 130, EmptyScreen, 'Forward', GREEN)
        CloseButton(wri)

    def after_open(self):  # After graph has been drawn
        def populate(rot):
            f = lambda theta : cmath.rect(1.15 * math.sin(5 * theta), theta) * rot # complex
            nmax = 150
            for n in range(nmax + 1):
                yield f(2 * cmath.pi * n / nmax)  # complex z

        PolarCurve(self.g, YELLOW, populate(1))
        PolarCurve(self.g, RED, populate(cmath.rect(1, cmath.pi/5),))

class RTPolar(Screen):
    def __init__(self):
        super().__init__()
        self.g = PolarGraph(wri, 2, 2, fgcolor=GREEN, gridcolor=LIGHTGREEN)
        Label(wri, 100, 2, 'Realtime polar data.')
        fwdbutton(wri, 30, 130, EmptyScreen, 'Forward', GREEN)
        CloseButton(wri)

    def after_open(self):  # After graph has been drawn
        self.reg_task(self.run(self.g), True)  # Cancel on screen change

    async def run(self, g):
        await asyncio.sleep_ms(0)
        curvey = PolarCurve(g, YELLOW)
        curver = PolarCurve(g, RED)
        for x in range(100):
            curvey.point(cmath.rect(x/100, -x * cmath.pi/30))
            curver.point(cmath.rect((100 - x)/100, -x * cmath.pi/30))
            await asyncio.sleep_ms(60)

class RTRect(Screen):
    def __init__(self):
        super().__init__()
        self.g = CartesianGraph(wri, 2, 2, fgcolor=GREEN, gridcolor=LIGHTGREEN)
        Label(wri, 100, 2, 'Realtime discontinuous data.')
        fwdbutton(wri, 30, 130, EmptyScreen, 'Forward', GREEN)
        CloseButton(wri)

    def after_open(self):  # After graph has been drawn
        self.reg_task(self.run(self.g), True)  # Cancel on screen change

    async def run(self, g):
        await asyncio.sleep_ms(0)
        curve = Curve(g, RED)
        x = -1
        for _ in range(40):
            y = 0.1/x if abs(x) > 0.05 else None  # Discontinuity
            curve.point(x, y)
            await asyncio.sleep_ms(100)
            x += 0.05
        g.clear()
        curve = Curve(g, YELLOW)
        x = -1
        for _ in range(40):
            y = -0.1/x if abs(x) > 0.05 else None  # Discontinuity
            curve.point(x, y)
            await asyncio.sleep_ms(100)
            x += 0.05

class TSeq(Screen):
    def __init__(self):
        super().__init__()
        self.g = CartesianGraph(wri, 2, 2, xorigin = 10, fgcolor=GREEN,
                           gridcolor=LIGHTGREEN, bdcolor=False)
        Label(wri, 100, 2, 'Time sequence.')
        fwdbutton(wri, 30, 130, EmptyScreen, 'Forward', GREEN)
        CloseButton(wri)

    def after_open(self):  # After graph has been drawn
        self.reg_task(self.run(self.g), True)  # Cancel on screen change

    async def run(self, g):
        await asyncio.sleep_ms(0)
        tsy = TSequence(g, YELLOW, 50)
        tsr = TSequence(g, RED, 50)
        t = 0
        while True:
            g.show()  # Redraw the empty graph
            tsy.add(0.9*math.sin(t/10))
            tsr.add(0.4*math.cos(t/10))  # Plot the new curves
            await asyncio.sleep_ms(400)
            t += 1


class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        d = OrderedDict()
        d['Cartesian'] = CartesianScreen
        d['Polar'] = PolarScreen
        d['Lissajous'] = Lissajous
        d['Lemniscate'] = Lemniscate
        d['Polar clipping'] = PolarClip
        d['Realtime polar'] = RTPolar
        d['Realtime rect'] = RTRect
        d['Time sequence'] = TSeq

        row = 2
        col = 2
        Listbox(wri, row, col, callback=self.lbcb, args=(d,),
                elements = tuple(d.keys()),
                bdcolor = GREEN, bgcolor = DARKGREEN)
        CloseButton(wri)

    def lbcb(self, lb, d):
        Screen.change(d[lb.textvalue()])

def test():
    if ssd.height < 128 or ssd.width < 200:
        print(' This test requires a display of at least 128x200 pixels.')
    else:
        print('Testing micro-gui...')
        Screen.change(BaseScreen)

test()
