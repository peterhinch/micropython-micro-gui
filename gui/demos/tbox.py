# tbox.py Test/demo of Textbox widget for micro-gui

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# Usage:
# import gui.demos.tbox

# Initialise hardware and framebuf before importing modules.
import hardware_setup  # Create a display instance

from gui.core.ugui import Screen, ssd
from gui.core.writer import CWriter

import uasyncio as asyncio
from gui.core.colors import *
import gui.fonts.arial10 as arial10
from gui.widgets import Label, Textbox, Button, CloseButton

wri = CWriter(ssd, arial10)  # verbose = True

def fwdbutton(wri, row, col, cls_screen, text='Next'):
    def fwd(button):
        Screen.change(cls_screen)
    b = Button(wri, row, col,
           callback = fwd, fgcolor = BLACK, bgcolor = GREEN,
           text = text, shape = RECTANGLE)
    return b.mrow


async def wrap(tb):
    s = '''The textbox displays multiple lines of text in a field of fixed dimensions. \
Text may be clipped to the width of the control or may be word-wrapped. If the number \
of lines of text exceeds the height available, scrolling may be performed \
by calling a method.
'''
    tb.clear()
    tb.append(s, ntrim = 100, line = 0)
    while True:
        await asyncio.sleep(1)
        if not tb.scroll(1):
            break

async def clip(tb):
    ss = ('clip demo', 'short', 'longer line', 'much longer line with spaces',
          'antidisestablishmentarianism', 'line with\nline break', 'Done')
    tb.clear()
    for s in ss:
        tb.append(s, ntrim = 100) # Default line=None scrolls to show most recent
        await asyncio.sleep(1)

# Args for textboxes
# Positional
pargs = (2, 2, 100, 7)  # Row, Col, Width, nlines

# Keyword
tbargs = {'fgcolor' : YELLOW,
        'bdcolor' : RED,
        'bgcolor' : BLACK,
        }


class TBCScreen(Screen):
    def __init__(self):
        super().__init__()
        self.tb = Textbox(wri, *pargs, clip=True, **tbargs)
        CloseButton(wri)
        asyncio.create_task(self.main())

    async def main(self):
        await clip(self.tb)

class TBWScreen(Screen):
    def __init__(self):
        super().__init__()
        self.tb = Textbox(wri, *pargs, clip=False, **tbargs)
        CloseButton(wri)
        asyncio.create_task(self.main())

    async def main(self):
        await wrap(self.tb)

user_str = '''The textbox displays multiple lines of text in a field of fixed dimensions. \
Text may be clipped to the width of the control or may be word-wrapped. If the number \
of lines of text exceeds the height available, scrolling may be performed \
by calling a method.

Please use the increase and decrease buttons (or encoder) to scroll this text.
'''

class TBUScreen(Screen):
    def __init__(self):
        super().__init__()
        tb = Textbox(wri, *pargs, clip=False, active=True, **tbargs)
        tb.append(user_str, ntrim=100)
        CloseButton(wri)
        

class MainScreen(Screen):
    def __init__(self):
        super().__init__()
        Label(wri, 2, 2, 'Select test to run')
        col = 2
        row = 20
        row = fwdbutton(wri, row, col, TBWScreen, 'Wrap') + 2
        row = fwdbutton(wri, row, col, TBCScreen, 'Clip') + 2
        fwdbutton(wri, row, col, TBUScreen, 'Scroll')
        CloseButton(wri)
        

def test():
    if ssd.height < 128 or ssd.width < 128:
        print(' This test requires a display of at least 128x128 pixels.')
    else:
        print('Textbox demo.')
        Screen.change(MainScreen)

test()
