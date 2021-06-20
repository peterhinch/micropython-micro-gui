# various.py micro-gui demo of multiple controls on a large display

# Initialise hardware and framebuf before importing modules.
# Create SSD instance. Must be done first because of RAM use.
import hardware_setup

from gui.core.ugui import Screen, ssd
from gui.core.writer import CWriter
import gui.fonts.arial10 as arial10  # Font for CWriter
from gui.core.colors import *
# Widgets
from gui.widgets.label import Label
from gui.widgets.dial import Dial, Pointer
from gui.widgets.meter import Meter
from gui.widgets.scale import Scale
from gui.widgets.buttons import Button, ButtonList, RadioButtons, CloseButton
from gui.widgets.checkbox import Checkbox
from gui.widgets.led import LED

import cmath
import uasyncio as asyncio
import utime
import gc


class FooScreen(Screen):
    def __init__(self):
        buttons = []

        # A ButtonList with two entries
        table_buttonset = (
            {'fgcolor' : RED, 'text' : 'Disable', 'args' : (buttons, True)},
            {'fgcolor' : GREEN, 'text' : 'Enable', 'args' : (buttons, False)},
        )

        table_radiobuttons = (
            {'text' : '1', 'args' : ('1',)},
            {'text' : '2', 'args' : ('2',)},
            {'text' : '3', 'args' : ('3',)},
            {'text' : '4', 'args' : ('4',)},
        )

        def tickcb(f, c):
            if f > 0.8:
                return RED
            if f < -0.8:
                return BLUE
            return c

        def bcb(b):
            print('Button pressed', b)

        super().__init__()
        self.rb0 = None
        self.bs0 = None
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        lbltim = Label(wri, 65, 100, 'this is a test', bdcolor=RED)

        m0 = Meter(wri, 10, 240, divisions = 4, ptcolor=YELLOW, height=80, width=15,
                label='Meter example', style=Meter.BAR, legends=('0.0', '0.5', '1.0'))
        # Instantiate displayable objects. bgcolor forces complete redraw.
        dial = Dial(wri, 2, 2, height = 75, ticks = 12, bgcolor=BLACK, bdcolor=None, label=120)  # Border in fg color
        scale = Scale(wri, 2, 100, width = 124, tickcb = tickcb,
                pointercolor=RED, fontcolor=YELLOW, bdcolor=CYAN)

        row = 105
        col = 2
        Label(wri, row, col, 'Normal buttons')
        # Four Button instances
        row = 120
        ht = 30
        for i, s in enumerate(('a', 'b', 'c', 'd')):
            col= 2 + i * (ht + 5)
            buttons.append(Button(wri, row, col, height=ht, callback=bcb, text=s, litcolor=RED, shape=CIRCLE, bgcolor=DARKGREEN))

        # ButtonList
        self.bs = ButtonList(self.callback)
        self.bs0 = None
        col+= 50
        Label(wri, row - 15, col, 'ButtonList')
        for t in table_buttonset: # Buttons overlay each other at same location
            button = self.bs.add_button(wri, row, col, shape=RECTANGLE, textcolor=BLUE, height=30, **t)
            if self.bs0 is None: # Save for reset button callback
                self.bs0 = button

        # Reset button
        col+= 60
        btn = Button(wri, row, col, height=30, callback=self.rstcb, text='reset', litcolor=RED, fgcolor=GREEN, bgcolor=DARKGREEN)

        col = 2
        row = 170
        Label(wri, row, col, 'Radio buttons')
        # Radio buttons
        row = 185
        self.rb = RadioButtons(BLUE, self.rbcb) # color of selected button
        self.rb0 = None
        for t in table_radiobuttons:
            button = self.rb.add_button(wri, row, col, textcolor = WHITE,
                                fgcolor = BLUE, bgcolor = DARKBLUE, shape=CIRCLE, height = 30, **t)
            if self.rb0 is None: # Save for reset button callback
                self.rb0 = button
            col+= 35
        # Checkbox
        col+= 35
        Label(wri, row - 15, col, 'Checkbox and LED')
        Checkbox(wri, row, col, callback=self.cbcb)
        col+= 40
        self.led = LED(wri, row, col, color=YELLOW, bdcolor=GREEN)
        CloseButton(wri)
        asyncio.create_task(run(dial, lbltim, m0, scale))


    def callback(self, button, buttons, val):
        buttons[2].greyed_out(val)

    def rbcb(self, button, val):
        print('RadioButtons callback', val)

    def rstcb(self, button):
        print('Reset button: init ButtonList and RadioButtons')
        self.bs.value(self.bs0)
        self.rb.value(self.rb0)

    def cbcb(self, cb):
        self.led.value(cb.value())
        gc.collect()
        print('Free RAM:', gc.mem_free())

async def run(dial, lbltim, m0, scale):
    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday')
    months = ('Jan', 'Feb', 'March', 'April', 'May', 'June', 'July',
            'Aug', 'Sept', 'Oct', 'Nov', 'Dec')
    uv = lambda phi : cmath.rect(1, phi)  # Return a unit vector of phase phi
    pi = cmath.pi
    hrs = Pointer(dial)
    mins = Pointer(dial)
    secs = Pointer(dial)

    hstart =  0 + 0.7j  # Pointer lengths and position at top
    mstart = 0 + 0.92j
    sstart = 0 + 0.92j 

    cv = -1.0  # Scale
    dv = 0.005
    while True:
        t = utime.localtime()
        hrs.value(hstart * uv(-t[3]*pi/6 - t[4]*pi/360), YELLOW)
        mins.value(mstart * uv(-t[4] * pi/30), YELLOW)
        secs.value(sstart * uv(-t[5] * pi/30), RED)
        lbltim.value('{:02d}.{:02d}.{:02d}'.format(t[3], t[4], t[5]))
        dial.text('{} {} {} {}'.format(days[t[6]], t[2], months[t[1] - 1], t[0]))
        m0.value(t[5]/60)
        scale.value(cv)
        await asyncio.sleep_ms(200)
        cv += dv
        if abs(cv) > 1.0:
            dv = -dv
            cv += dv


def test():
    if ssd.height < 240 or ssd.width < 320:
        print(' This test requires a display of at least 320x240 pixels.')
    else:
        print('Testing micro-gui...')
        Screen.change(FooScreen)

test()
