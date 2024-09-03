# color_image.py Minimal micro-gui demo.

# Released under the MIT License (MIT). See LICENSE.


import hardware_setup  # Create a display instance

from gui.core.ugui import Screen, ssd

from gui.widgets import Label, Button, CloseButton
from gui.widgets.color_bitmap import ColorBitMap
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *

import test_bitmap


class BaseScreen(Screen):

    def __init__(self):
        super().__init__()
        # verbose default indicates if fast rendering is enabled
        wri = CWriter(ssd, arial10, GREEN, BLACK)

        image = ColorBitMap(
            wri,
            20,
            0,
            96,
            318,
        )
        image.value(test_bitmap)
        CloseButton(wri)  # Quit the application


def test():
    print("Color image demo for 170x320px display")
    Screen.change(BaseScreen)  # A class is passed here, not an instance.


test()
