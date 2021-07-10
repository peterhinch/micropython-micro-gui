# menu.py micro-gui demo of Menu class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd
import gui.fonts.freesans20 as freesans20
from gui.core.writer import CWriter

from gui.widgets.menu import Menu
from gui.widgets.buttons import CloseButton
from gui.core.colors import *
from gui.widgets.dialog import DialogBox

class BaseScreen(Screen):

    def __init__(self):
        def cb(button, n):
            print('Top level callback', n)

        def cb_sm(lb, n):
            kwargs = {'writer' : wri, 'row': 60, 'col' : 2,
                    'elements' : (('Yes', GREEN), ('No', RED), ('Foo', YELLOW)),
                    'label' : 'Test dialog',
                    }
            print('Submenu callback', lb.value(), lb.textvalue(), n)
            if lb.value() == 0:
                Screen.change(DialogBox, kwargs = kwargs)

        super().__init__()
        mnu = (('Gas', cb_sm, (0,), ('Argon','Neon','Xenon','Radon')),
               ('Metal', cb_sm, (1,), ('Caesium', 'Lithium', 'Sodium', 'Potassium')),
               ('View', cb, (2,)))
        wri = CWriter(ssd, freesans20, GREEN, BLACK, verbose=False)
        Menu(wri, bgcolor=BLUE, textcolor=WHITE, args = mnu)
        CloseButton(wri)


Screen.change(BaseScreen)
