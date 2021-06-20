# active.py micro-gui demo of widgets that respond to user control

# Create SSD instance. Must be done first because of RAM use.
import hardware_setup
from gui.core.ugui import Screen, ssd
from gui.core.writer import CWriter
import gui.fonts.arial10 as arial10  # Font for CWriter
from gui.core.colors import *
# Widgets
from gui.widgets.label import Label
from gui.widgets.scale import Scale
from gui.widgets.scale_log import ScaleLog
from gui.widgets.buttons import Button, CloseButton
from gui.widgets.sliders import Slider, HorizSlider
from gui.widgets.knob import Knob
from gui.widgets.checkbox import Checkbox


class BaseScreen(Screen):
    def __init__(self):

        def tickcb(f, c):
            if f > 0.8:
                return RED
            if f < -0.8:
                return BLUE
            return c

        def tick_log_cb(f, c):
            if f > 20_000:
                return RED
            if f < 4:
                return BLUE
            return c

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        col = 2
        row = 200
        Label(wri, row, col, 'Result')
        col = 42
        self.lbl = Label(wri, row, col, 70, bdcolor=RED)

        self.vslider = Slider(wri, 2, 2, callback=self.slider_cb,
                             bdcolor=RED, slotcolor=BLUE, prcolor=CYAN,
                             legends=('0.0', '0.5', '1.0'), value=0.5)

        col = 80
        row = 15
        self.hslider = HorizSlider(wri, row, col, callback=self.slider_cb,
                                   bdcolor=YELLOW, slotcolor=BLUE,
                                   legends=('0.0', '0.5', '1.0'), value=0.7)
        row += 30
        self.scale = Scale(wri, row, col, width = 150, tickcb = tickcb,
                pointercolor=RED, fontcolor=YELLOW, bdcolor=CYAN,
                callback=self.cb, active=True)
        row += 40
        self.scale_log = ScaleLog(wri, row, col, width = 150, tickcb = tick_log_cb,
                                  pointercolor=RED, fontcolor=YELLOW, bdcolor=CYAN,
                                  callback=self.cb, value=10, active=True)
        row = 120
        self.knob = Knob(wri, row, 2, callback = self.cb,
                         bgcolor=DARKGREEN, color=LIGHTRED)
        col = 150
        row = 185
        Checkbox(wri, row, col, callback=self.cbcb)
        col += 35
        Label(wri, row, col, 'Enable/disable')
        CloseButton(wri)


    def cb(self, obj):
        self.lbl.value('{:4.2f}'.format(obj.value()))

    def cbcb(self, cb):
        val = cb.value()
        self.vslider.greyed_out(val)
        self.hslider.greyed_out(val)
        self.scale.greyed_out(val)
        self.scale_log.greyed_out(val)
        self.knob.greyed_out(val)

    def slider_cb(self, s):
        self.cb(s)
        v = s.value()
        if v < 0.2:
            s.color(BLUE)
        elif v > 0.8:
            s.color(RED)
        else:
            s.color(GREEN)

def test():
    if ssd.height < 240 or ssd.width < 320:
        print(' This test requires a display of at least 320x240 pixels.')
    else:
        print('Testing micro-gui...')
        Screen.change(BaseScreen)

test()
