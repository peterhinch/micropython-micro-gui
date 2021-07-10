# menu.py Extension to micro-gui providing the Menu class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# Usage:
# from gui.widgets.menu import Menu

from gui.core.ugui import Window, Screen
from gui.widgets.buttons import Button
from gui.widgets.listbox import Listbox
from gui.core.colors import *

# A SubMenu is a Window containing a Listbox
# Next and Prev close the listbox without running the callback. This is
# handled by Screen .move bound method
class SubMenu(Window):

    def __init__(self, menu, button, elements, cb, args):  # menu is parent Menu
        wri = menu.writer
        row = 10
        col = button.col + 4 # Drop down below top level menu button
        # Need to determine Window dimensions from size of Listbox, which
        # depends on number and length of elements.
        entry_height, lb_height, textwidth = Listbox.dimensions(wri, elements)
        lb_width = textwidth + 2
        # Calculate Window dimensions
        ap_height = lb_height + 6  # Allow for listbox border
        ap_width = lb_width + 6
        super().__init__(row, col, ap_height, ap_width)
        self.listbox = Listbox(wri, row + 3, col + 3, elements = elements, width = lb_width,
                               fgcolor = button.fgcolor, bgcolor = button.bgcolor, bdcolor=False, 
                               fontcolor = button.textcolor, select_color = menu.select_color,
                               callback = self.callback)
        self.cb = cb
        self.args = args

    def callback(self, obj_listbox):
        Screen.back()
        self.cb(obj_listbox, *self.args) # CB can access obj_listbox.value() or .textvalue()

# A Menu is a set of Button objects at the top of the screen. On press, Buttons either run the
# user callback or instantiate a SubMenu
class Menu:

    def __init__(self, writer, *, height=25, bgcolor=None, fgcolor=None, textcolor=None, select_color=DARKBLUE, args):   # ((text, cb, (args,)),(text, cb, (args,), (elements,)), ...)
        self.writer = writer
        self.select_color = select_color
        row = 2
        col = 2
        btn = {'bgcolor' : bgcolor,
               'fgcolor' : fgcolor,
               'height' : height,
               'textcolor' : textcolor, }
        for arg in args:
            if len(arg) == 4:  # Handle submenu
                # txt, cb, (cbargs,), (elements,) = arg
                b = Button(writer, row, col, text=arg[0],
                           callback=self.cb, args=arg, **btn)
            else:
                txt, cb, cbargs = arg
                b = Button(writer, row, col, text=txt,
                           callback=cb, args=cbargs, **btn)
            col = b.mcol

    def cb(self, button, txt, user_cb, args, elements):  # Button pushed which calls submenu
        args = (self, button, elements, user_cb, args)
        Screen.change(SubMenu, args = args)
