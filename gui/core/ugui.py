# ugui.py Micropython GUI library

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019-2023 Peter Hinch

# Credit to Bart Cerneels for devising and prototyping the 3-button mode
# Also for suggesting abstracting the input device class.
# Now requires firmware >= V1.20

import uasyncio as asyncio
from time import ticks_diff, ticks_ms
import gc
from array import array
import sys

from gui.core.colors import *
from gui.primitives import Pushbutton

if sys.implementation.version < (1, 20, 0):
    raise OSError("Firmware V1.20 or later required.")

# Globally available singleton objects
display = None  # Singleton instance
ssd = None
_vb = True

gc.collect()
__version__ = (0, 1, 11)


async def _g():
    pass


type_coro = type(_g())

# Navigation destinations
_FIRST = const(0)
_NEXT = const(1)
_PREV = const(2)
_LAST = const(3)


def quiet():
    global _vb
    _vb = False


# Input abstracts input from 2-5 pushbuttons or 3 buttons + encoder. Handles
# transitions between modes (normal, precision, adjustment)
# BTN class instantiates a push button (may be other than a switch).
class Input:
    def __init__(self, nxt, sel, prev, incr, decr, encoder, BTN):
        self._encoder = encoder  # Encoder in use
        self._precision = False  # Precision mode
        self._adj = False  # Adjustment mode
        # Count buttons
        self._nb = sum(1 for x in (nxt, sel, prev, incr, decr) if x is not None)
        # Mandatory buttons
        self._next = BTN(nxt)
        self._sel = BTN(sel, suppress=True)
        # Call current screen bound method
        self._next.press_func(Screen.ctrl_move, (_NEXT,))
        self._sel.release_func(Screen.sel_ctrl)
        if encoder or (self._nb > 2):  # Can use precision mode when in adjust mode
            self._sel.long_func(self.precision, (True,))
        if self._nb == 3:  # Special case of 3-button interface
            self._sel.double_func(self.adj_mode)  # Double click toggles adjust
        # Optional buttons
        if prev is not None:
            self._prev = BTN(prev)
            self._prev.press_func(Screen.ctrl_move, (_PREV,))
        if encoder:
            _vb and print("Using encoder.")
            if incr is None or decr is None:
                raise ValueError("Must specify pins for encoder.")
            from gui.primitives import Encoder

            self._enc = Encoder(incr, decr, div=encoder, callback=Screen.adjust)
        else:
            _vb and print("Using {:d} switches.".format(self._nb))
            # incr and decr methods get the button as an arg.
            if incr is not None:
                sup = BTN(incr)
                sup.press_func(Screen.adjust, (sup, 1))
            if decr is not None:
                sdn = BTN(decr)
                sdn.press_func(Screen.adjust, (sdn, -1))

    def precision(self, val):  # Also called by Screen.ctrl_move to cancel mode
        if val:
            if self._nb == 3 and not self._adj:
                self.adj_mode()
            self._precision = True
        else:
            self._precision = False
        Screen.redraw_co()

    def adj_mode(self, v=None):  # Set, clear or toggle adjustment mode
        if self._nb == 3:  # Called from menu and dropdown widgets
            self._adj = not self._adj if v is None else v
            # Change button function
            if self._adj:
                self._prev.press_func(Screen.adjust, (self._prev, -1))
                self._next.press_func(Screen.adjust, (self._next, 1))
            else:
                self._prev.press_func(Screen.ctrl_move, (_PREV,))
                self._next.press_func(Screen.ctrl_move, (_NEXT,))
                self._precision = False
            Screen.redraw_co()

    def encoder(self):
        return self._encoder

    def is_precision(self):
        return self._precision

    def is_adjust(self):
        return self._adj


