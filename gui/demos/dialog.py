# dialog.py micro-gui demo of the DialogBox class

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, Window, ssd

from gui.widgets.label import Label
from gui.widgets.buttons import Button, CloseButton
from gui.widgets.dialog import DialogBox
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.arial10 as arial10
from gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):
        super().__init__()
        # Callback for Button
        def fwd(button, my_kwargs):
            Screen.change(DialogBox, kwargs = my_kwargs)

        wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)

        row = 2
        col = 2
        # Trailing spaces ensure Label is wide enough to show results
        self.lbl = Label(wri, row, col, 'Dialog box test   ')
        # DialogBox constructor arguments. Here we pass all as keyword wargs.
        kwargs = {'writer' : wri,
                  'elements' : (('Yes', GREEN), ('No', RED), ('Foo', YELLOW)),
                  'label' : 'Test dialog',
                  }
        row = 30
        Button(wri, row, col, text = 'Dialog',
               bgcolor = RED, textcolor = WHITE,
               callback = fwd, args = (kwargs,))
        CloseButton(wri)  # Quit the application

    # Refresh the label after DialogBox has closed (but not when
    # the screen first opens).
    def after_open(self):
        if (v := Window.value()) is not None:
            self.lbl.value('Result: {}'.format(v))

def test():
    print('DialogBox demo.')
    Screen.change(BaseScreen)

test()
