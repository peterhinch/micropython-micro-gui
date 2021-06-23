# slider.py Minimal micro-gui demo showing a Slider with variable color.

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup
from gui.core.ugui import Screen, ssd

from gui.widgets.buttons import CloseButton
from gui.widgets.sliders import Slider
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        col = 2
        row = 2
        Slider(wri, row, col, callback=self.slider_cb,
               bdcolor=RED, slotcolor=BLUE,
               legends=('0.0', '0.5', '1.0'), value=0.5)
        CloseButton(wri)

    def slider_cb(self, s):
        v = s.value()
        if v < 0.2:
            s.color(BLUE)
        elif v > 0.8:
            s.color(RED)
        else:
            s.color(GREEN)

def test():
    print('Slider demo.')
    Screen.change(BaseScreen)

test()