# Special mode where an encoder with a "press" pushbutton is the only control.
# nxt and prev are Pin instances corresponding to encoder X and Y.
# sel is a Pin for the encoder's pushbutton.
# encoder is the division ratio.
# Note that using a single click for adjust mode failed because the mode changed when
# activating pushbuttons, checkboxes etc.
class InputEnc:
    def __init__(self, nxt, sel, prev, encoder):
        from gui.primitives import Encoder

        self._encoder = encoder  # Encoder in use
        self._enc = Encoder(nxt, prev, div=encoder, callback=self.enc_cb)
        self._precision = False  # Precision mode
        self._adj = False  # Adjustment mode
        self._sel = Pushbutton(sel, suppress=True)
        self._sel.release_func(self.release)  # Widgets are selected on release.
        self._sel.long_func(self.precision, (True,))  # Long press -> precision mode
        self._sel.double_func(self.adj_mode, (True,))  # Double press -> adjust mode

    # Screen.adjust: adjust the value of a widget. In this case 1st button arg
    # is an int (discarded), val is the delta. (With button interface 1st arg
    # is the button, delta is +1 or -1).
    def enc_cb(self, position, delta):  # Eencoder callback
        if self._adj:
            Screen.adjust(0, delta)
        else:
            Screen.ctrl_move(_NEXT if delta > 0 else _PREV)

    def release(self):
        self.adj_mode(False)  # Cancel adjust and precision
        Screen.sel_ctrl()

    def precision(self, val):  # Also called by Screen.ctrl_move to cancel mode
        if val:
            if not self._adj:
                self.adj_mode()
            self._precision = True
        else:
            self._precision = False
        Screen.redraw_co()

    # If v is None, toggle adjustment mode. Bool sets or clears
    def adj_mode(self, v=None):  # Set, clear or toggle adjustment mode
        self._adj = not self._adj if v is None else v
        if not self._adj:
            self._precision = False
        Screen.redraw_co()  # Redraw curret object

    def encoder(self):
        return self._encoder

    def is_precision(self):
        return self._precision

    def is_adjust(self):
        return self._adj


# Special mode where an encoder with a "press" pushbutton is the only control.
# nxt and prev are Pin instances corresponding to encoder X and Y.
# sel is a Pin for the encoder's pushbutton.
# encoder is the division ratio.
# Note that using a single click for adjust mode failed because the mode changed when
# activating pushbuttons, checkboxes etc.
class InputI2CEnc:
    def __init__(self, encoder):
        from gui.primitives import I2CEncoder

        self._encoder = encoder  # Encoder in use
        self._enc = I2CEncoder(encoder=encoder, callback=self.enc_cb)
        self._precision = False  # Precision mode
        self._adj = False  # Adjustment mode
        self._sel = Pushbutton(sel, suppress=True)
        self._sel.release_func(self.release)  # Widgets are selected on release.
        self._sel.long_func(self.precision, (True,))  # Long press -> precision mode
        self._sel.double_func(self.adj_mode, (True,))  # Double press -> adjust mode

    # Screen.adjust: adjust the value of a widget. In this case 1st button arg
    # is an int (discarded), val is the delta. (With button interface 1st arg
    # is the button, delta is +1 or -1).
    def enc_cb(self, position, delta):  # Eencoder callback
        if self._adj:
            Screen.adjust(0, delta)
        else:
            Screen.ctrl_move(_NEXT if delta > 0 else _PREV)

    def release(self):
        self.adj_mode(False)  # Cancel adjust and precision
        Screen.sel_ctrl()

    def precision(self, val):  # Also called by Screen.ctrl_move to cancel mode
        if val:
            if not self._adj:
                self.adj_mode()
            self._precision = True
        else:
            self._precision = False
        Screen.redraw_co()

    # If v is None, toggle adjustment mode. Bool sets or clears
    def adj_mode(self, v=None):  # Set, clear or toggle adjustment mode
        self._adj = not self._adj if v is None else v
        if not self._adj:
            self._precision = False
        Screen.redraw_co()  # Redraw curret object

    def encoder(self):
        return self._encoder

    def is_precision(self):
        return self._precision

    def is_adjust(self):
        return self._adj


