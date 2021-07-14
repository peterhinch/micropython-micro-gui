# menu.py micro-gui demo of Menu class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd
import gui.fonts.freesans20 as font
from gui.core.writer import CWriter

from gui.widgets.menu import Menu
from gui.widgets.buttons import CloseButton
from gui.core.colors import *

class BaseScreen(Screen):

    def __init__(self):
        def cb(button, n):
            print('Help callback', n)

        def cb_sm(lb, n):
            print('Submenu callback', lb.value(), lb.textvalue(), n)

        super().__init__()
        mnu = (('Gas', (('Helium', cb_sm, (0,)),
                        ('Neon', cb_sm, (1,)),
                        ('Argon', cb_sm, (2,)),
                        ('Krypton', cb_sm, (3,)),
                        ('Xenon', cb_sm, (4,)),
                        ('Radon', cb_sm, (5,)))),
               ('Metal',(('Lithium', cb_sm, (6,)),
                         ('Sodium', cb_sm, (7,)),
                         ('Potassium', cb_sm, (8,)),
                         ('Rubidium', cb_sm, (9,)),
                         ('More', (('Gold', cb_sm, (6,)),
                                   ('Silver', cb_sm, (7,)),
                                   ('Iron', cb_sm, (8,)),
                                   ('Zinc', cb_sm, (9,)),
                                   ('Copper', cb_sm, (10,)))))),
               ('Help', cb, (2,)))
        wri = CWriter(ssd, font, GREEN, BLACK, verbose=False)
        Menu(wri, bgcolor=BLUE, textcolor=WHITE, args = mnu)
        CloseButton(wri)


Screen.change(BaseScreen)
