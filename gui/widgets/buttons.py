# buttons.py Extension to ugui providing pushbutton classes

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

import uasyncio as asyncio
from gui.core.ugui import Screen, Widget, display
from gui.core.colors import *

dolittle = lambda *_: None


class Button(Widget):
    lit_time = 1000

    def __init__(
        self,
        writer,
        row,
        col,
        *,
        shape=RECTANGLE,
        height=20,
        width=50,
        fgcolor=None,
        bgcolor=None,
        bdcolor=False,
        textcolor=None,
        litcolor=None,
        text="",
        callback=dolittle,
        args=[]
    ):
        sl = writer.stringlen(text)
        if shape == CIRCLE:  # Only height need be specified
            width = max(sl, height)
            height = width
        else:
            width = max(sl + 10, width)  # Allow 5 pixels before and after text
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor, False, True)
        self.shape = shape
        self.radius = height // 2
        self.litcolor = litcolor
        self.textcolor = self.fgcolor if textcolor is None else textcolor
        self.text = text
        self.callback = callback
        self.callback_args = args

    def show(self):
        if self.screen is not Screen.current_screen:
            return
        x = self.col
        y = self.row
        w = self.width
        h = self.height
        if not self.visible:  # erase the button
            display.usegrey(False)
            display.fill_rect(x, y, w, h, self.bgcolor)
            return
        super().show()  # Blank rectangle containing button
        if self.shape == CIRCLE:  # Button coords are of top left corner of bounding box
            x += self.radius
            y += self.radius
            display.fillcircle(x, y, self.radius, self.bgcolor)
            display.circle(x, y, self.radius, self.fgcolor)
            if len(self.text):
                display.print_centred(self.writer, x, y, self.text, self.textcolor, self.bgcolor)
        else:
            xc = x + w // 2
            yc = y + h // 2
            if self.shape == RECTANGLE:  # rectangle
                display.fill_rect(x, y, w, h, self.bgcolor)
                display.rect(x, y, w, h, self.fgcolor)
                if len(self.text):
                    display.print_centred(
                        self.writer, xc, yc, self.text, self.textcolor, self.bgcolor
                    )
            elif self.shape == CLIPPED_RECT:  # clipped rectangle
                display.fill_clip_rect(x, y, w, h, self.bgcolor)
                display.clip_rect(x, y, w, h, self.fgcolor)
                if len(self.text):
                    display.print_centred(
                        self.writer, xc, yc, self.text, self.textcolor, self.bgcolor
                    )

    async def shownormal(self):  # Revert to normal color after a delay
        try:
            await asyncio.sleep_ms(Button.lit_time)
        except asyncio.CancelledError:  # Or prior to a screen change
            pass
        self.bgcolor = self.def_bgcolor
        self.draw = True  # Redisplay

    def do_sel(self):  # Select was pushed
        self.callback(self, *self.callback_args)  # CB takes self as 1st arg.
        if self.litcolor is not None and self.has_focus():  # CB may have changed focus
            if self.bgcolor != self.litcolor:
                self.bgcolor = self.litcolor
                self.draw = True  # Redisplay
                revert = asyncio.create_task(self.shownormal())
                Screen.current_screen.reg_task(revert, True)  # Cancel on screen change


# Preferred way to close a screen or dialog. Produces an X button at the top RHS.
# Note that if the bottom screen is closed, the application terminates.
class CloseButton(Button):
    def __init__(self, writer, width=0, callback=dolittle, args=(), bgcolor=RED):
        scr = Screen.current_screen
        # Calculate the button width if not provided. Button allows
        # 5 pixels either side.
        wd = width if width else (writer.stringlen("X") + 10)
        self.user_cb = callback
        self.user_args = args
        super().__init__(
            writer,
            *scr.locn(4, scr.width - wd - 4),
            width=wd,
            height=wd,
            bgcolor=bgcolor,
            callback=self.cb,
            text="X"
        )

    def cb(self, _):
        self.user_cb(self, *self.user_args)
        Screen.back()


# Group of buttons, typically at same location, where pressing one shows
# the next e.g. start/stop toggle or sequential select from short list
class ButtonList:
    def __init__(self, callback=dolittle, new_cb=False):
        self.user_callback = callback
        self._new_cb = new_cb
        self.lstbuttons = []
        self.current = None  # No current button
        self._greyed_out = False

    def add_button(self, *args, **kwargs):
        button = Button(*args, **kwargs)
        self.lstbuttons.append(button)
        active = self.current is None  # 1st button added is active
        button.visible = active
        button.callback = self._callback
        if active:
            self.current = button
        return button

    def value(self, button=None, new_cb=False):
        if button is not None and button is not self.current:
            old = self.current
            new = button
            self.current = new
            old.visible = False
            new.visible = True
            new.draw = True  # Redisplay without changing currency
            # Args for user callback: button instance followed by any specified.
            # Normal behaviour is to run cb of old button (see docs).
            # This may be overridden for programmatic value changes, or for
            # physical button presses via constructor arg. See docs.
            if new_cb or self._new_cb:
                self.user_callback(new, *new.callback_args)
            else:
                self.user_callback(old, *old.callback_args)
        return self.current

    def greyed_out(self, val=None):
        if val is not None and self._greyed_out != val:
            self._greyed_out = val
            for button in self.lstbuttons:
                button.greyed_out(val)
            self.current.draw = True
        return self._greyed_out

    def _callback(self, button, *_):
        old = button
        old_index = self.lstbuttons.index(button)
        new = self.lstbuttons[(old_index + 1) % len(self.lstbuttons)]
        self.current = new
        old.visible = False
        new.visible = True
        Screen.select(new)  # Move currency and redisplay
        if self._new_cb:
            self.user_callback(new, *new.callback_args)
        else:
            self.user_callback(old, *old.callback_args)


# Group of buttons at different locations, where pressing one shows
# only current button highlighted and oes callback from current one
class RadioButtons:
    def __init__(self, highlight, callback=dolittle, selected=0):
        self.user_callback = callback
        self.lstbuttons = []
        self.current = None  # No current button
        self.highlight = highlight
        self.selected = selected
        self._greyed_out = False

    def add_button(self, *args, **kwargs):
        button = Button(*args, **kwargs)
        self.lstbuttons.append(button)
        button.callback = self._callback
        active = len(self.lstbuttons) == self.selected + 1
        button.bgcolor = self.highlight if active else button.def_bgcolor
        if active:
            self.current = button
        return button

    def value(self, button=None):
        if button is not None and button is not self.current:
            self._callback(button, *button.callback_args)
        return self.current

    def greyed_out(self, val=None):
        if val is not None and self._greyed_out != val:
            self._greyed_out = val
            for button in self.lstbuttons:
                button.greyed_out(val)
        return self._greyed_out

    def _callback(self, button, *args):
        for but in self.lstbuttons:
            if but is button:
                but.bgcolor = self.highlight
                self.current = button
            else:
                but.bgcolor = but.def_bgcolor
            but.draw = True
        self.user_callback(button, *args)  # user gets button with args they specified