# Wrapper for global ssd object providing framebuf compatible methods.
# Must be subclassed: subclass provides input device and populates globals
# display and ssd.
class DisplayIP:
    # Populate array for clipped rect
    @staticmethod
    def crect(x, y, w, h):
        c = 4  # Clip pixels
        return array(
            "H",
            (
                x + c,
                y,
                x + w - c,
                y,
                x + w,
                y + c,
                x + w,
                y + h - c,
                x + w - c,
                y + h,
                x + c,
                y + h,
                x,
                y + h - c,
                x,
                y + c,
            ),
        )

    def __init__(self, ipdev):
        self.ipdev = ipdev
        self.height = ssd.height
        self.width = ssd.width
        self._is_grey = False  # Not greyed-out

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
    def _getcolor(self, color):
        # Takes in an integer color, bit size dependent on driver
        return color_map[GREY_OUT] if self._is_grey and color != color_map[BG] else color

    def usegrey(self, val):  # display.usegrey(True) sets greyed-out
        self._is_grey = val
        return self

    # Graphics primitives: despatch to device (i.e. framebuf) or
    # local function for methods not implemented by framebuf.
    # These methods support greying out color overrides.
    # Clear screen.
    def clr_scr(self):
        ssd.fill_rect(0, 0, self.width, self.height, color_map[BG])

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

    def circle(self, x0, y0, r, color):  # Draw circle (maybe grey)
        color = self._getcolor(color)
        ssd.ellipse(int(x0), int(y0), int(r), int(r), color)

    def fillcircle(self, x0, y0, r, color):  # Draw filled circle
        color = self._getcolor(color)
        ssd.ellipse(int(x0), int(y0), int(r), int(r), color, True)

    def clip_rect(self, x, y, w, h, color):
        ssd.poly(0, 0, self.crect(x, y, w, h), self._getcolor(color))

    def fill_clip_rect(self, x, y, w, h, color):
        ssd.poly(0, 0, self.crect(x, y, w, h), self._getcolor(color), True)


# Define an input device and populate global ssd and display objects.
class Display(DisplayIP):
    def __init__(
        self, objssd, nxt, sel, prev=None, incr=None, decr=None, encoder=False, touch=False
    ):
        global display, ssd
        ssd = objssd
        if incr is False:  # Special encoder-only mode
            if not isinstance(encoder, (int, bool)):
                assert touch is False and nxt is None and sel is None and prev is None and decr is None, "Invalid args"
                ipdev = InputI2CEnc(encoder)
            else:
                ev = isinstance(encoder, int)
                assert ev and touch is False and decr is None and prev is not None, "Invalid args"
                ipdev = InputEnc(nxt, sel, prev, encoder)
        else:
            if touch:
                from gui.primitives import ESP32Touch

                ESP32Touch.threshold(touch)
                ipdev = Input(nxt, sel, prev, incr, decr, encoder, ESP32Touch)
            else:
                ipdev = Input(nxt, sel, prev, incr, decr, encoder, Pushbutton)
        super().__init__(ipdev)
        display = self


