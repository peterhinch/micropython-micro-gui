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

    def __init__(self, menu, button, elements):  # menu is parent Menu
        self.menu = menu
        self.button = button
        wri = menu.writer
        row = button.height + 2
        col = button.col  # Drop down below top level menu button
        # Need to determine Window dimensions from size of Listbox, which
        # depends on number and length of elements.
        te = [x[0] for x in elements]  # Text part
        self.elements = elements
        entry_height, lb_height, _, textwidth = Listbox.dimensions(wri, te, None)
        lb_width = textwidth + 2
        # Calculate Window dimensions
        ap_height = lb_height + 6  # Allow for listbox border
        ap_width = lb_width + 6
        super().__init__(row, col, ap_height, ap_width)
        Listbox(wri, row + 3, col + 3, elements = te, width = lb_width,
                fgcolor = button.fgcolor, bgcolor = button.bgcolor, bdcolor=False, 
                fontcolor = button.textcolor, select_color = menu.select_color,
                callback = self.callback)

    def callback(self, lbox):
        Screen.back()
        el = self.elements[lbox.value()]  # (text, cb, args)
        if len(el) == 2:  # Recurse into submenu
            args = (self.menu, self.button, el[1])
            Screen.change(SubMenu, args = args)
        else:
            el[1](lbox, *el[2])

# A Menu is a set of Button objects at the top of the screen. On press, Buttons either run the
# user callback or instantiate a SubMenu
# args is a list comprising items which may be a mixture of two types
# Single items: (top_text, cb, (args, ...))
# Submenus: (top_text, ((mnu_text, cb, (args, ...)),(mnu_text, cb, (args, ...)),...)
class Menu:

    def __init__(self, writer, *, height=25, bgcolor=None, fgcolor=None,
                 textcolor=None, select_color=DARKBLUE, args):
        self.writer = writer
        self.select_color = select_color
        row = 2
        col = 2
        btn = {'bgcolor' : bgcolor,
               'fgcolor' : fgcolor,
               'height' : height,
               'textcolor' : textcolor, }
        for arg in args:
            if len(arg) == 2:  # Handle submenu
                # txt, ((element, cb, (cbargs,)),(element,cb, (cbargs,)), ..) = arg
                b = Button(writer, row, col, text=arg[0],
                           callback=self.cb, args=arg, **btn)
            else:
                txt, cb, cbargs = arg
                b = Button(writer, row, col, text=txt,
                           callback=cb, args=cbargs, **btn)
            col = b.mcol

    def cb(self, button, txt, elements):  # Button pushed which calls submenu
        args = (self, button, elements)
        Screen.change(SubMenu, args = args)
