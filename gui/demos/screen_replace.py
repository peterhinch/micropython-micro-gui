# screen_replace.py deemo showing non-stacked screens

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2024 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets import Button, CloseButton, Label
from gui.core.writer import CWriter

# Font for CWriter
import gui.fonts.freesans20 as font
from gui.core.colors import *

wri = CWriter(ssd, font, GREEN, BLACK, verbose=False)

# Defining a button in this way enables it to be re-used on
# multiple Screen instances. Note that a Screen class is
# passed, not an instance.
def fwdbutton(wri, row, col, cls_screen, text="Next", args=()):
    def fwd(button):
        Screen.change(cls_screen, args=args)  # Callback

    Button(wri, row, col, height=30, callback=fwd, fgcolor=BLACK, bgcolor=GREEN, text=text)


def navbutton(wri, row, col, gen, delta, text):
    def nav(button):
        cls_screen, num = gen(delta)  # gen.send(delta)
        Screen.change(cls_screen, mode=Screen.REPLACE, args=(num,))  # Callback

    Button(wri, row, col, height=30, callback=nav, fgcolor=BLACK, bgcolor=YELLOW, text=text)


class RingScreen(Screen):
    def __init__(self, num):
        super().__init__()
        Label(wri, 2, 2, f"Ring screen no. {num}.")
        navbutton(wri, 40, 2, nav, -1, "Left")
        navbutton(wri, 40, 80, nav, 1, "Right")
        CloseButton(wri)


# Create a tuple of Screen subclasses (in this case all are identical).
ring = ((RingScreen, 0), (RingScreen, 1), (RingScreen, 2))

# Define a means of navigating between these classes
def navigator():
    x = 0

    def nav(delta):
        nonlocal x
        v = x
        x = (x + delta) % len(ring)
        return ring[x]

    return nav


nav = navigator()

# This screen overlays BaseScreen.
class StackScreen(Screen):
    def __init__(self):
        super().__init__()
        Label(wri, 2, 2, "Stacked screen.")
        fwdbutton(wri, 40, 2, RingScreen, args=(0,))
        CloseButton(wri)


class BaseScreen(Screen):
    def __init__(self):

        super().__init__()
        Label(wri, 2, 2, "Base screen.")
        fwdbutton(wri, 40, 2, StackScreen)
        CloseButton(wri)


s = """
Demo of screen replace. Screen hierarchy:

Base Screen
 |
Stacked Screen
 |
<- Ring Screen 0 <-> Ring Screen 1 <-> Ring Screen 2 ->
"""


def test():
    print(s)
    Screen.change(BaseScreen)  # Pass class, not instance!


test()
