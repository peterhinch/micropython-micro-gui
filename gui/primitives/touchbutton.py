# touchbutton.py

# Copyright (c) 2018-2022 Peter Hinch
# Released under the MIT License (MIT) - see LICENSE file

# API is as per Pushbutton class with the following deviations:
# Assumes button is untouched at start so lacks sense constructor arg.
# Has sensitivity class variable.

import uasyncio as asyncio
import utime as time
from machine import TouchPad
from . import launch, Delay_ms

class Touchbutton:
    sensitivity = 0.9
    debounce_ms = 50
    long_press_ms = 1000
    double_click_ms = 400
    def __init__(self, pin, suppress=False):
        try:
            self._pad = TouchPad(pin)
        except ValueError:
            raise ValueError(pin)  # Let's have a bit of information :)
        self._thresh = 0  # Detection threshold
        self._supp = suppress
        self._dblpend = False  # Doubleclick waiting for 2nd click
        self._dblran = False  # Doubleclick executed user function
        self._tf = False
        self._ff = False
        self._df = False
        self._ld = False  # Delay_ms instance for long press
        self._dd = False  # Ditto for doubleclick
        self.state = False  # Initial state
        self._run = asyncio.create_task(self.buttoncheck())  # Thread runs forever

    def press_func(self, func=False, args=()):
        self._tf = func
        self._ta = args

    def release_func(self, func=False, args=()):
        self._ff = func
        self._fa = args

    def double_func(self, func=False, args=()):
        self._df = func
        self._da = args
        if func:  # If double timer already in place, leave it
            if not self._dd:
                self._dd = Delay_ms(self._ddto)
        else:
            self._dd = False  # Clearing down double func

    def long_func(self, func=False, args=()):
        if func:
            if self._ld:
                self._ld.callback(func, args)
            else:
                self._ld = Delay_ms(func, args)
        else:
            self._ld = False

    async def _get_thresh(self):
        await asyncio.sleep_ms(50)
        self._thresh = round(self._pad.read() * Touchbutton.sensitivity)
        # print(self._thresh)

    # Current logical button state: True == pressed
    def rawstate(self):
        return self._pad.read() < self._thresh

    # Current debounced state of button (True == pressed)
    def __call__(self):
        return self.state

    def _ddto(self):  # Doubleclick timeout: no doubleclick occurred
        self._dblpend = False
        if self._supp and not self.state:
            if not self._ld or (self._ld and not self._ld()):
                launch(self._ff, self._fa)

    async def buttoncheck(self):
        await self._get_thresh()
        while True:
            state = self.rawstate()
            # State has changed: act on it now.
            if state != self.state:
                self.state = state
                if state:  # Button pressed: launch pressed func
                    if self._tf:
                        launch(self._tf, self._ta)
                    if self._ld:  # There's a long func: start long press delay
                        self._ld.trigger(Touchbutton.long_press_ms)
                    if self._df:
                        if self._dd():  # Second click: timer running
                            self._dd.stop()
                            self._dblpend = False
                            self._dblran = True  # Prevent suppressed launch on release
                            launch(self._df, self._da)
                        else:
                            # First click: start doubleclick timer
                            self._dd.trigger(Touchbutton.double_click_ms)
                            self._dblpend = True  # Prevent suppressed launch on release
                else:  # Button release. Is there a release func?
                    if self._ff:
                        if self._supp:
                            d = self._ld 
                            # If long delay exists, is running and doubleclick status is OK
                            if not self._dblpend and not self._dblran:
                                if (d and d()) or not d:
                                    launch(self._ff, self._fa)
                        else:
                            launch(self._ff, self._fa)
                    if self._ld:
                        self._ld.stop()  # Avoid interpreting a second click as a long push
                    self._dblran = False
            # Ignore state changes until switch has settled
            # See https://github.com/peterhinch/micropython-async/issues/69
            await asyncio.sleep_ms(Touchbutton.debounce_ms)

    def deinit(self):
        self._run.cancel()
