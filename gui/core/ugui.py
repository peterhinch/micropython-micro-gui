# ugui.py Micropython GUI library

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019-2022 Peter Hinch

# Requires uasyncio V3

import uasyncio as asyncio
from uasyncio import Event
from time import ticks_diff, ticks_ms
import gc

from gui.core.colors import *
from hardware_setup import ssd

from gui.primitives.delay_ms import Delay_ms
from gui.primitives.switch import Switch

# Globally available singleton objects
display = None  # Singleton instance
ssd = None

gc.collect()
__version__ = (0, 1, 4)

# Null function
dolittle = lambda *_ : None

async def _g():
    pass
type_coro = type(_g())

_FIRST = const(0)
_NEXT = const(1)
_PREV = const(2)
_LAST = const(3)

# Wrapper for ssd providing buttons and framebuf compatible methods
class Display:
    verbose = True

    def __init__(self, objssd, nxt, sel, prev=None, incr=None, decr=None, encoder=False):
        global display, ssd
        self._next = Switch(nxt)
        self._sel = Switch(sel)
        self._last = None  # Last switch pressed.
        # Mandatory buttons
        # Call current screen bound method
        self._next.close_func(self._closure, (self._next, Screen.ctrl_move, _NEXT))
        self._sel.close_func(self._closure, (self._sel, Screen.sel_ctrl, 0))
        self._sel.open_func(Screen.unsel)

        self.height = objssd.height
        self.width = objssd.width

        # Optional buttons
        self._prev = None
        self.has_adjust_input = False
        if prev is not None:
            self._prev = Switch(prev)
            self._prev.close_func(self._closure, (self._prev, Screen.ctrl_move, _PREV))
        if encoder:
            self.verbose and print('Using encoder for up/down.')
            if incr is None or decr is None:
                raise ValueError('Must specify pins for encoder.')
            from gui.primitives.encoder import Encoder
            self._enc = Encoder(incr, decr, div=encoder, callback=Screen.adjust)
            self.has_adjust_input = True
        else:
            self.verbose and print('Using switches for up/down.')
            # incr and decr methods get the button as an arg.
            if incr is not None:
                sup = Switch(incr)
                sup.close_func(self._closure, (sup, Screen.adjust, 1))
                self.has_adjust_input = True
            if decr is not None:
                sdn = Switch(decr)
                sdn.close_func(self._closure, (sdn, Screen.adjust, -1))
                self.has_adjust_input = True
        self._is_grey = False  # Not greyed-out
        display = self  # Populate globals
        ssd = objssd

    # Reject button presses where a button is already pressed.
    # Execute if initialising, if same switch re-pressed or if last switch released
    def _closure(self, switch, func, arg):
        if (self._last is None) or (self._last == switch) or self._last():
            self._last = switch
            func(switch, arg)

    def print_centred(self, writer, x, y, text, fgcolor=None, bgcolor=None, invert=False):
        sl = writer.stringlen(text)
        writer.set_textpos(ssd, y - writer.height // 2, x - sl // 2)
        if self._is_grey:
            fgcolor = color_map[GREY_OUT]
        writer.setcolor(fgcolor, bgcolor)
        writer.printstring(text, invert)
        writer.setcolor()  # Restore defaults

    def print_left(self, writer, x, y, txt, fgcolor=None, bgcolor=None, invert=False):
        writer.set_textpos(ssd, y, x)
        if self._is_grey:
            fgcolor = color_map[GREY_OUT]
        writer.setcolor(fgcolor, bgcolor)
        writer.printstring(txt, invert)
        writer.setcolor()  # Restore defaults

    # Greying out has only one option given limitation of 4-bit display driver
    # It would be possible to do better with RGB565 but would need inverse transformation
    # to (r, g, b), scale and re-convert to integer.
    def _getcolor(self, color):  # Takes in an integer color, bit size dependent on driver
        return color_map[GREY_OUT] if self._is_grey and color != color_map[BG] else color

    def usegrey(self, val): # display.usegrey(True) sets greyed-out
        self._is_grey = val
        return self

    # Graphics primitives: despatch to device (i.e. framebuf) or
    # local function for methods not implemented by framebuf.
    # These methods support greying out color overrides.
    # Clear screen.
    def clr_scr(self):
        ssd.fill_rect(0, 0, self.width - 1, self.height - 1, color_map[BG])

    def rect(self, x1, y1, w, h, color):
        ssd.rect(x1, y1, w, h, self._getcolor(color))

    def fill_rect(self, x1, y1, w, h, color):
        ssd.fill_rect(x1, y1, w, h, self._getcolor(color))

    def vline(self, x, y, l, color):
        ssd.vline(x, y, l, self._getcolor(color))

    def hline(self, x, y, l, color):
        ssd.hline(x, y, l, self._getcolor(color))

    def line(self, x1, y1, x2, y2, color):
        ssd.line(x1, y1, x2, y2, self._getcolor(color))

    # Private method uses physical color
    def _circle(self, x0, y0, r, color): # Single pixel circle
        x = -r
        y = 0
        err = 2 -2*r
        while x <= 0:
            ssd.pixel(x0 -x, y0 +y, color)
            ssd.pixel(x0 +x, y0 +y, color)
            ssd.pixel(x0 +x, y0 -y, color)
            ssd.pixel(x0 -x, y0 -y, color)
            e2 = err
            if (e2 <= y):
                y += 1
                err += y*2 +1
                if (-x == y and e2 <= x):
                    e2 = 0
            if (e2 > x):
                x += 1
                err += x*2 +1

    def circle(self, x0, y0, r, color, width =1): # Draw circle (maybe grey)
        color = self._getcolor(color)
        x0, y0, r = int(x0), int(y0), int(r)
        for r in range(r, r -width, -1):
            self._circle(x0, y0, r, color)

    def fillcircle(self, x0, y0, r, color): # Draw filled circle
        color = self._getcolor(color)
        x0, y0, r = int(x0), int(y0), int(r)
        x = -r
        y = 0
        err = 2 -2*r
        while x <= 0:
            ssd.line(x0 -x, y0 -y, x0 -x, y0 +y, color)
            ssd.line(x0 +x, y0 -y, x0 +x, y0 +y, color)
            e2 = err
            if (e2 <= y):
                y +=1
                err += y*2 +1
                if (-x == y and e2 <= x):
                    e2 = 0
            if (e2 > x):
                x += 1
                err += x*2 +1

    def clip_rect(self, x, y, w, h, color):
        color = self._getcolor(color)
        c = 4
        ssd.hline(x + c, y, w - 2 * c, color)
        ssd.hline(x + c, y + h, w - 2 * c, color)
        ssd.vline(x, y + c, h - 2 * c, color)
        ssd.vline(x + w - 1, y + c, h - 2 * c, color)
        ssd.line(x + c, y, x, y + c, color)
        ssd.line(x + w - c - 1, y, x + w - 1, y + c, color)
        ssd.line(x, y + h - c - 1, x + c, y + h - 1, color)
        ssd.line(x + w - 1, y + h - c - 1, x + w - c - 1, y + h, color)

    def fill_clip_rect(self, x, y, w, h, color):
        color = self._getcolor(color)
        c = 4
        ssd.fill_rect(x, y + c, w, h - 2 * c, color)
        for z in range(c):
            l = w - 2 * (c - z)  # Line length
            ssd.hline(x + c - z, y + z, l, color)
            ssd.hline(x + c - z, y + h - z - 1, l, color)


class Screen:
    current_screen = None
    is_shutdown = Event()
    # These events enable user code to synchronise display refresh
    # to a realtime process.
    rfsh_start = Event()  # Refresh pauses until set (set by default).
    rfsh_done = Event()  # Flag a user task that a refresh was done.

    @classmethod
    def ctrl_move(cls, b, v):
        if cls.current_screen is not None:
            cls.current_screen.move(v, b)

    @classmethod
    def sel_ctrl(cls, b, _):
        if cls.current_screen is not None:
            cls.current_screen.do_sel()

    @classmethod
    def unsel(cls):
        if cls.current_screen is not None:
            cls.current_screen.unsel_i()

    # Adjust the value of a widget. If an encoder is used, button arg
    # is an int (discarded), val is the delta. If using buttons, 1st 
    # arg is the button, delta is +1 or -1
    @classmethod
    def adjust(cls, button, val):
        if cls.current_screen is not None:
            cls.current_screen.do_adj(button, val)

    # Move currency to a specific widget (e.g. ButtonList)
    @classmethod
    def select(cls, obj):
        if cls.current_screen is not None:
            return cls.current_screen.move_to(obj)
        
    @classmethod
    def show(cls, force):
        for obj in cls.current_screen.displaylist:
            if obj.visible: # In a buttonlist only show visible button
                if force or obj.draw:
                    obj.draw_border()
                    obj.show()
                    obj.draw = False

    @classmethod
    def change(cls, cls_new_screen, *, forward=True, args=[], kwargs={}):
        cs_old = cls.current_screen
        if cs_old is not None:  # Leaving an existing screen
            for entry in cls.current_screen.tasks:
                # Always cancel on back. Also on forward if requested.
                if entry[1] or not forward:
                    entry[0].cancel()
                    cls.current_screen.tasks.remove(entry)  # remove from list
            cs_old.on_hide()  # Optional method in subclass
        if forward:
            if isinstance(cls_new_screen, type):
                if isinstance(cs_old, Window):
                    raise ValueError('Windows are modal.')
                new_screen = cls_new_screen(*args, **kwargs)
                if not len(new_screen.lstactive):
                    raise ValueError("Screen has no active widgets.")
            else:
                raise ValueError('Must pass Screen class or subclass (not instance)')
            new_screen.parent = cs_old
            cs_new = new_screen
        else:
            cs_new = cls_new_screen # An object, not a class
        cls.current_screen = cs_new
        cs_new.on_open() # Optional subclass method
        cs_new._do_open(cs_old) # Clear and redraw
        cs_new.after_open() # Optional subclass method
        if cs_old is None:  # Initialising
            asyncio.run(Screen.monitor())  # Starts and ends uasyncio
            # Don't do asyncio.new_event_loop() as it prevents re-running
            # the same app.

    @classmethod
    async def monitor(cls):
        ar = asyncio.create_task(cls.auto_refresh())  # Start refreshing
        await cls.is_shutdown.wait()  # and wait for termination.
        cls.is_shutdown.clear()  # We're going down.
        # Task cancellation and shutdown
        ar.cancel()  # Refresh task
        for entry in cls.current_screen.tasks:
            # Screen instance will be discarded: no need to worry about .tasks
            entry[0].cancel()
        await asyncio.sleep_ms(0)  # Allow task cancellation to occur.
        display.clr_scr()
        ssd.show()
        cls.current_screen = None  # Ensure another demo can run

    # If the display driver has an async refresh method, determine the split
    # value which must be a factor of the height. In the unlikely event of
    # no factor, do_refresh confers no benefit, so use synchronous code.
    @classmethod
    async def auto_refresh(cls):
        arfsh = hasattr(ssd, 'do_refresh')  # Refresh can be asynchronous.
        # By default rfsh_start is permanently set. User code can clear this.
        cls.rfsh_start.set()
        if arfsh:
            h = ssd.height
            split = max(y for y in (1,2,3,5,7) if not h % y)
            if split == 1:
                arfsh = False
        while True:
            await cls.rfsh_start.wait()
            Screen.show(False)  # Update stale controls. No physical refresh.
            # Now perform physical refresh. 
            if arfsh:
                await ssd.do_refresh(split)
            else:
                ssd.show()  # Synchronous (blocking) refresh.
            # Flag user code.
            cls.rfsh_done.set()
            await asyncio.sleep_ms(0)  # Let user code respond to event

    @classmethod
    def back(cls):
        parent = cls.current_screen.parent
        if parent is None:  # Closing base screen. Quit.
            cls.shutdown()
        else:
            cls.change(parent, forward = False)

    @classmethod
    def addobject(cls, obj):
        cs = cls.current_screen
        if cs is None:
            raise OSError('You must create a Screen instance')
        # Populate list of active widgets (i.e. ones that can acquire focus).
        if obj.active:
            # Append to active list regrdless of disabled state which may
            # change at runtime.
            al = cs.lstactive
            empty = al == [] or all(o.greyed_out() for o in al)
            al.append(obj)
            if empty and not obj.greyed_out():
                cs.selected_obj = len(al) - 1  # Index into lstactive
        cs.displaylist.append(obj)  # All displayable objects

    @classmethod
    def shutdown(cls):
        cls.is_shutdown.set()  # Tell monitor() to shutdown

    def __init__(self):
        self.lstactive = []  # Controls which respond to Select button
        self.selected_obj = None  # Index of currently selected object
        self.displaylist = []  # All displayable objects
        self.tasks = []  # Instance can register tasks for cancellation
        self.height = ssd.height  # Occupies entire display
        self.width = ssd.width
        self.row = 0
        self.col = 0
        if Screen.current_screen is None: # Initialising class and task
            # Here we create singleton tasks
            asyncio.create_task(self._garbage_collect())
        Screen.current_screen = self
        self.parent = None

    def _do_open(self, old_screen): # Window overrides
        dev = display.usegrey(False)
        # If opening a Screen from a Window just blank and redraw covered area
        if isinstance(old_screen, Window):
            x0, y0, x1, y1, w, h = old_screen._list_dims()
            dev.fill_rect(x0, y0, w, h, color_map[BG]) # Blank to screen BG
            for obj in [z for z in self.displaylist if z.overlaps(x0, y0, x1, y1)]:
                if obj.visible:
                    obj.draw_border()
                    obj.show()
        # Normally clear the screen and redraw everything
        else:
            dev.clr_scr()  # Clear framebuf but don't update display
            Screen.show(True)  # Force full redraw

    # Return an active control or None
    # By default returns the selected control
    # else checks a given control by index into lstactive
    def get_obj(self, idx=None):
        so = self.selected_obj if idx is None else idx
        if so is not None:
            co = self.lstactive[so]
            if co.visible and not co.greyed_out():
                return co
        return None

    # Move currency to next enabled control. Arg is direction of move.
    def move(self, to, button):
        if to == _FIRST:
            idx = -1
            up = 1
        elif to == _LAST:
            idx = len(self.lstactive)
            up = -1
        else:
            idx = self.selected_obj
            up = 1 if to == _NEXT else -1

        lo = self.get_obj()  # Old current object

        # handle inc/dec with only 3 buttons
        if hasattr(lo, 'adjusting') and lo.adjusting:
            # invert direction to make more sense
            up = -up 
            self.do_adj(button, up)
            return

        done = False
        while not done:
            idx += up
            idx %= len(self.lstactive)
            co = self.get_obj(idx)
            if co is not None:
                if co is not lo:
                    self.selected_obj = idx
                    if lo is not None:
                        lo.leave()  # Tell object it's losing currency.
                        lo.show()  # Re-display with new status
                    co.enter()  # Tell object it has currency
                    co.show()
                #elif isinstance(self, Window):
                    # Special case of Window with one object: leave
                    # without making changes (Dropdown in particular)
                    #Screen.back()
                done = True

    # Move currency to a specific control.
    def move_to(self, obj):
        lo = self.get_obj()  # Old current object
        for idx in range(len(self.lstactive)) :
            co = self.get_obj(idx)
            if co is obj:
                self.selected_obj = idx
                if lo is not None:
                    lo.leave()  # Tell object it's losing currency.
                    lo.show()  # Re-display with new status
                co.enter()  # Tell object it has currency
                co.show()
                return True  # Success
        return False

    def do_sel(self):  # Direct to current control
        co = self.get_obj()
        if co is not None:
            co.do_sel()

    def unsel_i(self):
        co = self.get_obj()
        if co is not None:
            co.unsel()

    def do_adj(self, button, val):
        co = self.get_obj()
        if co is not None and hasattr(co, 'do_adj'):
            co.do_adj(button, val)  # Widget can handle up/down
        else:
            Screen.current_screen.move(_FIRST if val < 0 else _LAST, button)

    # Methods optionally implemented in subclass
    def on_open(self): 
        return

    def after_open(self):
        return

    def on_hide(self):
        return

    def locn(self, row, col):
        return self.row + row, self.col + col

    # Housekeeping methods
    def reg_task(self, task, on_change=False):  # May be passed a coro or a Task
        if isinstance(task, type_coro):
            task = asyncio.create_task(task)
        self.tasks.append((task, on_change))

    async def _garbage_collect(self):
        while True:
            await asyncio.sleep_ms(500)
            gc.collect()
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
            #print(gc.mem_free())

# Very basic window class. Cuts a rectangular hole in a screen on which
# content may be drawn.
class Window(Screen):

    _value = None
    # Allow a Window to store an arbitrary object. Retrieval may be
    # done by caller, after the Window instance was deleted
    @classmethod
    def value(cls, val=None):
        if val is not None:
            cls._value = val
        return cls._value

    @staticmethod
    def close():  # More intuitive name for popup window
        Screen.back()

    def __init__(self, row, col, height, width, *, draw_border=True,
                 bgcolor=None, fgcolor=None, writer=None):
        Screen.__init__(self)
        self.row = row
        self.col = col
        self.height = height
        self.width = width
        self.draw_border = draw_border
        self.fgcolor = fgcolor if fgcolor is not None else color_map[FG]
        self.bgcolor = bgcolor if bgcolor is not None else color_map[BG]
        if writer is not None:  # Special case of popup message
            DummyWidget(writer, self)  # Invisible active widget

    def _do_open(self, old_screen):
        dev = display.usegrey(False)
        x, y = self.col, self.row
        dev.fill_rect(x, y, self.width, self.height, self.bgcolor)
        if self.draw_border:
            dev.rect(x, y, self.width, self.height, self.fgcolor)
        Screen.show(True)

    def _list_dims(self):
        w = self.width
        h = self.height
        x = self.col
        y = self.row
        return x, y, x + w, y + h, w, h

# Base class for all displayable objects
class Widget:

    def __init__(self, writer, row, col, height, width,
                 fgcolor, bgcolor, bdcolor,
                 value=None, active=False):
        self.active = active
        self._greyed_out = False
        Screen.addobject(self)
        self.screen = Screen.current_screen
        writer.set_clip(True, True, False)  # Disable scrolling text
        self.writer = writer
        # The following assumes that the widget is mal-positioned, not oversize.
        if row < 0:
            row = 0
            self.warning()
        elif row + height >= ssd.height:
            row = ssd.height - height - 1
            self.warning()
        if col < 0:
            col = 0
            self.warning()
        elif col + width >= ssd.width:
            col = ssd.width - width - 1
            self.warning()
        self.row = row
        self.col = col
        self.height = height
        self.width = width
        # Maximum row and col. Defaults for user metrics. May be overridden
        self.mrow = row + height + 2  # in subclass. Allow for border.
        self.mcol = col + width + 2
        self.visible = True # Used by ButtonList class for invisible buttons
        self.draw = True  # Signals that obect must be redrawn
        self._value = value

        # Set colors. Writer colors cannot be None:
        #  bg == 0, fg == 1 are ultimate (monochrome) defaults.
        if fgcolor is None:
            fgcolor = writer.fgcolor
        if bgcolor is None:
            bgcolor = writer.bgcolor
        if bdcolor is None:
            bdcolor = fgcolor
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        # bdcolor is False if no border is to be drawn
        self.bdcolor = bdcolor
        # Default colors allow restoration after dynamic change
        self.def_fgcolor = fgcolor
        self.def_bgcolor = bgcolor
        self.def_bdcolor = bdcolor
        # has_border is True if a border was drawn
        self.has_border = False
        self.callback = dolittle # Value change callback
        self.args = []

        self.selcolor = None

    def warning(self):
        print('Warning: attempt to create {} outside screen dimensions.'.format(self.__class__.__name__))

    def value(self, val=None): # User method to get or set value
        if val is not None:
            if type(val) is float:
                val = min(max(val, 0.0), 1.0)
            if val != self._value:
                self._value = val
                self.draw = True  # Ensure a redraw on next refresh
                self.callback(self, *self.args)
        return self._value

    def __call__(self, val=None):
        return self.value(val)

    # Some widgets (e.g. Dial) have an associated Label
    def text(self, text=None, invert=False, fgcolor=None, bgcolor=None, bdcolor=None):
        if hasattr(self, 'label'):
            self.label.value(text, invert, fgcolor, bgcolor, bdcolor)
        else:
            raise ValueError('Method {}.text does not exist.'.format(self.__class__.__name__))

    # Called from subclass prior to populating framebuf with control
    def show(self, black=True):
        if self.screen != Screen.current_screen:
            # Can occur if a control's action is to change screen.
            return False  # Subclass abandons

        self.draw = False
        self.draw_border()
        # Blank controls' space
        if self.visible:
            dev = display.usegrey(self._greyed_out)
            x = self.col
            y = self.row
            dev.fill_rect(x, y, self.width, self.height, color_map[BG] if black else self.bgcolor)
        return True

# Called by Screen.show(). Draw background and bounding box if required.
# Border is always 2 pixels wide, outside control's bounding box
    def draw_border(self):
        if self.screen is Screen.current_screen:
            dev = display.usegrey(self._greyed_out)
            x = self.col - 2
            y = self.row - 2
            w = self.width + 4
            h = self.height + 4
            if self.has_focus() and not isinstance(self, DummyWidget):
                color = color_map[FOCUS]
                if hasattr(self, 'adjusting') and self.adjusting and self.selcolor is not None:
                    color = self.selcolor
                if hasattr(self, 'precision') and self.precision and self.prcolor is not None:
                    color = self.prcolor
                dev.rect(x, y, w, h, color)
                self.has_border = True
            else:
                if isinstance(self.bdcolor, bool):  # No border
                    if self.has_border:  # Border exists: erase it
                        dev.rect(x, y, w, h, color_map[BG])
                        self.has_border = False
                elif self.bdcolor:  # Border is required
                    dev.rect(x, y, w, h, self.bdcolor)
                    self.has_border = True

    def overlaps(self, xa, ya, xb, yb): # Args must be sorted: xb > xa and yb > ya
        x0 = self.col
        y0 = self.row
        x1 = x0 + self.width
        y1 = y0 + self.height
        if (ya <= y1 and yb >= y0) and (xa <= x1 and xb >= x0):
            return True
        return False

    def _set_callbacks(self, cb, args):  # Runs when value changes.
        self.callback = cb
        self.args = args

    def has_focus(self):
        if self.active:
            cs = Screen.current_screen
            if (cso := cs.selected_obj) is not None:
                return cs.lstactive[cso] is self
        return False

    def greyed_out(self, val=None):
        if val is not None and self.active and self._greyed_out != val:
            self._greyed_out = val
            if self.screen is Screen.current_screen:
                display.usegrey(val)
                self.draw_border()
                self.show()
        return self._greyed_out

    # Button press methods. Called from Screen if object not greyed out.
    # For subclassing if specific behaviour is required.
    def do_sel(self):  # Select button was pushed
        pass

    def unsel(self):  # Select button was released
        pass

    def enter(self):  # Control has acquired focus
        pass

    def leave(self):  # Control has lost focus
        pass

    # Optional methods. Implement for controls which respond to up and down.
    # No dummy methods as these would prevent "first" and "last" focus movement
    # when current control has focus but is inactive.
    # def do_up(self, button)
    # def do_down(self, button)

# A LinearIO widget uses the up and down buttons to vary a float. Such widgets
# have do_up and do_down methods which adjust the control's value in a
# time-dependent manner.
class LinearIO(Widget):
    def __init__(self, writer, row, col, height, width,
                fgcolor, bgcolor, bdcolor,
                value=None, active=True, prcolor=False,
                min_delta=0.01, max_delta=0.1):
        self.min_delta = min_delta
        self.max_delta = max_delta
        super().__init__(writer, row, col, height, width,
                fgcolor, bgcolor, bdcolor,
                value, active)
        # Handle variable precision. Start normal
        self.precision = False
        self.do_precision = prcolor is not False

        self.adjusting = False
        self.selcolor = color_map[ADJUSTING]
        
        if self.do_precision:
            # Subclass supports precision mode
            # 1 sec long press to set precise
            self.lpd = Delay_ms(self.precise, (True,))
            # Precision mode can only be entered when the active control has focus.
            # In this state it will have a white border. By default this turns yellow
            # but subclass can be defeat this with WHITE or another color
            self.prcolor = color_map[PRECISION] if prcolor is None else prcolor

    # Adjust widget's value. Args: button pressed, amount of increment
    def do_adj(self, button, val):
        encoder = isinstance(button, int)
        d = self.min_delta * 0.1 if self.precision else self.min_delta
        self.value(self.value() + val * d)
        if not encoder:
            asyncio.create_task(self.btnhan(button, val, d))

    # Handle increase and decrease buttons. Redefined by textbox.py, scale_log.py
    async def btnhan(self, button, up, d):
        maxd = self.max_delta if self.precision else d * 4  # Why move fast in precision mode?
        t = ticks_ms()
        while not button():
            await asyncio.sleep_ms(0)  # Quit fast on button release
            if ticks_diff(ticks_ms(), t) > 500:  # Button was held down
                d = min(maxd, d * 2)
                self.value(self.value() + up * d)
                t = ticks_ms()

    def precise(self, v):  # Timed out while button pressed
        self.precision = v
        # precision implies adjusting
        if not display.has_adjust_input:
            self.adjusting = v
        self.draw = True

    def do_sel(self):  # Select button was pushed
        if not display.has_adjust_input:
            self.adjusting = not self.adjusting
            self.draw = True
        if self.do_precision:  # Subclass handles precision mode
            if self.precision:  # Already in mode
                self.precise(False)
            else:  # Require a long press to enter mode
                self.lpd.trigger()

    def unsel(self):  # Select button was released
        self.do_precision and self.lpd.stop()

    def leave(self):  # Control has lost focus
        self.precise(False)

# The dummy enables popup windows by satisfying the need for at least one active
# widget on a screen. It is invisible and is drawn by Window constructor before
# any user labels..
class DummyWidget(Widget):
    
    def __init__(self, writer, window):
        super().__init__(writer, window.row + 1, window.col + 1, 4, 4,
                 window.fgcolor, window.bgcolor, False, None, True)
