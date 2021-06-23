# linked_sliders.py Minimal micro-gui demo one Slider controlling two others.

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets.buttons import CloseButton
from gui.widgets.sliders import Slider
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):
        args = {
                'bdcolor' : RED,
                'slotcolor' : BLUE,
                'legends' : ('0.0', '0.5', '1.0'), 
                'value' : 0.5,
                }
        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        col = 2
        row = 2
        dc = 45
        # Note: callback runs now, but other sliders have not yet been instantiated.
        self.s0 = Slider(wri, row, col, callback=self.slider_cb, **args)
        col += dc
        self.s1 = Slider(wri, row, col, **args)
        col += dc
        self.s2 = Slider(wri, row, col, **args)
        CloseButton(wri)

    def slider_cb(self, s):
        v = s.value()
        if hasattr(self, 's1'):  # If s1 & s2 have been instantiated
            self.s1.value(v)
            self.s2.value(v)

def test():
    print('Linked sliders. Leftmost one controls others.')
    Screen.change(BaseScreen)

test()
