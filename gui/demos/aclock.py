# aclock.py micro-gui analog clock demo.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# Initialise hardware and framebuf before importing modules.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd
from gui.widgets.label import Label
from gui.widgets.dial import Dial, Pointer
from gui.widgets.buttons import CloseButton

# Now import other modules
from cmath import rect, pi
import uasyncio as asyncio
import time
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as font
from gui.core.colors import *


# Adjust passed Dial and Label instances to show current time and date.
async def aclock(dial, lbldate, lbltim):
    # Return a unit vector of phase phi. Multiplying by this will
    # rotate a vector anticlockwise which is mathematically correct.
    # Alas clocks, modelled on sundials, were invented in the northern
    # hemisphere. Otherwise they would have rotated widdershins like
    # the maths. Hence negative sign when called.
    def uv(phi):
        return rect(1, phi)

    def suffix(n):
        if n in (1, 21, 31):
            return 'st'
        if n in (2, 22):
            return 'nd'
        if n in (3, 23):
            return 'rd'
        return 'th'

    days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
              'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

    hrs = Pointer(dial)
    mins = Pointer(dial)
    secs = Pointer(dial)

    hstart =  0 + 0.7j  # Pointer lengths. Will rotate relative to top.
    mstart = 0 + 1j
    sstart = 0 + 1j 

    while True:
        t = time.localtime()
        hrs.value(hstart * uv(-t[3] * pi/6 - t[4] * pi / 360), CYAN)
        mins.value(mstart * uv(-t[4] * pi/30), CYAN)
        secs.value(sstart * uv(-t[5] * pi/30), RED)
        lbltim.value('{:02d}.{:02d}.{:02d}'.format(t[3], t[4], t[5]))
        lbldate.value('{} {}{} {} {}'.format(days[t[6]], t[2], suffix(t[2]), months[t[1] - 1], t[0]))
        await asyncio.sleep(1)

class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        labels = {'bdcolor' : RED,
                  'fgcolor' : WHITE,
                  'bgcolor' : DARKGREEN,
                  }

        wri = CWriter(ssd, font, GREEN, BLACK)  # verbose = True
        dial = Dial(wri, 2, 2, height = 70, ticks = 12,
                    fgcolor = GREEN, pip = GREEN)
        # Set up clock display: instantiate labels
        # Demo of relative positioning.
        gap = 4  # Vertical gap between widgets
        row = dial.mrow + gap
        lbldate = Label(wri, row, 2, 100, **labels)
        row = lbldate.mrow + gap
        lbltim = Label(wri, row, 2, '00.00.00', **labels)
        self.reg_task(aclock(dial, lbldate, lbltim))
        CloseButton(wri)


def test():
    print('Analog clock demo.')
    Screen.change(BaseScreen)

test()
