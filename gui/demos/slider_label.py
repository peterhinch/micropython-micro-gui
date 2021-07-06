# slider_label.py Minimal micro-gui demo showing a Slider controlling a Label.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets.buttons import CloseButton
from gui.widgets.sliders import Slider
from gui.widgets.label import Label
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
        self.lbl = Label(wri, row + 45, col + 50, 35, bdcolor=RED, bgcolor=DARKGREEN)
        # Instantiate Label first, because Slider callback will run now.
        # See linked_sliders.py for another approach.
        Slider(wri, row, col, callback=self.slider_cb,
               bdcolor=RED, slotcolor=BLUE,
               legends=('0.0', '0.5', '1.0'), value=0.5)
        CloseButton(wri)

    def slider_cb(self, s):
        v = s.value()
        self.lbl.value('{:5.3f}'.format(v))

def test():
    print('Slider Label demo. Long press select for precision mode.')
    Screen.change(BaseScreen)

test()