class Screen:
    do_gc = True  # Allow user to take control of GC
    current_screen = None
    is_shutdown = asyncio.Event()
    # The lock enables user code to synchronise refresh with a realtime process.
    rfsh_lock = asyncio.Lock()
    BACK = 0
    STACK = 1
    REPLACE = 2

    @classmethod  # Called by Input when status change needs redraw of current obj
    def redraw_co(cls):
        if cls.current_screen is not None:
            obj = cls.current_screen.get_obj()
            if obj is not None:
                obj.draw = True

    @classmethod
    def ctrl_move(cls, v):
        if cls.current_screen is not None:
            display.ipdev.precision(False)  # Cancel precision mode
            cls.current_screen.move(v)

    @classmethod
    def sel_ctrl(cls):
        if cls.current_screen is not None:
            display.ipdev.precision(False)  # Cancel precision mode
            cls.current_screen.do_sel()

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
            if obj.visible:  # In a buttonlist only show visible button
                if force or obj.draw:
                    obj.show()

    @classmethod
    def change(cls, cls_new_screen, mode=1, *, args=[], kwargs={}):
        ins_old = cls.current_screen
        # If initialising ensure there is an event loop before instantiating the
        # first Screen: it may create tasks in the constructor.
        if ins_old is None:
            loop = asyncio.get_event_loop()
        else:  # Leaving an existing screen
            for entry in ins_old.tasks:
                # Always cancel on back. Also on forward if requested.
                if entry[1] or not mode:
                    entry[0].cancel()
                    ins_old.tasks.remove(entry)  # remove from list
            ins_old.on_hide()  # Optional method in subclass
        if mode:
            if isinstance(cls_new_screen, type):
                if isinstance(ins_old, Window):
                    raise ValueError("Windows are modal.")
                if mode == cls.REPLACE and isinstance(cls_new_screen, Window):
                    raise ValueError("Windows must be stacked.")
                ins_new = cls_new_screen(*args, **kwargs)
                if not len(ins_new.lstactive):
                    raise ValueError("Screen has no active widgets.")
            else:
                raise ValueError("Must pass Screen class or subclass (not instance)")
            # REPLACE: parent of new screen is parent of current screen
            ins_new.parent = ins_old if mode == cls.STACK else ins_old.parent
        else:
            ins_new = cls_new_screen  # cls_new_screen is an object, not a class
        display.ipdev.adj_mode(False)  # Ensure normal mode
        cls.current_screen = ins_new
        ins_new.on_open()  # Optional subclass method
        ins_new._do_open(ins_old)  # Clear and redraw
        ins_new.after_open()  # Optional subclass method
        if ins_old is None:  # Initialising
            loop.run_until_complete(cls.monitor())  # Starts and ends uasyncio
            # asyncio is no longer running
            if hasattr(ssd, "shutdown"):
                ssd.shutdown()  # An EPD with a special shutdown method.
            else:
                ssd.fill(0)
                ssd.show()
            cls.current_screen = None  # Ensure another demo can run
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

    # If the display driver has an async refresh method, determine the split
    # value which must be a factor of the height. In the unlikely event of
    # no factor, do_refresh confers no benefit, so use synchronous code.
    @classmethod
    async def auto_refresh(cls):
        arfsh = hasattr(ssd, "do_refresh")  # Refresh can be asynchronous.
        gran = hasattr(ssd, "lock_mode")  # Allow granular locking
        if arfsh:
            h = ssd.height
            split = max(y for y in (1, 2, 3, 5, 7) if not h % y)
            if split == 1:
                arfsh = False
        while True:
            Screen.show(False)  # Update stale controls. No physical refresh.
            # Now perform physical refresh.
            # If there is no user locking, .rfsh_lock will be acquired immediately
            if arfsh and gran and ssd.lock_mode:  # Async refresh, display driver can handle lock
                # User locking is granular: lock is released at intervals during refresh
                await ssd.do_refresh(split, cls.rfsh_lock)
            else:  # Either synchronous refresh or old style device driver
                # Lock for the entire refresh period.
                async with cls.rfsh_lock:
                    await asyncio.sleep_ms(0)  # Allow other tasks to detect lock
                    if arfsh:
                        await ssd.do_refresh(split)
                    else:
                        ssd.show()  # Synchronous (blocking) refresh.
            await asyncio.sleep_ms(0)  # Let user code respond to lock release

    @classmethod
    def back(cls):
        parent = cls.current_screen.parent
        if parent is None:  # Closing base screen. Quit.
            cls.shutdown()
        else:
            cls.change(parent, cls.BACK)

    @classmethod
    def addobject(cls, obj):
        cs = cls.current_screen
        if cs is None:
            raise OSError("You must create a Screen instance")
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
        if Screen.current_screen is None and Screen.do_gc:  # Initialising class and task
            # Here we create singleton tasks
            asyncio.create_task(self._garbage_collect())
        Screen.current_screen = self
        self.parent = None

    def _do_open(self, old_screen):  # Window overrides
        dev = display.usegrey(False)
        # If opening a Screen from a Window just blank and redraw covered area
        if isinstance(old_screen, Window):
            x0, y0, x1, y1, w, h = old_screen._list_dims()
            dev.fill_rect(x0, y0, w, h, color_map[BG])  # Blank to screen BG
            for obj in [z for z in self.displaylist if z.overlaps(x0, y0, x1, y1)]:
                if obj.visible:
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
    def move(self, to):
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
                done = True

    # Move currency to a specific control.
    def move_to(self, obj):
        lo = self.get_obj()  # Old current object
        for idx in range(len(self.lstactive)):
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

    def do_adj(self, button, val):
        co = self.get_obj()
        if co is not None and hasattr(co, "do_adj"):
            co.do_adj(button, val)  # Widget can handle up/down
        else:
            Screen.current_screen.move(_FIRST if val < 0 else _LAST)

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
        return task

    async def _garbage_collect(self):
        n = 0
        while Screen.do_gc:
            await asyncio.sleep_ms(500)
            gc.collect()
            n += 1
            n &= 0x1F
            _vb and (not n) and print("Free RAM", gc.mem_free())


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

    def __init__(
        self,
        row,
        col,
        height,
        width,
        *,
        draw_border=True,
        bgcolor=None,
        fgcolor=None,
        writer=None,
    ):
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
    def __init__(
        self,
        writer,
        row,
        col,
        height,
        width,
        fgcolor,
        bgcolor,
        bdcolor,
        value=None,
        active=False,
    ):
        self.active = active
        # By default widgets cannot be adjusted: no green border in adjust mode
        self.adjustable = False
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
        self.visible = True  # Used by ButtonList class for invisible buttons
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
        # Default colors allow restoration after dynamic change (Label)
        self.def_fgcolor = fgcolor
        self.def_bgcolor = bgcolor
        self.def_bdcolor = bdcolor
        # has_border is True if a border was drawn
        self.has_border = False
        self.callback = lambda *_: None  # Value change callback
        self.args = []

    def warning(self):
        print(
            "Warning: attempt to create {} outside screen dimensions.".format(
                self.__class__.__name__
            )
        )

    def value(self, val=None):  # User method to get or set value
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
        if hasattr(self, "label"):
            self.label.value(text, invert, fgcolor, bgcolor, bdcolor)
        else:
            raise ValueError("Method {}.text does not exist.".format(self.__class__.__name__))

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
            # print('border', self, display.ipdev.is_adjust())
            if self.has_focus() and not isinstance(self, DummyWidget):
                color = color_map[FOCUS]
                precision = (
                    hasattr(self, "do_precision")
                    and self.do_precision
                    and display.ipdev.is_precision()
                )
                if precision:
                    color = self.prcolor
                elif display.ipdev.is_adjust() and self.adjustable:
                    color = color_map[ADJUSTING]
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

    def overlaps(self, xa, ya, xb, yb):  # Args must be sorted: xb > xa and yb > ya
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
                self.show()
        return self._greyed_out

    # Button press methods. Called from Screen if object not greyed out.
    # For subclassing if specific behaviour is required.
    def do_sel(self):  # Select button was pushed
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
    def __init__(
        self,
        writer,
        row,
        col,
        height,
        width,
        fgcolor,
        bgcolor,
        bdcolor,
        value=None,
        active=True,
        prcolor=False,
        min_delta=0.01,
        max_delta=0.1,
    ):
        self.min_delta = min_delta
        self.max_delta = max_delta
        super().__init__(writer, row, col, height, width, fgcolor, bgcolor, bdcolor, value, active)
        self.adjustable = True  # Can show adjustable border
        self.do_precision = prcolor is not False
        if self.do_precision:
            self.prcolor = color_map[PRECISION] if prcolor is None else prcolor

    # Adjust widget's value. Args: button pressed, amount of increment
    def do_adj(self, button, val):
        d = self.min_delta * 0.1 if self.precision() else self.min_delta
        self.value(self.value() + val * d)
        if not display.ipdev.encoder():
            asyncio.create_task(self.btnhan(button, val, d))

    # Handle increase and decrease buttons. Redefined by textbox.py, scale_log.py
    async def btnhan(self, button, up, d):
        maxd = self.max_delta if self.precision() else d * 4  # Why move fast in precision mode?
        t = ticks_ms()
        while button():
            await asyncio.sleep_ms(0)  # Quit fast on button release
            if ticks_diff(ticks_ms(), t) > 500:  # Button was held down
                d = min(maxd, d * 2)
                self.value(self.value() + up * d)
                t = ticks_ms()

    # Get current status (also used by scale_log widget)
    def precision(self):
        return self.do_precision and display.ipdev.is_precision()


# The dummy enables popup windows by satisfying the need for at least one active
# widget on a screen. It is invisible and is drawn by Window constructor before
# any user labels..
class DummyWidget(Widget):
    def __init__(self, writer, window):
        super().__init__(
            writer,
            window.row + 1,
            window.col + 1,
            4,
            4,
            window.fgcolor,
            window.bgcolor,
            False,
            None,
            True,
        )
