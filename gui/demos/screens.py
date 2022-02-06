# screens.py micro-gui demo of multiple screens, dropdowns etc

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, Window, ssd

from gui.widgets.label import Label
from gui.widgets import Button, RadioButtons, CloseButton, Listbox, Dropdown, DialogBox
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *

# Note that litcolor is defeated by design, because the callback's action
# is to change the screen currency. This tests the bugfix.
def fwdbutton(writer, row, col, cls_screen, text, color, *args, **kwargs):
    def fwd(button):
        Screen.change(cls_screen, args = args, kwargs = kwargs)
    Button(writer, row, col, callback = fwd, bgcolor = color, litcolor = YELLOW,
           text = text, textcolor = WHITE, shape = CLIPPED_RECT)

# Demo of creating a dialog manually
class UserDialogBox(Window):
    def __init__(self, writer, callback, args):

        def back(button, text):
            Window.value(text)
            callback(Window, *args)
            Screen.back()

        def close_cb(button, text):
            Window.value(text)
            callback(Window, *args)

        height = 80
        width = 150
        super().__init__(20, 20, height, width, bgcolor = DARKGREEN)
        row = self.height - 30
        # .locn converts Window relative row, col to absolute row, col
        Button(writer, *self.locn(row, 20), height = 20, width = 50, textcolor = BLACK, bgcolor = RED,
               text = 'Cat', callback = back, args = ('Cat',))
        Button(writer, *self.locn(row, 80), height = 20, width = 50, textcolor = BLACK, bgcolor = GREEN,
               text = 'Dog', callback = back, args = ('Dog',))
        CloseButton(writer, callback=close_cb, args = ('Close',))

# Minimal screen change example
class Overlay(Screen):
    def __init__(self):
        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)
        Label(wri, 20, 20, 'Screen overlays base')
        CloseButton(wri)

class BaseScreen(Screen):

    def __init__(self):

        def lbcb(lb):
            print('Listbox', lb.textvalue())

        def ddcb(dd):
            print('Dropdown', tv := dd.textvalue())
            if tv == 'new screen':
                Screen.change(Overlay)
        
        def dbcb(window, label):
            label.value('Auto Dialog: {}'.format(window.value()))

        def udbcb(window, label):
            label.value('User Dialog: {}'.format(window.value()))

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)

        col = 2
        row = 2
        Listbox(wri, row, col, callback=lbcb,
                elements = ('cat', 'dog', 'aardvark', 'goat', 'pig', 'mouse'),
                bdcolor = GREEN, bgcolor = DARKGREEN,
                also = Listbox.ON_LEAVE)
        col = 70
        Dropdown(wri, row, col, callback=ddcb,
                elements = ('hydrogen', 'helium', 'neon', 'xenon', 'new screen'),
                bdcolor = GREEN, bgcolor = DARKGREEN)
        row += 30
        lbl = Label(wri, row, col, 'Result from dialog box.')
        row += 20
        dialog_elements = (('Yes', GREEN), ('No', RED), ('Foo', YELLOW))
        # 1st 6 args are for fwdbutton
        fwdbutton(wri, row, col, DialogBox, 'Dialog', RED,
                  # Args for DialogBox constructor
                  wri, elements = dialog_elements, label = 'Test dialog', callback = dbcb, args = (lbl,))
        col += 60
        fwdbutton(wri, row, col, UserDialogBox, 'User', BLUE,
                  # Args for UserDialogBox constructor
                  wri, udbcb, (lbl,))
        CloseButton(wri)  # Quit the application

def test():
    if ssd.height < 128 or ssd.width < 240:
        print('This test requires a display of at least 240x128 pixels.')
    else:
        print('Testing micro-gui...')
        Screen.change(BaseScreen)

test()
