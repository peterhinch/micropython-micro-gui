# dialog.py Extension to ugui providing the DialogBox class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

from gui.core.ugui import display, Window, Screen
from gui.core.colors import *
from gui.widgets.label import Label
from gui.widgets.buttons import Button, CloseButton

dolittle = lambda *_ : None

class DialogBox(Window):
    def __init__(self, writer, row=20, col=20, *, elements, label=None,
                 bgcolor=DARKGREEN, buttonwidth=25, closebutton=True, callback=dolittle, args=[]):

        def back(button, text):  # Callback for normal buttons
            Window.value(text)
            callback(Window, *args)
            Screen.back()

        def backbutton(button, text):
            Window.value(text)
            callback(Window, *args)

        height = 80
        spacing = 10
        buttonwidth = max(max(writer.stringlen(e[0]) for e in elements) + 4, buttonwidth)
        buttonheight = max(writer.height, 15)
        nelements = len(elements)
        width = spacing + (buttonwidth + spacing) * nelements
        if label is not None:
            width = max(width, writer.stringlen(label) + 2 * spacing)
        super().__init__(row, col, height, width, bgcolor = bgcolor)

        col = spacing # Coordinates relative to window
        row = self.height - buttonheight - 10
        gap = 0
        if nelements > 1:
            gap = ((width - 2 * spacing) - nelements * buttonwidth) // (nelements - 1)
        if label is not None:
            r, c = self.locn(10, col)
            Label(writer, r, c, label, bgcolor = bgcolor)
        for text, color in elements:
            Button(writer, *self.locn(row, col), height = buttonheight, width = buttonwidth,
                   textcolor = BLACK, bgcolor = color,
                   text = text, shape = RECTANGLE,
                   callback = back, args = (text,))
            col += buttonwidth + gap

        if closebutton:
            CloseButton(writer, callback = backbutton, args = ('Close',))
